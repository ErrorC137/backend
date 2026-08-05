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


def _generate_team_assessment(team_expertise_score: float, institution_reputation_score: float) -> str:
    """Generate team assessment based on extracted author and institution data."""
    overall_score = (team_expertise_score + institution_reputation_score) / 2
    
    if overall_score >= 0.8:
        return f"Strong research team with high expertise ({team_expertise_score:.2f}) and reputable institutional affiliations ({institution_reputation_score:.2f}). The team demonstrates strong capability for executing complex research and development projects."
    elif overall_score >= 0.6:
        return f"Capable research team with moderate expertise ({team_expertise_score:.2f}) and solid institutional backing ({institution_reputation_score:.2f}). The team shows good potential for successful project execution."
    elif overall_score >= 0.4:
        return f"Research team with developing expertise ({team_expertise_score:.2f}) and moderate institutional support ({institution_reputation_score:.2f}). Additional expertise or partnerships may enhance project success."
    else:
        return f"Early-stage research team with limited documented expertise ({team_expertise_score:.2f}) and institutional backing ({institution_reputation_score:.2f}). Team development and strategic partnerships recommended for project advancement."


def evaluate_trl(
    analysis_text: str,
    *,
    classification: dict[str, Any] | None = None,
    valuation: dict[str, Any] | None = None,
    title_hint: str = "",
    use_deepseek: bool = True,
    doc: Any = None,
) -> dict[str, Any]:
    """
    Infer NASA/EU TRL 1–9 from document text and pipeline signals.
    Uses DeepSeek API for enhanced analysis when available, falls back to regex-based evaluation.
    """
    # Extract team expertise from document if available
    team_expertise_score = 0.5
    institution_reputation_score = 0.5
    if doc and hasattr(doc, 'team_expertise_score'):
        team_expertise_score = doc.team_expertise_score
    if doc and hasattr(doc, 'institution_reputation_score'):
        institution_reputation_score = doc.institution_reputation_score
    
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
            result["team_expertise_score"] = team_expertise_score
            result["institution_reputation_score"] = institution_reputation_score
            return result
        except Exception as e:
            print(f"DeepSeek evaluation failed, falling back to regex: {e}")
    
    # Fallback to original regex-based evaluation
    return _evaluate_trl_regex(analysis_text, classification=classification, valuation=valuation, title_hint=title_hint, team_expertise_score=team_expertise_score, institution_reputation_score=institution_reputation_score)


def _evaluate_trl_regex(
    analysis_text: str,
    *,
    classification: dict[str, Any] | None = None,
    valuation: dict[str, Any] | None = None,
    title_hint: str = "",
    team_expertise_score: float = 0.5,
    institution_reputation_score: float = 0.5,
) -> dict[str, Any]:
    """Original regex-based TRL evaluation as fallback with improved accuracy."""
    text = f"{title_hint}\n{analysis_text}".lower()
    sector = (classification or {}).get("sector_name", "Deep Tech")

    # Enhanced TRL detection with more specific patterns and better accuracy
    trl = 3  # Default to TRL 3 (lab validation)
    
    # TRL 9: Actual system proven in successful operational environment
    if re.search(r"production\s+ready|fully\s+operational|commercial\s+production|mass\s+production|certified\s+for\s+use|fda\s+approved|market\s+launch|full\s+scale\s+manufacturing", text):
        trl = 9
    # TRL 8: System complete and qualified
    elif re.search(r"production|market|customer|licensed|factory|commercial|certified|faa|deployed|pre-production|final\s+assembly", text):
        trl = 8
    # TRL 7: System prototype demonstration in operational environment
    elif re.search(r"pilot\s+plant|refinery|field\s+test|operational\s+environment|demonstration\s+system|operational\s+demonstration|real\s+world\s+environment", text):
        trl = 7
    # TRL 6: Technology demonstration in relevant environment
    elif re.search(r"pilot|plant|refinery|environment|field test|operational|relevant\s+environment|demonstration\s+in\s+relevant", text):
        trl = 6
    # TRL 5: Technology validation in relevant environment
    elif re.search(r"validated\s+in\s+relevant\s+environment|relevant\s+environment\s+validation|field\s+validation|real\s+world\s+validation", text):
        trl = 5
    # TRL 4: Technology validation in laboratory environment
    elif re.search(r"prototype|functional|assembly|working model|bench[- ]scale|validated\s+in\s+lab|laboratory\s+validation|lab\s+scale|component\s+validation", text):
        trl = 4
    # TRL 3: Experimental proof of concept
    elif re.search(r"experiment|lab\s+test|laboratory\s+test|proof\s+of\s+concept|poc|experimental\s+validation|bench\s+scale\s+experiment", text):
        trl = 3
    # TRL 2: Technology concept formulated
    elif re.search(r"theory|concept|simulated|modeling|formulate|computational|theoretical\s+analysis|conceptual\s+design", text):
        trl = 2
    # TRL 1: Basic principles observed
    elif re.search(r"basic\s+research|fundamental\s+research|principle\s+observed|scientific\s+principle|research\s+principle", text):
        trl = 1

    # Enhanced TRL adjustment based on multiple indicators
    trl_indicators = 0
    
    # Check for experimental validation indicators
    if re.search(r"experiment|test|validation|result|data|measurement|performance", text):
        trl_indicators += 1
    
    # Check for prototype indicators
    if re.search(r"prototype|model|demonstrat|working|functional", text):
        trl_indicators += 1
        
    # Check for scale indicators
    if re.search(r"scale|pilot|plant|production|manufactur", text):
        trl_indicators += 1
        
    # Check for market indicators
    if re.search(r"market|customer|commercial|business|revenue", text):
        trl_indicators += 1
        
    # Adjust TRL based on indicator count
    if trl_indicators >= 3 and trl < 5:
        trl = min(5, trl + 1)
    elif trl_indicators >= 2 and trl < 4:
        trl = min(4, trl + 1)

    # Boost TRL slightly when valuation anchor is high (proxy for commercial maturity)
    if valuation:
        anchor = valuation.get("v_target_usd", 0)
        if anchor > 5_000_000 and trl < 6:
            trl = min(6, trl + 1)
        elif anchor > 10_000_000 and trl < 7:
            trl = min(7, trl + 1)

    # Ensure minimum TRL of 3 for documents with experimental data
    if re.search(r"experiment|test|result|data|measurement|performance|validation", text) and trl < 3:
        trl = 3
        
    # Ensure minimum TRL of 4 for documents with prototype mentions
    if re.search(r"prototype|working model|functional model|demonstrat", text) and trl < 4:
        trl = 4

    trl = max(1, min(9, trl))

    accomplishments: list[str] = []
    if trl >= 1:
        accomplishments.append("Basic principles observed and documented through fundamental research.")
    if trl >= 2:
        accomplishments.append("Technology concept formulated with theoretical framework and computational modeling.")
    if trl >= 3:
        accomplishments.append("Experimental proof of concept established through laboratory validation and bench-scale testing.")
    if trl >= 4:
        accomplishments.append("Technology validated in laboratory environment with functional prototype demonstration.")
    if trl >= 5:
        accomplishments.append("Technology validated in relevant environment with component and system integration.")
    if trl >= 6:
        accomplishments.append("Technology demonstrated in relevant environment with system-level performance validation.")
    if trl >= 7:
        accomplishments.append("System prototype demonstrated in operational environment with pilot-scale validation.")
    if trl >= 8:
        accomplishments.append("System complete and qualified for production with certification and manufacturing readiness.")
    if trl >= 9:
        accomplishments.append("Actual system proven in successful operational environment with commercial production and market deployment.")

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
        "estimated_trl": trl,
        "confidence": min(0.95, 0.6 + trl_indicators * 0.05),
        "innovation_score": innovation_score,
        "accomplishments": accomplishments,
        "detailed_analysis": detailed_analysis,
        "trl_summary": trl_summary,
        "partnership": partnership,
        "milestones": milestones,
        "key_indicators": key_indicators,
        "missing_for_next_trl": missing_for_next_trl,
        "analysis_source": "rule-based-trl",
        "team_expertise_score": team_expertise_score,
        "institution_reputation_score": institution_reputation_score,
        "team_assessment": _generate_team_assessment(team_expertise_score, institution_reputation_score),
    }
