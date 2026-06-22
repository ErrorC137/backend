"""End-to-end analysis pipeline."""

from __future__ import annotations

from typing import Any

from app.classifier import classify_document
from app.fto import analyze_fto
from app.ingestion import parse_upload
from app.originality import compute_originality
from app.security import sign_report
from app.trl import evaluate_trl
from app.valuation import calculate_valuation

# Import DeepSeek enhancements
try:
    from app.deepseek_valuation import enhance_valuation_with_deepseek, enhance_due_diligence_with_deepseek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False


async def run_analysis(filename: str, content: bytes) -> dict[str, Any]:
    doc = parse_upload(filename, content)
    analysis_text = f"{doc.abstract}\n{doc.methodology}\n{doc.claims_outcomes}"

    classification = classify_document(analysis_text)
    originality = compute_originality(analysis_text)
    fto = await analyze_fto(doc.methodology, originality["top_matches"])
    valuation = calculate_valuation(
        classification["ipc_primary"],
        originality["originality_premium_s"],
        fto["r_fto"],
        fto["expert_consultation_required"],
        classification=classification,
        originality=originality,
        fto=fto,
    )
    trl_evaluation = evaluate_trl(
        analysis_text,
        classification=classification,
        valuation=valuation,
        title_hint=doc.abstract[:120] if doc.abstract else "",
    )

    # Enhance with DeepSeek if available
    enhanced_valuation = valuation
    due_diligence_report = {}
    
    if DEEPSEEK_AVAILABLE:
        try:
            enhanced_valuation = enhance_valuation_with_deepseek(
                analysis_text,
                classification=classification,
                valuation=valuation,
                fto=fto,
                originality=originality,
                title_hint=doc.abstract[:120] if doc.abstract else "",
            )
            due_diligence_report = enhance_due_diligence_with_deepseek(
                analysis_text,
                classification=classification,
                title_hint=doc.abstract[:120] if doc.abstract else "",
            )
        except Exception as e:
            print(f"DeepSeek enhancement failed: {e}")

    result = {
        "document_profile": {
            "document_type": doc.document_type,
            "parsing_confidence": doc.parsing_confidence,
            "sections_found": doc.sections_found,
            "word_count": len(doc.raw_text.split()),
            "supports_tokenization": True,
            "note": (
                "Any scientific paper, preprint, or technical report can be processed through the same "
                "IPC classification → OpenAI embedding originality → FTO → USD valuation pipeline."
            ),
        },
        "classification": classification,
        "originality": {
            "max_cosine_similarity": originality["max_cosine_similarity"],
            "originality_premium_s": originality["originality_premium_s"],
            "embedding_model": originality["embedding_model"],
            "patent_corpus_size": originality["patent_corpus_size"],
            "top_patent_matches": originality["top_matches"][:5],
        },
        "fto": fto,
        "valuation": enhanced_valuation,
        "trl_evaluation": trl_evaluation,
        "due_diligence_report": due_diligence_report,
        "document_stats": {
            "abstract_chars": len(doc.abstract),
            "methodology_chars": len(doc.methodology),
            "claims_chars": len(doc.claims_outcomes),
        },
    }

    return sign_report(result)
