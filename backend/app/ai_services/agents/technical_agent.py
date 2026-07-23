"""Technical Analysis Agent for technical methodology evaluation and innovation assessment."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

from app.ai_services.base import AIService, Provider


@dataclass
class TechnicalAnalysisResult:
    """Result from technical analysis."""
    technical_maturity: str
    innovation_assessment: str
    methodology_evaluation: str
    technical_challenges: list[str]
    technical_strengths: list[str]
    development_recommendations: list[str]
    scientific_rigor: str
    scalability_assessment: str
    confidence: float
    provider_used: str
    tokens_used: int
    cost_usd: float


class TechnicalAnalysisAgent:
    """Specialized agent for technical analysis and innovation assessment."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.system_prompt = """You are an expert technical analyst specializing in materials science, energy storage, carbon capture, AI materials, biomaterials, and advanced materials technologies.

Your task is to evaluate the technical aspects of a technology based on the provided document content. Consider:

Technical Analysis Framework:
1. Technical Maturity
   - Development stage and readiness
   - Experimental validation status
   - Prototype development progress
   - Scale-up capabilities

2. Innovation Assessment
   - Novelty and uniqueness of the approach
   - Technical differentiation from existing solutions
   - Patentability and inventiveness
   - Scientific advancement level

3. Methodology Evaluation
   - Scientific rigor and validity
   - Experimental design quality
   - Data reliability and reproducibility
   - Theoretical foundation strength

4. Technical Challenges
   - Key technical hurdles
   - Risk factors and limitations
   - Technical feasibility concerns
   - Resource requirements

5. Technical Strengths
   - Key technical advantages
   - Performance characteristics
   - Efficiency improvements
   - Cost reduction potential

6. Development Recommendations
   - Technical development priorities
   - R&D focus areas
   - Validation requirements
   - Scale-up considerations

Be objective and thorough in your analysis - identify both strengths and challenges. Provide specific, actionable recommendations.

Your response must be in JSON format with the following structure:
{
    "technical_maturity": "assessment of technical development stage",
    "innovation_assessment": "evaluation of innovation and novelty",
    "methodology_evaluation": "assessment of scientific rigor and methodology",
    "technical_challenges": ["list of key technical challenges"],
    "technical_strengths": ["list of key technical strengths"],
    "development_recommendations": ["list of specific technical development recommendations"],
    "scientific_rigor": "assessment of scientific rigor and validity",
    "scalability_assessment": "evaluation of scalability potential",
    "confidence": float (0.0-1.0)
}"""
    
    async def analyze_technical(
        self,
        document_content: str,
        abstract: str,
        methodology: str,
        claims_outcomes: str,
        preferred_provider: Optional[Provider] = None,
    ) -> TechnicalAnalysisResult:
        """Analyze the technical aspects of a technology."""
        
        prompt = f"""Please analyze the technical aspects of the following technology.

Document Information:
- Abstract: {abstract[:2000]}
- Methodology: {methodology[:3000]}
- Claims/Outcomes: {claims_outcomes[:2000]}
- Full Content (first 3000 chars): {document_content[:3000]}

Provide your technical analysis in the specified JSON format."""
        
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=3000,
            temperature=0.3,
            preferred_provider=preferred_provider or Provider.ANTHROPIC,  # Prefer Claude for technical analysis
        )
        
        if not response.success:
            return self._fallback_analysis(methodology, claims_outcomes)
        
        try:
            result_data = json.loads(response.content)
            
            return TechnicalAnalysisResult(
                technical_maturity=result_data.get("technical_maturity", "Unknown"),
                innovation_assessment=result_data.get("innovation_assessment", "Unknown"),
                methodology_evaluation=result_data.get("methodology_evaluation", "Unknown"),
                technical_challenges=result_data.get("technical_challenges", []),
                technical_strengths=result_data.get("technical_strengths", []),
                development_recommendations=result_data.get("development_recommendations", []),
                scientific_rigor=result_data.get("scientific_rigor", "Unknown"),
                scalability_assessment=result_data.get("scalability_assessment", "Unknown"),
                confidence=result_data.get("confidence", 0.7),
                provider_used=response.provider.value,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
            )
        except (json.JSONDecodeError, KeyError):
            return self._fallback_analysis(methodology, claims_outcomes)
    
    def _fallback_analysis(self, methodology: str, claims_outcomes: str) -> TechnicalAnalysisResult:
        """Fallback technical analysis using keyword analysis."""
        
        content_lower = (methodology + " " + claims_outcomes).lower()
        
        # Assess technical maturity
        technical_maturity = "Early development stage"
        if any(
            term in content_lower
            for term in ["prototype", "validated", "demonstrated", "proof of concept"]
        ):
            technical_maturity = "Prototype development stage"
        if any(term in content_lower for term in ["pilot", "scale-up", "demonstration"]):
            technical_maturity = "Pilot-scale development"
        if any(term in content_lower for term in ["commercial", "production", "manufacturing"]):
            technical_maturity = "Commercialization stage"
        
        # Assess innovation
        innovation_terms = ["novel", "innovative", "unique", "breakthrough", "first", "new"]
        innovation_count = sum(1 for term in innovation_terms if term in content_lower)
        
        if innovation_count >= 3:
            innovation_assessment = "High innovation with significant novelty"
        elif innovation_count >= 2:
            innovation_assessment = "Moderate innovation with some novelty"
        else:
            innovation_assessment = "Incremental innovation with limited novelty"
        
        # Identify challenges
        challenges = []
        if "challenge" in content_lower or "difficulty" in content_lower:
            challenges.append("Technical challenges identified in methodology")
        if "limitation" in content_lower or "constraint" in content_lower:
            challenges.append("Limitations and constraints present")
        if "cost" in content_lower or "expensive" in content_lower:
            challenges.append("Cost considerations may impact scalability")
        
        if not challenges:
            challenges = ["Technical challenges not explicitly documented"]
        
        # Identify strengths
        strengths = []
        if "efficient" in content_lower or "effective" in content_lower:
            strengths.append("Demonstrated efficiency and effectiveness")
        if "scalable" in content_lower or "scale" in content_lower:
            strengths.append("Scalability potential indicated")
        if "performance" in content_lower or "improvement" in content_lower:
            strengths.append("Performance improvements demonstrated")
        
        if not strengths:
            strengths = ["Technical approach shows promise"]
        
        return TechnicalAnalysisResult(
            technical_maturity=technical_maturity,
            innovation_assessment=innovation_assessment,
            methodology_evaluation="Methodology appears sound based on available information",
            technical_challenges=challenges,
            technical_strengths=strengths,
            development_recommendations=[
                "Continue experimental validation",
                "Focus on scalability testing",
                "Strengthen patent position",
            ],
            scientific_rigor="Moderate scientific rigor indicated",
            scalability_assessment="Scalability potential requires further validation",
            confidence=0.5,
            provider_used="fallback",
            tokens_used=0,
            cost_usd=0.0,
        )
    
    async def analyze_technical_enhanced(
        self,
        document_content: str,
        abstract: str,
        methodology: str,
        claims_outcomes: str,
        trl_level: int,
        patent_data: Optional[dict[str, Any]] = None,
        preferred_provider: Optional[Provider] = None,
    ) -> TechnicalAnalysisResult:
        """Enhanced technical analysis with TRL and patent context."""
        
        additional_context = f"""
Technology Readiness Level: TRL {trl_level}
"""
        
        if patent_data:
            additional_context += f"""
Patent Information:
- Patent Count: {patent_data.get('total_patents', 0)}
- Similar Patents: {patent_data.get('similar_patents', 0)}
- Novelty Score: {patent_data.get('novelty_score', 'Unknown')}
"""
        
        prompt = f"""Please analyze the technical aspects of the following technology with enhanced context.

Document Information:
- Abstract: {abstract[:2000]}
- Methodology: {methodology[:3000]}
- Claims/Outcomes: {claims_outcomes[:2000]}
- Full Content (first 3000 chars): {document_content[:3000]}

{additional_context}

Provide your technical analysis in the specified JSON format, considering the technology's maturity level and patent position."""
        
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=3000,
            temperature=0.3,
            preferred_provider=preferred_provider or Provider.ANTHROPIC,
        )
        
        if not response.success:
            return self._fallback_analysis(methodology, claims_outcomes)
        
        try:
            result_data = json.loads(response.content)
            
            return TechnicalAnalysisResult(
                technical_maturity=result_data.get("technical_maturity", "Unknown"),
                innovation_assessment=result_data.get("innovation_assessment", "Unknown"),
                methodology_evaluation=result_data.get("methodology_evaluation", "Unknown"),
                technical_challenges=result_data.get("technical_challenges", []),
                technical_strengths=result_data.get("technical_strengths", []),
                development_recommendations=result_data.get("development_recommendations", []),
                scientific_rigor=result_data.get("scientific_rigor", "Unknown"),
                scalability_assessment=result_data.get("scalability_assessment", "Unknown"),
                confidence=result_data.get("confidence", 0.7),
                provider_used=response.provider.value,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
            )
        except (json.JSONDecodeError, KeyError):
            return self._fallback_analysis(methodology, claims_outcomes)
