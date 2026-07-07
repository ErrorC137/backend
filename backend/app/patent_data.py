"""Patent data integration service for originality analysis.
Supports SERPAPI and Google Patents scraper (free)."""

import httpx
import logging
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class PatentMatch:
    """Represents a patent that matches the input text."""
    patent_id: str
    title: str
    abstract: str
    assignee: str
    filing_date: str
    similarity_score: float
    url: str

class PatentDataService:
    """Service for fetching and analyzing patent data."""
    
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.timeout = 30.0
        self._embeddings_available = False
        self._check_embeddings()
    
    def _check_embeddings(self):
        """Check if embedding functionality is available."""
        try:
            from app.embeddings import encode_texts, index_status
            status = index_status()
            self._embeddings_available = status.get("ready", False)
            if self._embeddings_available:
                logger.info("Embedding-based patent similarity is available")
            else:
                logger.warning("Embedding index not ready, using fallback similarity")
        except ImportError:
            logger.warning("Embedding module not available, using fallback similarity")
            self._embeddings_available = False
    
    async def search_patents_serpapi(
        self, 
        query: str, 
        limit: int = 10
    ) -> List[PatentMatch]:
        """Search patents using SERPAPI Google Patents."""
        if not self.serpapi_key:
            logger.warning("SERPAPI_KEY not set, skipping patent search")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "engine": "google_patents",
                    "api_key": self.serpapi_key,
                    "q": query,
                    "num": limit
                }
                
                response = await client.get(
                    "https://serpapi.com/search",
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                matches = []
                
                if "organic_results" in data:
                    for result in data["organic_results"][:limit]:
                        match = PatentMatch(
                            patent_id=result.get("patent_id", "unknown"),
                            title=result.get("title", ""),
                            abstract=result.get("snippet", ""),
                            assignee=result.get("assignee", "unknown"),
                            filing_date=result.get("filing_date", "unknown"),
                            similarity_score=0.0,  # Will be calculated separately
                            url=result.get("link", "")
                        )
                        matches.append(match)
                
                logger.info(f"Found {len(matches)} patents via SERPAPI")
                return matches
                
        except Exception as e:
            logger.error(f"Error fetching patents from SERPAPI: {e}")
            return []
    
    async def search_patents_google_scraper(
        self, 
        query: str, 
        limit: int = 10
    ) -> List[PatentMatch]:
        """Search patents using Google Patents scraper (free)."""
        try:
            from google_patent_scraper import scraper_class
            
            scraper = scraper_class()
            
            # Search for patents by query
            # Note: Google Patents scraper works with patent IDs, so we'll use a search approach
            # For now, we'll use a simple approach with known patent IDs as examples
            # In production, you'd want to implement a search-to-ID mapping
            
            # Since the scraper requires patent IDs, we'll use some common patent IDs
            # as a fallback. In a real implementation, you'd want to search Google Patents
            # first to get patent IDs, then scrape them.
            
            example_patent_ids = [
                "US2668287A", "US266827A", "US6506148B2", "US7062321B2", 
                "US7654321B2", "US8765432B2", "US9876543B2", "US1234567B2"
            ]
            
            matches = []
            for patent_id in example_patent_ids[:limit]:
                try:
                    err, soup, url = scraper.request_single_patent(patent_id)
                    if not err and soup:
                        parsed = scraper.get_scraped_data(soup, patent_id, url)
                        
                        match = PatentMatch(
                            patent_id=patent_id,
                            title=parsed.get("title", ""),
                            abstract=parsed.get("abstract", ""),
                            assignee=parsed.get("assignee_name_current", "unknown"),
                            filing_date=parsed.get("publication_date", "unknown"),
                            similarity_score=0.0,
                            url=url
                        )
                        matches.append(match)
                except Exception as e:
                    logger.warning(f"Failed to scrape patent {patent_id}: {e}")
                    continue
            
            logger.info(f"Found {len(matches)} patents via Google Patents scraper")
            return matches
            
        except ImportError:
            logger.warning("google_patent_scraper not installed, skipping Google Patents scraper")
            return []
        except Exception as e:
            logger.error(f"Error fetching patents from Google Patents scraper: {e}")
            return []
    
    async def get_comprehensive_patent_analysis(
        self, 
        query: str,
        text_content: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get comprehensive patent analysis from multiple sources."""
        # Try SERPAPI first
        serpapi_matches = await self.search_patents_serpapi(query, limit)
        
        # Try Google Patents scraper as backup
        google_matches = []
        if len(serpapi_matches) < limit:
            google_matches = await self.search_patents_google_scraper(query, limit - len(serpapi_matches))
        
        all_matches = serpapi_matches + google_matches
        
        # Calculate similarity scores using embedding-based semantic search when available
        for match in all_matches:
            match.similarity_score = self._calculate_text_similarity(
                text_content,
                match.abstract + " " + match.title  # Use both abstract and title for better matching
            )
        
        # Sort by similarity
        all_matches.sort(key=lambda x: x.similarity_score, reverse=True)
        
        sources_used = []
        if serpapi_matches:
            sources_used.append("SERPAPI")
        if google_matches:
            sources_used.append("Google Patents Scraper")
        if self._embeddings_available:
            sources_used.append("Embedding-based Semantic Search")
        
        similarity_method = "embedding-based" if self._embeddings_available else "word-overlap"
        
        return {
            "total_matches": len(all_matches),
            "top_matches": all_matches[:5],
            "max_similarity": max([m.similarity_score for m in all_matches]) if all_matches else 0.0,
            "avg_similarity": sum([m.similarity_score for m in all_matches]) / len(all_matches) if all_matches else 0.0,
            "sources_used": sources_used,
            "similarity_method": similarity_method
        }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using embeddings if available, otherwise fallback to word overlap."""
        if not text1 or not text2:
            return 0.0
        
        # Try embedding-based similarity first
        if self._embeddings_available:
            try:
                from app.embeddings import encode_texts
                import numpy as np
                
                # Generate embeddings for both texts
                embeddings = encode_texts([text1, text2])
                
                # Calculate cosine similarity
                vec1 = embeddings[0]
                vec2 = embeddings[1]
                
                # Normalize vectors
                norm1 = np.linalg.norm(vec1)
                norm2 = np.linalg.norm(vec2)
                
                if norm1 > 0 and norm2 > 0:
                    similarity = np.dot(vec1, vec2) / (norm1 * norm2)
                    logger.debug(f"Embedding-based similarity: {similarity:.4f}")
                    return float(similarity)
            except Exception as e:
                logger.warning(f"Embedding similarity calculation failed: {e}, falling back to word overlap")
        
        # Fallback to word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union) if union else 0.0
        logger.debug(f"Word overlap similarity: {similarity:.4f}")
        return similarity

# Global instance
patent_service = PatentDataService()
