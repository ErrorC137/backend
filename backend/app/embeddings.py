"""OpenAI text-embedding-3-small embedding engine with cached vector index."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import httpx
import numpy as np

from app.patent_store import load_patent_corpus

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent / "data"
_CACHE_DIR = _DATA_DIR / "vector_cache"
_MODEL_NAME = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "50"))
_EMBEDDING_DIM = 1536

_patents: list[dict[str, Any]] = []
_embedding_matrix: np.ndarray | None = None
_ready = False


def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return vectors / norms


def _call_openai_embeddings(texts: list[str]) -> np.ndarray:
    if not _OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY environment variable is required for embeddings")

    cleaned = [(t[:8000] if t and t.strip() else " ") for t in texts]
    all_vectors: list[list[float]] = []

    with httpx.Client(timeout=120.0) as client:
        for i in range(0, len(cleaned), _BATCH_SIZE):
            batch = cleaned[i : i + _BATCH_SIZE]
            response = client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {_OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={"model": _MODEL_NAME, "input": batch},
            )
            response.raise_for_status()
            data = response.json()
            ordered = sorted(data["data"], key=lambda item: item["index"])
            all_vectors.extend(item["embedding"] for item in ordered)

    matrix = np.asarray(all_vectors, dtype=np.float32)
    return _normalize(matrix)


def encode_texts(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, _EMBEDDING_DIM), dtype=np.float32)
    return _call_openai_embeddings(texts)


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
        if cached_meta.get("model") == _MODEL_NAME and cached_meta.get("count") == len(_patents):
            _embedding_matrix = np.load(emb_path)
            _ready = True
            logger.info("Loaded cached patent index: %d patents", len(_patents))
            return {
                "status": "loaded_cache",
                "patent_count": len(_patents),
                "embedding_dimensions": int(_embedding_matrix.shape[1]),
                "model": _MODEL_NAME,
            }

    texts = [f"{p['title']}. {p['abstract']}" for p in _patents]
    logger.info("Encoding %d patents via OpenAI %s...", len(texts), _MODEL_NAME)
    _embedding_matrix = encode_texts(texts)
    np.save(emb_path, _embedding_matrix)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "model": _MODEL_NAME,
                "count": len(_patents),
                "embedding_dimensions": int(_embedding_matrix.shape[1]),
            },
            f,
        )

    _ready = True
    logger.info("Built patent index: %d x %d", *_embedding_matrix.shape)
    return {
        "status": "built",
        "patent_count": len(_patents),
        "embedding_dimensions": int(_embedding_matrix.shape[1]),
        "model": _MODEL_NAME,
    }


def ensure_index() -> None:
    if not _ready:
        build_index()


def index_status() -> dict[str, Any]:
    return {
        "ready": _ready,
        "patent_count": len(_patents),
        "model": _MODEL_NAME,
        "embedding_dimensions": int(_embedding_matrix.shape[1]) if _embedding_matrix is not None else _EMBEDDING_DIM,
        "provider": "openai",
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
