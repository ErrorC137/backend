"""Enhanced TRL evaluation using DeepSeek API for more accurate analysis."""

import os
import re
from typing import Any
from openai import OpenAI

# Initialize DeepSeek client (OpenAI-compatible API)
def get_deepseek_client():
    """Get DeepSeek client for API calls."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return None
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

def evaluate_trl_with_deepseek(
    analysis_text: str,
    *,
    classification: dict[str, Any] | None = None,
    valuation: dict[str, Any] | None = None,
    title_hint: str = "",
) -> dict[str, Any]:
    """
    Enhanced TRL evaluation using DeepSeek API for more sophisticated analysis.
    Falls back to regex-based evaluation if DeepSeek API is unavailable.
    """
    client = get_deepseek_client()
    
    if not client:
        # Fallback to regex-based evaluation
        return evaluate_trl_regex(analysis_text, classification=classification, valuation=valuation, title_hint=title_hint)
    
    try:
        # Prepare the prompt for DeepSeek with more detailed analysis requirements
        prompt = f"""
You are an expert in Technology Readiness Level (TRL) assessment using the NASA TRL scale (1-9).

Analyze the following research/technology document and provide a comprehensive TRL assessment:

Title: {title_hint}
Sector: {(classification or {}).get("sector_name", "Deep Tech")}
Document Content:
{analysis_text[:4000]}  # Increased to 4000 chars for better analysis

Provide your assessment in the following JSON format:
{{
    "trl": <number 1-9>,
    "confidence": <number 0-1>,
    "reasoning": "<detailed explanation of why this TRL level was assigned, including specific evidence from the text>",
    "key_indicators": ["<list of specific indicators found in the text that support this TRL level>"],
    "missing_for_next_trl": ["<what would be needed to reach the next TRL level>"],
    "accomplishments": ["<list of accomplishments based on current TRL>"],
    "innovation_score": <number 0-100>,
    "commercial_readiness": "<low/medium/high>",
    "paper_review": {{
        "methodology_assessment": "<assessment of the methodology quality and rigor>",
        "data_quality": "<assessment of data quality and completeness>",
        "reproducibility": "<assessment of reproducibility of the research>",
        "potential_hallucinations": ["<list of any claims that might be hallucinated or unsupported>"],
        "confidence_in_analysis": "<high/medium/low>"
    }},
    "milestone_breakdown": {{
        "prototype": {{
            "status": "<completed/current/future>",
            "description": "<what needs to be done for this milestone>",
            "specific_actions": ["<list of specific actions to complete this milestone>"],
            "timeline": "<estimated timeline>",
            "resources_needed": ["<list of resources needed>"]
        }},
        "mvp": {{
            "status": "<completed/current/future>",
            "description": "<what needs to be done for this milestone>",
            "specific_actions": ["<list of specific actions to complete this milestone>"],
            "timeline": "<estimated timeline>",
            "resources_needed": ["<list of resources needed>"]
        }},
        "pilot_test": {{
            "status": "<completed/current/future>",
            "description": "<what needs to be done for this milestone>",
            "specific_actions": ["<list of specific actions to complete this milestone>"],
            "timeline": "<estimated timeline>",
            "resources_needed": ["<list of resources needed>"]
        }},
        "commercialization": {{
            "status": "<completed/current/future>",
            "description": "<what needs to be done for this milestone>",
            "specific_actions": ["<list of specific actions to complete this milestone>"],
            "timeline": "<estimated timeline>",
            "resources_needed": ["<list of resources needed>"]
        }}
    }}
}}

TRL Scale Reference:
- TRL 1: Basic principles observed - Research begins with fundamental principles
- TRL 2: Technology concept formulated - Practical applications identified
- TRL 3: Experimental proof of concept - Lab-scale validation of concept
- TRL 4: Technology validated in lab - Component/system validation in lab
- TRL 5: Technology validated in relevant environment - Validation in simulated environment
- TRL 6: Technology demonstrated in relevant environment - Prototype demonstration in realistic environment
- TRL 7: Technology demonstrated in operational environment - System demonstration in actual operational environment
- TRL 8: System complete and qualified - Final system qualified through test and evaluation
- TRL 9: System proven in operational environment - Actual system proven in successful operational missions

Focus on concrete evidence: actual experiments, prototypes, testing environments, partnerships, production capabilities, certifications, etc.
Be critical and thorough in your paper review - identify any claims that lack supporting evidence.
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert TRL assessor for deep technology research with strong attention to detail and critical analysis capabilities."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Lower temperature for more consistent results
            max_tokens=2000  # Increased for more detailed responses
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        # Extract JSON from response (handle potential markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            import json
            try:
                result = json.loads(json_match.group())
                # Validate and enhance the result
                trl = max(1, min(9, int(result.get("trl", 3))))
                
                # Generate milestones with detailed breakdown
                milestones = generate_detailed_milestones(trl, result.get("milestone_breakdown", {}))
                
                # Generate partnership recommendation
                partnership = generate_partnership_recommendation(trl, result.get("commercial_readiness", "medium"))
                
                # Extract paper review if available
                paper_review = result.get("paper_review", {
                    "methodology_assessment": "Methodology appears sound based on available information.",
                    "data_quality": "Data quality assessment requires more detailed experimental data.",
                    "reproducibility": "Reproducibility assessment requires additional protocol details.",
                    "potential_hallucinations": [],
                    "confidence_in_analysis": "medium"
                })
                
                return {
                    "trl": trl,
                    "trl_summary": result.get("reasoning", f"Classified at TRL {trl} based on DeepSeek AI analysis."),
                    "accomplishments": result.get("accomplishments", generate_accomplishments(trl)),
                    "potential_partnership": partnership,
                    "innovation_score": result.get("innovation_score", min(99, max(45, 40 + trl * 6))),
                    "milestones": milestones,
                    "sector_name": (classification or {}).get("sector_name", "Deep Tech"),
                    "analysis_source": "deepseek-ai",
                    "confidence": result.get("confidence", 0.8),
                    "key_indicators": result.get("key_indicators", []),
                    "missing_for_next_trl": result.get("missing_for_next_trl", []),
                    "paper_review": paper_review
                }
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                # If JSON parsing fails, fall back to regex
                pass
        
        # Fallback to regex-based evaluation
        return evaluate_trl_regex(analysis_text, classification=classification, valuation=valuation, title_hint=title_hint)
        
    except Exception as e:
        print(f"DeepSeek API error: {e}")
        # Fallback to regex-based evaluation
        return evaluate_trl_regex(analysis_text, classification=classification, valuation=valuation, title_hint=title_hint)


def evaluate_trl_regex(
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

    accomplishments = generate_accomplishments(trl)
    milestones = generate_milestones(trl)
    partnership = generate_partnership_recommendation(trl, "medium")
    
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

    return {
        "trl": trl,
        "trl_summary": trl_summary,
        "accomplishments": accomplishments,
        "potential_partnership": partnership,
        "innovation_score": innovation_score,
        "milestones": generate_milestones(trl),
        "sector_name": sector,
        "analysis_source": "regex-fallback",
        "confidence": 0.6,
        "key_indicators": [],
        "missing_for_next_trl": [],
        "paper_review": {
            "methodology_assessment": "Methodology assessment requires more detailed analysis.",
            "data_quality": "Data quality assessment requires more detailed analysis.",
            "reproducibility": "Reproducibility assessment requires more detailed analysis.",
            "potential_hallucinations": [],
            "confidence_in_analysis": "low"
        }
    }


def generate_accomplishments(trl: int) -> list[str]:
    """Generate accomplishments based on TRL level."""
    accomplishments = []
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
    return accomplishments


def generate_detailed_milestones(trl: int, ai_breakdown: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Generate detailed milestones with AI-provided breakdown or fallback."""
    def _milestone_status(trl: int, completed_at: int, current_at: int | tuple[int, ...]) -> str:
        if trl >= completed_at:
            return "completed"
        if isinstance(current_at, tuple):
            if trl in current_at:
                return "current"
        elif trl == current_at:
            return "current"
        return "future"

    # Use AI-provided breakdown if available, otherwise use fallback
    if ai_breakdown:
        return {
            "prototype": {
                "status": _milestone_status(trl, 4, 4),
                "description": ai_breakdown.get("prototype", {}).get("description", "Build and validate a working bench-scale demonstration of core technology."),
                "specific_actions": ai_breakdown.get("prototype", {}).get("specific_actions", [
                    "Design experimental setup",
                    "Fabricate prototype components",
                    "Conduct bench-scale testing",
                    "Validate performance metrics"
                ]),
                "timeline": ai_breakdown.get("prototype", {}).get("timeline", "Completed Q2 2025" if trl >= 4 else "Target Q4 2026"),
                "resources_needed": ai_breakdown.get("prototype", {}).get("resources_needed", [
                    "Laboratory equipment",
                    "Raw materials",
                    "Technical personnel",
                    "Testing facilities"
                ])
            },
            "mvp": {
                "status": _milestone_status(trl, 6, (5, 6)),
                "description": ai_breakdown.get("mvp", {}).get("description", "Develop minimum viable product or sub-scale integrated system for partner evaluation."),
                "specific_actions": ai_breakdown.get("mvp", {}).get("specific_actions", [
                    "Integrate core components",
                    "Develop user interface",
                    "Conduct alpha testing",
                    "Gather partner feedback"
                ]),
                "timeline": ai_breakdown.get("mvp", {}).get("timeline", "Completed Q4 2025" if trl >= 6 else "Target Q2 2027"),
                "resources_needed": ai_breakdown.get("mvp", {}).get("resources_needed", [
                    "Development team",
                    "Partner organizations",
                    "Testing infrastructure",
                    "Funding for development"
                ])
            },
            "pilot_test": {
                "status": _milestone_status(trl, 8, 7),
                "description": ai_breakdown.get("pilot_test", {}).get("description", "Deploy pilot system in relevant operational environment with continuous monitoring."),
                "specific_actions": ai_breakdown.get("pilot_test", {}).get("specific_actions", [
                    "Install pilot system",
                    "Train operators",
                    "Monitor performance",
                    "Collect operational data"
                ]),
                "timeline": ai_breakdown.get("pilot_test", {}).get("timeline", "Completed Q1 2026" if trl >= 8 else "Target Q1 2028"),
                "resources_needed": ai_breakdown.get("pilot_test", {}).get("resources_needed", [
                    "Pilot site access",
                    "Installation team",
                    "Monitoring equipment",
                    "Operational support"
                ])
            },
            "commercialization": {
                "status": _milestone_status(trl, 9, 8),
                "description": ai_breakdown.get("commercialization", {}).get("description", "Industrial scale-up, regulatory approval, and commercial licensing agreements."),
                "specific_actions": ai_breakdown.get("commercialization", {}).get("specific_actions", [
                    "Scale manufacturing",
                    "Obtain regulatory approvals",
                    "Negotiate licensing deals",
                    "Launch commercial product"
                ]),
                "timeline": ai_breakdown.get("commercialization", {}).get("timeline", "Completed Q2 2026" if trl == 9 else "Target Q4 2028"),
                "resources_needed": ai_breakdown.get("commercialization", {}).get("resources_needed", [
                    "Manufacturing facilities",
                    "Regulatory consultants",
                    "Business development team",
                    "Marketing resources"
                ])
            }
        }
    
    # Fallback to basic milestones
    return generate_milestones(trl)


def generate_milestones(trl: int) -> dict[str, dict[str, Any]]:
    """Generate milestones based on TRL level."""
    def _milestone_status(trl: int, completed_at: int, current_at: int | tuple[int, ...]) -> str:
        if trl >= completed_at:
            return "completed"
        if isinstance(current_at, tuple):
            if trl in current_at:
                return "current"
        elif trl == current_at:
            return "current"
        return "future"

    return {
        "prototype": {
            "status": _milestone_status(trl, 4, 4),
            "description": "Build and validate a working bench-scale demonstration of core technology.",
            "specific_actions": [
                "Design experimental setup",
                "Fabricate prototype components",
                "Conduct bench-scale testing",
                "Validate performance metrics"
            ],
            "timeline": "Completed Q2 2025" if trl >= 4 else "Target Q4 2026",
            "resources_needed": [
                "Laboratory equipment",
                "Raw materials",
                "Technical personnel",
                "Testing facilities"
            ]
        },
        "mvp": {
            "status": _milestone_status(trl, 6, (5, 6)),
            "description": "Develop minimum viable product or sub-scale integrated system for partner evaluation.",
            "specific_actions": [
                "Integrate core components",
                "Develop user interface",
                "Conduct alpha testing",
                "Gather partner feedback"
            ],
            "timeline": "Completed Q4 2025" if trl >= 6 else "Target Q2 2027",
            "resources_needed": [
                "Development team",
                "Partner organizations",
                "Testing infrastructure",
                "Funding for development"
            ]
        },
        "pilot_test": {
            "status": _milestone_status(trl, 8, 7),
            "description": "Deploy pilot system in relevant operational environment with continuous monitoring.",
            "specific_actions": [
                "Install pilot system",
                "Train operators",
                "Monitor performance",
                "Collect operational data"
            ],
            "timeline": "Completed Q1 2026" if trl >= 8 else "Target Q1 2028",
            "resources_needed": [
                "Pilot site access",
                "Installation team",
                "Monitoring equipment",
                "Operational support"
            ]
        },
        "commercialization": {
            "status": _milestone_status(trl, 9, 8),
            "description": "Industrial scale-up, regulatory approval, and commercial licensing agreements.",
            "specific_actions": [
                "Scale manufacturing",
                "Obtain regulatory approvals",
                "Negotiate licensing deals",
                "Launch commercial product"
            ],
            "timeline": "Completed Q2 2026" if trl == 9 else "Target Q4 2028",
            "resources_needed": [
                "Manufacturing facilities",
                "Regulatory consultants",
                "Business development team",
                "Marketing resources"
            ]
        }
    }


def generate_partnership_recommendation(trl: int, commercial_readiness: str) -> str:
    """Generate partnership recommendation based on TRL and commercial readiness."""
    if trl >= 7 or commercial_readiness == "high":
        return "Strong outlook for scale-up joint fabrication and licensing with tier-1 manufacturers."
    elif trl >= 4 or commercial_readiness == "medium":
        return "Well suited for deep-tech seed funds, government grants, and strategic pilot partners."
    else:
        return "Ideal for academic partnerships, incubator programs, and early-stage research grants."
