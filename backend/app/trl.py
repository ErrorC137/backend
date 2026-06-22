"""Technology Readiness Level (TRL) evaluation — enhanced with DeepSeek API."""

from __future__ import annotations

import re
from typing import Any

# Import DeepSeek-enhanced evaluation
try:
    from app.deepseek_trl import evaluate_trl_with_deepseek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False


def _milestone_status(trl: int, completed_at: int, current_at: int | tuple[int, ...]) -> str:
    if trl >= completed_at:
        return "completed"
    if isinstance(current_at, tuple):
        if trl in current_at:
            return "current"
    elif trl == current_at:
        return "current"
    return "future"


def evaluate_trl(
    analysis_text: str,
    *,
    classification: dict[str, Any] | None = None,
    valuation: dict[str, Any] | None = None,
    title_hint: str = "",
    use_deepseek: bool = True,
) -> dict[str, Any]:
    """
    Infer NASA/EU TRL 1–9 from document text and pipeline signals.
    Uses DeepSeek API for enhanced analysis when available, falls back to regex-based evaluation.
    """
    # Try DeepSeek-enhanced evaluation first if available and enabled
    if use_deepseek and DEEPSEEK_AVAILABLE:
        try:
            result = evaluate_trl_with_deepseek(
                analysis_text,
                classification=classification,
                valuation=valuation,
                title_hint=title_hint
            )
            # Add analysis source indicator
            result["analysis_source"] = f"{result.get('analysis_source', 'unknown')}"
            return result
        except Exception as e:
            print(f"DeepSeek evaluation failed, falling back to regex: {e}")
    
    # Fallback to original regex-based evaluation
    return _evaluate_trl_regex(analysis_text, classification=classification, valuation=valuation, title_hint=title_hint)


def _evaluate_trl_regex(
    analysis_text: str,
    *,
    classification: dict[str, Any] | None = None,
    valuation: dict[str, Any] | None = None,
    title_hint: str = "",
) -> dict[str, Any]:
    """Original regex-based TRL evaluation as fallback."""
    text = f"{title_hint}\n{analysis_text}".lower()
    sector = (classification or {}).get("sector_name", "Deep Tech")

    trl = 3
    if re.search(r"production|market|customer|licensed|factory|commercial|certified|faa|deployed", text):
        trl = 8
    elif re.search(r"pilot\s+plant|refinery|field\s+test|operational\s+environment|demonstration\s+system", text):
        trl = 7
    elif re.search(r"pilot|plant|refinery|environment|field test|operational", text):
        trl = 6
    elif re.search(r"prototype|functional|assembly|working model|bench[- ]scale|validated\s+in\s+lab", text):
        trl = 4
    elif re.search(r"theory|concept|simulated|modeling|formulate|computational", text):
        trl = 2

    # Boost TRL slightly when valuation anchor is high (proxy for commercial maturity)
    if valuation:
        anchor = valuation.get("v_target_usd", 0)
        if anchor > 5_000_000 and trl < 6:
            trl = min(6, trl + 1)

    trl = max(1, min(9, trl))

    accomplishments: list[str] = []
    if trl >= 2:
        accomplishments.append("Formulated research framework and validated theoretical foundations.")
    if trl >= 3:
        accomplishments.append("Completed initial laboratory synthesis and bench-scale validations.")
    if trl >= 5:
        accomplishments.append("Demonstrated functional prototype performance in controlled environments.")
    if trl >= 7:
        accomplishments.append("Validated system performance under operational or pilot-scale conditions.")
    if trl >= 8:
        accomplishments.append("Achieved certification or pre-production readiness milestones.")

    originality_boost = 0
    innovation_score = min(99, max(45, 40 + trl * 6 + originality_boost))

    if valuation:
        s_orig = valuation.get("s_originality", 0)
        innovation_score = min(99, max(innovation_score, int(50 + s_orig * 100)))

    trl_summary = (
        f"Classified at Technology Readiness Level {trl} based on evidence in the submitted document. "
        f"Sector context: {sector}. "
        + (
            "The work shows commercialization signals including production, certification, or market deployment language."
            if trl >= 7
            else "The work indicates laboratory or prototype-stage validation with further scale-up required."
            if trl >= 4
            else "The work is primarily research-stage with proof-of-concept or theoretical foundations."
        )
    )

    partnership = (
        "Strong outlook for scale-up joint fabrication and licensing with tier-1 manufacturers."
        if trl >= 7
        else "Well suited for deep-tech seed funds, government grants, and strategic pilot partners."
        if trl >= 4
        else "Ideal for academic partnerships, incubator programs, and early-stage research grants."
    )

    milestones = {
        "prototype": {
            "status": _milestone_status(trl, 4, 4),
            "description": "Build and validate a working bench-scale demonstration of core technology.",
            "timeline": "Completed Q2 2025" if trl >= 4 else "Target Q4 2026",
        },
        "mvp": {
            "status": _milestone_status(trl, 6, (5, 6)),
            "description": "Develop minimum viable product or sub-scale integrated system for partner evaluation.",
            "timeline": "Completed Q4 2025" if trl >= 6 else "Target Q2 2027",
        },
        "pilot_test": {
            "status": _milestone_status(trl, 8, 7),
            "description": "Deploy pilot system in relevant operational environment with continuous monitoring.",
            "timeline": "Completed Q1 2026" if trl >= 8 else "Target Q1 2028",
        },
        "commercialization": {
            "status": _milestone_status(trl, 9, 8),
            "description": "Industrial scale-up, regulatory approval, and commercial licensing agreements.",
            "timeline": "Completed Q2 2026" if trl == 9 else "Target Q4 2028",
        },
    }

    return {
        "trl": trl,
        "trl_summary": trl_summary,
        "accomplishments": accomplishments,
        "potential_partnership": partnership,
        "innovation_score": innovation_score,
        "milestones": milestones,
        "sector_name": sector,
        "analysis_source": "regex-fallback",
        "confidence": 0.6,
        "key_indicators": [],
        "missing_for_next_trl": []
    }
