"""Comprehensive analysis generation for detailed insights and recommendations."""

from __future__ import annotations

from typing import Any

# Import multi-agent system
try:
    from app.ai_services.integration import analyze_with_multi_agent, get_multi_agent_system
    MULTI_AGENT_AVAILABLE = True
except ImportError:
    MULTI_AGENT_AVAILABLE = False


def generate_comprehensive_analysis(
    doc: Any,
    classification: dict[str, Any],
    originality: dict[str, Any],
    fto: dict[str, Any],
    valuation: dict[str, Any],
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any],
    nlp_analysis: dict[str, Any],
    title: str = "Unknown",
    use_multi_agent: bool = True,
) -> dict[str, Any]:
    """
    Generate comprehensive analysis with detailed paragraphs of insights
    and meaningful recommendations based on the paper content.
    
    Args:
        doc: Document object with abstract, methodology, claims_outcomes
        classification: Classification data including sector_name
        originality: Originality and patent data
        fto: Freedom to operate analysis data
        valuation: Valuation data
        trl_evaluation: TRL evaluation data
        market_mapping: Market mapping data
        nlp_analysis: NLP analysis data
        title: Document title
        use_multi_agent: Whether to use multi-agent system if available
    
    Returns:
        Dictionary with comprehensive analysis sections
    """
    
    # Try multi-agent system first if available and enabled
    if MULTI_AGENT_AVAILABLE and use_multi_agent:
        try:
            import asyncio
            
            # Check if we're in an async context
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're in an async context, need to handle differently
                    # For now, fall back to rule-based
                    pass
                else:
                    # We can create a new event loop
                    result = loop.run_until_complete(
                        analyze_with_multi_agent(
                            doc=doc,
                            classification=classification,
                            originality=originality,
                            fto=fto,
                            valuation=valuation,
                            trl_evaluation=trl_evaluation,
                            market_mapping=market_mapping,
                            nlp_analysis=nlp_analysis,
                            title=title,
                        )
                    )
                    return result
            except RuntimeError:
                # No event loop, create one
                result = asyncio.run(
                    analyze_with_multi_agent(
                        doc=doc,
                        classification=classification,
                        originality=originality,
                        fto=fto,
                        valuation=valuation,
                        trl_evaluation=trl_evaluation,
                        market_mapping=market_mapping,
                        nlp_analysis=nlp_analysis,
                        title=title,
                    )
                )
                return result
        except Exception as e:
            print(f"Multi-agent analysis failed, falling back to rule-based: {e}")
            # Fall through to rule-based analysis
    
    # Rule-based analysis (original implementation)
    return _generate_rule_based_analysis(
        doc, classification, originality, fto, valuation, trl_evaluation, market_mapping, nlp_analysis
    )


def _generate_rule_based_analysis(
    doc: Any,
    classification: dict[str, Any],
    originality: dict[str, Any],
    fto: dict[str, Any],
    valuation: dict[str, Any],
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any],
    nlp_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Generate rule-based comprehensive analysis (original implementation)."""
    
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
    """Generate detailed executive summary with extensive analysis."""
    trl = trl_evaluation.get("trl", 3)
    sector = classification.get("sector_name", "Deep Tech")
    ipc_primary = classification.get("ipc_primary", "Unknown")
    novelty_score = classification.get("novelty_score", 0.5)
    
    summary = f"""
## Executive Summary

This comprehensive analysis evaluates a {sector} technology classified under IPC code {ipc_primary}. The technology is currently positioned at Technology Readiness Level (TRL) {trl}, which indicates {'advanced development with demonstrated commercialization potential' if trl >= 7 else 'advanced development with commercialization pathway' if trl >= 6 else 'promising research requiring further validation' if trl >= 4 else 'early-stage research requiring significant development' if trl >= 2 else 'conceptual research requiring fundamental validation'}.

### Technology Overview and Innovation Assessment

{abstract[:800] if abstract else "The document presents innovative research in materials science with potential applications across multiple industrial sectors. The technology addresses critical challenges in the field through novel approaches that demonstrate significant potential for commercial application."}

The technology demonstrates {'exceptional novelty' if novelty_score > 0.8 else 'high novelty' if novelty_score > 0.6 else 'moderate novelty' if novelty_score > 0.4 else 'incremental innovation' if novelty_score > 0.2 else 'limited novelty'} with a novelty score of {novelty_score:.2f}. This indicates {'strong differentiation from existing solutions' if novelty_score > 0.6 else 'some differentiation from existing approaches' if novelty_score > 0.4 else 'incremental improvements over current technologies'}. The technical approach shows {'significant potential for disruption' if novelty_score > 0.7 else 'promising potential for market impact' if novelty_score > 0.5 else 'moderate potential for competitive advantage'}.

### Commercial Potential and Market Opportunity

Based on the comprehensive analysis, the technology demonstrates {'exceptional commercial viability' if trl >= 7 else 'strong commercial viability' if trl >= 6 else 'moderate commercial potential' if trl >= 4 else 'early-stage commercial promise' if trl >= 2 else 'conceptual commercial potential requiring validation'}. The estimated valuation range of ${valuation.get('v_baseline_usd', 0):,.0f} - ${valuation.get('v_target_usd', 0):,.0f} reflects the technology's current development stage, market opportunity, and competitive positioning.

The commercial potential is driven by several key factors:
- **Market Demand**: {'Strong and growing market demand for solutions in this domain' if trl >= 5 else 'Emerging market demand with significant growth potential' if trl >= 3 else 'Early market interest requiring validation'}
- **Technical Differentiation**: {'Clear technical advantages over existing solutions' if novelty_score > 0.6 else 'Some technical differentiation from competitors' if novelty_score > 0.4 else 'Incremental technical improvements'}
- **Development Stage**: {'Advanced development with clear path to commercialization' if trl >= 6 else 'Promising development with defined roadmap' if trl >= 4 else 'Early development requiring significant investment'}
- **Competitive Position**: {'Strong competitive positioning with defensible advantages' if novelty_score > 0.7 else 'Moderate competitive positioning with differentiation' if novelty_score > 0.4 else 'Competitive positioning requiring further development'}

### Key Strengths and Competitive Advantages

The technology exhibits several critical strengths that support its commercial potential:

**Technical Excellence:**
- {'Validated technical performance in relevant environments' if trl >= 6 else 'Demonstrated technical feasibility in controlled conditions' if trl >= 4 else 'Promising theoretical approach requiring experimental validation'}
- {'Robust and scalable technical architecture' if trl >= 5 else 'Well-defined technical approach with scalability potential' if trl >= 3 else 'Conceptual technical framework requiring development'}
- {'Clear technical differentiation from existing solutions' if novelty_score > 0.6 else 'Some technical differentiation from competitors' if novelty_score > 0.4 else 'Incremental technical improvements over current approaches'}

**Commercial Readiness:**
- {'Clear path to commercialization with defined milestones' if trl >= 7 else 'Defined commercialization roadmap with achievable milestones' if trl >= 5 else 'Commercialization pathway requiring further development' if trl >= 3 else 'Conceptual commercialization approach requiring validation'}
- {'Established market applications with clear customer segments' if trl >= 5 else 'Identified market opportunities with potential customer segments' if trl >= 3 else 'Emerging market applications requiring validation'}
- {'Strong competitive positioning with defensible advantages' if novelty_score > 0.7 else 'Moderate competitive positioning with differentiation' if novelty_score > 0.4 else 'Competitive positioning requiring further development'}

**Development Progress:**
- {'Significant development progress with validated results' if trl >= 6 else 'Promising development progress with demonstrated feasibility' if trl >= 4 else 'Early development progress with promising results' if trl >= 2 else 'Conceptual development requiring fundamental validation'}
- {'Clear development roadmap with achievable milestones' if trl >= 5 else 'Defined development approach with potential milestones' if trl >= 3 else 'Conceptual development framework requiring definition'}
- {'Strong technical team with relevant expertise' if trl >= 4 else 'Capable technical team with domain knowledge' if trl >= 2 else 'Technical team requiring development'}

### Development Status and Next Steps

The technology has achieved key milestones appropriate for TRL {trl}, with {'production-ready capabilities and demonstrated scalability' if trl >= 8 else 'pilot-scale validation with demonstrated performance' if trl >= 6 else 'prototype development with validated functionality' if trl >= 4 else 'laboratory validation with promising results' if trl >= 3 else 'proof-of-concept establishment with theoretical validation' if trl >= 2 else 'conceptual development requiring fundamental research'}. The current development stage indicates {'significant progress toward commercialization' if trl >= 6 else 'promising progress with clear development path' if trl >= 4 else 'early progress requiring significant development' if trl >= 2 else 'conceptual stage requiring fundamental validation'}.

The next critical phase involves {'scaling manufacturing and market entry' if trl >= 7 else 'operational environment testing and validation' if trl >= 5 else 'prototype development and validation' if trl >= 3 else 'experimental validation and proof-of-concept development' if trl >= 2 else 'fundamental research and concept validation'}. This phase will require {'significant investment in manufacturing and commercialization' if trl >= 6 else 'investment in operational testing and validation' if trl >= 4 else 'investment in prototype development and testing' if trl >= 2 else 'investment in fundamental research and development'}.

### Risk Assessment and Mitigation Strategies

The technology presents several key risks that require careful management:

**Technical Risks:**
- {'Scale-up challenges from laboratory to production environments' if trl >= 4 else 'Technical feasibility requiring experimental validation' if trl >= 2 else 'Conceptual feasibility requiring fundamental research'}
- {'Performance consistency in real-world conditions' if trl >= 5 else 'Performance validation in controlled environments' if trl >= 3 else 'Performance prediction requiring theoretical validation'}
- {'Manufacturing process development and optimization' if trl >= 6 else 'Manufacturing feasibility assessment' if trl >= 4 else 'Manufacturing concept requiring development'}

**Commercial Risks:**
- {'Market adoption and competitive response risks' if trl >= 6 else 'Market validation and customer acceptance risks' if trl >= 4 else 'Market demand validation risks'}
- {'Regulatory compliance and certification requirements' if trl >= 6 else 'Regulatory pathway assessment' if trl >= 4 else 'Regulatory requirements identification'}
- {'Pricing and revenue model validation' if trl >= 5 else 'Pricing strategy development' if trl >= 3 else 'Revenue model conceptualization'}

**Development Risks:**
- {'Timeline and budget execution risks' if trl >= 4 else 'Development planning and resource allocation risks' if trl >= 2 else 'Research direction and approach risks'}
- {'Technical team and expertise requirements' if trl >= 3 else 'Team development and expertise acquisition risks'}
- {'Intellectual property and competitive positioning risks' if novelty_score < 0.5 else 'IP protection and competitive defense strategies'}

### Investment Recommendation

Based on the comprehensive analysis, the technology represents a {'compelling investment opportunity with strong potential for significant returns' if trl >= 6 and novelty_score > 0.6 else 'promising investment opportunity with moderate risk-reward profile' if trl >= 4 and novelty_score > 0.4 else 'early-stage investment opportunity with higher risk profile' if trl >= 2 else 'conceptual investment opportunity requiring significant development'}. The investment thesis is supported by {'strong technical validation and clear commercialization path' if trl >= 6 else 'promising technical progress and defined development roadmap' if trl >= 4 else 'early technical progress and development potential' if trl >= 2 else 'conceptual framework and research potential'}.

The recommended investment approach is {'strategic investment with focus on commercialization support' if trl >= 6 else 'development investment with focus on technical validation' if trl >= 4 else 'research investment with focus on proof-of-concept development' if trl >= 2 else 'conceptual investment with focus on fundamental research'}. The investment should be structured to {'support commercialization and market entry' if trl >= 6 else 'support technical development and validation' if trl >= 4 else 'support research and development' if trl >= 2 else 'support fundamental research and concept validation'}.
"""
    return summary.strip()


def _generate_technical_analysis(
    methodology: str,
    classification: dict[str, Any],
    originality: dict[str, Any],
    fto: dict[str, Any]
) -> str:
    """Generate detailed technical analysis with extensive depth."""
    ipc_primary = classification.get("ipc_primary", "Unknown")
    novelty_score = originality.get("max_cosine_similarity", 0)
    patent_matches = len(originality.get("top_patent_matches", []))
    fto_risk = fto.get("risk_tier_pct", 0)
    sector = classification.get("sector_name", "Deep Technology")
    
    analysis = f"""
## Technical Analysis

### Classification and Domain Positioning

The technology falls under IPC classification {ipc_primary}, positioning it within the broader field of {sector}. This classification indicates the technology addresses {'established industrial challenges with proven market demand' if patent_matches > 5 else 'emerging market needs with growing demand' if patent_matches > 2 else 'novel application areas with potential for disruption'}. The IPC classification provides insights into the technology's technical domain and potential applications across various industries.

The technical domain encompasses {'multiple industrial applications with cross-sector potential' if patent_matches > 5 else 'specific industrial applications with focused market opportunities' if patent_matches > 2 else 'emerging applications with potential for market expansion'}. The technology's positioning within this domain suggests {'strong alignment with industry needs and market requirements' if patent_matches > 5 else 'good alignment with emerging market trends' if patent_matches > 2 else 'potential for creating new market opportunities'}.

### Innovation and Novelty Assessment

The technology demonstrates {'exceptional novelty' if novelty_score < 0.2 else 'high novelty' if novelty_score < 0.4 else 'moderate novelty' if novelty_score < 0.6 else 'incremental innovation' if novelty_score < 0.8 else 'limited novelty'} based on comprehensive patent landscape analysis. The novelty score of {novelty_score:.3f} indicates {'significant differentiation from existing solutions' if novelty_score < 0.4 else 'some differentiation from existing approaches' if novelty_score < 0.6 else 'incremental improvements over current technologies' if novelty_score < 0.8 else 'limited differentiation from existing solutions'}.

With {patent_matches} relevant patent matches identified in the patent corpus, the technology {'occupies a relatively unique position with strong competitive advantages' if patent_matches < 3 else 'has some prior art but maintains clear differentiation' if patent_matches < 6 else 'operates in a competitive patent landscape requiring careful IP strategy' if patent_matches < 10 else 'operates in a crowded patent landscape requiring comprehensive IP management'}. This patent landscape analysis suggests {'favorable conditions for IP protection and commercialization' if patent_matches < 4 else 'manageable IP landscape with strategic opportunities' if patent_matches < 8 else 'challenging IP landscape requiring comprehensive strategy'}.

The novelty assessment considers multiple factors:
- **Technical Approach**: {'Novel technical approach with significant innovation' if novelty_score < 0.4 else 'Innovative technical approach with some novelty' if novelty_score < 0.6 else 'Incremental technical improvements over existing approaches' if novelty_score < 0.8 else 'Limited technical novelty compared to existing solutions'}
- **Application Domain**: {'Novel application domain with disruption potential' if novelty_score < 0.4 else 'Innovative application with market differentiation' if novelty_score < 0.6 else 'Incremental application improvements' if novelty_score < 0.8 else 'Limited application novelty'}
- **Performance Characteristics**: {'Superior performance characteristics compared to existing solutions' if novelty_score < 0.4 else 'Improved performance characteristics' if novelty_score < 0.6 else 'Comparable performance characteristics' if novelty_score < 0.8 else 'Performance characteristics similar to existing solutions'}

### Technical Methodology and Approach

{methodology[:1200] if methodology else "The document outlines a systematic approach to technology development with emphasis on experimental validation, performance optimization, and scalability considerations. The technical methodology demonstrates a structured approach to research and development with clear objectives and defined milestones."}

The technical methodology exhibits {'exceptional rigor and scientific validity' if len(methodology) > 800 else 'strong scientific rigor with comprehensive validation' if len(methodology) > 500 else 'moderate scientific rigor with basic validation' if len(methodology) > 200 else 'limited scientific rigor requiring further development'}. The approach demonstrates {'comprehensive understanding of technical challenges and solutions' if len(methodology) > 800 else 'good understanding of technical requirements' if len(methodology) > 500 else 'basic understanding of technical challenges' if len(methodology) > 200 else 'limited technical understanding requiring development'}.

Key methodological strengths include:
- {'Comprehensive experimental design with appropriate controls' if 'experiment' in methodology.lower() or 'control' in methodology.lower() else 'Systematic experimental approach' if 'method' in methodology.lower() else 'Basic experimental design'}
- {'Detailed performance metrics and measurement protocols' if 'performance' in methodology.lower() or 'metric' in methodology.lower() else 'Performance measurement approach' if 'result' in methodology.lower() else 'Basic performance assessment'}
- {'Clear reproducibility protocols and documentation' if 'reproduc' in methodology.lower() or 'protocol' in methodology.lower() else 'Reproducibility considerations' if 'method' in methodology.lower() else 'Limited reproducibility documentation'}
- {'Scalability considerations and manufacturing feasibility' if 'scal' in methodology.lower() or 'manufactur' in methodology.lower() else 'Basic scalability assessment' if 'scale' in methodology.lower() else 'Limited scalability considerations'}

### Freedom to Operate (FTO) Analysis

The FTO assessment indicates {'minimal risk with favorable conditions for commercialization' if fto_risk < 15 else 'low risk with manageable IP considerations' if fto_risk < 30 else 'moderate risk requiring strategic IP management' if fto_risk < 50 else 'elevated risk requiring comprehensive IP strategy and potential licensing arrangements'}. The risk tier of {fto_risk:.1f}% reflects the complexity of the patent landscape and the potential for IP conflicts.

The FTO analysis considers several critical factors:
- **Patent Overlap**: {'Minimal patent overlap with existing solutions' if fto_risk < 20 else 'Some patent overlap requiring careful review' if fto_risk < 40 else 'Significant patent overlap requiring strategic management' if fto_risk < 60 else 'Extensive patent overlap requiring comprehensive strategy'}
- **Claim Scope**: {'Broad claim scope with strong IP protection potential' if fto_risk < 20 else 'Moderate claim scope with good IP protection' if fto_risk < 40 else 'Narrow claim scope with limited IP protection' if fto_risk < 60 else 'Limited claim scope requiring careful IP strategy'}
- **Licensing Requirements**: {'Minimal licensing requirements for commercialization' if fto_risk < 20 else 'Some licensing requirements for specific applications' if fto_risk < 40 else 'Significant licensing requirements for commercialization' if fto_risk < 60 else 'Extensive licensing requirements requiring comprehensive strategy'}

This FTO assessment suggests {'favorable conditions for commercialization with clear IP strategy' if fto_risk < 20 else 'manageable IP landscape with strategic opportunities' if fto_risk < 40 else 'challenging IP landscape requiring comprehensive strategy' if fto_risk < 60 else 'complex IP landscape requiring extensive management and potential licensing arrangements'}.

### Technical Maturity and Development Status

The technology demonstrates {'exceptional technical maturity with validated performance' if len(methodology) > 800 else 'strong technical maturity with demonstrated feasibility' if len(methodology) > 500 else 'moderate technical maturity with promising results' if len(methodology) > 200 else 'early technical maturity requiring further development'}. The development status indicates {'significant progress toward commercialization' if len(methodology) > 800 else 'promising progress with clear development path' if len(methodology) > 500 else 'early progress requiring significant development' if len(methodology) > 200 else 'conceptual stage requiring fundamental development'}.

Technical maturity indicators:
- **Experimental Validation**: {'Comprehensive experimental validation across multiple scenarios' if len(methodology) > 800 else 'Strong experimental validation with multiple test cases' if len(methodology) > 500 else 'Moderate experimental validation with basic testing' if len(methodology) > 200 else 'Limited experimental validation requiring further development'}
- **Performance Metrics**: {'Well-defined performance metrics with comprehensive measurement' if 'performance' in methodology.lower() and 'metric' in methodology.lower() else 'Defined performance metrics with measurement protocols' if 'performance' in methodology.lower() else 'Partially defined performance metrics' if 'result' in methodology.lower() else 'Performance metrics requiring definition'}
- **Reproducibility**: {'High reproducibility with detailed protocols and documentation' if 'reproduc' in methodology.lower() or 'protocol' in methodology.lower() else 'Good reproducibility with documented methods' if 'method' in methodology.lower() else 'Moderate reproducibility with basic documentation' if len(methodology) > 200 else 'Reproducibility requiring further validation and documentation'}
- **Scalability**: {'Clear scalability path with manufacturing considerations' if 'scal' in methodology.lower() or 'manufactur' in methodology.lower() else 'Scalability potential with basic considerations' if 'scale' in methodology.lower() else 'Scalability requiring further assessment and development'}

### Technical Challenges and Development Requirements

The technology faces several technical challenges that require attention:

**Scale-up Challenges:**
- {'Scale-up from laboratory to production environments with process optimization' if len(methodology) > 500 else 'Scale-up considerations for production environments' if len(methodology) > 200 else 'Scale-up challenges requiring development and validation'}
- {'Manufacturing process development and optimization for commercial production' if 'manufactur' in methodology.lower() else 'Manufacturing feasibility assessment' if len(methodology) > 200 else 'Manufacturing process requiring development'}
- {'Quality control and consistency in production environments' if len(methodology) > 500 else 'Quality control considerations for production' if len(methodology) > 200 else 'Quality control requiring development'}

**Performance Optimization:**
- {'Performance optimization for real-world applications and conditions' if 'performance' in methodology.lower() else 'Performance considerations for practical applications' if len(methodology) > 200 else 'Performance optimization requiring development'}
- {'Reliability and durability enhancement for commercial applications' if len(methodology) > 500 else 'Reliability considerations for commercial use' if len(methodology) > 200 else 'Reliability enhancement requiring development'}
- {'Cost reduction through process optimization and material selection' if 'cost' in methodology.lower() else 'Cost considerations for commercialization' if len(methodology) > 200 else 'Cost reduction requiring optimization'}

**Technical Validation:**
- {'Comprehensive technical validation across diverse operating conditions' if len(methodology) > 800 else 'Technical validation across relevant conditions' if len(methodology) > 500 else 'Basic technical validation requiring expansion' if len(methodology) > 200 else 'Technical validation requiring comprehensive development'}
- {'Long-term performance and stability assessment' if len(methodology) > 500 else 'Long-term performance considerations' if len(methodology) > 200 else 'Long-term performance assessment requiring development'}
- {'Regulatory compliance and certification requirements' if len(methodology) > 500 else 'Regulatory considerations for commercialization' if len(methodology) > 200 else 'Regulatory compliance requiring assessment and development'}
"""
    return analysis.strip()


def _generate_market_analysis(
    market_mapping: dict[str, Any],
    valuation: dict[str, Any],
    trl_evaluation: dict[str, Any]
) -> str:
    """Generate detailed market analysis with extensive depth."""
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

### Target Market Sector Overview

The technology is positioned within the {working_field} sector, which represents a {'mature and established market with clear growth trajectories' if trl >= 7 else 'growing and evolving market with significant expansion potential' if trl >= 4 else 'emerging and developing market with high growth potential' if trl >= 2 else 'nascent market requiring validation and development'}. The sector demonstrates {'strong and sustained growth driven by technological advancement and increasing demand' if trl >= 6 else 'promising growth patterns with emerging opportunities' if trl >= 4 else 'early-stage growth with significant potential' if trl >= 2 else 'conceptual growth requiring market validation'}.

The comprehensive market analysis identifies {total_opportunities} distinct market opportunities, with {top_opportunity} representing the most promising initial target for commercialization. This market opportunity selection is based on {'strong market demand, favorable competitive dynamics, and alignment with technology capabilities' if total_opportunities > 5 else 'market demand, competitive positioning, and technical fit' if total_opportunities > 2 else 'emerging market opportunities requiring validation'}.

### Market Opportunity Assessment and Validation

Based on the current development stage (TRL {trl}), the market mapping accuracy is estimated at {accuracy_score:.1f}%, reflecting {'high confidence in market fit with strong validation' if accuracy_score > 70 else 'moderate confidence requiring additional market validation' if accuracy_score > 50 else 'preliminary assessment needing comprehensive market testing and validation'}. This confidence level is derived from {'comprehensive market research and competitive analysis' if accuracy_score > 70 else 'market research and preliminary competitive analysis' if accuracy_score > 50 else 'initial market assessment requiring further validation'}.

The market opportunity assessment considers multiple critical factors:
- **Market Size**: {'Large and growing market with significant revenue potential' if total_opportunities > 5 else 'Moderate market size with growth potential' if total_opportunities > 2 else 'Early-stage market with growth potential requiring validation'}
- **Market Growth Rate**: {'Strong and sustained growth driven by technological advancement and increasing demand' if trl >= 6 else 'Promising growth patterns with emerging opportunities' if trl >= 4 else 'Early-stage growth with significant potential' if trl >= 2 else 'Conceptual growth requiring market validation'}
- **Market Demand**: {'Strong and validated market demand with clear customer needs' if trl >= 5 else 'Emerging market demand with potential customer segments' if trl >= 3 else 'Early market interest requiring validation'}
- **Competitive Dynamics**: {'Favorable competitive landscape with differentiation opportunities' if competitive.get('market_saturation') != 'High' else 'Competitive landscape requiring strategic positioning'}

### Market Entry Strategy and Implementation

The recommended market entry approach is {market_entry.get('recommended_approach', 'partnership-based')}, with an estimated timeline of {market_entry.get('timeline_estimate', '12-18 months')} to initial market entry. This strategy emphasizes {'direct commercial engagement with established customer relationships' if trl >= 7 else 'strategic partnerships for validation and market access' if trl >= 4 else 'research collaborations for development and market validation' if trl >= 2 else 'fundamental research and market exploration'}.

The market entry strategy is designed to {'maximize market penetration while minimizing risk and investment requirements' if trl >= 6 else 'balance market opportunity with development requirements and risk management' if trl >= 4 else 'validate market assumptions while building market presence' if trl >= 2 else 'explore market potential and validate assumptions'}. Key elements of the market entry strategy include:

- **Target Customer Segments**: {'Clearly defined customer segments with validated needs and purchasing power' if trl >= 5 else 'Identified customer segments with potential needs' if trl >= 3 else 'Emerging customer segments requiring validation'}
- **Value Proposition**: {'Strong and differentiated value proposition addressing critical customer needs' if trl >= 5 else 'Clear value proposition addressing customer needs' if trl >= 3 else 'Value proposition requiring validation and refinement'}
- **Pricing Strategy**: {'Strategic pricing aligned with value proposition and market dynamics' if trl >= 5 else 'Pricing strategy based on cost and competitive positioning' if trl >= 3 else 'Pricing strategy requiring market validation'}
- **Distribution Channels**: {'Established distribution channels with strong market access' if trl >= 5 else 'Identified distribution channels requiring development' if trl >= 3 else 'Distribution strategy requiring exploration and validation'}

### Competitive Landscape Analysis

The market shows {'high saturation with intense competition requiring differentiation' if competitive.get('market_saturation') == 'High' else 'moderate competition with opportunities for differentiation' if competitive.get('market_saturation') == 'Medium' else 'low saturation with significant opportunity for market entry'} levels of competition. The competitive analysis reveals {'challenging competitive dynamics requiring strategic positioning' if competitive.get('market_saturation') == 'High' else 'manageable competitive landscape with differentiation opportunities' if competitive.get('market_saturation') == 'Medium' else 'favorable competitive landscape with significant opportunity'}.

Key competitive dynamics include:
- **Competitive Intensity**: {'High competitive intensity with multiple established players' if competitive.get('market_saturation') == 'High' else 'Moderate competitive intensity with some established players' if competitive.get('market_saturation') == 'Medium' else 'Low competitive intensity with opportunity for market entry'}
- **Market Barriers**: {'Significant market barriers requiring strategic approach' if competitive.get('market_saturation') == 'High' else 'Moderate market barriers requiring careful planning' if competitive.get('market_saturation') == 'Medium' else 'Low market barriers facilitating market entry'}
- **Differentiation Opportunities**: {'Limited differentiation opportunities requiring innovation' if competitive.get('market_saturation') == 'High' else 'Some differentiation opportunities through technical innovation' if competitive.get('market_saturation') == 'Medium' else 'Significant differentiation opportunities through technical and commercial innovation'}

Key differentiation opportunities include:
"""
    
    for diff in competitive.get("differentiation_opportunities", [])[:6]:
        analysis += f"\n- {diff}"
    
    analysis += f"""

### Strategic Market Recommendations

Based on the comprehensive market analysis, the following strategic recommendations are provided to maximize market success:
"""
    for rec in strategic_recs[:6]:
        analysis += f"\n- {rec}"
    
    analysis += f"""

### Market Size and Growth Potential Analysis

The identified markets demonstrate {'strong and sustained growth trajectories driven by technological advancement and increasing demand' if trl >= 6 else 'promising growth potential with emerging opportunities' if trl >= 4 else 'early-stage growth patterns with significant potential' if trl >= 2 else 'conceptual growth requiring market validation'}. The valuation analysis suggests {'significant market upside with strong revenue potential' if valuation.get('v_target_usd', 0) > 1000000 else 'moderate market potential with clear revenue opportunities' if valuation.get('v_target_usd', 0) > 500000 else 'early-stage market opportunity with growth potential'}.

Market size and growth considerations:
- **Total Addressable Market (TAM)**: {'Large and growing market with significant revenue potential' if valuation.get('v_target_usd', 0) > 1000000 else 'Moderate market size with growth potential' if valuation.get('v_target_usd', 0) > 500000 else 'Early-stage market with growth potential'}
- **Serviceable Addressable Market (SAM)**: {'Significant market segment accessible with current technology' if trl >= 5 else 'Accessible market segment requiring development' if trl >= 3 else 'Market segment requiring validation and development'}
- **Serviceable Obtainable Market (SOM)**: {'Achievable market share with focused execution' if trl >= 5 else 'Realistic market share requiring strategic execution' if trl >= 3 else 'Market share requiring validation and strategic planning'}
- **Market Growth Rate**: {'Strong and sustained growth driven by technological advancement' if trl >= 6 else 'Promising growth patterns with emerging opportunities' if trl >= 4 else 'Early-stage growth with significant potential' if trl >= 2 else 'Conceptual growth requiring validation'}

### Market Risk Assessment and Mitigation

The market presents several key risks that require careful management:

**Market Adoption Risks:**
- {'Customer adoption challenges requiring education and validation' if trl >= 4 else 'Market acceptance requiring validation and demonstration' if trl >= 2 else 'Market adoption requiring comprehensive validation'}
- {'Competitive response and market dynamics requiring strategic positioning' if competitive.get('market_saturation') == 'High' else 'Competitive considerations requiring monitoring and response' if competitive.get('market_saturation') == 'Medium' else 'Competitive landscape monitoring'}
- {'Market timing and entry strategy optimization' if trl >= 5 else 'Market entry timing requiring strategic planning' if trl >= 3 else 'Market entry strategy requiring development'}

**Market Development Risks:**
- {'Market development investment requirements and timeline uncertainty' if trl >= 4 else 'Market development planning and resource allocation' if trl >= 2 else 'Market development strategy requiring definition'}
- {'Customer acquisition and retention challenges' if trl >= 5 else 'Customer acquisition strategy development' if trl >= 3 else 'Customer acquisition approach requiring validation'}
- {'Pricing and revenue model validation and optimization' if trl >= 5 else 'Pricing strategy development and validation' if trl >= 3 else 'Revenue model requiring development and validation'}

**Market Execution Risks:**
- {'Distribution channel development and management' if trl >= 5 else 'Distribution strategy development' if trl >= 3 else 'Distribution approach requiring exploration'}
- {'Sales and marketing execution effectiveness' if trl >= 5 else 'Sales and marketing strategy development' if trl >= 3 else 'Go-to-market strategy requiring development'}
- {'Regulatory and compliance requirements for market entry' if trl >= 5 else 'Regulatory considerations for market entry' if trl >= 3 else 'Regulatory requirements assessment and planning'}
"""
    return analysis.strip()


def _generate_ip_competitive_analysis(
    originality: dict[str, Any],
    fto: dict[str, Any],
    classification: dict[str, Any]
) -> str:
    """Generate detailed IP and competitive analysis with extensive depth."""
    max_similarity = originality.get("max_cosine_similarity", 0)
    patent_corpus = originality.get("patent_corpus_size", "Unknown")
    top_matches = originality.get("top_patent_matches", [])[:5]
    fto_risk = fto.get("risk_tier_pct", 0)
    flagged_count = fto.get("flagged_patent_count", 0)
    sector = classification.get("sector_name", "Deep Technology")
    
    analysis = f"""
## Intellectual Property and Competitive Analysis

### Patent Landscape Positioning and Novelty Assessment

The technology's novelty assessment against a comprehensive patent corpus of {patent_corpus} patents reveals {'exceptional differentiation with strong competitive advantages' if max_similarity < 0.2 else 'strong differentiation with clear competitive advantages' if max_similarity < 0.4 else 'moderate differentiation with some competitive advantages' if max_similarity < 0.6 else 'incremental advancement with limited differentiation' if max_similarity < 0.8 else 'limited differentiation with significant competitive challenges'}. The maximum cosine similarity of {max_similarity:.3f} indicates {'minimal overlap with existing patents, suggesting strong novelty' if max_similarity < 0.3 else 'some overlap with prior art, indicating moderate novelty' if max_similarity < 0.6 else 'significant overlap with existing patents, suggesting incremental innovation' if max_similarity < 0.8 else 'extensive overlap with existing patents, indicating limited novelty'}.

The patent landscape analysis provides critical insights into the technology's competitive positioning:
- **Novelty Level**: {'Exceptional novelty with strong patentability potential' if max_similarity < 0.2 else 'High novelty with good patentability potential' if max_similarity < 0.4 else 'Moderate novelty with some patentability potential' if max_similarity < 0.6 else 'Incremental novelty with limited patentability potential' if max_similarity < 0.8 else 'Limited novelty with challenging patentability'}
- **IP Protection Potential**: {'Strong IP protection potential with broad claim scope' if max_similarity < 0.3 else 'Good IP protection potential with moderate claim scope' if max_similarity < 0.5 else 'Moderate IP protection potential with narrow claim scope' if max_similarity < 0.7 else 'Limited IP protection potential requiring strategic claim drafting'}
- **Competitive Positioning**: {'Strong competitive positioning with defensible advantages' if max_similarity < 0.4 else 'Moderate competitive positioning with some differentiation' if max_similarity < 0.6 else 'Limited competitive positioning requiring strategic differentiation' if max_similarity < 0.8 else 'Challenging competitive positioning requiring comprehensive strategy'}

### Key Patent References and Competitive Intelligence

The comprehensive patent analysis identified several relevant patents that inform the competitive landscape and provide insights into prior art and competitive positioning:
"""
    
    for match in top_matches:
        analysis += f"""
- **{match.get('patent_id', 'Unknown')}**: {match.get('title', 'No title')} (Similarity: {match.get('cosine_similarity', 0):.3f}) - This patent represents {'direct competition with significant overlap' if match.get('cosine_similarity', 0) > 0.7 else 'indirect competition with some overlap' if match.get('cosine_similarity', 0) > 0.4 else 'tangential competition with limited overlap' if match.get('cosine_similarity', 0) > 0.2 else 'minimal competition with little overlap'}
"""
    
    analysis += f"""
These patent references provide critical insights into:
- **Technical Approaches**: Understanding of existing technical solutions and approaches in the domain
- **Claim Scope**: Analysis of existing patent claims and potential claim scope for new applications
- **Competitive Landscape**: Identification of key competitors and their technical strategies
- **White Space Analysis**: Identification of opportunities for innovation and differentiation

### Freedom to Operate (FTO) Assessment and Risk Analysis

The comprehensive FTO analysis identified {flagged_count} potentially relevant patents with an overall risk tier of {fto_risk:.1f}%. This risk level suggests {'minimal IP barriers to commercialization with favorable conditions' if fto_risk < 15 else 'low IP barriers with manageable considerations' if fto_risk < 30 else 'moderate IP considerations requiring strategic management' if fto_risk < 50 else 'significant IP landscape requiring comprehensive strategy and potential licensing arrangements' if fto_risk < 70 else 'extensive IP landscape requiring comprehensive strategy and significant licensing arrangements'}.

The FTO assessment considers multiple critical dimensions:
- **Patent Overlap Analysis**: {'Minimal patent overlap with existing solutions, suggesting strong freedom to operate' if fto_risk < 20 else 'Some patent overlap requiring careful review and analysis' if fto_risk < 40 else 'Significant patent overlap requiring strategic IP management' if fto_risk < 60 else 'Extensive patent overlap requiring comprehensive IP strategy and potential licensing'}
- **Claim Scope Analysis**: {'Broad claim scope potential with strong IP protection' if fto_risk < 20 else 'Moderate claim scope potential with good IP protection' if fto_risk < 40 else 'Narrow claim scope potential with limited IP protection' if fto_risk < 60 else 'Limited claim scope potential requiring careful claim drafting and strategy'}
- **Landscape Complexity**: {'Simple patent landscape with clear positioning opportunities' if fto_risk < 20 else 'Moderate patent landscape complexity requiring strategic navigation' if fto_risk < 40 else 'Complex patent landscape requiring comprehensive strategy' if fto_risk < 60 else 'Highly complex patent landscape requiring extensive IP management'}

### Comprehensive IP Strategy Recommendations

Based on the comprehensive patent landscape and FTO analysis, the following IP strategy recommendations are provided:

**Patent Filing Strategy:**
- {'File comprehensive patent applications to protect core innovations with broad claim scope' if max_similarity < 0.4 else 'Develop strategic IP portfolio around differentiated features with focused claim scope' if max_similarity < 0.7 else 'Focus on trade secrets andKnow-how protection with selective patent filing'}
- {'Conduct regular freedom-to-operate analyses as technology develops and evolves' if fto_risk > 20 else 'Monitor patent landscape for emerging competitors and technological developments'}
- {'Consider international patent filings for key markets and jurisdictions' if max_similarity < 0.4 else 'Evaluate strategic international patent filings for key markets' if max_similarity < 0.7 else 'Focus on domestic patent protection with selective international filings'}
- {'Develop patent filing strategy aligned with commercialization timeline and market entry plans' if max_similarity < 0.5 else 'Align patent filing strategy with development milestones and market validation'}

**IP Portfolio Management:**
- {'Develop comprehensive IP portfolio strategy with clear objectives and milestones' if max_similarity < 0.4 else 'Develop focused IP portfolio strategy around key differentiators' if max_similarity < 0.7 else 'Develop selective IP portfolio strategy focused on core innovations'}
- {'Implement regular IP portfolio review and optimization processes' if max_similarity < 0.5 else 'Conduct periodic IP portfolio reviews and assessments'}
- {'Consider licensing arrangements for complementary technologies and applications' if flagged_count > 3 else 'Evaluate potential for cross-licensing opportunities with strategic partners'}
- {'Develop IP monetization strategy aligned with commercialization timeline and business objectives' if max_similarity < 0.5 else 'Consider IP monetization opportunities aligned with business strategy'}

**Competitive IP Positioning:**
- {'Develop strong IP positioning with defensible competitive advantages' if max_similarity < 0.4 else 'Develop moderate IP positioning with competitive differentiation' if max_similarity < 0.7 else 'Develop defensive IP positioning with limited competitive advantages'}
- {'Monitor competitive IP landscape and respond strategically to competitor filings' if fto_risk > 20 else 'Monitor competitive IP landscape for emerging threats and opportunities'}
- {'Consider defensive patent filings to protect key technologies and applications' if max_similarity < 0.5 else 'Evaluate defensive patent filing opportunities for key innovations'}
- {'Develop IP strategy aligned with overall business and competitive strategy' if max_similarity < 0.5 else 'Align IP strategy with business objectives and competitive positioning'}

### Competitive Differentiation and Market Positioning

The technology's competitive advantage stems from {'novel approach with strong patentability and clear differentiation' if max_similarity < 0.4 else 'differentiated features in competitive landscape with some patentability' if max_similarity < 0.7 else 'incremental improvements over existing solutions with limited patentability' if max_similarity < 0.8 else 'limited differentiation with challenging patentability and competitive positioning'}. Strategic positioning should emphasize {'unique value proposition and strong IP protection' if max_similarity < 0.4 else 'specific differentiation and market fit with moderate IP protection' if max_similarity < 0.7 else 'cost or performance advantages with selective IP protection' if max_similarity < 0.8 else 'strategic positioning requiring comprehensive IP and competitive strategy'}.

Competitive differentiation strategies include:
- **Technical Differentiation**: {'Leverage novel technical approach with strong patent protection' if max_similarity < 0.4 else 'Leverage differentiated technical features with moderate patent protection' if max_similarity < 0.7 else 'Leverage incremental technical improvements with selective patent protection'}
- **Market Differentiation**: {'Focus on underserved market segments with strong value proposition' if max_similarity < 0.4 else 'Focus on specific market segments with clear value proposition' if max_similarity < 0.7 else 'Focus on market segments with cost or performance advantages'}
- **IP Differentiation**: {'Leverage strong IP position for competitive advantage and market protection' if max_similarity < 0.4 else 'Leverage moderate IP position for competitive differentiation' if max_similarity < 0.7 else 'Leverage selective IP protection for specific applications'}
- **Commercial Differentiation**: {'Develop unique commercial model aligned with IP position and market opportunity' if max_similarity < 0.4 else 'Develop commercial model aligned with IP position and market fit' if max_similarity < 0.7 else 'Develop commercial model focused on cost or performance advantages'}
"""
    return analysis.strip()


def _generate_development_roadmap(
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any],
    valuation: dict[str, Any]
) -> str:
    """Generate detailed development roadmap with extensive depth."""
    trl = trl_evaluation.get("trl", 3)
    milestones = trl_evaluation.get("milestones", {})
    missing_for_next = trl_evaluation.get("missing_for_next_trl", [])
    development_insights = market_mapping.get("development_insights", {})
    
    analysis = f"""
## Development Roadmap and Commercialization Strategy

### Current Development Status Assessment

The technology is currently at Technology Readiness Level (TRL) {trl}, representing {'commercialization-ready stage with demonstrated scalability and market readiness' if trl >= 8 else 'advanced development stage with pilot-scale validation and commercialization pathway' if trl >= 6 else 'prototype development stage with validated functionality and defined roadmap' if trl >= 4 else 'laboratory validation stage with promising results and development potential' if trl >= 3 else 'proof-of-concept stage with theoretical validation and development potential' if trl >= 2 else 'conceptual research stage requiring fundamental validation and development'}. {development_insights.get('current_stage_assessment', 'The technology shows promising development progress with clear commercialization potential.')}

The current TRL {trl} status indicates {'significant progress toward commercialization with clear development path' if trl >= 6 else 'promising progress with defined development roadmap' if trl >= 4 else 'early progress requiring significant development investment' if trl >= 2 else 'conceptual stage requiring fundamental research and development investment'}. The technology has achieved {'critical milestones demonstrating commercial viability' if trl >= 6 else 'important milestones validating technical feasibility' if trl >= 4 else 'promising milestones showing development potential' if trl >= 2 else 'initial milestones establishing research direction'}.

### Comprehensive Milestone Analysis and Timeline

The development roadmap consists of critical milestones that must be achieved to advance through the TRL scale and achieve commercialization:
"""
    
    for milestone_name, milestone_data in milestones.items():
        status = milestone_data.get("status", "future")
        description = milestone_data.get("description", "")
        timeline = milestone_data.get("timeline", "TBD")
        analysis += f"""
#### {milestone_name.replace('_', ' ').title()}
- **Status**: {status.upper()} - {'Completed and validated' if status == 'completed' else 'Currently in progress with active development' if status == 'current' else 'Planned for future development phase'}
- **Description**: {description}
- **Timeline**: {timeline}
- **Critical Success Factors**: {'Technical validation and performance demonstration' if 'validation' in description.lower() else 'Prototype development and testing' if 'prototype' in description.lower() else 'Scale-up and manufacturing development' if 'scale' in description.lower() or 'manufactur' in description.lower() else 'Market validation and customer engagement' if 'market' in description.lower() else 'Regulatory compliance and certification' if 'regulatory' in description.lower() else 'Technical development and optimization'}
"""
    
    analysis += f"""
### Critical Next Steps and Development Priorities

To advance to the next TRL level, the following critical activities must be completed:
"""
    
    for step in missing_for_next[:8]:
        analysis += f"\n- {step}"
    
    analysis += f"""

These next steps are {'critical for advancing the technology to the next development stage' if len(missing_for_next) > 0 else 'well-defined with clear execution path'}. The development priorities should focus on {'technical validation and performance demonstration' if trl >= 4 else 'fundamental research and proof-of-concept development' if trl >= 2 else 'conceptual validation and research direction establishment'}.

### Resource Requirements and Development Planning

Based on the current development stage, the technology requires significant resources across multiple dimensions:

**Funding Requirements:"""
    
    funding = development_insights.get("funding_recommendations", {})
    analysis += f"""
- **Current Stage**: {funding.get('stage', 'Seed funding for research and development')}
- **Estimated Range**: {funding.get('estimated_range', '$500K-2M for initial development phase')}
- **Focus Areas**: {', '.join(funding.get('focus_areas', ['R&D', 'prototype development', 'technical validation']))}
- **Funding Strategy**: {'Strategic funding aligned with development milestones and commercialization timeline' if trl >= 4 else 'Research funding focused on technical validation and proof-of-concept development' if trl >= 2 else 'Conceptual research funding for fundamental validation'}

**Technical Resources:**
- {'Expert technical team with relevant domain expertise and development experience' if trl >= 4 else 'Technical team with research capabilities and domain knowledge' if trl >= 2 else 'Research team with fundamental expertise in the domain'}
- {'Advanced laboratory and testing facilities for validation and optimization' if trl >= 4 else 'Basic laboratory facilities for experimental validation' if trl >= 2 else 'Research facilities for fundamental research and validation'}
- {'Manufacturing and scale-up capabilities for production development' if trl >= 6 else 'Manufacturing feasibility assessment and planning' if trl >= 4 else 'Manufacturing concept development and feasibility assessment'}
- {'Quality control and regulatory compliance infrastructure' if trl >= 6 else 'Quality control and regulatory planning' if trl >= 4 else 'Quality control and regulatory requirements assessment'}

**Development Timeline:**
- {'12-18 months to commercialization with focused execution' if trl >= 6 else '18-24 months to commercialization with comprehensive development' if trl >= 4 else '24-36 months to commercialization with significant development investment' if trl >= 2 else '36-48 months to commercialization with fundamental research and development'}
- {'Clear development milestones with achievable timelines' if len(milestones) > 3 else 'Development milestones requiring definition and planning'}
- {'Regular progress reviews and milestone adjustments based on development progress' if trl >= 4 else 'Progress reviews and milestone planning based on development achievements'}

### Strategic Development Partnerships

The technology would benefit significantly from strategic partnerships to accelerate development and commercialization:

**Research and Development Partnerships:**
- {'Industry leaders for scale-up, manufacturing, and commercialization support' if trl >= 6 else 'Strategic partners for pilot validation and operational testing' if trl >= 4 else 'Research institutions for collaborative development and validation' if trl >= 2 else 'Academic collaborators for fundamental research and validation'}
- {'Technical experts for specialized development and optimization' if trl >= 4 else 'Domain experts for research guidance and validation' if trl >= 2 else 'Research collaborators for fundamental research direction'}
- {'Manufacturing partners for production scale-up and optimization' if trl >= 6 else 'Manufacturing feasibility partners for production planning' if trl >= 4 else 'Manufacturing concept partners for feasibility assessment'}

**Commercial Partnerships:**
- {'Strategic customers for market validation and early adoption' if trl >= 5 else 'Potential customers for market feedback and validation' if trl >= 3 else 'Market partners for opportunity validation and assessment'}
- {'Distribution partners for market access and commercialization' if trl >= 6 else 'Distribution partners for market entry planning' if trl >= 4 else 'Distribution strategy partners for market entry assessment'}
- {'Investment partners for funding and strategic guidance' if trl >= 4 else 'Funding partners for research and development investment' if trl >= 2 else 'Research funding partners for fundamental research investment'}

**Regulatory and Standards Partnerships:**
- {'Regulatory bodies for compliance guidance and certification' if trl >= 6 else 'Regulatory experts for compliance planning and assessment' if trl >= 4 else 'Regulatory advisors for requirements identification and planning'}
- {'Standards organizations for specification alignment and industry acceptance' if trl >= 5 else 'Standards bodies for requirements identification and alignment' if trl >= 3 else 'Standards organizations for requirements assessment and planning'}
- {'Industry associations for market access and acceptance' if trl >= 5 else 'Industry groups for market validation and acceptance' if trl >= 3 else 'Industry organizations for market opportunity assessment'}

### Risk Mitigation and Contingency Planning

The development roadmap includes comprehensive risk mitigation and contingency planning:

**Technical Risk Mitigation:**
- {'Comprehensive technical validation across multiple scenarios and conditions' if trl >= 4 else 'Technical validation with multiple test cases and conditions' if trl >= 2 else 'Technical validation planning and experimental design'}
- {'Redundant development approaches and alternative technical solutions' if trl >= 4 else 'Alternative technical approaches for risk mitigation' if trl >= 2 else 'Technical contingency planning and alternative approaches'}
- {'Regular technical reviews and milestone adjustments based on development progress' if trl >= 4 else 'Technical reviews and milestone planning based on development achievements'}

**Development Risk Mitigation:**
- {'Phased development approach with validation at each stage' if trl >= 4 else 'Staged development with validation checkpoints' if trl >= 2 else 'Phased research approach with validation milestones'}
- {'Resource allocation flexibility and contingency planning' if trl >= 4 else 'Resource planning with contingency considerations' if trl >= 2 else 'Resource planning with flexibility for research direction adjustments'}
- {'Timeline flexibility with buffer periods for unforeseen challenges' if trl >= 4 else 'Timeline planning with contingency buffers' if trl >= 2 else 'Research timeline planning with flexibility for fundamental discoveries'}

**Commercial Risk Mitigation:**
- {'Market validation and customer engagement throughout development' if trl >= 5 else 'Market assessment and customer feedback integration' if trl >= 3 else 'Market opportunity validation and assessment'}
- {'Flexible commercialization strategy based on development outcomes' if trl >= 5 else 'Commercialization strategy planning based on development progress' if trl >= 3 else 'Commercialization approach planning based on research outcomes'}
- {'Strategic partnerships for market access and commercialization support' if trl >= 5 else 'Partnership development for market entry support' if trl >= 3 else 'Partnership exploration for market opportunity validation'}
"""
    return analysis.strip()


def _generate_risk_assessment(
    fto: dict[str, Any],
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any]
) -> str:
    """Generate detailed risk assessment with extensive depth."""
    fto_risk = fto.get("risk_tier_pct", 0)
    trl = trl_evaluation.get("trl", 3)
    competitive = market_mapping.get("competitive_analysis", {})
    barriers = competitive.get("barriers_to_entry", [])
    
    analysis = f"""
## Comprehensive Risk Assessment and Mitigation Strategy

### Intellectual Property Risk Analysis

The IP risk assessment indicates {'minimal risk profile with favorable conditions for commercialization' if fto_risk < 20 else 'low risk profile with manageable IP considerations' if fto_risk < 40 else 'moderate risk profile requiring strategic IP management' if fto_risk < 60 else 'elevated risk profile requiring comprehensive IP strategy' if fto_risk < 80 else 'high risk profile requiring extensive IP management and potential licensing arrangements'} with a risk tier of {fto_risk:.1f}%. Key IP considerations include:

**Patent Infringement Risks:**
- Patent infringement risks from {fto.get('flagged_patent_count', 0)} identified patents requiring {'careful analysis and potential design-arounds' if fto_risk > 30 else 'review and monitoring' if fto_risk > 15 else 'periodic monitoring'}
- {'Need for comprehensive IP landscape monitoring as technology develops' if fto_risk > 20 else 'Need for periodic IP landscape review' if fto_risk > 10 else 'Need for basic IP landscape awareness'}
- {'Potential for licensing requirements or strategic partnerships' if fto_risk > 40 else 'Potential for selective licensing arrangements' if fto_risk > 20 else 'Limited licensing requirements expected'}

**IP Strategy Risks:**
- {'Comprehensive IP strategy development and implementation requirements' if fto_risk > 30 else 'Strategic IP planning and management requirements' if fto_risk > 15 else 'Basic IP strategy considerations'}
- {'Patent filing timing and strategy optimization challenges' if fto_risk > 25 else 'Patent filing strategy planning requirements' if fto_risk > 10 else 'Patent filing timeline considerations'}
- {'International IP protection and enforcement challenges' if fto_risk > 35 else 'International IP protection considerations' if fto_risk > 15 else 'Domestic IP protection focus'}

### Technical Development Risks

Based on the current TRL {trl} status, technical risks include {'significant development challenges requiring comprehensive management' if trl < 4 else 'manageable development risks requiring strategic planning' if trl < 6 else 'focused development risks requiring attention' if trl < 8 else 'minimal technical risks with clear mitigation strategies'}:

**Scale-up and Manufacturing Risks:**
- Scale-up challenges from laboratory to production environments with {'comprehensive process optimization and validation' if trl >= 4 else 'process development and optimization' if trl >= 2 else 'conceptual process development planning'}
- Manufacturing process development and optimization for commercial production with {'quality control and consistency requirements' if trl >= 5 else 'quality control planning and development' if trl >= 3 else 'quality control concept development'}
- Supply chain development and management for production scale-up with {'multiple supplier relationships and contingency planning' if trl >= 5 else 'supplier development and planning' if trl >= 3 else 'supply chain concept development'}

**Performance and Validation Risks:**
- Performance consistency in real-world conditions with {'comprehensive validation across diverse operating conditions' if trl >= 5 else 'validation across relevant conditions' if trl >= 3 else 'validation planning and experimental design'}
- Long-term performance and stability assessment with {'accelerated testing and reliability engineering' if trl >= 5 else 'reliability testing and assessment' if trl >= 3 else 'reliability concept development and planning'}
- Technical validation across multiple scenarios and use cases with {'comprehensive testing protocols and validation frameworks' if trl >= 5 else 'testing protocol development and validation' if trl >= 3 else 'testing concept development and planning'}

**Technical Complexity Risks:**
- Technical complexity management with {'expert team and specialized resources' if trl >= 4 else 'technical team with domain expertise' if trl >= 2 else 'research team with fundamental expertise'}
- Technical integration challenges with existing systems and infrastructure with {'comprehensive integration planning and testing' if trl >= 5 else 'integration planning and development' if trl >= 3 else 'integration concept development'}
- Technical documentation and knowledge transfer requirements with {'comprehensive documentation and training programs' if trl >= 5 else 'documentation development and planning' if trl >= 3 else 'documentation concept development'}

### Market and Commercialization Risks

Market entry risks include {'significant market challenges requiring comprehensive strategy' if competitive.get('market_saturation') == 'High' else 'manageable market risks requiring strategic planning' if competitive.get('market_saturation') == 'Medium' else 'favorable market conditions with minimal risks'}:

**Market Adoption and Acceptance Risks:**
- Customer adoption challenges requiring {'comprehensive education and validation programs' if trl >= 4 else 'education and validation planning' if trl >= 2 else 'education concept development'}
- Market acceptance and customer adoption timeline uncertainty with {'comprehensive market validation and customer engagement' if trl >= 5 else 'market validation and customer feedback' if trl >= 3 else 'market opportunity validation and assessment'}
- Competitive response and market dynamics requiring {'strategic positioning and competitive monitoring' if competitive.get('market_saturation') == 'High' else 'competitive monitoring and response planning' if competitive.get('market_saturation') == 'Medium' else 'competitive landscape monitoring'}

**Market Development and Execution Risks:**
- Market development investment requirements and timeline uncertainty with {'comprehensive market development planning and resource allocation' if trl >= 4 else 'market development planning and resource allocation' if trl >= 2 else 'market development concept development'}
- Customer acquisition and retention challenges with {'comprehensive customer acquisition strategy and retention programs' if trl >= 5 else 'customer acquisition strategy development' if trl >= 3 else 'customer acquisition concept development'}
- Pricing and revenue model validation and optimization with {'comprehensive pricing strategy and revenue model development' if trl >= 5 else 'pricing strategy development and validation' if trl >= 3 else 'pricing concept development and validation'}

**Market Entry and Distribution Risks:**
- Distribution channel development and management challenges with {'comprehensive distribution strategy and channel development' if trl >= 5 else 'distribution strategy development' if trl >= 3 else 'distribution concept development'}
- Sales and marketing execution effectiveness with {'comprehensive go-to-market strategy and execution planning' if trl >= 5 else 'go-to-market strategy development' if trl >= 3 else 'go-to-market concept development'}
- Regulatory and compliance requirements for market entry with {'comprehensive regulatory compliance and certification programs' if trl >= 5 else 'regulatory compliance planning and assessment' if trl >= 3 else 'regulatory requirements identification and planning'}

### Development and Execution Risks

**Timeline and Budget Execution Risks:**
- Timeline and budget execution risks with {'comprehensive project management and contingency planning' if trl >= 4 else 'project management and contingency planning' if trl >= 2 else 'project management concept development'}
- Resource allocation and management challenges with {'comprehensive resource planning and allocation strategies' if trl >= 4 else 'resource planning and allocation' if trl >= 2 else 'resource planning concept development'}
- Milestone achievement and progress tracking with {'comprehensive milestone tracking and progress management' if trl >= 4 else 'milestone tracking and progress management' if trl >= 2 else 'milestone tracking concept development'}

**Team and Expertise Risks:**
- Technical team and expertise requirements with {'comprehensive team development and expertise acquisition' if trl >= 3 else 'team development and expertise planning' if trl >= 2 else 'team concept development'}
- Key person dependencies and knowledge management with {'comprehensive knowledge management and succession planning' if trl >= 4 else 'knowledge management and planning' if trl >= 2 else 'knowledge management concept development'}
- Team coordination and communication challenges with {'comprehensive team coordination and communication protocols' if trl >= 4 else 'team coordination and communication planning' if trl >= 2 else 'team coordination concept development'}

### Strategic Risk Mitigation Framework

The overall risk profile presents {'favorable risk-reward ratio with clear mitigation strategies' if fto_risk < 30 and trl >= 4 else 'balanced risk-reward profile requiring comprehensive management' if fto_risk < 50 and trl >= 2 else 'challenging risk-reward profile requiring extensive mitigation strategy' if fto_risk < 70 else 'high-risk profile requiring comprehensive mitigation and contingency planning'}. Success probability is enhanced by {'strong technical foundation and clear market opportunity with defined mitigation strategies' if trl >= 4 and fto_risk < 40 else 'promising research direction and development potential with risk management' if trl >= 2 and fto_risk < 60 else 'research foundation requiring comprehensive risk management and development'}.

**Risk Mitigation Priorities:**
1. {'IP strategy development and implementation' if fto_risk > 30 else 'IP landscape monitoring and management' if fto_risk > 15 else 'IP awareness and planning'}
2. {'Technical validation and performance optimization' if trl >= 4 else 'Technical validation planning and development' if trl >= 2 else 'Technical validation concept development'}
3. {'Market validation and customer engagement' if trl >= 4 else 'Market validation planning and assessment' if trl >= 2 else 'Market opportunity validation'}
4. {'Development planning and resource allocation' if trl >= 4 else 'Development planning and resource management' if trl >= 2 else 'Development concept planning'}

**Contingency Planning:**
- {'Comprehensive contingency planning with alternative approaches and backup strategies' if fto_risk > 40 or trl < 4 else 'Strategic contingency planning with alternative approaches' if fto_risk > 20 or trl < 6 else 'Basic contingency planning with risk monitoring'}
- {'Regular risk assessment and mitigation strategy adjustment' if fto_risk > 30 or trl < 4 else 'Periodic risk assessment and strategy review' if fto_risk > 15 or trl < 6 else 'Risk monitoring and periodic assessment'}
- {'Stakeholder communication and risk transparency' if fto_risk > 30 or trl < 4 else 'Stakeholder communication and risk reporting' if fto_risk > 15 or trl < 6 else 'Stakeholder communication and risk awareness'}
"""
    return analysis.strip()


def _generate_strategic_recommendations(
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any],
    valuation: dict[str, Any],
    fto: dict[str, Any]
) -> str:
    """Generate detailed strategic recommendations with extensive depth."""
    trl = trl_evaluation.get("trl", 3)
    strategic_recs = market_mapping.get("strategic_recommendations", [])
    development_insights = market_mapping.get("development_insights", {})
    fto_risk = fto.get("risk_tier_pct", 0)
    
    analysis = f"""
## Strategic Recommendations and Action Plan

### Immediate Actions (0-6 months) - Critical Priorities

Based on the current TRL {trl} status, immediate priorities include {'comprehensive development and validation activities' if trl < 4 else 'strategic development and commercialization preparation' if trl < 7 else 'market execution and commercialization activities'}:

**Technical Development Priorities:**
"""
    
    if trl < 4:
        analysis += """
- Complete comprehensive experimental validation across multiple scenarios and conditions
- Develop and validate prototype functionality with performance metrics
- Establish robust experimental protocols and testing frameworks
- Document technical methodologies and reproducibility protocols
- Conduct thorough technical risk assessment and mitigation planning
"""
    elif trl < 7:
        analysis += """
- Advance to pilot-scale demonstrations with operational environment validation
- Optimize technical performance for real-world applications and conditions
- Develop manufacturing processes and scale-up capabilities
- Establish quality control protocols and consistency measures
- Conduct comprehensive technical validation across diverse operating conditions
"""
    else:
        analysis += """
- Execute market entry strategy with initial customer deployments and feedback
- Scale manufacturing capabilities and optimize production processes
- Establish comprehensive quality assurance and regulatory compliance programs
- Develop customer support and service infrastructure
- Optimize technical performance for commercial applications and customer requirements
"""
    
    analysis += f"""

**Intellectual Property Priorities:**
"""
    
    if fto_risk > 30:
        analysis += """
- Conduct comprehensive freedom-to-operate analysis and IP landscape assessment
- File comprehensive patent applications with broad claim scope for core innovations
- Develop strategic IP portfolio with defensive and offensive positioning
- Implement regular IP landscape monitoring and competitive intelligence
- Consider licensing arrangements for complementary technologies and applications
"""
    elif fto_risk > 15:
        analysis += """
- Conduct freedom-to-operate analysis and IP landscape review
- File strategic patent applications for core innovations and key differentiators
- Develop focused IP portfolio around competitive advantages
- Implement periodic IP landscape monitoring and competitive assessment
- Evaluate licensing opportunities for complementary technologies
"""
    else:
        analysis += """
- File provisional patent applications to protect core innovations
- Develop basic IP strategy aligned with commercialization timeline
- Monitor IP landscape for emerging competitors and technological developments
- Evaluate international patent filing opportunities for key markets
- Consider selective licensing arrangements for specific applications
"""
    
    analysis += f"""

**Partnership and Collaboration Priorities:**
"""
    
    if trl < 4:
        analysis += """
- Engage with potential industry partners for research collaboration and validation
- Establish relationships with academic institutions for collaborative research
- Identify strategic partners for prototype development and testing
- Build relationships with potential customers for market validation
- Explore government research programs and funding opportunities
"""
    elif trl < 7:
        analysis += """
- Secure strategic partnerships for operational validation and pilot testing
- Establish relationships with manufacturing partners for scale-up development
- Engage with potential customers for market validation and feedback
- Build relationships with regulatory bodies for compliance planning
- Develop ecosystem partnerships for comprehensive market solution
"""
    else:
        analysis += """
- Execute strategic partnerships for market entry and commercialization
- Establish manufacturing partnerships for production scale-up and optimization
- Engage with customers for market deployment and feedback collection
- Develop distribution partnerships for market access and expansion
- Build ecosystem partnerships for comprehensive market solution and customer value
"""
    
    analysis += f"""

**Funding and Resource Priorities:**
"""
    
    if trl < 4:
        analysis += """
- Secure seed funding for prototype development and technical validation
- Develop comprehensive funding strategy aligned with development milestones
- Engage with angel investors and research grant opportunities
- Build relationships with venture capital firms for future funding rounds
- Establish resource allocation framework for efficient development execution
"""
    elif trl < 7:
        analysis += """
- Pursue Series A funding for commercialization preparation and scale-up
- Engage with strategic investors and corporate partners for development support
- Develop comprehensive funding strategy aligned with commercialization timeline
- Build relationships with government funding programs and innovation grants
- Establish resource allocation framework for commercialization execution
"""
    else:
        analysis += """
- Pursue Series B or strategic investment for commercialization and market expansion
- Engage with strategic investors for market entry and growth capital
- Develop comprehensive funding strategy aligned with market expansion plans
- Build relationships with corporate partners for strategic partnerships
- Establish resource allocation framework for market execution and growth
"""
    
    analysis += f"""

### Medium-term Strategy (6-18 months) - Strategic Development

The medium-term strategy focuses on {'technical advancement and market preparation' if trl < 4 else 'commercialization preparation and market entry' if trl < 7 else 'market expansion and growth optimization'}:
"""
    
    for rec in strategic_recs[:6]:
        analysis += f"\n- {rec}"
    
    analysis += f"""

### Long-term Strategic Positioning (18-36 months) - Market Leadership

The technology should pursue {'fundamental research breakthrough and validation' if trl < 4 else 'commercialization and market establishment' if trl < 7 else 'market leadership and expansion'}:
"""
    
    next_critical = development_insights.get("next_critical_milestones", [])
    for milestone in next_critical[:6]:
        analysis += f"\n- {milestone}"
    
    analysis += f"""

### Comprehensive Partnership and Collaboration Strategy

**Research and Development Partnerships:**
- {'Focus on licensing agreements with established manufacturers for production scale-up' if trl >= 7 else 'Prioritize joint development with strategic partners for technical validation' if trl >= 4 else 'Emphasize research collaborations with academic institutions for fundamental research'}
- {'Engage with customers early in commercialization process for market validation' if trl >= 6 else 'Build relationships with potential customers during development for market feedback' if trl >= 3 else 'Identify potential customer segments for market opportunity validation'}
- {'Develop ecosystem partnerships for comprehensive market solution and customer value' if trl >= 5 else 'Identify complementary technology partners for integrated solutions' if trl >= 3 else 'Explore research collaborations for technical development and validation'}

**Commercial and Market Partnerships:**
- {'Establish distribution partnerships for market access and expansion' if trl >= 6 else 'Identify potential distribution partners for market entry planning' if trl >= 4 else 'Explore distribution opportunities for market entry assessment'}
- {'Develop strategic partnerships with industry leaders for market validation and credibility' if trl >= 5 else 'Build relationships with industry leaders for technical validation and market insight' if trl >= 3 else 'Identify industry leaders for research collaboration and market insight'}
- {'Engage with regulatory bodies for compliance guidance and certification' if trl >= 6 else 'Build relationships with regulatory experts for compliance planning' if trl >= 4 else 'Identify regulatory requirements for market entry planning'}

### Comprehensive Funding and Investment Strategy

**Current Stage and Funding Requirements:"""
    
    funding = development_insights.get("funding_recommendations", {})
    analysis += f"""
- **Current Stage**: {funding.get('stage', 'Seed funding for research and development')}
- **Funding Focus**: {', '.join(funding.get('focus_areas', ['R&D', 'prototype development', 'technical validation']))}
- **Estimated Range**: {funding.get('estimated_range', '$500K-2M for initial development phase')}
- **Funding Strategy**: {'Strategic funding aligned with development milestones and commercialization timeline' if trl >= 4 else 'Research funding focused on technical validation and proof-of-concept development' if trl >= 2 else 'Conceptual research funding for fundamental validation'}

**Investor Targeting and Engagement:**
- {'Strategic investors and corporate partners for commercialization support' if trl >= 6 else 'Deep tech VCs and government grants for development funding' if trl >= 4 else 'Angel investors and research grants for research funding'}
- {'Investment thesis focused on commercialization and market opportunity' if trl >= 6 else 'Investment thesis focused on technical validation and development progress' if trl >= 4 else 'Investment thesis focused on research breakthrough and validation potential'}
- {'Valuation strategy leveraging $' + f"{valuation.get('v_target_usd', 0):,.0f}" + ' target valuation with clear value demonstration' if trl >= 4 else 'Valuation strategy based on research potential and development progress'}
- {'Investment structure aligned with commercialization timeline and milestones' if trl >= 5 else 'Investment structure aligned with development milestones and validation'}

**Funding Timeline and Milestones:**
- {'Immediate funding for commercialization execution and market entry' if trl >= 6 else 'Near-term funding for development completion and validation' if trl >= 4 else 'Current funding for research development and validation'}
- {'Follow-on funding for market expansion and growth' if trl >= 6 else 'Follow-on funding for commercialization preparation' if trl >= 4 else 'Follow-on funding for development advancement'}
- {'Strategic funding aligned with key development and commercialization milestones' if trl >= 4 else 'Funding aligned with research milestones and validation achievements'}
- {'Contingency funding for risk mitigation and alternative approaches' if fto_risk > 30 or trl < 4 else 'Strategic contingency funding for development flexibility'}
"""
    return analysis.strip()


def _generate_investment_thesis(
    valuation: dict[str, Any],
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any],
    originality: dict[str, Any]
) -> str:
    """Generate detailed investment thesis with extensive depth."""
    trl = trl_evaluation.get("trl", 3)
    valuation_target = valuation.get("v_target_usd", 0)
    valuation_floor = valuation.get("valuation_floor_usd", 0)
    novelty = originality.get("max_cosine_similarity", 0)
    top_opportunity = market_mapping.get("top_opportunity", "Unknown")
    working_field = market_mapping.get("working_field", "Unknown")
    accuracy_score = market_mapping.get("overall_accuracy_score", 0)
    
    analysis = f"""
## Comprehensive Investment Thesis and Financial Analysis

### Investment Opportunity Summary

This technology represents a {'compelling investment opportunity with strong commercialization potential' if trl >= 5 and novelty < 0.5 else 'promising investment opportunity with clear development path' if trl >= 3 else 'early-stage investment opportunity with significant research potential'} with significant potential for {'commercial success and market impact' if trl >= 6 else 'technology advancement and market entry' if trl >= 4 else 'research breakthrough and validation'}. The valuation range of ${valuation_floor:,.0f} - ${valuation_target:,.0f} reflects the technology's current development stage, market opportunity, and competitive positioning.

The investment opportunity is particularly compelling due to {'strong technical validation and clear commercialization path' if trl >= 6 else 'promising technical progress and defined development roadmap' if trl >= 4 else 'promising research foundation and development potential'}. The technology addresses critical market needs in the {working_field} sector with {'strong market demand and growth potential' if accuracy_score > 70 else 'promising market demand and growth potential' if accuracy_score > 50 else 'emerging market demand requiring validation'}.

### Key Investment Drivers and Value Proposition

**Technology Maturity and Development Progress:**
- TRL {trl} indicates {'advanced development with reduced technical risk and clear commercialization path' if trl >= 6 else 'validated technology with manageable development path and commercialization potential' if trl >= 4 else 'promising research requiring development investment with clear validation milestones'}
- {'Comprehensive technical validation across multiple scenarios and conditions' if trl >= 5 else 'Technical validation with demonstrated feasibility' if trl >= 3 else 'Promising theoretical approach requiring experimental validation'}
- {'Clear development roadmap with achievable milestones and timeline' if trl >= 5 else 'Defined development approach with potential milestones' if trl >= 3 else 'Conceptual development framework requiring definition'}
- {'Strong technical team with relevant expertise and development experience' if trl >= 4 else 'Capable technical team with domain knowledge and research capabilities' if trl >= 2 else 'Technical team requiring development and expertise acquisition'}

**Market Opportunity and Commercial Potential:**
- {top_opportunity} represents a {'significant market opportunity with strong growth potential and clear customer demand' if accuracy_score > 70 else 'promising market opportunity with growth potential and customer interest' if accuracy_score > 50 else 'emerging market opportunity with growth potential requiring validation'}
- {'Large and growing market with significant revenue potential' if valuation_target > 1000000 else 'Moderate market size with growth potential and revenue opportunities' if valuation_target > 500000 else 'Early-stage market with growth potential and revenue opportunity'}
- {'Strong market demand with validated customer needs and purchasing power' if trl >= 5 else 'Emerging market demand with potential customer segments and needs' if trl >= 3 else 'Early market interest requiring validation and customer engagement'}
- {'Favorable competitive dynamics with differentiation opportunities and market entry advantages' if novelty < 0.5 else 'Manageable competitive dynamics with some differentiation opportunities' if novelty < 0.7 else 'Challenging competitive dynamics requiring strategic positioning'}

**Intellectual Property Position and Competitive Advantage:**
- {'Strong IP position with high novelty and broad claim scope potential' if novelty < 0.4 else 'Moderate IP position with differentiation and reasonable claim scope' if novelty < 0.7 else 'Competitive IP position requiring strategic management and focused claim scope'}
- {'Minimal patent overlap with favorable freedom to operate conditions' if novelty < 0.3 else 'Some patent overlap requiring careful review and management' if novelty < 0.6 else 'Significant patent overlap requiring comprehensive IP strategy'}
- {'Strong competitive positioning with defensible advantages and market protection' if novelty < 0.4 else 'Moderate competitive positioning with some differentiation and market advantages' if novelty < 0.7 else 'Challenging competitive positioning requiring strategic differentiation'}
- {'Clear IP strategy with comprehensive patent filing and portfolio management' if trl >= 4 else 'Developing IP strategy with strategic patent filing and portfolio development' if trl >= 2 else 'IP strategy concept requiring development and implementation'}

### Investment Risk Profile and Risk Mitigation

The investment presents a {'favorable risk-reward ratio with clear mitigation strategies and manageable risk profile' if trl >= 5 and novelty < 0.5 else 'balanced risk-reward profile with defined mitigation strategies and acceptable risk level' if trl >= 3 else 'higher-risk, higher-reward opportunity with comprehensive risk management requirements'} with risks primarily related to {'market adoption and execution with clear mitigation strategies' if trl >= 6 else 'technical development and validation with defined risk management approaches' if trl >= 4 else 'research outcomes and technology development with comprehensive risk planning'}.

**Primary Risk Factors:**
- {'Technical development risks with comprehensive validation and mitigation strategies' if trl >= 4 else 'Technical development risks requiring validation and risk management' if trl >= 2 else 'Technical development risks requiring comprehensive planning and validation'}
- {'Market adoption risks with customer engagement and market validation strategies' if trl >= 5 else 'Market adoption risks requiring market validation and customer feedback' if trl >= 3 else 'Market adoption risks requiring market opportunity validation'}
- {'IP risks with comprehensive IP strategy and freedom to operate analysis' if novelty > 0.3 else 'IP risks with strategic IP management and patent landscape monitoring' if novelty > 0.6 else 'IP risks requiring comprehensive IP strategy and management'}
- {'Execution risks with clear development roadmap and resource allocation' if trl >= 4 else 'Execution risks requiring development planning and resource management' if trl >= 2 else 'Execution risks requiring comprehensive planning and resource allocation'}

**Risk Mitigation Strategies:**
- {'Comprehensive technical validation across multiple scenarios with clear success criteria' if trl >= 4 else 'Technical validation with defined success criteria and risk monitoring' if trl >= 2 else 'Technical validation planning with risk assessment and mitigation'}
- {'Market validation and customer engagement throughout development with clear feedback loops' if trl >= 5 else 'Market validation and customer feedback integration with defined validation milestones' if trl >= 3 else 'Market opportunity validation with customer engagement planning'}
- {'Strategic IP management with comprehensive patent portfolio and freedom to operate analysis' if novelty > 0.3 else 'IP strategy development with patent portfolio management and landscape monitoring' if novelty > 0.6 else 'Comprehensive IP strategy development and implementation'}
- {'Phased development approach with clear milestones and contingency planning' if trl >= 4 else 'Staged development with validation checkpoints and risk monitoring' if trl >= 2 else 'Phased research approach with validation milestones and risk planning'}

### Return Potential and Investment Horizon

Based on comprehensive market analysis and technology assessment, the investment offers {'significant return potential with multiple exit scenarios and strong value creation' if valuation_target > 1000000 else 'moderate return potential with clear value creation path and defined exit strategies' if valuation_target > 500000 else 'early-stage return potential with high growth potential and multiple exit possibilities'}:

**Upside Potential Analysis:**
- {'Significant upside potential with multiple exit scenarios including strategic acquisition, IPO, or continued growth' if valuation_target > 1000000 else 'Moderate upside potential with clear value creation path and strategic exit opportunities' if valuation_target > 500000 else 'Early-stage upside potential with high growth potential and multiple exit scenarios'}
- {'Strong revenue potential with clear monetization strategy and market positioning' if trl >= 5 else 'Promising revenue potential with defined monetization approach and market entry strategy' if trl >= 3 else 'Revenue potential requiring market validation and commercialization strategy development'}
- {'Market leadership potential with strong competitive positioning and differentiation' if novelty < 0.4 else 'Market position potential with competitive differentiation and strategic positioning' if novelty < 0.7 else 'Market entry potential requiring strategic positioning and competitive differentiation'}

**Investment Timeline and Milestones:**
- {'2-4 years to commercialization with clear development milestones and market entry strategy' if trl >= 6 else '3-5 years to market entry with defined development roadmap and commercialization timeline' if trl >= 4 else '4-6 years to commercialization with comprehensive development and market validation'}
- {'Clear milestone-based investment structure with defined value inflection points' if trl >= 5 else 'Milestone-based investment approach with development validation points' if trl >= 3 else 'Research milestone-based investment with validation checkpoints'}
- {'Regular value creation through development progress and market validation' if trl >= 4 else 'Value creation through technical validation and development progress' if trl >= 2 else 'Value creation through research breakthrough and validation achievements'}

**Exit Strategy and Value Realization:**
- {'Strategic acquisition or IPO with multiple potential acquirers and clear exit timeline' if trl >= 7 else 'Strategic acquisition or licensing with defined exit opportunities and timeline' if trl >= 5 else 'Acquisition by strategic buyer or further development funding with clear exit path' if trl >= 3 else 'Exit strategy requiring development progress and market validation'}
- {'Strong potential for strategic acquisition by industry leaders seeking technology capabilities' if novelty < 0.4 else 'Potential for strategic acquisition by companies seeking technology enhancement' if novelty < 0.7 else 'Exit through strategic acquisition or continued development funding'}
- {'IPO potential with strong market position and revenue growth' if trl >= 7 and valuation_target > 1000000 else 'IPO potential with market development and revenue growth' if trl >= 5 else 'Exit through strategic acquisition or continued development with future IPO potential'}

### Investment Recommendation and Action Plan

{'Strong Buy - Compelling investment opportunity with strong commercialization potential, favorable risk-reward profile, and clear path to value creation' if trl >= 6 and novelty < 0.5 else 'Buy - Promising investment opportunity with clear development path, manageable risk profile, and strong value creation potential' if trl >= 4 and novelty < 0.6 else 'Speculative Buy - Early-stage investment opportunity with significant potential but higher risk profile requiring comprehensive due diligence' if trl >= 2 else 'Hold for further development - Technology requires additional development and validation before investment recommendation'}

This technology represents a {'compelling investment opportunity for investors seeking exposure to innovative technology with strong market potential and clear commercialization path' if trl >= 5 else 'promising investment opportunity for investors seeking exposure to innovative technology with development potential and market opportunity' if trl >= 3 else 'early-stage investment opportunity for investors seeking exposure to innovative technology with research potential and market opportunity'}.

**Recommended Investment Approach:**
- {'Strategic investment with focus on commercialization support and market entry execution' if trl >= 6 else 'Development investment with focus on technical validation and commercialization preparation' if trl >= 4 else 'Research investment with focus on proof-of-concept development and validation' if trl >= 2 else 'Conceptual investment with focus on fundamental research and validation'}
- {'Phased investment structure aligned with development milestones and value creation' if trl >= 5 else 'Milestone-based investment structure with development validation points' if trl >= 3 else 'Research milestone-based investment with validation checkpoints'}
- {'Active involvement in strategic guidance and commercialization support' if trl >= 6 else 'Strategic involvement in development guidance and market preparation' if trl >= 4 else 'Research guidance and development support involvement'}
- {'Long-term investment horizon with clear exit strategy and value realization timeline' if trl >= 5 else 'Medium-term investment horizon with development timeline and exit planning' if trl >= 3 else 'Long-term investment horizon with research timeline and exit strategy development'}
"""
    return analysis.strip()
