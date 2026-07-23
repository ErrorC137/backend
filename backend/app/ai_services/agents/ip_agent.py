"""IP Analysis Agent for patent landscape analysis and Freedom to Operate assessment."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

from app.ai_services.base import AIService, Provider


@dataclass
class IPAnalysisResult:
    """Result from IP analysis."""
    patent_positioning: str
    fto_assessment: str
    ip_strategy_recommendations: list[str]
    key_patents: list[dict[str, Any]]
    infringement_risks: list[str]
    patent_filing_recommendations: list[str]
    competitive_ip_landscape: str
    confidence: float
    provider_used: str
    tokens_used: int
    cost_usd: float


class IPAnalysisAgent:
    """Specialized agent for IP analysis and patent assessment."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.system_prompt = """You are an expert intellectual property analyst specializing in patent landscape analysis, Freedom to Operate (FTO) assessment, and IP strategy for materials science, energy storage, carbon capture, AI materials, biomaterials, and advanced materials technologies.

Your task is to analyze the IP position of a technology based on the provided document content and patent data. Consider:

IP Analysis Framework:
1. Patent Positioning
   - Novelty and inventiveness of the technology
   - Patentability assessment
   - Differentiation from existing patents
   - Strength of IP position

2. Freedom to Operate (FTO)
   - Potential infringement risks
   - Blocking patents and barriers
   - Design-around opportunities
   - Licensing requirements

3. IP Strategy
   - Patent filing recommendations
   - Geographic filing strategy
   - Defensive vs. offensive IP strategy
   - Trade secret considerations

4. Competitive IP Landscape
   - Key competitors and their patent positions
   - White space opportunities
   - Patent thickets and risks
   - Collaboration and licensing opportunities

Be thorough in your analysis - identify potential risks and provide actionable recommendations. Consider both immediate and long-term IP strategy.

Your response must be in JSON format with the following structure:
{
    "patent_positioning": "assessment of the technology's patent position and novelty",
    "fto_assessment": "freedom to operate assessment with risk level",
    "ip_strategy_recommendations": ["list of strategic IP recommendations"],
    "key_patents": [{"patent_id": "ID", "relevance": "description", "risk_level": "low/medium/high"}],
    "infringement_risks": ["list of potential infringement risks"],
    "patent_filing_recommendations": ["list of specific patent filing recommendations"],
    "competitive_ip_landscape": "overview of competitive IP landscape",
    "confidence": float (0.0-1.0)
}"""
    
    async def analyze_ip(
        self,
        document_content: str,
        abstract: str,
        methodology: str,
        patent_data: Optional[dict[str, Any]] = None,
        preferred_provider: Optional[Provider] = None,
    ) -> IPAnalysisResult:
        """Analyze the IP position of a technology."""
        
        patent_context = ""
        if patent_data:
            patent_context = f"""
Patent Data:
- Total Similar Patents: {patent_data.get('total_patents', 0)}
- High Similarity Patents: {patent_data.get('high_similarity', 0)}
- Medium Similarity Patents: {patent_data.get('medium_similarity', 0)}
- FTO Risk Level: {patent_data.get('fto_risk', 'Unknown')}
- Key Patent References: {patent_data.get('key_references', [])}
"""
        
        prompt = f"""Please analyze the intellectual property position of the following technology.

Document Information:
- Abstract: {abstract[:2000]}
- Methodology: {methodology[:2000]}
- Full Content (first 3000 chars): {document_content[:3000]}

{patent_context}

Provide your IP analysis in the specified JSON format."""
        
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=3000,
            temperature=0.3,
            preferred_provider=preferred_provider or Provider.OPENROUTER,  # Prefer OpenRouter for IP analysis
        )
        
        if not response.success:
            return self._fallback_analysis(patent_data)
        
        try:
            result_data = json.loads(response.content)
            
            return IPAnalysisResult(
                patent_positioning=result_data.get("patent_positioning", "Unknown"),
                fto_assessment=result_data.get("fto_assessment", "Unknown"),
                ip_strategy_recommendations=result_data.get("ip_strategy_recommendations", []),
                key_patents=result_data.get("key_patents", []),
                infringement_risks=result_data.get("infringement_risks", []),
                patent_filing_recommendations=result_data.get("patent_filing_recommendations", []),
                competitive_ip_landscape=result_data.get("competitive_ip_landscape", "Unknown"),
                confidence=result_data.get("confidence", 0.7),
                provider_used=response.provider.value,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
            )
        except (json.JSONDecodeError, KeyError):
            return self._fallback_analysis(patent_data)
    
    def _fallback_analysis(self, patent_data: Optional[dict[str, Any]] = None) -> IPAnalysisResult:
        """Fallback IP analysis using patent data."""
        
        fto_risk = patent_data.get("fto_risk", "Unknown") if patent_data else "Unknown"
        total_patents = patent_data.get("total_patents", 0) if patent_data else 0
        
        # Determine FTO assessment based on patent data
        if fto_risk == "High" or total_patents > 10:
            fto_assessment = "High risk - multiple similar patents identified"
            infringement_risks = [
                "Potential infringement with similar patents",
                "Design-around may be required",
                "Licensing negotiations recommended",
            ]
        elif fto_risk == "Medium" or total_patents > 5:
            fto_assessment = "Medium risk - some similar patents exist"
            infringement_risks = [
                "Moderate infringement risk",
                "Careful claim drafting required",
                "Consider licensing options",
            ]
        else:
            fto_assessment = "Low risk - good patent positioning"
            infringement_risks = [
                "Minimal infringement risk identified",
                "Strong novelty potential",
            ]
        
        return IPAnalysisResult(
            patent_positioning="Technology shows good novelty with patentable features",
            fto_assessment=fto_assessment,
            ip_strategy_recommendations=[
                "File comprehensive patent applications",
                "Conduct regular FTO analysis",
                "Consider international filings",
                "Develop defensive IP portfolio",
            ],
            key_patents=[],
            infringement_risks=infringement_risks,
            patent_filing_recommendations=[
                "File provisional patent application",
                "Consider PCT filing for international protection",
                "File continuation applications for variants",
                "Monitor competitor patent filings",
            ],
            competitive_ip_landscape="Moderately competitive with opportunities for differentiation",
            confidence=0.5,
            provider_used="fallback",
            tokens_used=0,
            cost_usd=0.0,
        )
    
    async def analyze_ip_enhanced(
        self,
        document_content: str,
        abstract: str,
        methodology: str,
        patent_data: Optional[dict[str, Any]] = None,
        trl_level: int = 3,
        preferred_provider: Optional[Provider] = None,
    ) -> IPAnalysisResult:
        """Enhanced IP analysis with TRL context."""
        
        patent_context = ""
        if patent_data:
            patent_context = f"""
Patent Data:
- Total Similar Patents: {patent_data.get('total_patents', 0)}
- High Similarity Patents: {patent_data.get('high_similarity', 0)}
- Medium Similarity Patents: {patent_data.get('medium_similarity', 0)}
- FTO Risk Level: {patent_data.get('fto_risk', 'Unknown')}
- Key Patent References: {patent_data.get('key_references', [])}
"""
        
        trl_context = f"""
Technology Readiness Level: TRL {trl_level}
"""
        
        # Adjust strategy based on TRL
        if trl_level < 4:
            trl_context += "IP Strategy Focus: Early-stage patent protection and broad claims"
        elif trl_level < 7:
            trl_context += "IP Strategy Focus: Strengthen patent position and prepare for commercialization"
        else:
            trl_context += "IP Strategy Focus: Defensive patenting and freedom to operate management"
        
        prompt = f"""Please analyze the intellectual property position of the following technology with enhanced context.

Document Information:
- Abstract: {abstract[:2000]}
- Methodology: {methodology[:2000]}
- Full Content (first 3000 chars): {document_content[:3000]}

{patent_context}
{trl_context}

Provide your IP analysis in the specified JSON format, considering the technology's maturity level and adjusting recommendations accordingly."""
        
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=3000,
            temperature=0.3,
            preferred_provider=preferred_provider or Provider.OPENROUTER,
        )
        
        if not response.success:
            return self._fallback_analysis(patent_data)
        
        try:
            result_data = json.loads(response.content)
            
            return IPAnalysisResult(
                patent_positioning=result_data.get("patent_positioning", "Unknown"),
                fto_assessment=result_data.get("fto_assessment", "Unknown"),
                ip_strategy_recommendations=result_data.get("ip_strategy_recommendations", []),
                key_patents=result_data.get("key_patents", []),
                infringement_risks=result_data.get("infringement_risks", []),
                patent_filing_recommendations=result_data.get("patent_filing_recommendations", []),
                competitive_ip_landscape=result_data.get("competitive_ip_landscape", "Unknown"),
                confidence=result_data.get("confidence", 0.7),
                provider_used=response.provider.value,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
            )
        except (json.JSONDecodeError, KeyError):
            return self._fallback_analysis(patent_data)
