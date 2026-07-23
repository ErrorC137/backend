"""Integration layer for multi-agent system with existing comprehensive analysis pipeline."""

from __future__ import annotations

import os
from typing import Any, Optional

from app.ai_services.agents.coordinator import AgentCoordinator, AgentTask, CoordinatorResult
from app.ai_services.agents.qa_agent import QualityAssuranceAgent, QAValidationResult
from app.ai_services.agents.synthesis_agent import SynthesisAgent, SynthesisResult
from app.ai_services.base import AIService, create_ai_service
from app.ai_services.rate_limiter import get_cost_monitor, get_rate_limiter
from app.comprehensive_analysis import generate_comprehensive_analysis


class MultiAgentAnalysis:
    """Multi-agent analysis system with integration to existing pipeline."""
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_MULTI_AGENT", "true").lower() == "true"
        self.fallback_to_rules = os.getenv("AGENT_FALLBACK_TO_RULES", "true").lower() == "true"
        self.timeout = int(os.getenv("AGENT_COORDINATOR_TIMEOUT", "300"))
        self.rate_limiter = get_rate_limiter()
        self.cost_monitor = get_cost_monitor()
        
        if self.enabled:
            try:
                self.ai_service = create_ai_service()
                self.coordinator = AgentCoordinator(self.ai_service, timeout=self.timeout)
                self.synthesis_agent = SynthesisAgent(self.ai_service)
                self.qa_agent = QualityAssuranceAgent(self.ai_service)
                self.available = True
            except Exception as e:
                print(f"Failed to initialize multi-agent system: {e}")
                self.available = False
                if self.fallback_to_rules:
                    print("Falling back to rule-based analysis")
        else:
            self.available = False
    
    async def analyze_document(
        self,
        doc: Any,
        classification: dict[str, Any],
        originality: dict[str, Any],
        fto: dict[str, Any],
        valuation: dict[str, Any],
        trl_evaluation: dict[str, Any],
        market_mapping: dict[str, Any],
        nlp_analysis: dict[str, Any],
        title: str = "Unknown",
    ) -> dict[str, Any]:
        """Analyze document using multi-agent system or fallback to rule-based."""
        
        if not self.available:
            if self.fallback_to_rules:
                return self._fallback_analysis(
                    doc, classification, originality, fto, valuation, trl_evaluation, market_mapping, nlp_analysis
                )
            else:
                return {"error": "Multi-agent system unavailable and fallback disabled"}
        
        try:
            # Extract document content
            abstract = doc.abstract if doc else ""
            methodology = doc.methodology if doc else ""
            claims_outcomes = doc.claims_outcomes if doc else ""
            document_content = abstract + " " + methodology + " " + claims_outcomes
            
            # Extract sector and working field
            sector = classification.get("sector_name", "Unknown")
            working_field = market_mapping.get("working_field", sector)
            
            # Create agent task
            task = AgentTask(
                task_type="comprehensive",
                document_content=document_content,
                abstract=abstract,
                methodology=methodology,
                claims_outcomes=claims_outcomes,
                sector=sector,
                working_field=working_field,
                patent_data={
                    "total_patents": originality.get("total_patents", 0),
                    "similar_patents": originality.get("similar_patents", 0),
                    "high_similarity": originality.get("high_similarity", 0),
                    "medium_similarity": originality.get("medium_similarity", 0),
                    "fto_risk": fto.get("fto_risk", "Unknown"),
                    "key_references": originality.get("key_references", []),
                },
                market_data={
                    "market_stage": market_mapping.get("market_stage", "Unknown"),
                    "commercial_readiness": market_mapping.get("commercial_readiness", "Unknown"),
                    "customer_validation": market_mapping.get("customer_validation", "Unknown"),
                },
                valuation_data={
                    "valuation": valuation.get("v_target_usd", 0),
                    "market_potential": valuation.get("market_potential", "Unknown"),
                    "investment_attractiveness": valuation.get("investment_attractiveness", "Unknown"),
                },
                trl_level=trl_evaluation.get("trl", 3),
            )
            
            # Execute coordinator
            coordinator_result = await self.coordinator.coordinate_analysis(task, parallel=True)
            
            # Synthesize results
            synthesis_result = await self.synthesis_agent.synthesize(
                coordinator_result=coordinator_result,
                document_title=title,
                document_abstract=abstract,
            )
            
            # Quality assurance validation
            qa_result = await self.qa_agent.validate_analysis(
                synthesis_result=synthesis_result,
                document_content=document_content,
                document_abstract=abstract,
            )
            
            # Build comprehensive analysis result
            result = self._build_comprehensive_result(
                coordinator_result=coordinator_result,
                synthesis_result=synthesis_result,
                qa_result=qa_result,
                classification=classification,
                originality=originality,
                fto=fto,
                valuation=valuation,
                trl_evaluation=trl_evaluation,
                market_mapping=market_mapping,
            )
            
            # Add metadata
            result["ai_analysis_metadata"] = {
                "system_used": "multi-agent",
                "coordinator_stats": self.coordinator.get_coordinator_stats(coordinator_result),
                "qa_validation": {
                    "overall_quality_score": qa_result.overall_quality_score,
                    "consistency_score": qa_result.consistency_score,
                    "factual_accuracy_score": qa_result.factual_accuracy_score,
                    "completeness_score": qa_result.completeness_score,
                    "identified_issues": qa_result.identified_issues,
                    "validated_sections": qa_result.validated_sections,
                },
                "total_cost_usd": coordinator_result.total_cost_usd + synthesis_result.cost_usd + qa_result.cost_usd,
                "total_tokens_used": coordinator_result.total_tokens_used + synthesis_result.tokens_used + qa_result.tokens_used,
            }
            
            return result
            
        except Exception as e:
            print(f"Multi-agent analysis failed: {e}")
            if self.fallback_to_rules:
                print("Falling back to rule-based analysis")
                return self._fallback_analysis(
                    doc, classification, originality, fto, valuation, trl_evaluation, market_mapping, nlp_analysis
                )
            else:
                return {
                    "error": f"Multi-agent analysis failed: {str(e)}",
                    "fallback_disabled": True,
                }
    
    def _build_comprehensive_result(
        self,
        coordinator_result: CoordinatorResult,
        synthesis_result: SynthesisResult,
        qa_result: QAValidationResult,
        classification: dict[str, Any],
        originality: dict[str, Any],
        fto: dict[str, Any],
        valuation: dict[str, Any],
        trl_evaluation: dict[str, Any],
        market_mapping: dict[str, Any],
    ) -> dict[str, Any]:
        """Build comprehensive analysis result from agent outputs."""
        
        result = {}
        
        # Executive Summary
        result["executive_summary"] = synthesis_result.executive_summary
        
        # Technical Analysis
        if coordinator_result.technical_analysis:
            tech = coordinator_result.technical_analysis
            result["technical_analysis"] = f"""
### Classification and Methodology
The technology is classified in the {classification.get('sector_name', 'Unknown')} sector with a working field of {market_mapping.get('working_field', 'Unknown')}.

### Innovation and Novelty Assessment
{tech.innovation_assessment}

### Methodology Evaluation
{tech.methodology_evaluation}

### Technical Maturity
{tech.technical_maturity}

### Scientific Rigor
{tech.scientific_rigor}

### Scalability Assessment
{tech.scalability_assessment}

### Technical Strengths
{chr(10).join(f'- {strength}' for strength in tech.technical_strengths)}

### Technical Challenges
{chr(10).join(f'- {challenge}' for challenge in tech.technical_challenges)}

### Development Recommendations
{chr(10).join(f'- {rec}' for rec in tech.development_recommendations)}
"""
        
        # Market Analysis
        if coordinator_result.market_analysis:
            market = coordinator_result.market_analysis
            result["market_analysis"] = f"""
### Target Market Sector Overview
{market.target_market}

### Market Opportunity Assessment
Market Size: {market.market_size}
Growth Potential: {market.growth_potential}

### Competitive Landscape
{market.competitive_landscape}

### Market Entry Strategy
{market.market_entry_strategy}

### Recommended Timeline
{market.recommended_timeline}

### Strategic Market Recommendations
{chr(10).join(f'- {rec}' for rec in market.key_opportunities)}

### Market Challenges
{chr(10).join(f'- {challenge}' for challenge in market.key_challenges)}
"""
        
        # IP and Competitive Analysis
        if coordinator_result.ip_analysis:
            ip = coordinator_result.ip_analysis
            result["ip_competitive_analysis"] = f"""
### Patent Landscape Positioning
{ip.patent_positioning}

### Freedom to Operate Assessment
{ip.fto_assessment}

### IP Strategy Recommendations
{chr(10).join(f'- {rec}' for rec in ip.ip_strategy_recommendations)}

### Patent Filing Recommendations
{chr(10).join(f'- {rec}' for rec in ip.patent_filing_recommendations)}

### Infringement Risks
{chr(10).join(f'- {risk}' for risk in ip.infringement_risks)}

### Competitive IP Landscape
{ip.competitive_ip_landscape}
"""
        
        # Development Roadmap
        if coordinator_result.trl_assessment:
            trl = coordinator_result.trl_assessment
            result["development_roadmap"] = f"""
### Current Development Status
The technology is at Technology Readiness Level (TRL) {trl.trl_level} with {trl.confidence:.0%} confidence.

### TRL Assessment
{trl.reasoning}

### Key Indicators
{chr(10).join(f'- {indicator}' for indicator in trl.key_indicators)}

### Critical Next Steps
{chr(10).join(f'- {milestone}' for milestone in trl.next_milestones)}

### Development Timeline
Estimated time to next TRL level: {trl.estimated_time_to_next_level}

### Resource Requirements
- Technical validation and experimental work
- IP protection and patent filing
- Market engagement and partnership development
- Scale-up and manufacturing preparation
"""
        
        # Risk Assessment
        result["risk_assessment"] = f"""
### Intellectual Property Risk Analysis
{coordinator_result.ip_analysis.fto_assessment if coordinator_result.ip_analysis else "IP risks require strategic management"}

### Technical Development Risks
{chr(10).join(f'- {challenge}' for challenge in coordinator_result.technical_analysis.technical_challenges if coordinator_result.technical_analysis)}

### Market and Commercialization Risks
{chr(10).join(f'- {challenge}' for challenge in coordinator_result.market_analysis.key_challenges if coordinator_result.market_analysis)}

### Development and Execution Risks
- Technical development timeline risks
- Resource allocation and funding risks
- Partnership and collaboration risks
- Regulatory and compliance risks

### Risk Mitigation Strategies
- Phased development approach with clear milestones
- Comprehensive validation at each development stage
- Strategic partnerships to share risks
- Diversified funding strategy
- Regular market and competitive intelligence

### Strategic Risk Mitigation Framework
The overall risk profile presents a manageable risk-reward ratio with clear mitigation strategies. Key risks include technical development challenges, market adoption uncertainties, and IP landscape complexity. These are mitigated through phased development, comprehensive validation, strategic partnerships, and proactive IP management.
"""
        
        # Strategic Recommendations
        result["strategic_recommendations"] = f"""
### Immediate Actions
{chr(10).join(f'- {rec}' for rec in synthesis_result.strategic_recommendations[:3])}

### Medium-Term Strategy
Focus on advancing the technology through the development roadmap while building strategic partnerships and securing necessary resources for scale-up and commercialization.

### Long-Term Strategic Positioning
Establish strong market position through differentiated technology, comprehensive IP protection, and strategic customer relationships.

### Comprehensive Partnership and Collaboration Strategy
- Identify strategic partners in target markets
- Develop joint development agreements
- Secure licensing opportunities
- Build distribution and commercialization partnerships

### Comprehensive Funding and Investment Strategy
- Align funding with development milestones
- Pursue strategic investors with sector expertise
- Consider government grants and research funding
- Plan for Series A/B funding rounds as technology matures
"""
        
        # Investment Thesis
        result["investment_thesis"] = f"""
### Investment Opportunity Summary
{synthesis_result.investment_thesis}

### Key Investment Drivers
- Technology innovation and differentiation
- Market size and growth potential
- IP position and competitive advantages
- Development progress and TRL advancement
- Experienced team and strategic partnerships

### Investment Risk Profile
The investment presents moderate risk with significant upside potential. Key risks include technical development challenges, market adoption uncertainties, and competitive dynamics. These are mitigated through the technology's strong innovation, clear development path, and comprehensive IP strategy.

### Return Potential
Based on the market opportunity and technology potential, the investment offers significant return potential through multiple exit scenarios including acquisition, IPO, or strategic licensing.

### Investment Recommendation
{synthesis_result.investment_thesis}

### Valuation Considerations
Current valuation estimate: ${valuation.get('v_target_usd', 0):,.0f}
Market potential: {valuation.get('market_potential', 'Unknown')}
Investment attractiveness: {valuation.get('investment_attractiveness', 'Unknown')}
"""
        
        # Key Insights
        result["key_insights"] = synthesis_result.key_insights
        
        return result
    
    def _fallback_analysis(
        self,
        doc: Any,
        classification: dict[str, Any],
        originality: dict[str, Any],
        fto: dict[str, Any],
        valuation: dict[str, Any],
        trl_evaluation: dict[str, Any],
        market_mapping: dict[str, Any],
        nlp_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Fallback to rule-based comprehensive analysis."""
        
        result = generate_comprehensive_analysis(
            doc=doc,
            classification=classification,
            originality=originality,
            fto=fto,
            valuation=valuation,
            trl_evaluation=trl_evaluation,
            market_mapping=market_mapping,
            nlp_analysis=nlp_analysis,
        )
        
        result["ai_analysis_metadata"] = {
            "system_used": "rule-based-fallback",
            "reason": "Multi-agent system unavailable or failed",
        }
        
        return result
    
    def get_usage_stats(self) -> dict[str, Any]:
        """Get usage statistics from AI service."""
        if self.available and hasattr(self, 'ai_service'):
            return self.ai_service.get_usage_stats()
        return {
            "total_requests": 0,
            "failed_requests": 0,
            "success_rate": 0.0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "average_cost_per_request": 0.0,
        }
    
    def close(self):
        """Close AI service connections."""
        if self.available and hasattr(self, 'ai_service'):
            self.ai_service.close()


# Global instance
_multi_agent_system: Optional[MultiAgentAnalysis] = None


def get_multi_agent_system() -> MultiAgentAnalysis:
    """Get or create the global multi-agent system instance."""
    global _multi_agent_system
    if _multi_agent_system is None:
        _multi_agent_system = MultiAgentAnalysis()
    return _multi_agent_system


async def analyze_with_multi_agent(
    doc: Any,
    classification: dict[str, Any],
    originality: dict[str, Any],
    fto: dict[str, Any],
    valuation: dict[str, Any],
    trl_evaluation: dict[str, Any],
    market_mapping: dict[str, Any],
    nlp_analysis: dict[str, Any],
    title: str = "Unknown",
) -> dict[str, Any]:
    """Convenience function for multi-agent analysis."""
    system = get_multi_agent_system()
    return await system.analyze_document(
        doc, classification, originality, fto, valuation, trl_evaluation, market_mapping, nlp_analysis, title
    )
