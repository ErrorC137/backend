"""End-to-end analysis pipeline."""

from __future__ import annotations

from typing import Any
import time

from app.classifier import classify_document
from app.fto import analyze_fto
from app.ingestion import parse_upload
from app.originality import compute_originality
from app.security import sign_report
from app.trl import evaluate_trl
from app.valuation import calculate_valuation
from app.patent_data import patent_service
from app.nlp_analysis import nlp_analyzer
from app.market_mapping import analyze_market_mapping
from app.comprehensive_analysis import generate_comprehensive_analysis

# Import DeepSeek enhancements
try:
    from app.deepseek_valuation import enhance_valuation_with_deepseek, enhance_due_diligence_with_deepseek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False

# API usage tracking
api_usage = {
    "deepseek_calls": 0,
    "openai_calls": 0,
    "cohere_calls": 0,
    "patent_api_calls": 0,
    "total_analysis_time": 0
}


async def run_analysis(filename: str, content: bytes) -> dict[str, Any]:
    start_time = time.time()
    
    doc = parse_upload(filename, content)
    analysis_text = f"{doc.abstract}\n{doc.methodology}\n{doc.claims_outcomes}"

    classification = classify_document(analysis_text)
    
    # Enhanced originality with real patent data
    originality = compute_originality(analysis_text)
    
    # Try to get real patent matches from external sources
    try:
        patent_analysis = await patent_service.get_comprehensive_patent_analysis(
            query=doc.abstract[:200] if doc.abstract else analysis_text[:200],
            text_content=analysis_text,
            limit=10
        )
        api_usage["patent_api_calls"] += 1
        
        # If we got real patent data, enhance originality with it
        if patent_analysis["total_matches"] > 0:
            originality["external_patent_matches"] = patent_analysis
            originality["max_cosine_similarity"] = max(
                originality.get("max_cosine_similarity", 0),
                patent_analysis["max_similarity"]
            )
            # Update top matches with real data
            if patent_analysis["top_matches"]:
                originality["top_matches"] = [
                    {
                        "patent_id": match.patent_id,
                        "title": match.title,
                        "ipc": classification.get("ipc_primary", "C01B"),
                        "cosine_similarity": match.similarity_score
                    }
                    for match in patent_analysis["top_matches"]
                ]
    except Exception as e:
        # Fall back to original originality calculation if patent service fails
        pass
    
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

    # Perform comprehensive NLP analysis
    nlp_analysis = nlp_analyzer.comprehensive_analysis(analysis_text)
    
    # Perform market mapping analysis
    market_mapping = analyze_market_mapping(
        analysis_text,
        classification,
        trl_evaluation.get("estimated_trl", 3),
        doc.document_type,
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
            api_usage["deepseek_calls"] += 1
            due_diligence_report = enhance_due_diligence_with_deepseek(
                analysis_text,
                classification=classification,
                title_hint=doc.abstract[:120] if doc.abstract else "",
            )
            api_usage["deepseek_calls"] += 1
        except Exception as e:
            print(f"DeepSeek enhancement failed: {e}")

    # Calculate total analysis time
    total_time = time.time() - start_time
    api_usage["total_analysis_time"] = round(total_time, 2)

    # Generate comprehensive analysis with detailed paragraphs
    comprehensive_analysis = generate_comprehensive_analysis(
        doc=doc,
        classification=classification,
        originality=originality,
        fto=fto,
        valuation=enhanced_valuation,
        trl_evaluation=trl_evaluation,
        market_mapping=market_mapping,
        nlp_analysis=nlp_analysis,
    )

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
            "similarity_method": originality.get("external_patent_matches", {}).get("similarity_method", "unknown"),
        },
        "fto": fto,
        "valuation": enhanced_valuation,
        "trl_evaluation": trl_evaluation,
        "due_diligence_report": due_diligence_report,
        "nlp_analysis": nlp_analysis,
        "market_mapping": market_mapping,
        "comprehensive_analysis": comprehensive_analysis,
        "document_stats": {
            "abstract_chars": len(doc.abstract),
            "methodology_chars": len(doc.methodology),
            "claims_chars": len(doc.claims_outcomes),
        },
        "api_usage": api_usage.copy(),
    }

    return sign_report(result)
