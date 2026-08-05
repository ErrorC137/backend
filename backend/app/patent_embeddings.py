"""Patent-specific embedding models for semantic similarity search.
Supports PatentSBERTa and other specialized patent embedding models."""

import os
import logging
from typing import Any, Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class PatentEmbeddingModel:
    """Base class for patent embedding models."""
    
    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the embedding model."""
        raise NotImplementedError
    
    def encode(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Encode texts to embeddings."""
        raise NotImplementedError
    
    def encode_single(self, text: str) -> List[float]:
        """Encode a single text to embedding."""
        embeddings = self.encode([text])
        return embeddings[0] if embeddings else []


class PatentSBERTaModel(PatentEmbeddingModel):
    """PatentSBERTa model for patent-specific embeddings."""
    
    def __init__(self, model_name: str = "anferico/bert-for-patents"):
        """
        Initialize PatentSBERTa model.
        
        Args:
            model_name: HuggingFace model name for patent embeddings
        """
        super().__init__()
        self.model_name = model_name
    
    def initialize(self):
        """Initialize the PatentSBERTa model."""
        if self._initialized:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading PatentSBERTa model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            self._initialized = True
            logger.info("PatentSBERTa model loaded successfully")
            
        except ImportError:
            logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load PatentSBERTa model: {e}")
            raise
    
    def encode(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Encode texts using PatentSBERTa."""
        self.initialize()
        
        try:
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            return []


class MPNetPatentModel(PatentEmbeddingModel):
    """MPNet-based model for patent embeddings."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        """
        Initialize MPNet model.
        
        Args:
            model_name: HuggingFace model name
        """
        super().__init__()
        self.model_name = model_name
    
    def initialize(self):
        """Initialize the MPNet model."""
        if self._initialized:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading MPNet model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            self._initialized = True
            logger.info("MPNet model loaded successfully")
            
        except ImportError:
            logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load MPNet model: {e}")
            raise
    
    def encode(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Encode texts using MPNet."""
        self.initialize()
        
        try:
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            return []


class PatentEmbeddingService:
    """Service for patent embedding generation and similarity calculation."""
    
    def __init__(self, model_type: str = "patentsberta"):
        """
        Initialize patent embedding service.
        
        Args:
            model_type: Type of embedding model ("patentsberta" or "mpnet")
        """
        self.model_type = model_type.lower()
        self._model: Optional[PatentEmbeddingModel] = None
    
    def _get_model(self) -> PatentEmbeddingModel:
        """Get or create embedding model instance."""
        if self._model is None:
            if self.model_type == "patentsberta":
                self._model = PatentSBERTaModel()
            elif self.model_type == "mpnet":
                self._model = MPNetPatentModel()
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
        return self._model
    
    def encode_patent_text(
        self,
        title: str,
        abstract: str,
        claims: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> List[float]:
        """
        Encode patent document to embedding.
        
        Args:
            title: Patent title
            abstract: Patent abstract
            claims: List of patent claims
            description: Detailed description
            
        Returns:
            Embedding vector
        """
        # Combine relevant patent text fields
        text_parts = [title, abstract]
        
        if claims:
            text_parts.extend(claims[:5])  # Limit to first 5 claims
        
        if description:
            text_parts.append(description[:1000])  # Limit description length
        
        combined_text = " ".join([t for t in text_parts if t])
        
        model = self._get_model()
        return model.encode_single(combined_text)
    
    def encode_batch_patents(
        self,
        patents: List[Dict[str, Any]]
    ) -> List[List[float]]:
        """
        Encode batch of patents to embeddings.
        
        Args:
            patents: List of patent dictionaries with title, abstract, etc.
            
        Returns:
            List of embedding vectors
        """
        texts = []
        for patent in patents:
            title = patent.get("title", "")
            abstract = patent.get("abstract", "")
            claims = patent.get("claims", [])
            description = patent.get("description", "")
            
            text_parts = [title, abstract]
            if claims:
                text_parts.extend(claims[:5])
            if description:
                text_parts.append(description[:1000])
            
            combined_text = " ".join([t for t in text_parts if t])
            texts.append(combined_text)
        
        model = self._get_model()
        return model.encode(texts)
    
    def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def find_most_similar(
        self,
        query_embedding: List[float],
        patent_embeddings: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find most similar patents to query embedding.
        
        Args:
            query_embedding: Query embedding vector
            patent_embeddings: List of dicts with 'embedding' and patent data
            top_k: Number of top results to return
            
        Returns:
            List of similar patents with similarity scores
        """
        similarities = []
        
        for patent_data in patent_embeddings:
            patent_embedding = patent_data.get("embedding", [])
            if not patent_embedding:
                continue
            
            similarity = self.calculate_similarity(query_embedding, patent_embedding)
            
            similarities.append({
                "patent": patent_data,
                "similarity_score": similarity
            })
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similarities[:top_k]


# Global service instance
_patent_embedding_service: Optional[PatentEmbeddingService] = None


def get_patent_embedding_service(
    model_type: str = "patentsberta"
) -> PatentEmbeddingService:
    """
    Get or create global patent embedding service instance.
    
    Args:
        model_type: Type of embedding model
        
    Returns:
        Patent embedding service instance
    """
    global _patent_embedding_service
    if _patent_embedding_service is None:
        _patent_embedding_service = PatentEmbeddingService(model_type=model_type)
    return _patent_embedding_service
