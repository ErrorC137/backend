"""Market Analysis Agent for market opportunity assessment and competitive analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

from app.ai_services.base import AIService, Provider


@dataclass
class MarketAnalysisResult:
    """Result from market analysis."""
    target_market: str
    market_size: str
    growth_potential: str
    competitive_landscape: str
    market_entry_strategy: str
    key_opportunities: list[str]
    key_challenges: list[str]
    recommended_timeline: str
    confidence: float
    provider_used: str
    tokens_used: int
    cost_usd: float


class MarketAnalysisAgent:
    """Specialized agent for market analysis and competitive assessment."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.system_prompt = """You are an expert market analyst specializing in materials science, energy storage, carbon capture, AI materials, biomaterials, and advanced materials markets.

Your task is to analyze the market opportunity for a technology based on the provided document content. Consider:

Market Analysis Framework:
1. Target Market Identification
   - Primary market sectors and applications
   - Market size and growth projections
   - Geographic market distribution
   - Customer segments and use cases

2. Competitive Landscape
   - Key competitors and their market positions
   - Differentiation opportunities
   - Market saturation levels
   - Barriers to entry

3. Market Entry Strategy
   - Optimal entry approach (partnership, direct sales, licensing)
   - Timeline for market penetration
   - Resource requirements
   - Regulatory considerations

4. Opportunities and Challenges
   - Key market opportunities
   - Potential risks and challenges
   - Mitigation strategies
   - Success factors

Be realistic in your assessment - avoid over-optimistic projections. Base your analysis on the technical capabilities described in the document and realistic market dynamics.

Your response must be in JSON format with the following structure:
{
    "target_market": "primary market sector and applications",
    "market_size": "estimated market size and growth rate",
    "growth_potential": "assessment of growth potential with timeframe",
    "competitive_landscape": "overview of competitive environment",
    "market_entry_strategy": "recommended approach for market entry",
    "key_opportunities": ["list of key market opportunities"],
    "key_challenges": ["list of key challenges and risks"],
    "recommended_timeline": "estimated timeline for market entry",
    "confidence": float (0.0-1.0)
}"""
    
    async def analyze_market(
        self,
        document_content: str,
        abstract: str,
        sector: str,
        working_field: str,
        preferred_provider: Optional[Provider] = None,
    ) -> MarketAnalysisResult:
        """Analyze the market opportunity for a technology."""
        
        prompt = f"""Please analyze the market opportunity for the following technology.

Document Information:
- Abstract: {abstract[:2000]}
- Technology Sector: {sector}
- Working Field: {working_field}
- Full Content (first 3000 chars): {document_content[:3000]}

Provide your market analysis in the specified JSON format."""
        
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=2500,
            temperature=0.3,
            preferred_provider=preferred_provider or Provider.GOOGLE,  # Prefer Google for market analysis
        )
        
        if not response.success:
            return self._fallback_analysis(sector, working_field)
        
        try:
            result_data = json.loads(response.content)
            
            return MarketAnalysisResult(
                target_market=result_data.get("target_market", sector),
                market_size=result_data.get("market_size", "Unknown"),
                growth_potential=result_data.get("growth_potential", "Unknown"),
                competitive_landscape=result_data.get("competitive_landscape", "Unknown"),
                market_entry_strategy=result_data.get("market_entry_strategy", "Unknown"),
                key_opportunities=result_data.get("key_opportunities", []),
                key_challenges=result_data.get("key_challenges", []),
                recommended_timeline=result_data.get("recommended_timeline", "Unknown"),
                confidence=result_data.get("confidence", 0.7),
                provider_used=response.provider.value,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
            )
        except (json.JSONDecodeError, KeyError):
            return self._fallback_analysis(sector, working_field)
    
    def _fallback_analysis(self, sector: str, working_field: str) -> MarketAnalysisResult:
        """Fallback market analysis using sector-based defaults."""
        
        # Sector-specific market data
        sector_data = {
            "Energy Storage": {
                "market_size": "$50-100B by 2030",
                "growth_potential": "High growth (20-30% CAGR) driven by EV adoption and grid storage",
                "competitive_landscape": "Highly competitive with established players and new entrants",
                "market_entry_strategy": "Partnership with automotive or utility companies",
                "timeline": "2-4 years for significant market penetration",
            },
            "Carbon Capture": {
                "market_size": "$5-10B by 2030",
                "growth_potential": "Very high growth (30-40% CAGR) driven by climate regulations",
                "competitive_landscape": "Emerging market with few established players",
                "market_entry_strategy": "Pilot projects with industrial partners",
                "timeline": "3-5 years for commercial deployment",
            },
            "AI Materials": {
                "market_size": "$10-20B by 2030",
                "growth_potential": "Very high growth (25-35% CAGR) driven by AI adoption",
                "competitive_landscape": "Early stage with significant opportunity",
                "market_entry_strategy": "Direct sales to research institutions and tech companies",
                "timeline": "1-3 years for market entry",
            },
            "Biomaterials": {
                "market_size": "$15-30B by 2030",
                "growth_potential": "High growth (15-25% CAGR) driven by sustainability trends",
                "competitive_landscape": "Moderately competitive with growing interest",
                "market_entry_strategy": "Partnership with healthcare and consumer goods companies",
                "timeline": "2-4 years for market penetration",
            },
            "Advanced Materials": {
                "market_size": "$100-200B by 2030",
                "growth_potential": "Moderate growth (10-15% CAGR) with sector-specific variation",
                "competitive_landscape": "Highly competitive across sub-sectors",
                "market_entry_strategy": "Sector-specific partnerships and direct sales",
                "timeline": "2-5 years depending on application",
            },
        }
        
        data = sector_data.get(sector, sector_data.get("Advanced Materials", {}))
        
        return MarketAnalysisResult(
            target_market=f"{sector} - {working_field}",
            market_size=data.get("market_size", "Unknown"),
            growth_potential=data.get("growth_potential", "Unknown"),
            competitive_landscape=data.get("competitive_landscape", "Unknown"),
            market_entry_strategy=data.get("market_entry_strategy", "Unknown"),
            key_opportunities=[
                "Growing market demand",
                "Technological differentiation",
                "Sustainability benefits",
            ],
            key_challenges=[
                "Competition from established players",
                "Regulatory requirements",
                "Market education needed",
            ],
            recommended_timeline=data.get("timeline", "2-4 years"),
            confidence=0.5,
            provider_used="fallback",
            tokens_used=0,
            cost_usd=0.0,
        )
    
    async def analyze_market_enhanced(
        self,
        document_content: str,
        abstract: str,
        sector: str,
        working_field: str,
        trl_level: int,
        valuation_data: Optional[dict[str, Any]] = None,
        preferred_provider: Optional[Provider] = None,
    ) -> MarketAnalysisResult:
        """Enhanced market analysis with TRL and valuation context."""
        
        additional_context = f"""
Technology Readiness Level: TRL {trl_level}
"""
        
        if valuation_data:
            additional_context += f"""
Valuation Information:
- Estimated Valuation: {valuation_data.get('valuation', 'Unknown')}
- Market Potential: {valuation_data.get('market_potential', 'Unknown')}
- Investment Attractiveness: {valuation_data.get('investment_attractiveness', 'Unknown')}
"""
        
        prompt = f"""Please analyze the market opportunity for the following technology with enhanced context.

Document Information:
- Abstract: {abstract[:2000]}
- Technology Sector: {sector}
- Working Field: {working_field}
- Full Content (first 3000 chars): {document_content[:3000]}

{additional_context}

Provide your market analysis in the specified JSON format, considering the technology's maturity level and valuation potential."""
        
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=2500,
            temperature=0.3,
            preferred_provider=preferred_provider or Provider.GOOGLE,
        )
        
        if not response.success:
            return self._fallback_analysis(sector, working_field)
        
        try:
            result_data = json.loads(response.content)
            
            return MarketAnalysisResult(
                target_market=result_data.get("target_market", sector),
                market_size=result_data.get("market_size", "Unknown"),
                growth_potential=result_data.get("growth_potential", "Unknown"),
                competitive_landscape=result_data.get("competitive_landscape", "Unknown"),
                market_entry_strategy=result_data.get("market_entry_strategy", "Unknown"),
                key_opportunities=result_data.get("key_opportunities", []),
                key_challenges=result_data.get("key_challenges", []),
                recommended_timeline=result_data.get("recommended_timeline", "Unknown"),
                confidence=result_data.get("confidence", 0.7),
                provider_used=response.provider.value,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
            )
        except (json.JSONDecodeError, KeyError):
            return self._fallback_analysis(sector, working_field)
