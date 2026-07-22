"""Comprehensive analysis generation for detailed insights and recommendations."""

from __future__ import annotations

from typing import Any


def generate_comprehensive_analysis(
    doc: Any,
    classification: dict[str, Any],
    originality: dict[str, Any],
    fto: dict[str, Any],
    valuation: dict[str, Any],
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any],
    nlp_analysis: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate comprehensive analysis with detailed paragraphs of insights
    and meaningful recommendations based on the paper content.
    """
    
    # Extract key information
    abstract = doc.abstract if doc else ""
    methodology = doc.methodology if doc else ""
    claims = doc.claims_outcomes if doc else ""
    document_type = doc.document_type if doc else "unknown"
    
    # Generate detailed executive summary
    executive_summary = _generate_executive_summary(
        abstract, classification, trl_evaluation, valuation
    )
    
    # Generate technical analysis
    technical_analysis = _generate_technical_analysis(
        methodology, classification, originality, fto
    )
    
    # Generate market analysis
    market_analysis = _generate_market_analysis(
        market_mapping, valuation, trl_evaluation
    )
    
    # Generate IP and competitive analysis
    ip_competitive_analysis = _generate_ip_competitive_analysis(
        originality, fto, classification
    )
    
    # Generate development roadmap
    development_roadmap = _generate_development_roadmap(
        trl_evaluation, market_mapping, valuation
    )
    
    # Generate risk assessment
    risk_assessment = _generate_risk_assessment(
        fto, trl_evaluation, market_mapping
    )
    
    # Generate strategic recommendations
    strategic_recommendations = _generate_strategic_recommendations(
        trl_evaluation, market_mapping, valuation, fto
    )
    
    # Generate investment thesis
    investment_thesis = _generate_investment_thesis(
        valuation, trl_evaluation, market_mapping, originality
    )
    
    return {
        "executive_summary": executive_summary,
        "technical_analysis": technical_analysis,
        "market_analysis": market_analysis,
        "ip_competitive_analysis": ip_competitive_analysis,
        "development_roadmap": development_roadmap,
        "risk_assessment": risk_assessment,
        "strategic_recommendations": strategic_recommendations,
        "investment_thesis": investment_thesis,
        "analysis_metadata": {
            "document_type": document_type,
            "word_count": len(doc.raw_text.split()) if doc else 0,
            "analysis_depth": "comprehensive",
            "confidence_level": trl_evaluation.get("confidence", 0.6)
        }
    }


def _generate_executive_summary(
    abstract: str,
    classification: dict[str, Any],
    trl_evaluation: dict[str, Any],
    valuation: dict[str, Any]
) -> str:
    """Generate detailed executive summary."""
    trl = trl_evaluation.get("trl", 3)
    sector = classification.get("sector_name", "Deep Tech")
    ipc_primary = classification.get("ipc_primary", "Unknown")
    
    summary = f"""
## Executive Summary

This document presents a comprehensive analysis of {sector} technology classified under IPC code {ipc_primary}. 
The technology is currently positioned at Technology Readiness Level (TRL) {trl}, indicating {'advanced development with commercialization potential' if trl >= 6 else 'promising research requiring further validation' if trl >= 4 else 'early-stage research with significant development needed'}.

### Technology Overview
{abstract[:500] if abstract else "The document describes innovative research in materials science with potential applications across multiple industrial sectors."}

### Commercial Potential
Based on the analysis, the technology demonstrates {'strong commercial viability' if trl >= 6 else 'moderate commercial potential' if trl >= 4 else 'early-stage commercial promise'}. 
The estimated valuation range of ${valuation.get('v_baseline_usd', 0):,.0f} - ${valuation.get('v_target_usd', 0):,.0f} reflects the technology's current development stage and market opportunity.

### Key Strengths
- {'Validated technical performance in relevant environments' if trl >= 6 else 'Demonstrated technical feasibility' if trl >= 4 else 'Innovative theoretical approach'}
- {'Clear path to commercialization' if trl >= 7 else 'Defined development roadmap' if trl >= 4 else 'Strong research foundation'}
- {'Established market applications' if trl >= 5 else 'Identified market opportunities'}
- {'Competitive differentiation through novel approach' if classification.get('novelty_score', 0) > 0.7 else 'Potential for competitive advantage'}

### Development Status
The technology has achieved key milestones appropriate for TRL {trl}, with {'production-ready capabilities' if trl >= 8 else 'pilot-scale validation' if trl >= 6 else 'prototype development' if trl >= 4 else 'laboratory validation' if trl >= 3 else 'proof-of-concept establishment'}. 
The next critical phase involves {'scaling manufacturing and market entry' if trl >= 7 else 'operational environment testing' if trl >= 5 else 'prototype development and validation' if trl >= 3 else 'further experimental validation'}.
"""
    return summary.strip()


def _generate_technical_analysis(
    methodology: str,
    classification: dict[str, Any],
    originality: dict[str, Any],
    fto: dict[str, Any]
) -> str:
    """Generate detailed technical analysis."""
    ipc_primary = classification.get("ipc_primary", "Unknown")
    novelty_score = originality.get("max_cosine_similarity", 0)
    patent_matches = len(originality.get("top_patent_matches", []))
    fto_risk = fto.get("risk_tier_pct", 0)
    
    analysis = f"""
## Technical Analysis

### Classification and Domain
The technology falls under IPC classification {ipc_primary}, positioning it within the broader field of {classification.get('sector_name', 'Deep Technology')}. 
This classification indicates the technology addresses {'established industrial challenges' if patent_matches > 5 else 'emerging market needs' if patent_matches > 2 else 'novel application areas'}.

### Innovation and Novelty Assessment
The technology demonstrates {'high novelty' if novelty_score < 0.3 else 'moderate novelty' if novelty_score < 0.6 else 'incremental innovation'} based on patent landscape analysis. 
With {patent_matches} relevant patent matches identified, the technology {'occupies a relatively unique position' if patent_matches < 3 else 'has some prior art but maintains differentiation' if patent_matches < 6 else 'operates in a crowded patent landscape requiring careful navigation'}.

### Technical Methodology
{methodology[:600] if methodology else "The document outlines a systematic approach to technology development with emphasis on experimental validation and performance optimization."}

### Freedom to Operate (FTO) Analysis
The FTO assessment indicates {'low risk' if fto_risk < 20 else 'moderate risk' if fto_risk < 40 else 'high risk'} with a risk tier of {fto_risk:.1f}%. 
This suggests {'favorable conditions for commercialization' if fto_risk < 20 else 'need for strategic IP management' if fto_risk < 40 else 'requirement for comprehensive IP strategy and potential licensing arrangements'}.

### Technical Maturity Indicators
- Experimental validation: {'Comprehensive' if len(methodology) > 500 else 'Moderate' if len(methodology) > 200 else 'Limited'}
- Performance metrics: {'Well-defined' if 'performance' in methodology.lower() else 'Partially defined' if 'result' in methodology.lower() else 'Needs definition'}
- Reproducibility: {'High potential' if 'method' in methodology.lower() else 'Moderate potential' if 'approach' in methodology.lower() else 'Requires clarification'}
"""
    return analysis.strip()


def _generate_market_analysis(
    market_mapping: dict[str, Any],
    valuation: dict[str, Any],
    trl_evaluation: dict[str, Any]
) -> str:
    """Generate detailed market analysis."""
    working_field = market_mapping.get("working_field", "Unknown")
    total_opportunities = market_mapping.get("total_opportunities", 0)
    top_opportunity = market_mapping.get("top_opportunity", "Unknown")
    accuracy_score = market_mapping.get("overall_accuracy_score", 0)
    trl = trl_evaluation.get("trl", 3)
    
    strategic_recs = market_mapping.get("strategic_recommendations", [])
    market_entry = market_mapping.get("market_entry_strategy", {})
    competitive = market_mapping.get("competitive_analysis", {})
    
    analysis = f"""
## Market Analysis

### Target Market Sector
The technology is positioned within the {working_field} sector, which represents a {'mature and established' if trl >= 7 else 'growing and evolving' if trl >= 4 else 'emerging and developing'} market landscape. 
The analysis identifies {total_opportunities} distinct market opportunities, with {top_opportunity} representing the most promising initial target.

### Market Opportunity Assessment
Based on the current development stage (TRL {trl}), the market mapping accuracy is estimated at {accuracy_score:.1f}%, reflecting {'high confidence in market fit' if accuracy_score > 70 else 'moderate confidence requiring validation' if accuracy_score > 50 else 'preliminary assessment needing market testing'}.

### Market Entry Strategy
The recommended market entry approach is {market_entry.get('recommended_approach', 'partnership-based')}, with an estimated timeline of {market_entry.get('timeline_estimate', '12-18 months')} to initial market entry. 
This strategy emphasizes {'direct commercial engagement' if trl >= 7 else 'strategic partnerships for validation' if trl >= 4 else 'research collaborations for development'}.

### Competitive Landscape
The market shows {'high saturation' if competitive.get('market_saturation') == 'High' else 'moderate competition' if competitive.get('market_saturation') == 'Medium' else 'low saturation with opportunity'} levels of competition. 
Key differentiation opportunities include:
"""
    
    for diff in competitive.get("differentiation_opportunities", [])[:4]:
        analysis += f"\n- {diff}"
    
    analysis += f"""

### Strategic Market Recommendations
"""
    for rec in strategic_recs[:4]:
        analysis += f"\n- {rec}"
    
    analysis += f"""

### Market Size and Growth Potential
The identified markets demonstrate {'strong growth trajectories' if trl >= 6 else 'promising growth potential' if trl >= 4 else 'emerging growth patterns'} driven by technological advancement and increasing demand for innovative solutions. 
The valuation analysis suggests {'significant market upside' if valuation.get('v_target_usd', 0) > 1000000 else 'moderate market potential' if valuation.get('v_target_usd', 0) > 500000 else 'early-stage market opportunity'}.
"""
    return analysis.strip()


def _generate_ip_competitive_analysis(
    originality: dict[str, Any],
    fto: dict[str, Any],
    classification: dict[str, Any]
) -> str:
    """Generate IP and competitive analysis."""
    max_similarity = originality.get("max_cosine_similarity", 0)
    patent_corpus = originality.get("patent_corpus_size", "Unknown")
    top_matches = originality.get("top_patent_matches", [])[:3]
    fto_risk = fto.get("risk_tier_pct", 0)
    flagged_count = fto.get("flagged_patent_count", 0)
    
    analysis = f"""
## Intellectual Property and Competitive Analysis

### Patent Landscape Positioning
The technology's novelty assessment against a patent corpus of {patent_corpus} patents reveals {'strong differentiation' if max_similarity < 0.3 else 'moderate differentiation' if max_similarity < 0.6 else 'incremental advancement'}. 
The maximum cosine similarity of {max_similarity:.3f} indicates {'low overlap with existing patents' if max_similarity < 0.3 else 'some overlap with prior art' if max_similarity < 0.6 else 'significant overlap requiring careful IP strategy'}.

### Key Patent References
The analysis identified several relevant patents that inform the competitive landscape:
"""
    
    for match in top_matches:
        analysis += f"""
- **{match.get('patent_id', 'Unknown')}**: {match.get('title', 'No title')} (Similarity: {match.get('cosine_similarity', 0):.3f})
"""
    
    analysis += f"""
### Freedom to Operate Assessment
The FTO analysis identified {flagged_count} potentially relevant patents with an overall risk tier of {fto_risk:.1f}%. 
This risk level suggests {'minimal IP barriers to commercialization' if fto_risk < 20 else 'manageable IP considerations requiring attention' if fto_risk < 40 else 'significant IP landscape requiring comprehensive strategy'}.

### IP Strategy Recommendations
- {'File comprehensive patent applications to protect core innovations' if max_similarity < 0.4 else 'Develop strategic IP portfolio around differentiated features' if max_similarity < 0.7 else 'Focus on trade secrets and know-how protection'}
- {'Conduct regular freedom-to-operate analyses as technology develops' if fto_risk > 20 else 'Monitor patent landscape for emerging competitors'}
- {'Consider licensing arrangements for complementary technologies' if flagged_count > 3 else 'Evaluate potential for cross-licensing opportunities'}
- {'Develop IP monetization strategy aligned with commercialization timeline' if max_similarity < 0.5 else 'Focus on defensive IP positioning'}

### Competitive Differentiation
The technology's competitive advantage stems from {'novel approach with strong patentability' if max_similarity < 0.4 else 'differentiated features in competitive landscape' if max_similarity < 0.7 else 'incremental improvements over existing solutions'}. 
Strategic positioning should emphasize {'unique value proposition and IP protection' if max_similarity < 0.4 else 'specific differentiation and market fit' if max_similarity < 0.7 else 'cost or performance advantages'}.
"""
    return analysis.strip()


def _generate_development_roadmap(
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any],
    valuation: dict[str, Any]
) -> str:
    """Generate development roadmap."""
    trl = trl_evaluation.get("trl", 3)
    milestones = trl_evaluation.get("milestones", {})
    missing_for_next = trl_evaluation.get("missing_for_next_trl", [])
    development_insights = market_mapping.get("development_insights", {})
    
    analysis = f"""
## Development Roadmap

### Current Development Status
The technology is currently at TRL {trl}, representing {'commercialization-ready stage' if trl >= 8 else 'advanced development stage' if trl >= 6 else 'prototype development stage' if trl >= 4 else 'laboratory validation stage' if trl >= 3 else 'proof-of-concept stage'}. 
{development_insights.get('current_stage_assessment', 'The technology shows promising development progress.')}

### Key Milestones and Timeline
"""
    
    for milestone_name, milestone_data in milestones.items():
        status = milestone_data.get("status", "future")
        description = milestone_data.get("description", "")
        timeline = milestone_data.get("timeline", "TBD")
        analysis += f"""
#### {milestone_name.replace('_', ' ').title()}
- **Status**: {status.upper()}
- **Description**: {description}
- **Timeline**: {timeline}
"""
    
    analysis += f"""
### Critical Next Steps
To advance to the next TRL level, the following key activities are required:
"""
    
    for step in missing_for_next[:5]:
        analysis += f"\n- {step}"
    
    analysis += f"""

### Resource Requirements
Based on the current development stage, the technology requires:
"""
    
    funding = development_insights.get("funding_recommendations", {})
    analysis += f"""
- **Funding Stage**: {funding.get('stage', 'Seed')}
- **Estimated Range**: {funding.get('estimated_range', '$500K-2M')}
- **Focus Areas**: {', '.join(funding.get('focus_areas', ['R&D', 'prototype development']))}

### Development Partnerships
The technology would benefit from partnerships with:
- {'Industry leaders for scale-up and commercialization' if trl >= 6 else 'Strategic partners for pilot validation' if trl >= 4 else 'Research institutions for collaborative development'}
- {'Manufacturing partners for production scale-up' if trl >= 7 else 'Technical experts for development support' if trl >= 4 else 'Academic collaborators for research enhancement'}
- {'Regulatory bodies for compliance guidance' if trl >= 6 else 'Standards organizations for specification alignment'}
"""
    return analysis.strip()


def _generate_risk_assessment(
    fto: dict[str, Any],
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any]
) -> str:
    """Generate risk assessment."""
    fto_risk = fto.get("risk_tier_pct", 0)
    trl = trl_evaluation.get("trl", 3)
    competitive = market_mapping.get("competitive_analysis", {})
    barriers = competitive.get("barriers_to_entry", [])
    
    analysis = f"""
## Risk Assessment

### Intellectual Property Risks
The IP risk assessment indicates {'low risk profile' if fto_risk < 20 else 'moderate risk profile' if fto_risk < 40 else 'elevated risk profile'} with a risk tier of {fto_risk:.1f}%. 
Key IP considerations include:
- Patent infringement risks from {fto.get('flagged_patent_count', 0)} identified patents
- Need for ongoing IP landscape monitoring
- Potential for licensing requirements or design-arounds

### Technical Development Risks
Based on the current TRL {trl} status, technical risks include:
"""
    
    if trl < 4:
        analysis += """
- Scale-up challenges from laboratory to production environments
- Performance consistency in real-world conditions
- Manufacturing process development and optimization
"""
    elif trl < 7:
        analysis += """
- Operational environment validation requirements
- Manufacturing cost and yield optimization
- Supply chain and quality control establishment
"""
    else:
        analysis += """
- Market adoption and competitive response risks
- Regulatory compliance and certification requirements
- Production scaling and quality assurance
"""
    
    analysis += f"""
### Market and Commercialization Risks
Market entry risks include:
"""
    
    for barrier in barriers[:4]:
        analysis += f"\n- {barrier}"
    
    analysis += f"""

### Risk Mitigation Strategies
- **IP Risk**: Implement comprehensive IP strategy with regular FTO analysis
- **Technical Risk**: Phased development approach with validation at each stage
- **Market Risk**: Strategic partnerships and customer engagement early in development
- **Regulatory Risk**: Early engagement with regulatory bodies and standards organizations

### Overall Risk Profile
The technology presents a {'favorable risk-reward profile' if fto_risk < 25 and trl >= 4 else 'moderate risk profile requiring careful management' if fto_risk < 50 else 'challenging risk profile requiring comprehensive mitigation strategy'}. 
Success probability is enhanced by {'strong technical foundation and market opportunity' if trl >= 4 else 'promising research direction and development potential'}.
"""
    return analysis.strip()


def _generate_strategic_recommendations(
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any],
    valuation: dict[str, Any],
    fto: dict[str, Any]
) -> str:
    """Generate strategic recommendations."""
    trl = trl_evaluation.get("trl", 3)
    strategic_recs = market_mapping.get("strategic_recommendations", [])
    development_insights = market_mapping.get("development_insights", {})
    
    analysis = f"""
## Strategic Recommendations

### Immediate Actions (0-6 months)
Based on the current TRL {trl} status, immediate priorities include:
"""
    
    if trl < 4:
        analysis += """
- Complete comprehensive experimental validation
- File provisional patent applications to protect core innovations
- Engage with potential industry partners for collaboration
- Secure seed funding for prototype development
"""
    elif trl < 7:
        analysis += """
- Advance to pilot-scale demonstrations
- Secure strategic partnerships for operational validation
- Develop comprehensive IP portfolio
- Pursue Series A funding for commercialization preparation
"""
    else:
        analysis += """
- Execute market entry strategy with initial customers
- Scale manufacturing capabilities
- Obtain necessary regulatory certifications
- Pursue Series B or strategic investment for commercialization
"""
    
    analysis += f"""
### Medium-term Strategy (6-18 months)
"""
    
    for rec in strategic_recs[:3]:
        analysis += f"\n- {rec}"
    
    analysis += f"""

### Long-term Strategic Positioning
The technology should pursue:
"""
    
    next_critical = development_insights.get("next_critical_milestones", [])
    for milestone in next_critical[:3]:
        analysis += f"\n- {milestone}"
    
    analysis += f"""

### Partnership and Collaboration Strategy
- {'Focus on licensing agreements with established manufacturers' if trl >= 7 else 'Prioritize joint development with strategic partners' if trl >= 4 else 'Emphasize research collaborations with academic institutions'}
- {'Engage with customers early in commercialization process' if trl >= 6 else 'Build relationships with potential customers during development'}
- {'Develop ecosystem partnerships for comprehensive market solution' if trl >= 5 else 'Identify complementary technology partners'}

### Funding Strategy
"""
    
    funding = development_insights.get("funding_recommendations", {})
    analysis += f"""
- **Current Stage**: {funding.get('stage', 'Seed funding')}
- **Funding Focus**: {', '.join(funding.get('focus_areas', ['R&D', 'prototype development']))}
- **Investor Targeting**: {'Strategic investors and corporate partners' if trl >= 6 else 'Deep tech VCs and government grants' if trl >= 4 else 'Angel investors and research grants'}
- **Valuation Strategy**: Leverage ${valuation.get('v_target_usd', 0):,.0f} target valuation with clear value demonstration
"""
    return analysis.strip()


def _generate_investment_thesis(
    valuation: dict[str, Any],
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any],
    originality: dict[str, Any]
) -> str:
    """Generate investment thesis."""
    trl = trl_evaluation.get("trl", 3)
    valuation_target = valuation.get("v_target_usd", 0)
    valuation_floor = valuation.get("valuation_floor_usd", 0)
    novelty = originality.get("max_cosine_similarity", 0)
    top_opportunity = market_mapping.get("top_opportunity", "Unknown")
    
    analysis = f"""
## Investment Thesis

### Investment Opportunity Summary
This technology represents a {'compelling investment opportunity' if trl >= 5 and novelty < 0.5 else 'promising investment opportunity' if trl >= 3 else 'early-stage investment opportunity'} with significant potential for {'commercial success and market impact' if trl >= 6 else 'technology advancement and market entry' if trl >= 4 else 'research breakthrough and validation'}. 
The valuation range of ${valuation_floor:,.0f} - ${valuation_target:,.0f} reflects the technology's current development stage and future market potential.

### Key Investment Drivers
- **Technology Maturity**: TRL {trl} indicates {'advanced development with reduced technical risk' if trl >= 6 else 'validated technology with manageable development path' if trl >= 4 else 'promising research requiring development investment'}
- **Market Opportunity**: {top_opportunity} represents a significant market opportunity with strong growth potential
- **IP Position**: {'Strong IP position with high novelty' if novelty < 0.4 else 'Moderate IP position with differentiation' if novelty < 0.7 else 'Competitive IP position requiring strategic management'}
- **Development Progress**: {'Clear path to commercialization' if trl >= 6 else 'Defined development roadmap' if trl >= 4 else 'Established research foundation'}

### Investment Risk Profile
The investment presents a {'favorable risk-reward ratio' if trl >= 5 and novelty < 0.5 else 'balanced risk-reward profile' if trl >= 3 else 'higher-risk, higher-reward opportunity'} with risks primarily related to {'market adoption and execution' if trl >= 6 else 'technical development and validation' if trl >= 4 else 'research outcomes and technology development'}.

### Return Potential
Based on market analysis and technology assessment, the investment offers:
- **Upside Potential**: {'Significant with multiple exit scenarios' if valuation_target > 1000000 else 'Moderate with clear value creation path' if valuation_target > 500000 else 'Early-stage with high growth potential'}
- **Time Horizon**: {'2-4 years to commercialization' if trl >= 6 else '3-5 years to market entry' if trl >= 4 else '4-6 years to commercialization'}
- **Exit Strategy**: {'Strategic acquisition or IPO' if trl >= 7 else 'Strategic acquisition or licensing' if trl >= 5 else 'Acquisition by strategic buyer or further development funding'}

### Investment Recommendation
{'Strong Buy' if trl >= 6 and novelty < 0.5 else 'Buy' if trl >= 4 and novelty < 0.6 else 'Speculative Buy' if trl >= 2 else 'Hold for further development'} - This technology represents a {'compelling investment opportunity' if trl >= 5 else 'promising investment opportunity' if trl >= 3 else 'early-stage investment opportunity'} for investors seeking exposure to innovative technology with strong market potential.
"""
    return analysis.strip()
