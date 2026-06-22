"""Enhanced IP valuation and due diligence analysis using DeepSeek API."""

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

def enhance_valuation_with_deepseek(
    analysis_text: str,
    *,
    classification: dict[str, Any] | None = None,
    valuation: dict[str, Any] | None = None,
    fto: dict[str, Any] | None = None,
    originality: dict[str, Any] | None = None,
    title_hint: str = "",
) -> dict[str, Any]:
    """
    Enhance IP valuation analysis using DeepSeek API for more sophisticated insights.
    Falls back to original valuation if DeepSeek API is unavailable.
    """
    client = get_deepseek_client()
    
    if not client:
        return valuation or {}
    
    try:
        # Prepare the prompt for DeepSeek
        prompt = f"""
You are an expert in intellectual property valuation and technology commercialization.

Analyze the following research/technology document and provide a comprehensive IP valuation assessment:

Title: {title_hint}
Sector: {(classification or {}).get("sector_name", "Deep Tech")}
Document Content:
{analysis_text[:3500]}

Current Valuation Metrics:
- Baseline Value: ${valuation.get("v_baseline_usd", 0):,.0f}
- Originality Premium: {valuation.get("s_originality", 0):.4f}
- FTO Risk: {valuation.get("r_fto", 0):.4f}
- Target Valuation: ${valuation.get("v_target_usd", 0):,.0f}
- Valuation Floor: ${valuation.get("valuation_floor_usd", 0):,.0f}

FTO Analysis:
- Flagged Patents: {fto.get("flagged_patent_count", 0)}
- Risk Tier: {fto.get("risk_tier_pct", 0):.1f}%

Originality Analysis:
- Max Similarity: {originality.get("max_cosine_similarity", 0):.4f}
- Patent Corpus Size: {originality.get("patent_corpus_size", "N/A")}

Provide your assessment in the following JSON format:
{{
    "market_opportunity": {{
        "total_addressable_market": "<estimated TAM in USD>",
        "serviceable_addressable_market": "<estimated SAM in USD>",
        "market_growth_rate": "<annual growth rate %>",
        "competitive_landscape": "<analysis of competitive landscape>",
        "differentiation_factors": ["<list of key differentiation factors>"]
    }},
    "commercialization_path": {{
        "time_to_market": "<estimated months to market>",
        "regulatory_requirements": ["<list of regulatory requirements>"],
        "key_partnerships": ["<types of partnerships needed>"],
        "licensing_potential": "<assessment of licensing potential>",
        "exit_strategy_options": ["<potential exit strategies>"]
    }},
    "risk_factors": {{
        "technical_risks": ["<list of technical risks>"],
        "market_risks": ["<list of market risks>"],
        "regulatory_risks": ["<list of regulatory risks>"],
        "intellectual_property_risks": ["<list of IP risks>"]
    }},
    "valuation_insights": {{
        "strengths": ["<list of valuation strengths>"],
        "weaknesses": ["<list of valuation weaknesses>"],
        "sensitivity_analysis": "<how valuation changes with key assumptions>",
        "comparable_deals": ["<list of comparable deals or benchmarks>"]
    }},
    "recommendations": {{
        "immediate_actions": ["<list of immediate actions to maximize value>"],
        "long_term_strategy": "<strategic recommendations>",
        "funding_requirements": "<estimated funding needs and stages>"
    }}
}}

Focus on providing specific, actionable insights based on the technology and market context.
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert IP valuation analyst with deep knowledge of technology commercialization and market analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            import json
            try:
                result = json.loads(json_match.group())
                
                # Merge with existing valuation
                enhanced_valuation = valuation.copy() if valuation else {}
                enhanced_valuation["deepseek_enhancement"] = result
                enhanced_valuation["analysis_source"] = "deepseek-ai"
                
                return enhanced_valuation
            except json.JSONDecodeError as e:
                print(f"JSON parsing error in valuation enhancement: {e}")
        
        # Fallback to original valuation
        return valuation or {}
        
    except Exception as e:
        print(f"DeepSeek valuation enhancement error: {e}")
        return valuation or {}


def enhance_due_diligence_with_deepseek(
    analysis_text: str,
    *,
    classification: dict[str, Any] | None = None,
    title_hint: str = "",
) -> dict[str, Any]:
    """
    Enhanced due diligence analysis using DeepSeek API for more comprehensive assessment.
    """
    client = get_deepseek_client()
    
    if not client:
        return {}
    
    try:
        prompt = f"""
You are an expert in scientific due diligence and technology investment analysis.

Analyze the following research/technology document and provide a comprehensive due diligence assessment:

Title: {title_hint}
Sector: {(classification or {}).get("sector_name", "Deep Tech")}
Document Content:
{analysis_text[:3500]}

Provide your assessment in the following JSON format:
{{
    "scientific_rigor": {{
        "methodology_quality": "<assessment of methodology>",
        "experimental_design": "<assessment of experimental design>",
        "data_analysis": "<assessment of data analysis methods>",
        "statistical_significance": "<assessment of statistical significance>",
        "reproducibility_score": "<high/medium/low>"
    }},
    "innovation_assessment": {{
        "technical_novelty": "<assessment of technical novelty>",
        "prior_art_analysis": "<analysis of prior art and differentiation>",
        "patentability_potential": "<assessment of patentability>",
        "publication_quality": "<assessment of publication quality>"
    }},
    "team_capability": {{
        "technical_expertise": "<assessment of technical expertise demonstrated>",
        "research_track_record": "<assessment of research track record>",
        "collaboration_network": "<assessment of collaboration network>",
        "resource_availability": "<assessment of resource availability>"
    }},
    "market_fit": {{
        "problem_solving": "<assessment of problem being solved>",
        "market_need": "<assessment of market need>",
        "competitive_advantage": "<assessment of competitive advantage>",
        "scalability_potential": "<assessment of scalability>"
    }},
    "risk_assessment": {{
        "technical_risks": ["<list of technical risks>"],
        "execution_risks": ["<list of execution risks>"],
        "market_risks": ["<list of market risks>"],
        "regulatory_risks": ["<list of regulatory risks>"]
    }},
    "investment_recommendation": {{
        "overall_score": "<number 0-100>",
        "investment_tier": "<Tier A/Tier B/Tier C>",
        "recommended_action": "<recommended investment action>",
        "key_concerns": ["<list of key concerns>"],
        "key_strengths": ["<list of key strengths>"]
    }},
    "next_steps": {{
        "due_diligence_items": ["<list of additional due diligence items>"],
        "information_requests": ["<list of information to request>"],
        "expert_consultation_needed": ["<list of expert consultations needed>"]
    }}
}}

Be thorough and critical in your assessment. Identify both strengths and weaknesses.
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert due diligence analyst with strong attention to detail and critical analysis capabilities."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            import json
            try:
                result = json.loads(json_match.group())
                result["analysis_source"] = "deepseek-ai"
                return result
            except json.JSONDecodeError as e:
                print(f"JSON parsing error in due diligence enhancement: {e}")
        
        return {}
        
    except Exception as e:
        print(f"DeepSeek due diligence enhancement error: {e}")
        return {}
