"""Patent Claim Analysis Agent for 35 USC § 102/103 analysis.
Analyzes patent claims for novelty and non-obviousness assessment."""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PatentClaim:
    """Represents a patent claim."""
    claim_number: int
    claim_type: str  # "independent" or "dependent"
    text: str
    elements: List[str]


@dataclass
class NoveltyAnalysis:
    """Analysis of novelty under 35 USC § 102."""
    novel_elements: List[str]
    anticipated_elements: List[str]
    novelty_score: float
    prior_art_references: List[str]
    analysis_summary: str


@dataclass
class NonObviousnessAnalysis:
    """Analysis of non-obviousness under 35 USC § 103."""
    obvious_combinations: List[str]
    non_obvious_features: List[str]
    teaching_away: List[str]
    secondary_considerations: List[str]
    non_obviousness_score: float
    analysis_summary: str


@dataclass
class ClaimAnalysisResult:
    """Complete patent claim analysis result."""
    patent_id: str
    claims: List[PatentClaim]
    novelty_analysis: NoveltyAnalysis
    non_obviousness_analysis: NonObviousnessAnalysis
    overall_patentability: str
    recommendations: List[str]


class PatentClaimAnalyzer:
    """Agent for analyzing patent claims under 35 USC § 102 and § 103."""
    
    def __init__(self):
        self._initialized = False
    
    def parse_claims(self, patent_text: str) -> List[PatentClaim]:
        """
        Parse patent claims from patent text.
        
        Args:
            patent_text: Full patent document text
            
        Returns:
            List of parsed patent claims
        """
        claims = []
        
        # Find claims section
        claims_match = re.search(
            r"(?i)(?:claims|what is claimed)[\s:]+(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)",
            patent_text,
            re.DOTALL
        )
        
        if not claims_match:
            logger.warning("Could not find claims section in patent text")
            return claims
        
        claims_text = claims_match.group(1)
        
        # Split into individual claims
        claim_pattern = r"(\d+)\.\s+([^0-9]+?)(?=\n\d+\.|\Z)"
        claim_matches = re.findall(claim_pattern, claims_text, re.DOTALL)
        
        for claim_num, claim_text in claim_matches:
            claim_num = int(claim_num)
            claim_text = claim_text.strip()
            
            # Determine claim type
            claim_type = "independent" if claim_num == 1 or not re.search(r"wherein|wherein said", claim_text, re.IGNORECASE) else "dependent"
            
            # Extract claim elements (simplified parsing)
            elements = self._extract_claim_elements(claim_text)
            
            claim = PatentClaim(
                claim_number=claim_num,
                claim_type=claim_type,
                text=claim_text,
                elements=elements
            )
            claims.append(claim)
        
        logger.info(f"Parsed {len(claims)} patent claims")
        return claims
    
    def _extract_claim_elements(self, claim_text: str) -> List[str]:
        """
        Extract individual elements from a claim.
        
        Args:
            claim_text: Claim text
            
        Returns:
            List of claim elements
        """
        # Split by common delimiters
        delimiters = [
            r";\s*wherein",
            r";\s*wherein said",
            r";\s*further comprising",
            r";\s*where",
            r";\s*and",
            r",\s*wherein"
        ]
        
        elements = [claim_text]
        
        for delimiter in delimiters:
            new_elements = []
            for element in elements:
                parts = re.split(delimiter, element, flags=re.IGNORECASE)
                if len(parts) > 1:
                    new_elements.extend(parts)
                else:
                    new_elements.append(element)
            elements = new_elements
        
        # Clean up elements
        elements = [e.strip() for e in elements if len(e.strip()) > 10]
        
        return elements[:10]  # Limit to top 10 elements
    
    def analyze_novelty_102(
        self,
        invention_disclosure: str,
        prior_art_claims: List[PatentClaim],
        uspto_references: Optional[List[Dict[str, Any]]] = None
    ) -> NoveltyAnalysis:
        """
        Analyze novelty under 35 USC § 102.
        
        Args:
            invention_disclosure: The invention disclosure text
            prior_art_claims: Claims from prior art patents
            uspto_references: USPTO patent references
            
        Returns:
            Novelty analysis result
        """
        invention_elements = self._extract_claim_elements(invention_disclosure)
        
        novel_elements = []
        anticipated_elements = []
        prior_art_refs = []
        
        # Compare invention elements with prior art claims
        for prior_claim in prior_art_claims:
            for prior_element in prior_claim.elements:
                for invention_element in invention_elements:
                    similarity = self._calculate_element_similarity(invention_element, prior_element)
                    
                    if similarity > 0.8:
                        if prior_claim.claim_type == "independent":
                            anticipated_elements.append(invention_element)
                            if prior_claim.claim_number not in prior_art_refs:
                                prior_art_refs.append(f"Claim {prior_claim.claim_number}")
                    elif similarity < 0.3:
                        if invention_element not in novel_elements:
                            novel_elements.append(invention_element)
        
        # Add USPTO references if available
        if uspto_references:
            for ref in uspto_references:
                patent_id = ref.get("patent_id", "")
                if patent_id and patent_id not in prior_art_refs:
                    prior_art_refs.append(patent_id)
        
        # Calculate novelty score
        total_elements = len(invention_elements)
        novel_count = len(novel_elements)
        novelty_score = (novel_count / total_elements) if total_elements > 0 else 0.5
        
        # Generate analysis summary
        if novelty_score > 0.7:
            summary = "Strong novelty under 35 USC § 102. The invention contains significant novel elements not anticipated by prior art. High probability of patentability on novelty grounds."
        elif novelty_score > 0.4:
            summary = "Moderate novelty under 35 USC § 102. Some elements are anticipated by prior art, but novel features are present. Patentability may require careful claim drafting to emphasize novel aspects."
        else:
            summary = "Limited novelty under 35 USC § 102. Many invention elements are anticipated by prior art. Patentability on novelty grounds is challenging; consider emphasizing specific combinations or applications."
        
        return NoveltyAnalysis(
            novel_elements=novel_elements,
            anticipated_elements=anticipated_elements,
            novelty_score=novelty_score,
            prior_art_references=prior_art_refs,
            analysis_summary=summary
        )
    
    def analyze_non_obviousness_103(
        self,
        invention_disclosure: str,
        prior_art_claims: List[PatentClaim],
        uspto_references: Optional[List[Dict[str, Any]]] = None
    ) -> NonObviousnessAnalysis:
        """
        Analyze non-obviousness under 35 USC § 103.
        
        Args:
            invention_disclosure: The invention disclosure text
            prior_art_claims: Claims from prior art patents
            uspto_references: USPTO patent references
            
        Returns:
            Non-obviousness analysis result
        """
        invention_elements = self._extract_claim_elements(invention_disclosure)
        
        obvious_combinations = []
        non_obvious_features = []
        teaching_away = []
        secondary_considerations = []
        
        # Check for obvious combinations
        for i, prior_claim_1 in enumerate(prior_art_claims):
            for prior_claim_2 in prior_art_claims[i+1:]:
                combination_score = self._check_combination_obviousness(
                    invention_elements,
                    prior_claim_1.elements,
                    prior_claim_2.elements
                )
                
                if combination_score > 0.7:
                    obvious_combinations.append(
                        f"Combination of claim {prior_claim_1.claim_number} and claim {prior_claim_2.claim_number}"
                    )
        
        # Identify non-obvious features
        for element in invention_elements:
            is_obvious = False
            for prior_claim in prior_art_claims:
                for prior_element in prior_claim.elements:
                    similarity = self._calculate_element_similarity(element, prior_element)
                    if similarity > 0.6:
                        is_obvious = True
                        break
                if is_obvious:
                    break
            
            if not is_obvious:
                non_obvious_features.append(element)
        
        # Check for teaching away indicators
        teaching_away_patterns = [
            r"would not work",
            r"contrary to",
            r"unexpected result",
            r"surprising",
            r"unanticipated",
            r"teaches away"
        ]
        
        for pattern in teaching_away_patterns:
            if re.search(pattern, invention_disclosure, re.IGNORECASE):
                teaching_away.append(f"Found '{pattern}' indicating teaching away from prior art")
        
        # Check for secondary considerations
        secondary_patterns = [
            r"commercial success",
            r"long-felt need",
            r"failure of others",
            r"copying",
            r"licensing",
            r"praise"
        ]
        
        for pattern in secondary_patterns:
            if re.search(pattern, invention_disclosure, re.IGNORECASE):
                secondary_considerations.append(f"Found '{pattern}' as secondary consideration")
        
        # Calculate non-obviousness score
        total_elements = len(invention_elements)
        non_obvious_count = len(non_obvious_features)
        teaching_bonus = len(teaching_away) * 0.1
        secondary_bonus = len(secondary_considerations) * 0.05
        
        base_score = (non_obvious_count / total_elements) if total_elements > 0 else 0.5
        non_obviousness_score = min(1.0, base_score + teaching_bonus + secondary_bonus)
        
        # Generate analysis summary
        if non_obviousness_score > 0.7:
            summary = "Strong non-obviousness under 35 USC § 103. The invention presents non-obvious features and may have teaching away or secondary considerations supporting patentability."
        elif non_obviousness_score > 0.4:
            summary = "Moderate non-obviousness under 35 USC § 103. Some features may be obvious combinations, but novel aspects exist. Patentability may require emphasizing unexpected results or secondary considerations."
        else:
            summary = "Limited non-obviousness under 35 USC § 103. Many features appear to be obvious combinations of prior art. Patentability on non-obviousness grounds is challenging; consider emphasizing specific advantages or secondary considerations."
        
        return NonObviousnessAnalysis(
            obvious_combinations=obvious_combinations,
            non_obvious_features=non_obvious_features,
            teaching_away=teaching_away,
            secondary_considerations=secondary_considerations,
            non_obviousness_score=non_obviousness_score,
            analysis_summary=summary
        )
    
    def _calculate_element_similarity(self, element1: str, element2: str) -> float:
        """
        Calculate similarity between two claim elements.
        
        Args:
            element1: First claim element
            element2: Second claim element
            
        Returns:
            Similarity score (0-1)
        """
        # Simple word overlap similarity
        words1 = set(re.findall(r"\b\w+\b", element1.lower()))
        words2 = set(re.findall(r"\b\w+\b", element2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union) if union else 0.0
        return similarity
    
    def _check_combination_obviousness(
        self,
        invention_elements: List[str],
        prior_elements1: List[str],
        prior_elements2: List[str]
    ) -> float:
        """
        Check if invention is an obvious combination of prior art.
        
        Args:
            invention_elements: Invention claim elements
            prior_elements1: First prior art claim elements
            prior_elements2: Second prior art claim elements
            
        Returns:
            Obviousness score (0-1)
        """
        combined_prior = prior_elements1 + prior_elements2
        
        matched_elements = 0
        for invention_element in invention_elements:
            for prior_element in combined_prior:
                similarity = self._calculate_element_similarity(invention_element, prior_element)
                if similarity > 0.7:
                    matched_elements += 1
                    break
        
        if not invention_elements:
            return 0.0
        
        obviousness = matched_elements / len(invention_elements)
        return obviousness
    
    def analyze_claims(
        self,
        patent_text: str,
        invention_disclosure: str,
        prior_art_claims: Optional[List[PatentClaim]] = None,
        uspto_references: Optional[List[Dict[str, Any]]] = None
    ) -> ClaimAnalysisResult:
        """
        Perform complete patent claim analysis.
        
        Args:
            patent_text: Patent document text
            invention_disclosure: Invention disclosure text
            prior_art_claims: Prior art claims for comparison
            uspto_references: USPTO patent references
            
        Returns:
            Complete claim analysis result
        """
        # Parse claims from patent text
        claims = self.parse_claims(patent_text)
        
        # If no prior art claims provided, use claims from the patent itself for self-analysis
        if prior_art_claims is None:
            prior_art_claims = claims
        
        # Analyze novelty (35 USC § 102)
        novelty_analysis = self.analyze_novelty_102(
            invention_disclosure,
            prior_art_claims,
            uspto_references
        )
        
        # Analyze non-obviousness (35 USC § 103)
        non_obviousness_analysis = self.analyze_non_obviousness_103(
            invention_disclosure,
            prior_art_claims,
            uspto_references
        )
        
        # Determine overall patentability
        overall_score = (novelty_analysis.novelty_score + non_obviousness_analysis.non_obviousness_score) / 2
        
        if overall_score > 0.7:
            overall_patentability = "Strong patentability potential"
        elif overall_score > 0.4:
            overall_patentability = "Moderate patentability potential"
        else:
            overall_patentability = "Limited patentability potential"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            novelty_analysis,
            non_obviousness_analysis,
            claims
        )
        
        patent_id = re.search(r"US\s*[\d,]+[A-Z]?", patent_text)
        patent_id = patent_id.group(0) if patent_id else "Unknown"
        
        return ClaimAnalysisResult(
            patent_id=patent_id,
            claims=claims,
            novelty_analysis=novelty_analysis,
            non_obviousness_analysis=non_obviousness_analysis,
            overall_patentability=overall_patentability,
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        novelty_analysis: NoveltyAnalysis,
        non_obviousness_analysis: NonObviousnessAnalysis,
        claims: List[PatentClaim]
    ) -> List[str]:
        """Generate patentability recommendations."""
        recommendations = []
        
        # Novelty recommendations
        if novelty_analysis.novelty_score < 0.5:
            recommendations.append(
                "Consider narrowing claim scope to focus on novel elements not anticipated by prior art"
            )
            recommendations.append(
                "Emphasize specific combinations or applications that are not disclosed in prior art"
            )
        
        # Non-obviousness recommendations
        if non_obviousness_analysis.non_obviousness_score < 0.5:
            recommendations.append(
                "Document unexpected results or surprising advantages to support non-obviousness"
            )
            recommendations.append(
                "Gather evidence of secondary considerations (commercial success, long-felt need, etc.)"
            )
        
        # Claim structure recommendations
        independent_claims = [c for c in claims if c.claim_type == "independent"]
        if len(independent_claims) == 0:
            recommendations.append("Ensure at least one independent claim is present")
        elif len(independent_claims) > 3:
            recommendations.append("Consider reducing number of independent claims for clarity")
        
        # General recommendations
        if novelty_analysis.novelty_score > 0.6 and non_obviousness_analysis.non_obviousness_score > 0.6:
            recommendations.append(
                "Strong patentability position; proceed with filing with confidence"
            )
        
        return recommendations


# Global analyzer instance
_patent_claim_analyzer: Optional[PatentClaimAnalyzer] = None


def get_patent_claim_analyzer() -> PatentClaimAnalyzer:
    """Get or create global patent claim analyzer instance."""
    global _patent_claim_analyzer
    if _patent_claim_analyzer is None:
        _patent_claim_analyzer = PatentClaimAnalyzer()
    return _patent_claim_analyzer
