"""TRL Assessment Agent for Technology Readiness Level evaluation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

from app.ai_services.base import AIService, Provider


@dataclass
class TRLAssessmentResult:
    """Result from TRL assessment."""
    trl_level: int
    confidence: float
    reasoning: str
    key_indicators: list[str]
    next_milestones: list[str]
    estimated_time_to_next_level: str
    provider_used: str
    tokens_used: int
    cost_usd: float


class TRLAssessmentAgent:
    """Specialized agent for Technology Readiness Level assessment."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.system_prompt = """You are an expert Technology Readiness Level (TRL) assessor specializing in materials science, energy storage, carbon capture, AI materials, biomaterials, and advanced materials technologies.

Your task is to evaluate the TRL of a technology based on the provided document content. Use the standard TRL scale (TRL 1-9):

TRL 1: Basic principles observed and reported
TRL 2: Technology concept and/or application formulated
TRL 3: Experimental proof of concept
TRL 4: Technology validated in lab
TRL 5: Technology validated in relevant environment
TRL 6: Technology demonstrated in relevant environment
TRL 7: Technology demonstrated in operational environment
TRL 8: System complete and qualified
TRL 9: Actual system proven in operational environment

Assessment criteria:
- Experimental validation and prototype development
- Scale-up capabilities and pilot demonstrations
- Manufacturing readiness and production capabilities
- Market testing and customer validation
- Regulatory compliance and certification
- Commercial deployment and operational use

Provide detailed reasoning for your TRL assessment, citing specific evidence from the document. Be conservative in your assessment - only assign higher TRL levels when there is clear evidence of the required milestones.

Your response must be in JSON format with the following structure:
{
    "trl_level": int (1-9),
    "confidence": float (0.0-1.0),
    "reasoning": "detailed explanation of the assessment",
    "key_indicators": ["list of key indicators supporting the TRL level"],
    "next_milestones": ["list of specific milestones needed to reach the next TRL level"],
    "estimated_time_to_next_level": "estimated time (e.g., '6-12 months')"
}"""
    
    async def assess_trl(
        self,
        document_content: str,
        abstract: str,
        methodology: str,
        claims_outcomes: str,
        preferred_provider: Optional[Provider] = None,
    ) -> TRLAssessmentResult:
        """Assess the TRL level of a technology."""
        
        prompt = f"""Please assess the Technology Readiness Level (TRL) of the following technology based on the document content.

Document Information:
- Abstract: {abstract[:2000]}
- Methodology: {methodology[:2000]}
- Claims/Outcomes: {claims_outcomes[:2000]}
- Full Content (first 3000 chars): {document_content[:3000]}

Provide your assessment in the specified JSON format."""
        
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=2000,
            temperature=0.2,  # Lower temperature for more consistent TRL assessment
            preferred_provider=preferred_provider or Provider.ANTHROPIC,  # Prefer Claude for structured reasoning
        )
        
        if not response.success:
            # Fallback to basic assessment if AI fails
            return self._fallback_assessment(document_content)
        
        try:
            # Parse JSON response
            result_data = json.loads(response.content)
            
            return TRLAssessmentResult(
                trl_level=result_data.get("trl_level", 3),
                confidence=result_data.get("confidence", 0.7),
                reasoning=result_data.get("reasoning", ""),
                key_indicators=result_data.get("key_indicators", []),
                next_milestones=result_data.get("next_milestones", []),
                estimated_time_to_next_level=result_data.get("estimated_time_to_next_level", "Unknown"),
                provider_used=response.provider.value,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
            )
        except (json.JSONDecodeError, KeyError) as e:
            # If JSON parsing fails, use fallback
            return self._fallback_assessment(document_content)
    
    def _fallback_assessment(self, document_content: str) -> TRLAssessmentResult:
        """Fallback TRL assessment using simple keyword matching."""
        content_lower = document_content.lower()
        
        trl_level = 3  # Default to TRL 3 (proof of concept)
        confidence = 0.5
        reasoning = "Fallback assessment using keyword matching due to AI service unavailability."
        key_indicators = []
        next_milestones = []
        
        # Check for experimental validation
        if any(
            term in content_lower
            for term in [
                "experiment",
                "prototype",
                "lab-scale",
                "proof of concept",
                "validated",
            ]
        ):
            trl_level = max(trl_level, 4)
            key_indicators.append("Experimental validation observed")
            next_milestones = [
                "Advance to pilot-scale demonstrations",
                "Validate in relevant environment",
            ]
        
        # Check for pilot demonstrations
        if any(
            term in content_lower
            for term in [
                "pilot",
                "demonstration",
                "scale-up",
                "relevant environment",
            ]
        ):
            trl_level = max(trl_level, 5)
            key_indicators.append("Pilot-scale demonstrations")
            next_milestones = [
                "Demonstrate in operational environment",
                "Complete system integration",
            ]
        
        # Check for operational demonstrations
        if any(
            term in content_lower
            for term in [
                "operational",
                "field test",
                "commercial",
                "deployment",
            ]
        ):
            trl_level = max(trl_level, 7)
            key_indicators.append("Operational demonstrations")
            next_milestones = [
                "Complete system qualification",
                "Scale to full commercial deployment",
            ]
        
        # Check for commercial deployment
        if any(
            term in content_lower
            for term in [
                "commercial deployment",
                "market launch",
                "production",
                "manufacturing",
            ]
        ):
            trl_level = max(trl_level, 9)
            key_indicators.append("Commercial deployment")
            next_milestones = []
        
        # Estimate time to next level
        time_estimates = {
            1: "12-24 months to TRL 2",
            2: "12-18 months to TRL 3",
            3: "6-12 months to TRL 4",
            4: "12-18 months to TRL 5",
            5: "12-18 months to TRL 6",
            6: "12-18 months to TRL 7",
            7: "18-24 months to TRL 8",
            8: "12-18 months to TRL 9",
            9: "N/A - Already at highest TRL",
        }
        
        estimated_time = time_estimates.get(trl_level, "Unknown")
        
        return TRLAssessmentResult(
            trl_level=trl_level,
            confidence=confidence,
            reasoning=reasoning,
            key_indicators=key_indicators,
            next_milestones=next_milestones,
            estimated_time_to_next_level=estimated_time,
            provider_used="fallback",
            tokens_used=0,
            cost_usd=0.0,
        )
    
    async def assess_trl_enhanced(
        self,
        document_content: str,
        abstract: str,
        methodology: str,
        claims_outcomes: str,
        patent_data: Optional[dict[str, Any]] = None,
        market_data: Optional[dict[str, Any]] = None,
        preferred_provider: Optional[Provider] = None,
    ) -> TRLAssessmentResult:
        """Enhanced TRL assessment with additional context from patents and market data."""
        
        additional_context = ""
        
        if patent_data:
            additional_context += f"""
Patent Information:
- Patent Count: {patent_data.get('total_patents', 0)}
- Similar Patents: {patent_data.get('similar_patents', 0)}
- FTO Risk: {patent_data.get('fto_risk', 'Unknown')}
"""
        
        if market_data:
            additional_context += f"""
Market Information:
- Market Stage: {market_data.get('market_stage', 'Unknown')}
- Commercial Readiness: {market_data.get('commercial_readiness', 'Unknown')}
- Customer Validation: {market_data.get('customer_validation', 'Unknown')}
"""
        
        prompt = f"""Please assess the Technology Readiness Level (TRL) of the following technology with enhanced context.

Document Information:
- Abstract: {abstract[:2000]}
- Methodology: {methodology[:2000]}
- Claims/Outcomes: {claims_outcomes[:2000]}
- Full Content (first 3000 chars): {document_content[:3000]}

{additional_context}

Provide your assessment in the specified JSON format, considering both technical development and commercialization indicators."""
        
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=2500,
            temperature=0.2,
            preferred_provider=preferred_provider or Provider.ANTHROPIC,
        )
        
        if not response.success:
            return self._fallback_assessment(document_content)
        
        try:
            result_data = json.loads(response.content)
            
            return TRLAssessmentResult(
                trl_level=result_data.get("trl_level", 3),
                confidence=result_data.get("confidence", 0.7),
                reasoning=result_data.get("reasoning", ""),
                key_indicators=result_data.get("key_indicators", []),
                next_milestones=result_data.get("next_milestones", []),
                estimated_time_to_next_level=result_data.get("estimated_time_to_next_level", "Unknown"),
                provider_used=response.provider.value,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
            )
        except (json.JSONDecodeError, KeyError):
            return self._fallback_assessment(document_content)
