"""Patent data integration service for originality analysis.
Supports SERPAPI, LENS.org, and local patent corpus comparison."""

import httpx
import logging
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

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
        self.lens_api_key = os.getenv("LENS_API_KEY")
        self.timeout = 30.0
    
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
    
    async def search_patents_lens(
        self, 
        query: str, 
        limit: int = 10
    ) -> List[PatentMatch]:
        """Search patents using LENS.org API."""
        if not self.lens_api_key:
            logger.warning("LENS_API_KEY not set, skipping patent search")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.lens_api_key}",
                    "Content-Type": "application/json"
                }
                
                # LENS.org API endpoint for patent search
                params = {
                    "query": query,
                    "per_page": limit
                }
                
                response = await client.get(
                    "https://api.lens.org/patent/search",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                matches = []
                
                if "data" in data:
                    for result in data["data"][:limit]:
                        match = PatentMatch(
                            patent_id=result.get("patent_id", "unknown"),
                            title=result.get("title", ""),
                            abstract=result.get("abstract", ""),
                            assignee=result.get("assignee", "unknown"),
                            filing_date=result.get("publication_date", "unknown"),
                            similarity_score=0.0,
                            url=result.get("lens_url", "")
                        )
                        matches.append(match)
                
                logger.info(f"Found {len(matches)} patents via LENS.org")
                return matches
                
        except Exception as e:
            logger.error(f"Error fetching patents from LENS.org: {e}")
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
        
        # Try LENS.org as backup
        lens_matches = []
        if len(serpapi_matches) < limit:
            lens_matches = await self.search_patents_lens(query, limit - len(serpapi_matches))
        
        all_matches = serpapi_matches + lens_matches
        
        # Calculate similarity scores (simplified - in production would use embeddings)
        for match in all_matches:
            match.similarity_score = self._calculate_text_similarity(
                text_content,
                match.abstract
            )
        
        # Sort by similarity
        all_matches.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return {
            "total_matches": len(all_matches),
            "top_matches": all_matches[:5],
            "max_similarity": max([m.similarity_score for m in all_matches]) if all_matches else 0.0,
            "avg_similarity": sum([m.similarity_score for m in all_matches]) / len(all_matches) if all_matches else 0.0,
            "sources_used": ["SERPAPI"] if serpapi_matches else (["LENS.org"] if lens_matches else [])
        }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (word overlap).
        In production, this would use embedding similarity."""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

# Global instance
patent_service = PatentDataService()
