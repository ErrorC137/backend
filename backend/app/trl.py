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

    # Generate detailed analysis based on TRL level
    detailed_analysis = []
    if trl >= 7:
        detailed_analysis.extend([
            "Evidence of operational deployment in real-world environments detected.",
            "Production readiness indicators suggest near-term commercial viability.",
            "Certification and regulatory compliance language indicates advanced development stage.",
            "Scale-up capabilities and manufacturing processes appear established."
        ])
    elif trl >= 4:
        detailed_analysis.extend([
            "Prototype validation demonstrates technical feasibility in controlled settings.",
            "Bench-scale experimental results provide foundation for further development.",
            "Functional performance metrics indicate potential for scale-up.",
            "Laboratory validation supports progression to pilot-scale testing."
        ])
    else:
        detailed_analysis.extend([
            "Research focuses on theoretical foundations and proof-of-concept validation.",
            "Early-stage experimental work suggests promising research direction.",
            "Concept formulation indicates potential but requires substantial development.",
            "Further laboratory validation needed to establish technical feasibility."
        ])

    trl_summary = (
        f"Classified at Technology Readiness Level {trl} based on comprehensive analysis of the submitted document. "
        f"Sector context: {sector}. "
        f"Key findings: {' '.join(detailed_analysis[:3])}. "
        + (
            "The work shows strong commercialization signals including production, certification, or market deployment language, indicating readiness for scale-up and market entry."
            if trl >= 7
            else "The work indicates laboratory or prototype-stage validation with demonstrated technical feasibility, requiring further scale-up and operational environment testing before commercial deployment."
            if trl >= 4
            else "The work is primarily research-stage with proof-of-concept or theoretical foundations, requiring additional experimental validation and prototype development to advance toward commercialization."
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

    # Generate key indicators based on TRL level
    key_indicators = []
    if trl >= 7:
        key_indicators.extend([
            "Production-scale manufacturing capabilities",
            "Regulatory certification or approval status",
            "Commercial deployment in operational environments",
            "Established supply chain and distribution channels"
        ])
    elif trl >= 4:
        key_indicators.extend([
            "Functional prototype with validated performance",
            "Bench-scale experimental validation",
            "Technical feasibility demonstrated",
            "Initial performance metrics established"
        ])
    else:
        key_indicators.extend([
            "Theoretical framework established",
            "Proof-of-concept experimental results",
            "Research methodology defined",
            "Initial data collection and analysis"
        ])

    # Generate missing items for next TRL level
    missing_for_next_trl = []
    if trl < 9:
        if trl < 7:
            missing_for_next_trl.extend([
                "Develop and validate pilot-scale system",
                "Conduct operational environment testing",
                "Establish manufacturing processes",
                "Obtain necessary regulatory certifications"
            ])
        if trl < 4:
            missing_for_next_trl.extend([
                "Build and validate functional prototype",
                "Conduct comprehensive bench-scale testing",
                "Establish performance metrics and benchmarks",
                "Validate reproducibility of results"
            ])
        if trl < 2:
            missing_for_next_trl.extend([
                "Formulate clear theoretical framework",
                "Design experimental validation approach",
                "Establish research methodology",
                "Conduct initial proof-of-concept experiments"
            ])

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
        "key_indicators": key_indicators,
        "missing_for_next_trl": missing_for_next_trl,
        "detailed_analysis": detailed_analysis
    }
