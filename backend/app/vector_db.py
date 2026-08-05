"""Enterprise vector database integration for patent similarity search.
Supports Pinecone and Qdrant for high-fidelity semantic search."""

import os
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VectorSearchResult:
    """Result from vector similarity search."""
    patent_id: str
    title: str
    abstract: str
    similarity_score: float
    metadata: Dict[str, Any]


class VectorDatabaseClient:
    """Abstract base class for vector database clients."""
    
    async def index_patents(self, patents: List[Dict[str, Any]]) -> bool:
        """Index patent documents for similarity search."""
        raise NotImplementedError
    
    async def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search for similar patents by embedding."""
        raise NotImplementedError
    
    async def delete_index(self) -> bool:
        """Delete the entire patent index."""
        raise NotImplementedError


class PineconeClient(VectorDatabaseClient):
    """Pinecone vector database client for patent similarity search."""
    
    def __init__(self, api_key: Optional[str] = None, index_name: str = "matdao-patents"):
        """
        Initialize Pinecone client.
        
        Args:
            api_key: Pinecone API key
            index_name: Name of the Pinecone index
        """
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.index_name = index_name
        self._client = None
        self._index = None
        self._initialized = False
    
    def _initialize(self):
        """Initialize Pinecone client and index."""
        if self._initialized:
            return
        
        try:
            import pinecone
            pinecone.init(api_key=self.api_key)
            self._client = pinecone
            
            # Check if index exists, create if not
            if self.index_name not in self._client.list_indexes():
                self._client.create_index(
                    name=self.index_name,
                    dimension=768,  # Standard embedding dimension
                    metric="cosine",
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": "us-east-1"
                        }
                    }
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            
            self._index = self._client.Index(self.index_name)
            self._initialized = True
            logger.info("Pinecone client initialized successfully")
            
        except ImportError:
            logger.error("pinecone-client not installed. Install with: pip install pinecone-client")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    async def index_patents(self, patents: List[Dict[str, Any]]) -> bool:
        """Index patent documents in Pinecone."""
        self._initialize()
        
        try:
            # Prepare vectors for upsert
            vectors = []
            for patent in patents:
                patent_id = patent.get("patent_id", "")
                embedding = patent.get("embedding", [])
                
                if not embedding:
                    logger.warning(f"No embedding for patent {patent_id}, skipping")
                    continue
                
                vectors.append({
                    "id": patent_id,
                    "values": embedding,
                    "metadata": {
                        "title": patent.get("title", ""),
                        "abstract": patent.get("abstract", ""),
                        "assignee": patent.get("assignee", ""),
                        "ipc_codes": patent.get("ipc_codes", []),
                        "cpc_codes": patent.get("cpc_codes", [])
                    }
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self._index.upsert(vectors=batch)
            
            logger.info(f"Indexed {len(vectors)} patents in Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index patents in Pinecone: {e}")
            return False
    
    async def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search for similar patents in Pinecone."""
        self._initialize()
        
        try:
            query_filter = None
            if filters:
                # Convert filters to Pinecone filter format
                query_filter = self._convert_filters(filters)
            
            results = self._index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=query_filter,
                include_metadata=True
            )
            
            search_results = []
            for match in results.matches:
                search_results.append(VectorSearchResult(
                    patent_id=match.id,
                    title=match.metadata.get("title", ""),
                    abstract=match.metadata.get("abstract", ""),
                    similarity_score=match.score,
                    metadata=match.metadata
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search Pinecone: {e}")
            return []
    
    def _convert_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Convert filter dict to Pinecone filter format."""
        pinecone_filters = {}
        for key, value in filters.items():
            if isinstance(value, list):
                pinecone_filters[key] = {"$in": value}
            else:
                pinecone_filters[key] = value
        return pinecone_filters
    
    async def delete_index(self) -> bool:
        """Delete the Pinecone index."""
        self._initialize()
        
        try:
            self._client.delete_index(self.index_name)
            logger.info(f"Deleted Pinecone index: {self.index_name}")
            self._initialized = False
            return True
        except Exception as e:
            logger.error(f"Failed to delete Pinecone index: {e}")
            return False


class QdrantClient(VectorDatabaseClient):
    """Qdrant vector database client for patent similarity search."""
    
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None, collection_name: str = "matdao-patents"):
        """
        Initialize Qdrant client.
        
        Args:
            url: Qdrant server URL
            api_key: Qdrant API key
            collection_name: Name of the Qdrant collection
        """
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name
        self._client = None
        self._initialized = False
    
    def _initialize(self):
        """Initialize Qdrant client and collection."""
        if self._initialized:
            return
        
        try:
            from qdrant_client import QdrantClient
            self._client = QdrantClient(url=self.url, api_key=self.api_key)
            
            # Check if collection exists, create if not
            collections = self._client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self._client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={
                        "size": 768,
                        "distance": "Cosine"
                    }
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            
            self._initialized = True
            logger.info("Qdrant client initialized successfully")
            
        except ImportError:
            logger.error("qdrant-client not installed. Install with: pip install qdrant-client")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {e}")
            raise
    
    async def index_patents(self, patents: List[Dict[str, Any]]) -> bool:
        """Index patent documents in Qdrant."""
        self._initialize()
        
        try:
            from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
            
            points = []
            for patent in patents:
                patent_id = patent.get("patent_id", "")
                embedding = patent.get("embedding", [])
                
                if not embedding:
                    logger.warning(f"No embedding for patent {patent_id}, skipping")
                    continue
                
                points.append(PointStruct(
                    id=hash(patent_id) % (2**32),  # Use hash as integer ID
                    vector=embedding,
                    payload={
                        "patent_id": patent_id,
                        "title": patent.get("title", ""),
                        "abstract": patent.get("abstract", ""),
                        "assignee": patent.get("assignee", ""),
                        "ipc_codes": patent.get("ipc_codes", []),
                        "cpc_codes": patent.get("cpc_codes", [])
                    }
                ))
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self._client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
            
            logger.info(f"Indexed {len(points)} patents in Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index patents in Qdrant: {e}")
            return False
    
    async def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search for similar patents in Qdrant."""
        self._initialize()
        
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            query_filter = None
            if filters:
                # Convert filters to Qdrant filter format
                conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        conditions.append(
                            FieldCondition(key=key, match=MatchValue(any=value))
                        )
                    else:
                        conditions.append(
                            FieldCondition(key=key, match=MatchValue(value=value))
                        )
                query_filter = Filter(must=conditions)
            
            results = self._client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=query_filter
            )
            
            search_results = []
            for result in results:
                search_results.append(VectorSearchResult(
                    patent_id=result.payload.get("patent_id", str(result.id)),
                    title=result.payload.get("title", ""),
                    abstract=result.payload.get("abstract", ""),
                    similarity_score=result.score,
                    metadata=result.payload
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search Qdrant: {e}")
            return []
    
    async def delete_index(self) -> bool:
        """Delete the Qdrant collection."""
        self._initialize()
        
        try:
            self._client.delete_collection(self.collection_name)
            logger.info(f"Deleted Qdrant collection: {self.collection_name}")
            self._initialized = False
            return True
        except Exception as e:
            logger.error(f"Failed to delete Qdrant collection: {e}")
            return False


def get_vector_client(
    provider: str = "pinecone",
    **kwargs
) -> VectorDatabaseClient:
    """
    Get vector database client instance.
    
    Args:
        provider: Vector database provider ("pinecone" or "qdrant")
        **kwargs: Provider-specific configuration
        
    Returns:
        Vector database client instance
    """
    provider = provider.lower()
    
    if provider == "pinecone":
        return PineconeClient(**kwargs)
    elif provider == "qdrant":
        return QdrantClient(**kwargs)
    else:
        raise ValueError(f"Unsupported vector database provider: {provider}")


# Global client instance
_vector_client: Optional[VectorDatabaseClient] = None


def get_global_vector_client() -> Optional[VectorDatabaseClient]:
    """Get or create global vector database client instance."""
    global _vector_client
    if _vector_client is None:
        # Try Pinecone first, fall back to Qdrant
        try:
            _vector_client = get_vector_client(provider="pinecone")
        except Exception:
            logger.warning("Pinecone initialization failed, trying Qdrant")
            try:
                _vector_client = get_vector_client(provider="qdrant")
            except Exception:
                logger.error("Failed to initialize any vector database client")
    return _vector_client
