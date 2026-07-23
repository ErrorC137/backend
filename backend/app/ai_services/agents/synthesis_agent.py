"""Synthesis Agent for combining agent outputs into comprehensive analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

from app.ai_services.agents.coordinator import CoordinatorResult
from app.ai_services.agents.ip_agent import IPAnalysisResult
from app.ai_services.agents.market_agent import MarketAnalysisResult
from app.ai_services.agents.technical_agent import TechnicalAnalysisResult
from app.ai_services.agents.trl_agent import TRLAssessmentResult
from app.ai_services.base import AIService, Provider


@dataclass
class SynthesisResult:
    """Result from synthesis agent."""
    executive_summary: str
    integrated_analysis: str
    key_insights: list[str]
    strategic_recommendations: list[str]
    risk_assessment: str
    investment_thesis: str
    confidence: float
    provider_used: str
    tokens_used: int
    cost_usd: float


class SynthesisAgent:
    """Agent for synthesizing outputs from multiple specialized agents."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.system_prompt = """You are an expert synthesis analyst specializing in combining technical, market, IP, and TRL assessments into comprehensive investment and strategic analysis for materials science technologies.

Your task is to synthesize the outputs from multiple specialized AI agents into a cohesive, comprehensive analysis that provides actionable insights for investors, researchers, and strategic decision-makers.

Synthesis Framework:
1. Executive Summary
   - High-level overview of the technology
   - Key investment highlights
   - Overall assessment and recommendation
   - Critical success factors

2. Integrated Analysis
   - Technical innovation assessment
   - Market opportunity evaluation
   - IP position and strategic value
   - Development roadmap and timeline
   - Risk-reward profile

3. Key Insights
   - Most significant findings across all domains
   - Competitive advantages and differentiation
   - Market positioning and opportunities
   - Technical and commercial risks

4. Strategic Recommendations
   - Prioritized action items
   - Development milestones
   - IP strategy recommendations
   - Market entry strategy
   - Funding and partnership recommendations

5. Risk Assessment
   - Technical risks and mitigation
   - Market and commercialization risks
   - IP and competitive risks
   - Execution and operational risks
   - Overall risk profile

6. Investment Thesis
   - Investment opportunity summary
   - Valuation considerations
   - Return potential and timeline
   - Investment recommendation
   - Key investment drivers

Ensure consistency across all sections and avoid contradictions. Provide specific, actionable recommendations backed by the agent analyses.

Your response must be in JSON format with the following structure:
{
    "executive_summary": "comprehensive executive summary",
    "integrated_analysis": "detailed integrated analysis combining all agent outputs",
    "key_insights": ["list of 5-7 key insights"],
    "strategic_recommendations": ["list of 5-7 prioritized strategic recommendations"],
    "risk_assessment": "comprehensive risk assessment",
    "investment_thesis": "detailed investment thesis with recommendation",
    "confidence": float (0.0-1.0)
}"""
    
    async def synthesize(
        self,
        coordinator_result: CoordinatorResult,
        document_title: str,
        document_abstract: str,
        preferred_provider: Optional[Provider] = None,
    ) -> SynthesisResult:
        """Synthesize agent outputs into comprehensive analysis."""
        
        # Build context from agent results
        context = self._build_synthesis_context(coordinator_result, document_title, document_abstract)
        
        prompt = f"""Please synthesize the following agent analyses into a comprehensive investment and strategic analysis.

{context}

Provide your synthesis in the specified JSON format."""
        
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=4000,
            temperature=0.3,
            preferred_provider=preferred_provider or Provider.ANTHROPIC,  # Prefer Claude for synthesis
        )
        
        if not response.success:
            return self._fallback_synthesis(coordinator_result, document_title)
        
        try:
            result_data = json.loads(response.content)
            
            return SynthesisResult(
                executive_summary=result_data.get("executive_summary", ""),
                integrated_analysis=result_data.get("integrated_analysis", ""),
                key_insights=result_data.get("key_insights", []),
                strategic_recommendations=result_data.get("strategic_recommendations", []),
                risk_assessment=result_data.get("risk_assessment", ""),
                investment_thesis=result_data.get("investment_thesis", ""),
                confidence=result_data.get("confidence", 0.7),
                provider_used=response.provider.value,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
            )
        except (json.JSONDecodeError, KeyError):
            return self._fallback_synthesis(coordinator_result, document_title)
    
    def _build_synthesis_context(
        self,
        coordinator_result: CoordinatorResult,
        document_title: str,
        document_abstract: str,
    ) -> str:
        """Build context string from agent results."""
        
        context = f"""
Document Information:
- Title: {document_title}
- Abstract: {document_abstract[:1000]}

Agent Analysis Results:
"""
        
        # TRL Assessment
        if coordinator_result.trl_assessment:
            trl = coordinator_result.trl_assessment
            context += f"""
TRL Assessment:
- TRL Level: {trl.trl_level}
- Confidence: {trl.confidence}
- Reasoning: {trl.reasoning[:500]}
- Key Indicators: {', '.join(trl.key_indicators[:3])}
- Next Milestones: {', '.join(trl.next_milestones[:3])}
- Time to Next Level: {trl.estimated_time_to_next_level}
"""
        
        # Market Analysis
        if coordinator_result.market_analysis:
            market = coordinator_result.market_analysis
            context += f"""
Market Analysis:
- Target Market: {market.target_market}
- Market Size: {market.market_size}
- Growth Potential: {market.growth_potential}
- Competitive Landscape: {market.competitive_landscape[:300]}
- Market Entry Strategy: {market.market_entry_strategy[:300]}
- Key Opportunities: {', '.join(market.key_opportunities[:3])}
- Key Challenges: {', '.join(market.key_challenges[:3])}
- Recommended Timeline: {market.recommended_timeline}
"""
        
        # IP Analysis
        if coordinator_result.ip_analysis:
            ip = coordinator_result.ip_analysis
            context += f"""
IP Analysis:
- Patent Positioning: {ip.patent_positioning[:300]}
- FTO Assessment: {ip.fto_assessment[:300]}
- IP Strategy Recommendations: {', '.join(ip.ip_strategy_recommendations[:3])}
- Infringement Risks: {', '.join(ip.infringement_risks[:3])}
- Patent Filing Recommendations: {', '.join(ip.patent_filing_recommendations[:3])}
- Competitive IP Landscape: {ip.competitive_ip_landscape[:300]}
"""
        
        # Technical Analysis
        if coordinator_result.technical_analysis:
            tech = coordinator_result.technical_analysis
            context += f"""
Technical Analysis:
- Technical Maturity: {tech.technical_maturity[:300]}
- Innovation Assessment: {tech.innovation_assessment[:300]}
- Methodology Evaluation: {tech.methodology_evaluation[:300]}
- Technical Challenges: {', '.join(tech.technical_challenges[:3])}
- Technical Strengths: {', '.join(tech.technical_strengths[:3])}
- Development Recommendations: {', '.join(tech.development_recommendations[:3])}
- Scientific Rigor: {tech.scientific_rigor[:300]}
- Scalability Assessment: {tech.scalability_assessment[:300]}
"""
        
        # Execution Statistics
        context += f"""
Execution Statistics:
- Total Execution Time: {coordinator_result.total_execution_time_ms:.0f}ms
- Total Tokens Used: {coordinator_result.total_tokens_used}
- Total Cost: ${coordinator_result.total_cost_usd:.4f}
- Successful Agents: {len([r for r in coordinator_result.agent_results if r.success])}/{len(coordinator_result.agent_results)}
"""
        
        return context
    
    def _fallback_synthesis(
        self,
        coordinator_result: CoordinatorResult,
        document_title: str,
    ) -> SynthesisResult:
        """Fallback synthesis using simple combination of agent results."""
        
        # Build executive summary from available data
        executive_parts = []
        
        if coordinator_result.trl_assessment:
            trl = coordinator_result.trl_assessment
            executive_parts.append(f"The technology is at TRL {trl.trl_level} with {trl.confidence:.0%} confidence.")
        
        if coordinator_result.market_analysis:
            market = coordinator_result.market_analysis
            executive_parts.append(f"Target market: {market.target_market} with {market.growth_potential} growth potential.")
        
        if coordinator_result.technical_analysis:
            tech = coordinator_result.technical_analysis
            executive_parts.append(f"Technical assessment: {tech.innovation_assessment}.")
        
        executive_summary = " ".join(executive_parts) if executive_parts else "Comprehensive analysis completed with partial agent results."
        
        # Build integrated analysis
        integrated_analysis = "This analysis combines insights from multiple specialized agents assessing technology readiness, market opportunity, IP position, and technical innovation. "
        
        if coordinator_result.trl_assessment:
            integrated_analysis += f"TRL assessment indicates {coordinator_result.trl_assessment.reasoning[:200]}. "
        
        if coordinator_result.market_analysis:
            integrated_analysis += f"Market analysis shows {coordinator_result.market_analysis.market_entry_strategy[:200]}. "
        
        if coordinator_result.ip_analysis:
            integrated_analysis += f"IP analysis suggests {coordinator_result.ip_analysis.patent_positioning[:200]}. "
        
        if coordinator_result.technical_analysis:
            integrated_analysis += f"Technical analysis reveals {coordinator_result.technical_analysis.technical_maturity[:200]}. "
        
        # Build key insights
        key_insights = []
        if coordinator_result.trl_assessment:
            key_insights.append(f"TRL {coordinator_result.trl_assessment.trl_level} with clear development path")
        if coordinator_result.market_analysis:
            key_insights.extend(coordinator_result.market_analysis.key_opportunities[:2])
        if coordinator_result.technical_analysis:
            key_insights.extend(coordinator_result.technical_analysis.technical_strengths[:2])
        
        if len(key_insights) > 7:
            key_insights = key_insights[:7]
        
        # Build strategic recommendations
        strategic_recommendations = []
        if coordinator_result.trl_assessment:
            strategic_recommendations.extend(coordinator_result.trl_assessment.next_milestones[:2])
        if coordinator_result.ip_analysis:
            strategic_recommendations.extend(coordinator_result.ip_analysis.patent_filing_recommendations[:2])
        if coordinator_result.technical_analysis:
            strategic_recommendations.extend(coordinator_result.technical_analysis.development_recommendations[:2])
        
        if len(strategic_recommendations) > 7:
            strategic_recommendations = strategic_recommendations[:7]
        
        # Build risk assessment
        risk_assessment = "Risk assessment identifies several key areas: "
        if coordinator_result.technical_analysis:
            risk_assessment += f"Technical challenges include {', '.join(coordinator_result.technical_analysis.technical_challenges[:2])}. "
        if coordinator_result.market_analysis:
            risk_assessment += f"Market challenges include {', '.join(coordinator_result.market_analysis.key_challenges[:2])}. "
        if coordinator_result.ip_analysis:
            risk_assessment += f"IP considerations include {coordinator_result.ip_analysis.fto_assessment[:200]}. "
        
        # Build investment thesis
        investment_thesis = f"Investment thesis for {document_title}: "
        if coordinator_result.market_analysis:
            investment_thesis += f"The technology targets {coordinator_result.market_analysis.target_market} with {coordinator_result.market_analysis.growth_potential} growth potential. "
        if coordinator_result.trl_assessment:
            investment_thesis += f"At TRL {coordinator_result.trl_assessment.trl_level}, the technology requires {coordinator_result.trl_assessment.estimated_time_to_next_level} to advance. "
        investment_thesis += "The investment offers moderate risk with significant upside potential given the innovation and market opportunity."
        
        return SynthesisResult(
            executive_summary=executive_summary,
            integrated_analysis=integrated_analysis,
            key_insights=key_insights,
            strategic_recommendations=strategic_recommendations,
            risk_assessment=risk_assessment,
            investment_thesis=investment_thesis,
            confidence=0.6,
            provider_used="fallback",
            tokens_used=0,
            cost_usd=0.0,
        )
