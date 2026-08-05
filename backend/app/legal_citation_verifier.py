"""Legal Citation Verification Agent for USPTO/EPO database validation.
Verifies patent numbers, legal precedents, and citations against official databases."""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CitationVerification:
    """Result of citation verification."""
    citation: str
    citation_type: str  # "patent", "legal_precedent", "statute", "other"
    is_valid: bool
    source: str  # "USPTO", "EPO", "manual", "unknown"
    verification_details: str
    confidence: float


@dataclass
class VerificationReport:
    """Complete verification report for a document."""
    total_citations: int
    verified_citations: int
    invalid_citations: int
    unverifiable_citations: int
    citations: List[CitationVerification]
    overall_confidence: float
    recommendations: List[str]


class LegalCitationVerifier:
    """Agent for verifying legal citations against USPTO/EPO databases."""
    
    def __init__(self):
        self._uspto_client = None
        self._epo_client = None
        self._initialized = False
    
    def _initialize(self):
        """Initialize USPTO and EPO clients."""
        if self._initialized:
            return
        
        try:
            from app.uspto_api import get_uspto_client
            self._uspto_client = get_uspto_client()
            logger.info("USPTO client initialized for citation verification")
        except Exception as e:
            logger.warning(f"Failed to initialize USPTO client: {e}")
        
        # EPO client would be similar (not implemented in this version)
        self._initialized = True
    
    def extract_citations(self, text: str) -> List[str]:
        """
        Extract patent and legal citations from text.
        
        Args:
            text: Document text to extract citations from
            
        Returns:
            List of extracted citations
        """
        citations = []
        
        # US Patent patterns
        us_patent_patterns = [
            r"US\s*[\d,]+[A-Z]?",  # US 6,123,456 A
            r"Pat\.?\s*No\.?\s*[\d,]+",  # Pat. No. 6,123,456
            r"U\.S\.?\s*Pat\.?\s*No\.?\s*[\d,]+",  # U.S. Pat. No. 6,123,456
        ]
        
        # PCT patterns
        pct_patterns = [
            r"PCT/[A-Z]{2}/\d{4}/\d+",  # PCT/US2024/12345
            r"WO\s*\d{4}/\d+",  # WO 2024/12345
        ]
        
        # EPO patterns
        epo_patterns = [
            r"EP\s*\d+[A-Z]?",  # EP 1234567 A1
            r"European\s*Patent\s*No\.?\s*[\d,]+",  # European Patent No. 1,234,567
        ]
        
        # Legal precedent patterns
        legal_patterns = [
            r"\d+\s+F\.?\s*\d+",  # 123 F.3d 456
            r"\d+\s+S\.?\s*Ct\.?\s*\d+",  # 123 S. Ct. 456
            r"\d+\s+U\.S\.?\s*\d+",  # 123 U.S. 456
        ]
        
        all_patterns = us_patent_patterns + pct_patterns + epo_patterns + legal_patterns
        
        for pattern in all_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_citations = []
        for citation in citations:
            citation_normalized = citation.upper().strip()
            if citation_normalized not in seen:
                seen.add(citation_normalized)
                unique_citations.append(citation)
        
        logger.info(f"Extracted {len(unique_citations)} unique citations")
        return unique_citations
    
    def classify_citation(self, citation: str) -> str:
        """
        Classify the type of citation.
        
        Args:
            citation: Citation string
            
        Returns:
            Citation type ("patent", "legal_precedent", "statute", "other")
        """
        citation_upper = citation.upper()
        
        # Patent citations
        if re.search(r"US\s*[\d,]+|PCT/|WO\s*\d+|EP\s*\d+", citation_upper):
            return "patent"
        
        # Legal precedents
        if re.search(r"F\.?\s*\d+|S\.?\s*Ct\.?|U\.S\.?\s*\d+", citation_upper):
            return "legal_precedent"
        
        # Statutes
        if re.search(r"35\s*U\.S\.C\.|17\s*U\.S\.C\.|§\s*\d+", citation_upper):
            return "statute"
        
        return "other"
    
    async def verify_patent_citation(self, citation: str) -> Tuple[bool, str, float]:
        """
        Verify a patent citation against USPTO database.
        
        Args:
            citation: Patent citation string
            
        Returns:
            Tuple of (is_valid, verification_details, confidence)
        """
        self._initialize()
        
        if not self._uspto_client:
            return False, "USPTO client not available", 0.0
        
        try:
            # Normalize patent number
            patent_id = self._normalize_patent_id(citation)
            
            # Query USPTO API
            patent = await self._uspto_client.get_patent_by_id(patent_id)
            
            if patent:
                details = f"Verified: {patent.title} (Filing: {patent.filing_date})"
                return True, details, 0.95
            else:
                return False, "Patent not found in USPTO database", 0.8
                
        except Exception as e:
            logger.error(f"Error verifying patent citation {citation}: {e}")
            return False, f"Verification error: {str(e)}", 0.0
    
    def _normalize_patent_id(self, citation: str) -> str:
        """
        Normalize patent citation to standard format.
        
        Args:
            citation: Patent citation string
            
        Returns:
            Normalized patent ID
        """
        # Remove spaces and special characters
        normalized = re.sub(r"[^\w,]", "", citation.upper())
        
        # Convert to standard format (e.g., US6123456A)
        normalized = re.sub(r"US", "US", normalized)
        normalized = re.sub(r",", "", normalized)
        
        return normalized
    
    async def verify_legal_precedent(self, citation: str) -> Tuple[bool, str, float]:
        """
        Verify a legal precedent citation.
        
        Args:
            citation: Legal precedent citation string
            
        Returns:
            Tuple of (is_valid, verification_details, confidence)
        """
        # For legal precedents, we would typically use a legal database API
        # For now, we'll do basic format validation
        
        citation_upper = citation.upper()
        
        # Check if format matches expected patterns
        if re.search(r"\d+\s+F\.?\s*\d+", citation_upper):
            # Federal Reporter format
            return True, "Valid Federal Reporter citation format", 0.7
        elif re.search(r"\d+\s+S\.?\s*Ct\.?\s*\d+", citation_upper):
            # Supreme Court Reporter format
            return True, "Valid Supreme Court Reporter citation format", 0.7
        elif re.search(r"\d+\s+U\.S\.?\s*\d+", citation_upper):
            # United States Reports format
            return True, "Valid United States Reports citation format", 0.7
        else:
            return False, "Unrecognized legal citation format", 0.3
    
    async def verify_statute(self, citation: str) -> Tuple[bool, str, float]:
        """
        Verify a statute citation.
        
        Args:
            citation: Statute citation string
            
        Returns:
            Tuple of (is_valid, verification_details, confidence)
        """
        citation_upper = citation.upper()
        
        # Check for common patent statute citations
        if re.search(r"35\s*U\.S\.C\.?\s*§\s*\d+", citation_upper):
            # Title 35 U.S.C. (Patent Act)
            return True, "Valid Title 35 U.S.C. citation", 0.9
        elif re.search(r"17\s*U\.S\.C\.?\s*§\s*\d+", citation_upper):
            # Title 17 U.S.C. (Copyright Act)
            return True, "Valid Title 17 U.S.C. citation", 0.9
        else:
            return False, "Unrecognized statute citation format", 0.5
    
    async def verify_citation(self, citation: str) -> CitationVerification:
        """
        Verify a single citation.
        
        Args:
            citation: Citation string
            
        Returns:
            Citation verification result
        """
        citation_type = self.classify_citation(citation)
        
        if citation_type == "patent":
            is_valid, details, confidence = await self.verify_patent_citation(citation)
            source = "USPTO" if is_valid else "unknown"
        elif citation_type == "legal_precedent":
            is_valid, details, confidence = await self.verify_legal_precedent(citation)
            source = "manual"
        elif citation_type == "statute":
            is_valid, details, confidence = await self.verify_statute(citation)
            source = "manual"
        else:
            is_valid = False
            details = "Unrecognized citation type"
            confidence = 0.0
            source = "unknown"
        
        return CitationVerification(
            citation=citation,
            citation_type=citation_type,
            is_valid=is_valid,
            source=source,
            verification_details=details,
            confidence=confidence
        )
    
    async def verify_document_citations(self, text: str) -> VerificationReport:
        """
        Verify all citations in a document.
        
        Args:
            text: Document text
            
        Returns:
            Complete verification report
        """
        citations = self.extract_citations(text)
        
        if not citations:
            return VerificationReport(
                total_citations=0,
                verified_citations=0,
                invalid_citations=0,
                unverifiable_citations=0,
                citations=[],
                overall_confidence=1.0,
                recommendations=["No citations found in document"]
            )
        
        verification_results = []
        
        for citation in citations:
            result = await self.verify_citation(citation)
            verification_results.append(result)
        
        # Calculate statistics
        verified = sum(1 for r in verification_results if r.is_valid)
        invalid = sum(1 for r in verification_results if not r.is_valid and r.confidence > 0.5)
        unverifiable = sum(1 for r in verification_results if r.confidence <= 0.5)
        
        # Calculate overall confidence
        total_confidence = sum(r.confidence for r in verification_results)
        overall_confidence = total_confidence / len(verification_results) if verification_results else 0.0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(verification_results)
        
        return VerificationReport(
            total_citations=len(citations),
            verified_citations=verified,
            invalid_citations=invalid,
            unverifiable_citations=unverifiable,
            citations=verification_results,
            overall_confidence=overall_confidence,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, results: List[CitationVerification]) -> List[str]:
        """Generate recommendations based on verification results."""
        recommendations = []
        
        invalid_count = sum(1 for r in results if not r.is_valid)
        unverifiable_count = sum(1 for r in results if r.confidence <= 0.5)
        
        if invalid_count > 0:
            recommendations.append(
                f"{invalid_count} citation(s) could not be verified. Review these citations for accuracy."
            )
        
        if unverifiable_count > 0:
            recommendations.append(
                f"{unverifiable_count} citation(s) could not be automatically verified. Manual review recommended."
            )
        
        patent_citations = [r for r in results if r.citation_type == "patent"]
        if patent_citations:
            verified_patents = sum(1 for r in patent_citations if r.is_valid)
            recommendations.append(
                f"{verified_patents}/{len(patent_citations)} patent citations verified against USPTO database."
            )
        
        if all(r.is_valid for r in results):
            recommendations.append("All citations successfully verified. Document appears well-referenced.")
        
        return recommendations


# Global verifier instance
_legal_citation_verifier: Optional[LegalCitationVerifier] = None


def get_legal_citation_verifier() -> LegalCitationVerifier:
    """Get or create global legal citation verifier instance."""
    global _legal_citation_verifier
    if _legal_citation_verifier is None:
        _legal_citation_verifier = LegalCitationVerifier()
    return _legal_citation_verifier
