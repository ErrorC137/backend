"""USPTO Open Data Portal API client for prior art retrieval."""

import os
import httpx
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PatentReference:
    """USPTO patent reference data."""
    patent_id: str
    title: str
    abstract: str
    inventors: List[str]
    assignee: str
    filing_date: str
    publication_date: str
    claims: List[str]
    ipc_codes: List[str]
    cpc_codes: List[str]


class USPTOClient:
    """Client for USPTO Open Data Portal API."""
    
    BASE_URL = "https://developer.uspto.gov/ptab-api"
    PATENTS_URL = "https://api.patentsview.org/patents/query"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize USPTO client.
        
        Args:
            api_key: Optional API key for enhanced rate limits
        """
        self.api_key = api_key or os.getenv("USPTO_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_patents(
        self,
        query: str,
        limit: int = 10,
        fields: Optional[List[str]] = None
    ) -> List[PatentReference]:
        """
        Search patents using PatentsView API.
        
        Args:
            query: Search query (text, IPC code, etc.)
            limit: Maximum number of results
            fields: Specific fields to retrieve
            
        Returns:
            List of patent references
        """
        if fields is None:
            fields = [
                "patent_number",
                "patent_title",
                "patent_abstract",
                "inventors",
                "assignees",
                "app_date",
                "grant_date",
                "ipc",
                "cpc"
            ]
        
        try:
            payload = {
                "q": f'{{"patent_abstract":"{query}"}}',
                "f": fields,
                "o": {"page": 1, "per_page": limit}
            }
            
            response = await self.client.post(
                self.PATENTS_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            return self._parse_patents_response(data)
            
        except httpx.HTTPError as e:
            logger.error(f"USPTO API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching patents: {e}")
            return []
    
    def _parse_patents_response(self, data: Dict[str, Any]) -> List[PatentReference]:
        """Parse PatentsView API response."""
        patents = []
        
        for item in data.get("patents", []):
            try:
                patent = PatentReference(
                    patent_id=item.get("patent_number", ""),
                    title=item.get("patent_title", ""),
                    abstract=item.get("patent_abstract", ""),
                    inventors=[inv.get("inventor_name", "") for inv in item.get("inventors", [])],
                    assignee=item.get("assignees", [{}])[0].get("assignee_organization", ""),
                    filing_date=item.get("app_date", ""),
                    publication_date=item.get("grant_date", ""),
                    claims=[],  # Claims not available in basic PatentsView
                    ipc_codes=item.get("ipc", []),
                    cpc_codes=item.get("cpc", [])
                )
                patents.append(patent)
            except Exception as e:
                logger.warning(f"Error parsing patent: {e}")
                continue
        
        return patents
    
    async def get_patent_by_id(self, patent_id: str) -> Optional[PatentReference]:
        """
        Get detailed patent information by ID.
        
        Args:
            patent_id: Patent number or application number
            
        Returns:
            Patent reference or None if not found
        """
        try:
            payload = {
                "q": f'{{"patent_number":"{patent_id}"}}',
                "f": [
                    "patent_number",
                    "patent_title",
                    "patent_abstract",
                    "inventors",
                    "assignees",
                    "app_date",
                    "grant_date",
                    "ipc",
                    "cpc"
                ]
            }
            
            response = await self.client.post(
                self.PATENTS_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            patents = self._parse_patents_response(data)
            return patents[0] if patents else None
            
        except Exception as e:
            logger.error(f"Error getting patent {patent_id}: {e}")
            return None
    
    async def search_by_ipc(self, ipc_code: str, limit: int = 20) -> List[PatentReference]:
        """
        Search patents by IPC classification code.
        
        Args:
            ipc_code: IPC classification code (e.g., "B01J")
            limit: Maximum number of results
            
        Returns:
            List of patent references
        """
        try:
            payload = {
                "q": f'{{"ipc":"{ipc_code}"}}',
                "f": [
                    "patent_number",
                    "patent_title",
                    "patent_abstract",
                    "inventors",
                    "assignees",
                    "app_date",
                    "grant_date",
                    "ipc",
                    "cpc"
                ],
                "o": {"page": 1, "per_page": limit}
            }
            
            response = await self.client.post(
                self.PATENTS_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            return self._parse_patents_response(data)
            
        except Exception as e:
            logger.error(f"Error searching by IPC {ipc_code}: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global client instance
_uspto_client: Optional[USPTOClient] = None


def get_uspto_client() -> USPTOClient:
    """Get or create global USPTO client instance."""
    global _uspto_client
    if _uspto_client is None:
        _uspto_client = USPTOClient()
    return _uspto_client
