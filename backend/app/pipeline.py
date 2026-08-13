"""End-to-end analysis pipeline."""

from __future__ import annotations

from typing import Any
import os
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


def _calculate_originality_confidence(originality: dict, doc: Any) -> dict:
    """Calculate confidence score for originality assessment."""
    score = 0.5  # Base confidence
    factors = []
    
    # Factor 1: Patent corpus size (larger corpus = higher confidence)
    corpus_size = originality.get("patent_corpus_size", 0)
    if corpus_size > 1000:
        score += 0.2
        factors.append("Large patent corpus")
    elif corpus_size > 500:
        score += 0.1
        factors.append("Moderate patent corpus")
    
    # Factor 2: Document quality (more content = higher confidence)
    word_count = len(doc.raw_text.split()) if doc else 0
    if word_count > 1000:
        score += 0.15
        factors.append("Comprehensive document content")
    elif word_count > 500:
        score += 0.08
        factors.append("Adequate document content")
    
    # Factor 3: Similarity method quality
    similarity_method = originality.get("similarity_method", "unknown")
    if similarity_method == "external_patent_api":
        score += 0.15
        factors.append("External patent API data")
    elif similarity_method == "embedding":
        score += 0.05
        factors.append("Embedding-based similarity")
    
    # Factor 4: Number of patent matches (more matches = more data points)
    top_matches = len(originality.get("top_patent_matches", []))
    if top_matches > 5:
        score += 0.1
        factors.append("Multiple patent references")
    elif top_matches > 2:
        score += 0.05
        factors.append("Some patent references")
    
    # Factor 5: Parsing confidence
    if doc and hasattr(doc, 'parsing_confidence'):
        if doc.parsing_confidence > 0.8:
            score += 0.1
            factors.append("High parsing confidence")
        elif doc.parsing_confidence > 0.6:
            score += 0.05
            factors.append("Moderate parsing confidence")
    
    # Cap score at 1.0
    score = min(score, 1.0)
    
    # Determine confidence level
    if score >= 0.8:
        level = "high"
    elif score >= 0.6:
        level = "medium"
    else:
        level = "low"
    
    return {
        "score": score,
        "level": level,
        "factors": factors,
    }


def _calculate_fto_confidence(fto: dict, originality: dict, doc: Any) -> dict:
    """Calculate confidence score for FTO assessment."""
    score = 0.5  # Base confidence
    factors = []
    
    # Factor 1: Originality data quality (better originality = better FTO)
    originality_score = originality.get("max_cosine_similarity", 1)
    if originality_score < 0.3:
        score += 0.2
        factors.append("Low similarity to existing patents")
    elif originality_score < 0.5:
        score += 0.1
        factors.append("Moderate similarity to existing patents")
    
    # Factor 2: Risk tier clarity
    risk_tier = fto.get("risk_tier_pct", 50)
    if risk_tier < 20 or risk_tier > 80:
        score += 0.15
        factors.append("Clear risk tier indication")
    elif risk_tier < 40 or risk_tier > 60:
        score += 0.08
        factors.append("Moderate risk tier indication")
    
    # Factor 3: Document methodology quality
    if doc and len(doc.methodology) > 500:
        score += 0.15
        factors.append("Detailed methodology description")
    elif doc and len(doc.methodology) > 200:
        score += 0.08
        factors.append("Basic methodology description")
    
    # Factor 4: Expert consultation flag
    if not fto.get("expert_consultation_required", False):
        score += 0.1
        factors.append("No expert consultation required")
    
    # Factor 5: Patent match quality
    top_matches = originality.get("top_patent_matches", [])
    if len(top_matches) > 0:
        score += 0.1
        factors.append("Patent references available")
    
    # Cap score at 1.0
    score = min(score, 1.0)
    
    # Determine confidence level
    if score >= 0.8:
        level = "high"
    elif score >= 0.6:
        level = "medium"
    else:
        level = "low"
    
    return {
        "score": score,
        "level": level,
        "factors": factors,
    }


def _calculate_valuation_confidence(valuation: dict, trl_evaluation: dict, doc: Any) -> dict:
    """Calculate confidence score for valuation assessment."""
    score = 0.5  # Base confidence
    factors = []
    
    # Factor 1: TRL level (higher TRL = more confident valuation)
    trl = trl_evaluation.get("trl", 3)
    if trl >= 7:
        score += 0.2
        factors.append("High TRL (commercialization stage)")
    elif trl >= 5:
        score += 0.15
        factors.append("Medium-high TRL (validation stage)")
    elif trl >= 3:
        score += 0.08
        factors.append("Medium TRL (development stage)")
    
    # Factor 2: TRL confidence
    trl_confidence = trl_evaluation.get("confidence", 0.5)
    if trl_confidence > 0.8:
        score += 0.15
        factors.append("High TRL assessment confidence")
    elif trl_confidence > 0.6:
        score += 0.08
        factors.append("Moderate TRL assessment confidence")
    
    # Factor 3: Valuation range spread (narrower range = higher confidence)
    v_baseline = valuation.get("v_baseline_usd", 0)
    v_target = valuation.get("v_target_usd", 0)
    if v_baseline > 0 and v_target > 0:
        spread = abs(v_target - v_baseline) / v_baseline
        if spread < 0.5:
            score += 0.15
            factors.append("Narrow valuation range")
        elif spread < 1.0:
            score += 0.08
            factors.append("Moderate valuation range")
    
    # Factor 4: Market data availability
    if valuation.get("market_potential") and valuation.get("market_potential") != "Unknown":
        score += 0.1
        factors.append("Market potential data available")
    
    # Factor 5: Document completeness
    if doc and len(doc.abstract) > 200 and len(doc.methodology) > 300:
        score += 0.1
        factors.append("Comprehensive document content")
    
    # Cap score at 1.0
    score = min(score, 1.0)
    
    # Determine confidence level
    if score >= 0.8:
        level = "high"
    elif score >= 0.6:
        level = "medium"
    else:
        level = "low"
    
    return {
        "score": score,
        "level": level,
        "factors": factors,
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
        doc=doc,
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

    # Use the multi-agent system when at least one configured provider is
    # available.  The integration layer falls back to the deterministic report
    # if an upstream provider is unavailable or fails.
    comprehensive_analysis = await generate_comprehensive_analysis(
        doc=doc,
        classification=classification,
        originality=originality,
        fto=fto,
        valuation=enhanced_valuation,
        trl_evaluation=trl_evaluation,
        market_mapping=market_mapping,
        nlp_analysis=nlp_analysis,
        title=doc.abstract[:100] if doc.abstract else filename,
        use_multi_agent=os.getenv("ENABLE_MULTI_AGENT", "true").lower() == "true",
    )

    # Calculate confidence scores for key metrics
    originality_confidence = _calculate_originality_confidence(originality, doc)
    fto_confidence = _calculate_fto_confidence(fto, originality, doc)
    valuation_confidence = _calculate_valuation_confidence(valuation, trl_evaluation, doc)

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
            "confidence": originality_confidence,
        },
        "fto": {
            **fto,
            "confidence": fto_confidence,
        },
        "valuation": {
            **enhanced_valuation,
            "confidence": valuation_confidence,
        },
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
        "confidence_metrics": {
            "originality": originality_confidence,
            "fto": fto_confidence,
            "valuation": valuation_confidence,
            "overall": (originality_confidence["score"] + fto_confidence["score"] + valuation_confidence["score"]) / 3,
        },
        "api_usage": api_usage.copy(),
    }

    return sign_report(result)
