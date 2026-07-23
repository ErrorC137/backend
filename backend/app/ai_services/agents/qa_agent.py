"""Quality Assurance Agent for fact-checking and consistency validation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Optional

from app.ai_services.agents.synthesis_agent import SynthesisResult
from app.ai_services.base import AIService, Provider


@dataclass
class QAValidationResult:
    """Result from quality assurance validation."""
    overall_quality_score: float
    consistency_score: float
    factual_accuracy_score: float
    completeness_score: float
    identified_issues: list[dict[str, Any]]
    recommendations: list[str]
    validated_sections: list[str]
    confidence: float
    provider_used: str
    tokens_used: int
    cost_usd: float


class QualityAssuranceAgent:
    """Agent for quality assurance and fact-checking of synthesized analysis."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.system_prompt = """You are an expert quality assurance analyst specializing in validating technical, market, and investment analyses for materials science technologies.

Your task is to review the synthesized analysis for quality, consistency, factual accuracy, and completeness. Identify any issues, contradictions, or areas that require clarification.

QA Framework:
1. Consistency Validation
   - Check for contradictions between sections
   - Verify TRL, market, and technical assessments align
   - Ensure timeline and milestone consistency
   - Validate risk and opportunity alignment

2. Factual Accuracy Check
   - Identify unsupported claims or assertions
   - Flag overly optimistic or pessimistic projections
   - Verify technical claims are plausible
   - Check market data and valuation reasonableness

3. Completeness Assessment
   - Ensure all required sections are present
   - Verify key questions are addressed
   - Check for missing critical information
   - Assess depth and detail of analysis

4. Quality Scoring
   - Overall quality assessment (0.0-1.0)
   - Consistency score (0.0-1.0)
   - Factual accuracy score (0.0-1.0)
   - Completeness score (0.0-1.0)

5. Issue Identification
   - List specific issues found
   - Categorize by severity (critical, major, minor)
   - Provide recommendations for resolution

6. Recommendations
   - Specific improvements needed
   - Additional analysis required
   - Clarifications needed
   - Formatting or structure improvements

Be thorough but constructive - identify real issues while recognizing the complexity of the analysis. Provide actionable recommendations.

Your response must be in JSON format with the following structure:
{
    "overall_quality_score": float (0.0-1.0),
    "consistency_score": float (0.0-1.0),
    "factual_accuracy_score": float (0.0-1.0),
    "completeness_score": float (0.0-1.0),
    "identified_issues": [
        {
            "section": "section name",
            "issue": "description of the issue",
            "severity": "critical/major/minor",
            "recommendation": "how to fix"
        }
    ],
    "recommendations": ["list of improvement recommendations"],
    "validated_sections": ["list of sections that passed validation"],
    "confidence": float (0.0-1.0)
}"""
    
    async def validate_analysis(
        self,
        synthesis_result: SynthesisResult,
        document_content: str,
        document_abstract: str,
        preferred_provider: Optional[Provider] = None,
    ) -> QAValidationResult:
        """Validate the synthesized analysis for quality and accuracy."""
        
        context = self._build_qa_context(synthesis_result, document_content, document_abstract)
        
        prompt = f"""Please validate the following synthesized analysis for quality, consistency, factual accuracy, and completeness.

{context}

Provide your validation in the specified JSON format."""
        
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=3000,
            temperature=0.2,  # Lower temperature for consistent validation
            preferred_provider=preferred_provider or Provider.GOOGLE,  # Prefer Google for validation
        )
        
        if not response.success:
            return self._fallback_validation(synthesis_result)
        
        try:
            result_data = json.loads(response.content)
            
            return QAValidationResult(
                overall_quality_score=result_data.get("overall_quality_score", 0.7),
                consistency_score=result_data.get("consistency_score", 0.7),
                factual_accuracy_score=result_data.get("factual_accuracy_score", 0.7),
                completeness_score=result_data.get("completeness_score", 0.7),
                identified_issues=result_data.get("identified_issues", []),
                recommendations=result_data.get("recommendations", []),
                validated_sections=result_data.get("validated_sections", []),
                confidence=result_data.get("confidence", 0.7),
                provider_used=response.provider.value,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
            )
        except (json.JSONDecodeError, KeyError):
            return self._fallback_validation(synthesis_result)
    
    def _build_qa_context(
        self,
        synthesis_result: SynthesisResult,
        document_content: str,
        document_abstract: str,
    ) -> str:
        """Build context string for QA validation."""
        
        context = f"""
Document Information:
- Abstract: {document_abstract[:1000]}
- Content Sample: {document_content[:1500]}

Synthesized Analysis:
- Executive Summary: {synthesis_result.executive_summary[:800]}
- Integrated Analysis: {synthesis_result.integrated_analysis[:800]}
- Key Insights: {', '.join(synthesis_result.key_insights[:5])}
- Strategic Recommendations: {', '.join(synthesis_result.strategic_recommendations[:5])}
- Risk Assessment: {synthesis_result.risk_assessment[:800]}
- Investment Thesis: {synthesis_result.investment_thesis[:800]}

Please validate this analysis for:
1. Consistency between sections
2. Factual accuracy and plausibility
3. Completeness of coverage
4. Quality of insights and recommendations
"""
        
        return context
    
    def _fallback_validation(self, synthesis_result: SynthesisResult) -> QAValidationResult:
        """Fallback validation using basic checks."""
        
        issues = []
        validated_sections = []
        
        # Check executive summary
        if synthesis_result.executive_summary and len(synthesis_result.executive_summary) > 100:
            validated_sections.append("Executive Summary")
        else:
            issues.append({
                "section": "Executive Summary",
                "issue": "Executive summary is too short or missing",
                "severity": "major",
                "recommendation": "Expand executive summary with key findings",
            })
        
        # Check integrated analysis
        if synthesis_result.integrated_analysis and len(synthesis_result.integrated_analysis) > 200:
            validated_sections.append("Integrated Analysis")
        else:
            issues.append({
                "section": "Integrated Analysis",
                "issue": "Integrated analysis lacks depth",
                "severity": "major",
                "recommendation": "Provide more detailed integrated analysis",
            })
        
        # Check key insights
        if len(synthesis_result.key_insights) >= 3:
            validated_sections.append("Key Insights")
        else:
            issues.append({
                "section": "Key Insights",
                "issue": "Insufficient key insights provided",
                "severity": "minor",
                "recommendation": "Add more key insights from the analysis",
            })
        
        # Check strategic recommendations
        if len(synthesis_result.strategic_recommendations) >= 3:
            validated_sections.append("Strategic Recommendations")
        else:
            issues.append({
                "section": "Strategic Recommendations",
                "issue": "Insufficient strategic recommendations",
                "severity": "major",
                "recommendation": "Provide more specific strategic recommendations",
            })
        
        # Check risk assessment
        if synthesis_result.risk_assessment and len(synthesis_result.risk_assessment) > 100:
            validated_sections.append("Risk Assessment")
        else:
            issues.append({
                "section": "Risk Assessment",
                "issue": "Risk assessment is incomplete",
                "severity": "major",
                "recommendation": "Expand risk assessment with specific risks",
            })
        
        # Check investment thesis
        if synthesis_result.investment_thesis and len(synthesis_result.investment_thesis) > 150:
            validated_sections.append("Investment Thesis")
        else:
            issues.append({
                "section": "Investment Thesis",
                "issue": "Investment thesis lacks detail",
                "severity": "major",
                "recommendation": "Provide more detailed investment thesis",
            })
        
        # Calculate scores
        consistency_score = 0.7  # Default moderate score
        factual_accuracy_score = 0.7  # Default moderate score
        completeness_score = len(validated_sections) / 6.0  # 6 sections total
        overall_quality_score = (consistency_score + factual_accuracy_score + completeness_score) / 3.0
        
        # Generate recommendations
        recommendations = [
            "Ensure all sections are present and complete",
            "Provide specific, actionable recommendations",
            "Include quantitative data where possible",
            "Cross-validate claims across sections",
        ]
        
        if issues:
            recommendations.extend([issue["recommendation"] for issue in issues[:5]])
        
        return QAValidationResult(
            overall_quality_score=overall_quality_score,
            consistency_score=consistency_score,
            factual_accuracy_score=factual_accuracy_score,
            completeness_score=completeness_score,
            identified_issues=issues,
            recommendations=recommendations,
            validated_sections=validated_sections,
            confidence=0.6,
            provider_used="fallback",
            tokens_used=0,
            cost_usd=0.0,
        )
    
    def check_for_hallucinations(
        self,
        synthesis_result: SynthesisResult,
        document_content: str,
    ) -> list[dict[str, Any]]:
        """Check for potential hallucinations in the analysis."""
        
        potential_hallucinations = []
        
        # Extract numbers and statistics from synthesis
        number_pattern = r'\$[\d,]+|\d+[%]|TRL\s*\d+|\d+\s*(years|months|days|percent|%|million|billion|trillion)'
        
        all_text = (
            synthesis_result.executive_summary
            + " "
            + synthesis_result.integrated_analysis
            + " "
            + synthesis_result.risk_assessment
            + " "
            + synthesis_result.investment_thesis
        )
        
        extracted_numbers = re.findall(number_pattern, all_text, re.IGNORECASE)
        
        # Check if numbers appear in document
        for number in extracted_numbers:
            if number.lower() not in document_content.lower():
                potential_hallucinations.append({
                    "type": "number",
                    "value": number,
                    "context": "Number not found in original document",
                    "severity": "minor",
                })
        
        # Check for overly specific claims without evidence
        specific_claims = [
            "first",
            "only",
            "unique",
            "breakthrough",
            "revolutionary",
            "unprecedented",
        ]
        
        for claim in specific_claims:
            if claim in all_text.lower() and claim not in document_content.lower():
                potential_hallucinations.append({
                    "type": "claim",
                    "value": claim,
                    "context": f"Claim '{claim}' not supported by document",
                    "severity": "minor",
                })
        
        return potential_hallucinations
    
    def check_consistency(
        self,
        synthesis_result: SynthesisResult,
    ) -> list[dict[str, Any]]:
        """Check for internal consistency in the analysis."""
        
        consistency_issues = []
        
        # Extract TRL mentions
        trl_pattern = r'TRL\s*(\d+)'
        trl_matches = re.findall(
            trl_pattern,
            synthesis_result.executive_summary
            + " "
            + synthesis_result.integrated_analysis
            + " "
            + synthesis_result.investment_thesis,
            re.IGNORECASE,
        )
        
        # Check for inconsistent TRL mentions
        if len(set(trl_matches)) > 1:
            consistency_issues.append({
                "type": "trl_inconsistency",
                "values": trl_matches,
                "context": "Multiple different TRL levels mentioned",
                "severity": "major",
            })
        
        # Check for contradictory risk/opportunity statements
        if "high risk" in synthesis_result.risk_assessment.lower() and "low risk" in synthesis_result.risk_assessment.lower():
            consistency_issues.append({
                "type": "contradiction",
                "context": "Contradictory risk statements",
                "severity": "major",
            })
        
        # Check timeline consistency
        time_pattern = r'(\d+)\s*(years|months)'
        time_matches = re.findall(
            time_pattern,
            synthesis_result.integrated_analysis
            + " "
            + synthesis_result.investment_thesis,
            re.IGNORECASE,
        )
        
        # Flag if there are wildly different time estimates
        if time_matches:
            time_values = [int(match[0]) for match in time_matches if match[1].lower() in ["years", "year"]]
            if time_values and (max(time_values) - min(time_values)) > 10:
                consistency_issues.append({
                    "type": "timeline_inconsistency",
                    "values": time_matches,
                    "context": "Widely varying timeline estimates",
                    "severity": "minor",
                })
        
        return consistency_issues
