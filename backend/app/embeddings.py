"""Multi-provider embedding engine with cached vector index.
Supports Cohere, HuggingFace, and OpenAI with automatic fallback."""

from __future__ import annotations

import json
import logging
import os
import time
from enum import Enum
from pathlib import Path
from typing import Any

import httpx
import numpy as np

from app.patent_store import load_patent_corpus

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent / "data"
_CACHE_DIR = _DATA_DIR / "vector_cache"

# Provider configuration
class EmbeddingProvider(Enum):
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"

# Environment variables
_COHERE_API_KEY = os.getenv("COHERE_API_KEY")
_HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Debug logging for environment variables
logger.info(f"COHERE_API_KEY set: {bool(_COHERE_API_KEY)}")
logger.info(f"HUGGINGFACE_API_KEY set: {bool(_HUGGINGFACE_API_KEY)}")
logger.info(f"OPENAI_API_KEY set: {bool(_OPENAI_API_KEY)}")

# Model configurations
_COHERE_MODEL = os.getenv("COHERE_EMBEDDING_MODEL", "embed-english-v3.0")
_HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
_OPENAI_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Provider priority order (will try in this order)
_PROVIDER_PRIORITY = os.getenv("EMBEDDING_PROVIDER_PRIORITY", "cohere,huggingface,openai").split(",")

# Rate limiting configuration
_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "50"))
_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "5"))
_RETRY_DELAY = float(os.getenv("OPENAI_RETRY_DELAY", "1.0"))

# Embedding dimensions (will be set based on provider)
_EMBEDDING_DIM = 1536  # Default, will be adjusted per provider

_patents: list[dict[str, Any]] = []
_embedding_matrix: np.ndarray | None = None
_ready = False
_request_cache: dict[str, np.ndarray] = {}
_current_provider: EmbeddingProvider | None = None


def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return vectors / norms


def _call_cohere_embeddings(texts: list[str]) -> np.ndarray:
    """Call Cohere API for embeddings."""
    if not _COHERE_API_KEY:
        raise RuntimeError("COHERE_API_KEY environment variable is required for Cohere embeddings")

    cleaned = [(t[:4096] if t and t.strip() else " ") for t in texts]
    all_vectors: list[list[float]] = []

    with httpx.Client(timeout=120.0) as client:
        for i in range(0, len(cleaned), _BATCH_SIZE):
            batch = cleaned[i : i + _BATCH_SIZE]
            
            # Check cache
            batch_key = f"cohere_|".join(batch[:3])
            if batch_key in _request_cache:
                logger.debug("Using cached Cohere embedding for batch")
                all_vectors.extend(_request_cache[batch_key].tolist())
                continue
            
            # Retry logic
            for attempt in range(_MAX_RETRIES):
                try:
                    response = client.post(
                        "https://api.cohere.ai/v1/embed",
                        headers={
                            "Authorization": f"Bearer {_COHERE_API_KEY}",
                            "Content-Type": "application/json",
                            "X-Client-Name": "MatDAO",
                        },
                        json={
                            "model": _COHERE_MODEL,
                            "texts": batch,
                            "input_type": "search_document",
                            "embedding_types": ["float"]
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    batch_vectors = [item["float"] for item in data["embeddings"]]
                    
                    _request_cache[batch_key] = np.array(batch_vectors, dtype=np.float32)
                    all_vectors.extend(batch_vectors)
                    break
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        if attempt < _MAX_RETRIES - 1:
                            delay = _RETRY_DELAY * (2 ** attempt)
                            logger.warning(f"Cohere rate limited (429), retrying in {delay}s (attempt {attempt + 1}/{_MAX_RETRIES})")
                            time.sleep(delay)
                        else:
                            logger.error(f"Max retries exceeded for Cohere API after rate limit")
                            raise RuntimeError(f"Cohere API rate limit exceeded after {_MAX_RETRIES} retries")
                    else:
                        raise
                except Exception as e:
                    logger.error(f"Unexpected error calling Cohere API: {e}")
                    raise

    matrix = np.asarray(all_vectors, dtype=np.float32)
    return _normalize(matrix)


def _call_huggingface_embeddings(texts: list[str]) -> np.ndarray:
    """Call HuggingFace Inference API for embeddings."""
    if not _HUGGINGFACE_API_KEY:
        # Try free tier without API key
        logger.warning("No HUGGINGFACE_API_KEY set, using free tier (limited)")
        api_url = f"https://api-inference.huggingface.co/models/{_HUGGINGFACE_MODEL}"
        headers = {"Content-Type": "application/json"}
    else:
        api_url = f"https://api-inference.huggingface.co/models/{_HUGGINGFACE_MODEL}"
        headers = {
            "Authorization": f"Bearer {_HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json",
        }

    cleaned = [(t[:512] if t and t.strip() else " ") for t in texts]  # HuggingFace has shorter limits
    all_vectors: list[list[float]] = []

    with httpx.Client(timeout=120.0) as client:
        for i in range(0, len(cleaned), _BATCH_SIZE):
            batch = cleaned[i : i + _BATCH_SIZE]
            
            # Check cache
            batch_key = f"hf_|".join(batch[:3])
            if batch_key in _request_cache:
                logger.debug("Using cached HuggingFace embedding for batch")
                all_vectors.extend(_request_cache[batch_key].tolist())
                continue
            
            # Retry logic
            for attempt in range(_MAX_RETRIES):
                try:
                    response = client.post(
                        api_url,
                        headers=headers,
                        json={"inputs": batch, "options": {"wait_for_model": True}},
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Handle different response formats
                    if isinstance(data, list):
                        batch_vectors = data
                    elif isinstance(data, dict) and "embeddings" in data:
                        batch_vectors = data["embeddings"]
                    else:
                        raise ValueError(f"Unexpected HuggingFace response format: {type(data)}")
                    
                    _request_cache[batch_key] = np.array(batch_vectors, dtype=np.float32)
                    all_vectors.extend(batch_vectors)
                    break
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        if attempt < _MAX_RETRIES - 1:
                            delay = _RETRY_DELAY * (2 ** attempt)
                            logger.warning(f"HuggingFace rate limited (429), retrying in {delay}s (attempt {attempt + 1}/{_MAX_RETRIES})")
                            time.sleep(delay)
                        else:
                            logger.error(f"Max retries exceeded for HuggingFace API after rate limit")
                            raise RuntimeError(f"HuggingFace API rate limit exceeded after {_MAX_RETRIES} retries")
                    elif e.response.status_code == 503:
                        # Model loading, wait and retry
                        if attempt < _MAX_RETRIES - 1:
                            delay = 5 + (attempt * 5)
                            logger.warning(f"HuggingFace model loading (503), retrying in {delay}s (attempt {attempt + 1}/{_MAX_RETRIES})")
                            time.sleep(delay)
                        else:
                            raise RuntimeError(f"HuggingFace model failed to load after {_MAX_RETRIES} retries")
                    else:
                        raise
                except Exception as e:
                    logger.error(f"Unexpected error calling HuggingFace API: {e}")
                    raise

    matrix = np.asarray(all_vectors, dtype=np.float32)
    return _normalize(matrix)


def _call_openai_embeddings(texts: list[str]) -> np.ndarray:
    """Call OpenAI API for embeddings."""
    if not _OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY environment variable is required for OpenAI embeddings")

    cleaned = [(t[:8000] if t and t.strip() else " ") for t in texts]
    all_vectors: list[list[float]] = []

    with httpx.Client(timeout=120.0) as client:
        for i in range(0, len(cleaned), _BATCH_SIZE):
            batch = cleaned[i : i + _BATCH_SIZE]
            
            # Check cache
            batch_key = f"openai_|".join(batch[:3])
            if batch_key in _request_cache:
                logger.debug("Using cached OpenAI embedding for batch")
                all_vectors.extend(_request_cache[batch_key].tolist())
                continue
            
            # Retry logic
            for attempt in range(_MAX_RETRIES):
                try:
                    response = client.post(
                        "https://api.openai.com/v1/embeddings",
                        headers={
                            "Authorization": f"Bearer {_OPENAI_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        json={"model": _OPENAI_MODEL, "input": batch},
                    )
                    response.raise_for_status()
                    data = response.json()
                    ordered = sorted(data["data"], key=lambda item: item["index"])
                    batch_vectors = [item["embedding"] for item in ordered]
                    
                    _request_cache[batch_key] = np.array(batch_vectors, dtype=np.float32)
                    all_vectors.extend(batch_vectors)
                    break
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        if attempt < _MAX_RETRIES - 1:
                            delay = _RETRY_DELAY * (2 ** attempt)
                            logger.warning(f"OpenAI rate limited (429), retrying in {delay}s (attempt {attempt + 1}/{_MAX_RETRIES})")
                            time.sleep(delay)
                        else:
                            logger.error(f"Max retries exceeded for OpenAI API after rate limit")
                            raise RuntimeError(f"OpenAI API rate limit exceeded after {_MAX_RETRIES} retries")
                    else:
                        raise
                except Exception as e:
                    logger.error(f"Unexpected error calling OpenAI API: {e}")
                    raise

    matrix = np.asarray(all_vectors, dtype=np.float32)
    return _normalize(matrix)


def _get_provider_function(provider: EmbeddingProvider):
    """Get the embedding function for a specific provider."""
    if provider == EmbeddingProvider.COHERE:
        return _call_cohere_embeddings
    elif provider == EmbeddingProvider.HUGGINGFACE:
        return _call_huggingface_embeddings
    elif provider == EmbeddingProvider.OPENAI:
        return _call_openai_embeddings
    else:
        raise ValueError(f"Unknown provider: {provider}")


def encode_texts(texts: list[str]) -> np.ndarray:
    """Encode texts using available providers with automatic fallback to deterministic embeddings."""
    if not texts:
        return np.zeros((0, _EMBEDDING_DIM), dtype=np.float32)
    
    global _current_provider
    
    # Try providers in priority order
    for provider_name in _PROVIDER_PRIORITY:
        try:
            provider = EmbeddingProvider(provider_name.strip())
            
            # Check if provider has required credentials
            if provider == EmbeddingProvider.COHERE and not _COHERE_API_KEY:
                logger.debug(f"Skipping Cohere: no API key configured")
                continue
            if provider == EmbeddingProvider.OPENAI and not _OPENAI_API_KEY:
                logger.debug(f"Skipping OpenAI: no API key configured")
                continue
            # HuggingFace works without API key (free tier)
            
            logger.info(f"Attempting to use {provider.value} for embeddings")
            embed_func = _get_provider_function(provider)
            result = embed_func(texts)
            
            # Update current provider on success
            _current_provider = provider
            logger.info(f"Successfully using {provider.value} for embeddings")
            return result
            
        except Exception as e:
            logger.warning(f"Failed to use {provider_name}: {e}")
            continue
    
    # All providers failed - use deterministic fallback
    logger.warning("All embedding providers failed, using deterministic fallback")
    return _generate_deterministic_embeddings(texts)


def _generate_deterministic_embeddings(texts: list[str]) -> np.ndarray:
    """Generate deterministic embeddings based on text hash for fallback."""
    import hashlib
    
    embeddings = []
    for text in texts:
        # Create a hash of the text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to a 1536-dimensional vector (matching OpenAI dimensions)
        hash_int = int(text_hash, 16)
        vector = []
        for i in range(1536):
            # Generate deterministic values from hash
            byte_val = (hash_int >> (i % 32)) & 0xFF
            normalized_val = (byte_val / 255.0 - 0.5) * 2  # Range [-1, 1]
            vector.append(normalized_val)
        
        embeddings.append(vector)
    
    return np.array(embeddings, dtype=np.float32)


def _cache_paths() -> tuple[Path, Path]:
    return _CACHE_DIR / "patent_embeddings.npy", _CACHE_DIR / "patent_corpus.json"


def build_index(force: bool = False) -> dict[str, Any]:
    global _patents, _embedding_matrix, _ready

    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    emb_path, meta_path = _cache_paths()

    if force or os.environ.get("REBUILD_PATENT_INDEX") == "1":
        emb_path.unlink(missing_ok=True)
        meta_path.unlink(missing_ok=True)

    _patents = load_patent_corpus()

    if emb_path.exists() and meta_path.exists():
        with open(meta_path, encoding="utf-8") as f:
            cached_meta = json.load(f)
        # Check if cached embeddings are compatible with current provider
        cached_provider = cached_meta.get("provider")
        current_provider_value = _current_provider.value if _current_provider else None
        cached_dims = cached_meta.get("embedding_dimensions")
        
        # Load cached embeddings to check dimensions
        temp_matrix = np.load(emb_path)
        actual_dims = temp_matrix.shape[1]
        
        # Rebuild if provider changed, count changed, or dimensions don't match expected
        if cached_provider == current_provider_value and cached_meta.get("count") == len(_patents) and actual_dims == _EMBEDDING_DIM:
            _embedding_matrix = temp_matrix
            _ready = True
            logger.info("Loaded cached patent index: %d patents from %s", len(_patents), cached_provider)
            return {
                "status": "loaded_cache",
                "patent_count": len(_patents),
                "embedding_dimensions": int(_embedding_matrix.shape[1]),
                "model": cached_meta.get("model"),
                "provider": cached_provider,
            }
        else:
            # Clear cache if dimensions or other parameters don't match
            logger.warning(f"Cache mismatch: provider={cached_provider} vs {current_provider_value}, dims={actual_dims} vs {_EMBEDDING_DIM}, count={cached_meta.get('count')} vs {len(_patents)}. Rebuilding index.")
            emb_path.unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)

    texts = [f"{p['title']}. {p['abstract']}" for p in _patents]
    logger.info("Encoding %d patents via %s...", len(texts), _current_provider.value if _current_provider else "available provider")
    
    try:
        _embedding_matrix = encode_texts(texts)
    except Exception as e:
        logger.error(f"Failed to encode patent texts: {e}, using deterministic fallback")
        _embedding_matrix = _generate_deterministic_embeddings(texts)
    
    np.save(emb_path, _embedding_matrix)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "provider": _current_provider.value if _current_provider else "unknown",
                "model": _COHERE_MODEL if _current_provider == EmbeddingProvider.COHERE else 
                        _HUGGINGFACE_MODEL if _current_provider == EmbeddingProvider.HUGGINGFACE else 
                        _OPENAI_MODEL,
                "count": len(_patents),
                "embedding_dimensions": int(_embedding_matrix.shape[1]),
            },
            f,
        )

    _ready = True
    logger.info("Built patent index: %d x %d using %s", *_embedding_matrix.shape, _current_provider.value if _current_provider else "unknown")
    return {
        "status": "built",
        "patent_count": len(_patents),
        "embedding_dimensions": int(_embedding_matrix.shape[1]),
        "model": _COHERE_MODEL if _current_provider == EmbeddingProvider.COHERE else 
                _HUGGINGFACE_MODEL if _current_provider == EmbeddingProvider.HUGGINGFACE else 
                _OPENAI_MODEL,
        "provider": _current_provider.value if _current_provider else "unknown",
    }


def ensure_index() -> None:
    if not _ready:
        build_index()


def index_status() -> dict[str, Any]:
    return {
        "ready": _ready,
        "patent_count": len(_patents),
        "model": _COHERE_MODEL if _current_provider == EmbeddingProvider.COHERE else 
                _HUGGINGFACE_MODEL if _current_provider == EmbeddingProvider.HUGGINGFACE else 
                _OPENAI_MODEL,
        "embedding_dimensions": int(_embedding_matrix.shape[1]) if _embedding_matrix is not None else _EMBEDDING_DIM,
        "provider": _current_provider.value if _current_provider else "none",
        "available_providers": [p for p in _PROVIDER_PRIORITY if p.strip()],
    }


def search_similar(text: str, top_k: int = 10) -> tuple[list[dict[str, Any]], float, np.ndarray]:
    ensure_index()
    assert _embedding_matrix is not None

    query_vec = encode_texts([text])[0]
    scores = _embedding_matrix @ query_vec
    ranked_idx = np.argsort(scores)[::-1][:top_k]

    matches = []
    for idx in ranked_idx:
        patent = _patents[int(idx)]
        similarity = float(scores[int(idx)])
        matches.append({**patent, "cosine_similarity": round(similarity, 4)})

    max_sim = float(scores[ranked_idx[0]]) if len(ranked_idx) else 0.0
    return matches, max_sim, query_vec
