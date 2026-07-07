"""Sophisticated NLP analysis without external API dependencies.
Uses rule-based and statistical methods for document understanding."""

import re
import logging
from typing import Any, Dict, List, Tuple
from collections import Counter
import math

logger = logging.getLogger(__name__)

class NLPAnalyzer:
    """Advanced NLP analysis for document understanding without external APIs."""
    
    def __init__(self):
        self.technical_indicators = self._load_technical_indicators()
        self.methodology_patterns = self._load_methodology_patterns()
        self.result_patterns = self._load_result_patterns()
    
    def _load_technical_indicators(self) -> Dict[str, List[str]]:
        """Load technical indicators by category."""
        return {
            "materials": ["nanotube", "graphene", "polymer", "composite", "ceramic", "alloy", "carbon", "silicon", "metal", "oxide"],
            "processes": ["synthesis", "fabrication", "manufacturing", "processing", "deposition", "annealing", "sintering", "curing"],
            "properties": ["conductivity", "strength", "durability", "thermal", "mechanical", "electrical", "optical", "magnetic"],
            "applications": ["battery", "catalyst", "sensor", "electronics", "energy", "medical", "automotive", "aerospace"],
            "measurements": ["characterization", "analysis", "measurement", "testing", "evaluation", "performance", "efficiency"]
        }
    
    def _load_methodology_patterns(self) -> List[str]:
        """Load methodology-related patterns."""
        return [
            r"method|approach|technique|procedure|protocol|experiment|test|validate",
            r"prepared|synthesized|fabricated|manufactured|processed",
            r"using|via|through|by means of|employing",
            r"conditions|parameters|temperature|pressure|time|duration",
            r"reagents|chemicals|materials|precursors|substrates"
        ]
    
    def _load_result_patterns(self) -> List[str]:
        """Load result-related patterns."""
        return [
            r"result|outcome|finding|observation|data|measurement",
            r"show|demonstrate|reveal|indicate|suggest|confirm",
            r"significant|notable|substantial|considerable|marked",
            r"improve|enhance|increase|decrease|reduce|optimize",
            r"performance|efficiency|yield|output|throughput"
        ]
    
    def analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document structure and sections."""
        sentences = self._split_sentences(text)
        paragraphs = text.split('\n\n')
        
        # Identify sections based on headers and content
        sections = self._identify_sections(text)
        
        # Analyze sentence complexity
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # Analyze paragraph structure
        paragraph_lengths = [len(p.split()) for p in paragraphs if p.strip()]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        return {
            "total_sentences": len(sentences),
            "total_paragraphs": len(paragraphs),
            "avg_sentence_length": avg_sentence_length,
            "avg_paragraph_length": avg_paragraph_length,
            "identified_sections": sections,
            "document_complexity": self._calculate_complexity(avg_sentence_length, avg_paragraph_length)
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex."""
        # Handle common abbreviations
        text = re.sub(r'\b(?:Dr|Mr|Mrs|Ms|Prof|etc)\.', r'\0<abbr>', text)
        sentences = re.split(r'[.!?]+', text)
        # Restore abbreviations
        sentences = [s.replace('<abbr>', '.') for s in sentences]
        return [s.strip() for s in sentences if s.strip()]
    
    def _identify_sections(self, text: str) -> List[str]:
        """Identify document sections based on headers."""
        section_patterns = [
            r'\babstract\b',
            r'\bintroduction\b',
            r'\bbackground\b',
            r'\bmethodology\b|\bmethods\b',
            r'\bexperimental\b',
            r'\bresults\b',
            r'\bdiscussion\b',
            r'\bconclusion\b',
            r'\breferences\b',
            r'\bappendix\b'
        ]
        
        found_sections = []
        text_lower = text.lower()
        
        for pattern in section_patterns:
            if re.search(pattern, text_lower):
                section_name = pattern.replace(r'\b', '').replace('|', '/').upper()
                found_sections.append(section_name)
        
        return found_sections
    
    def _calculate_complexity(self, avg_sentence_length: float, avg_paragraph_length: float) -> str:
        """Calculate document complexity based on structure."""
        if avg_sentence_length > 25 and avg_paragraph_length > 150:
            return "high"
        elif avg_sentence_length > 15 and avg_paragraph_length > 100:
            return "medium"
        else:
            return "low"
    
    def extract_technical_content(self, text: str) -> Dict[str, Any]:
        """Extract technical content and indicators."""
        text_lower = text.lower()
        
        # Find technical indicators by category
        technical_findings = {}
        for category, indicators in self.technical_indicators.items():
            found_indicators = [ind for ind in indicators if ind in text_lower]
            if found_indicators:
                technical_findings[category] = found_indicators
        
        # Extract technical terms using noun phrase patterns
        technical_terms = self._extract_technical_terms(text)
        
        # Identify numerical data
        numerical_data = self._extract_numerical_data(text)
        
        return {
            "technical_indicators": technical_findings,
            "technical_terms": technical_terms[:20],  # Top 20
            "numerical_data": numerical_data,
            "technical_density": len(technical_terms) / len(text.split()) if text.split() else 0
        }
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms using patterns."""
        # Look for capitalized technical terms
        technical_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b'
        potential_terms = re.findall(technical_pattern, text)
        
        # Filter out common words
        common_words = {'The', 'This', 'That', 'These', 'Those', 'However', 'Therefore', 'Moreover', 'Furthermore'}
        technical_terms = [term for term in potential_terms if term not in common_words and len(term.split()) <= 3]
        
        # Count frequency
        term_counts = Counter(technical_terms)
        
        # Return most common terms
        return [term for term, count in term_counts.most_common(50)]
    
    def _extract_numerical_data(self, text: str) -> List[Dict[str, Any]]:
        """Extract numerical data with context."""
        # Pattern for numbers with units
        number_pattern = r'\b(\d+\.?\d*)\s*([a-zA-Z%]+)\b'
        matches = re.finditer(number_pattern, text)
        
        numerical_data = []
        for match in matches:
            value = float(match.group(1))
            unit = match.group(2)
            context_start = max(0, match.start() - 50)
            context_end = min(len(text), match.end() + 50)
            context = text[context_start:context_end].strip()
            
            numerical_data.append({
                "value": value,
                "unit": unit,
                "context": context
            })
        
        return numerical_data[:30]  # Top 30
    
    def analyze_methodology(self, text: str) -> Dict[str, Any]:
        """Analyze methodology section for experimental rigor."""
        text_lower = text.lower()
        
        # Check for methodology keywords
        methodology_score = 0
        methodology_evidence = []
        
        for pattern in self.methodology_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                methodology_score += len(matches) * 0.1
                methodology_evidence.extend(matches[:3])  # Top 3 matches per pattern
        
        # Check for specific experimental elements
        experimental_elements = {
            "has_controls": bool(re.search(r'control|baseline|reference', text_lower)),
            "has_replicates": bool(re.search(r'replicat|repeat|duplicate', text_lower)),
            "has_statistics": bool(re.search(r'statistical|significant|p-value|confidence', text_lower)),
            "has_error_analysis": bool(re.search(r'error|uncertainty|deviation|standard', text_lower)),
            "has_validation": bool(re.search(r'valid|verify|confirm|corroborate', text_lower))
        }
        
        methodology_score += sum(experimental_elements.values()) * 0.15
        
        return {
            "methodology_score": min(1.0, methodology_score),
            "methodology_evidence": list(set(methodology_evidence))[:10],
            "experimental_elements": experimental_elements,
            "experimental_rigor": self._assess_rigor(experimental_elements, methodology_score)
        }
    
    def _assess_rigor(self, elements: Dict[str, bool], score: float) -> str:
        """Assess experimental rigor based on elements and score."""
        element_count = sum(elements.values())
        
        if element_count >= 4 and score >= 0.7:
            return "high"
        elif element_count >= 2 and score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def analyze_results(self, text: str) -> Dict[str, Any]:
        """Analyze results section for findings and significance."""
        text_lower = text.lower()
        
        # Extract result statements
        result_statements = []
        for pattern in self.result_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                statement = text[start:end].strip()
                if len(statement.split()) > 5:  # Filter short matches
                    result_statements.append(statement)
        
        # Identify significant findings
        significance_indicators = [
            "significant", "notable", "substantial", "considerable", "marked",
            "improved", "enhanced", "increased", "decreased", "reduced", "optimized"
        ]
        
        significant_findings = []
        for indicator in significance_indicators:
            if indicator in text_lower:
                # Find context around the indicator
                pattern = rf'.{{0,50}}{indicator}.{{0,50}}'
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                significant_findings.extend(matches[:2])  # Top 2 per indicator
        
        return {
            "result_statements": result_statements[:10],
            "significant_findings": significant_findings[:10],
            "results_clarity": self._assess_results_clarity(len(result_statements), len(significant_findings))
        }
    
    def _assess_results_clarity(self, statement_count: int, finding_count: int) -> str:
        """Assess clarity of results presentation."""
        if statement_count >= 5 and finding_count >= 3:
            return "high"
        elif statement_count >= 3 and finding_count >= 2:
            return "medium"
        else:
            return "low"
    
    def calculate_innovation_score(self, text: str, technical_content: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate innovation score based on technical content and novelty."""
        text_lower = text.lower()
        
        # Novelty indicators
        novelty_indicators = [
            "novel", "new", "innovative", "unique", "first", "pioneering",
            "breakthrough", "revolutionary", "groundbreaking", "unprecedented"
        ]
        
        novelty_score = 0
        novelty_evidence = []
        
        for indicator in novelty_indicators:
            if indicator in text_lower:
                novelty_score += 0.15
                # Find context
                pattern = rf'.{{0,30}}{indicator}.{{0,30}}'
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                novelty_evidence.extend(matches[:1])
        
        # Technical complexity bonus
        technical_density = technical_content.get("technical_density", 0)
        complexity_bonus = min(0.3, technical_density * 10)
        
        # Diversity of technical indicators
        indicator_diversity = len(technical_content.get("technical_indicators", {}))
        diversity_bonus = min(0.2, indicator_diversity * 0.05)
        
        total_score = min(1.0, novelty_score + complexity_bonus + diversity_bonus)
        
        return {
            "innovation_score": total_score,
            "novelty_evidence": novelty_evidence[:5],
            "technical_complexity_bonus": complexity_bonus,
            "indicator_diversity_bonus": diversity_bonus,
            "innovation_level": self._assess_innovation_level(total_score)
        }
    
    def _assess_innovation_level(self, score: float) -> str:
        """Assess innovation level based on score."""
        if score >= 0.7:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def comprehensive_analysis(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive NLP analysis."""
        logger.info("Starting comprehensive NLP analysis")
        
        structure = self.analyze_document_structure(text)
        technical = self.extract_technical_content(text)
        methodology = self.analyze_methodology(text)
        results = self.analyze_results(text)
        innovation = self.calculate_innovation_score(text, technical)
        
        # Overall quality assessment
        quality_score = (
            (1.0 if structure["document_complexity"] != "low" else 0.5) * 0.2 +
            methodology["methodology_score"] * 0.3 +
            (1.0 if results["results_clarity"] != "low" else 0.5) * 0.2 +
            innovation["innovation_score"] * 0.3
        )
        
        logger.info(f"Comprehensive analysis completed. Quality score: {quality_score:.2f}")
        
        return {
            "document_structure": structure,
            "technical_content": technical,
            "methodology_analysis": methodology,
            "results_analysis": results,
            "innovation_assessment": innovation,
            "overall_quality": quality_score,
            "quality_level": self._assess_innovation_level(quality_score),
            "analysis_source": "rule-based-nlp"
        }

# Global instance
nlp_analyzer = NLPAnalyzer()
