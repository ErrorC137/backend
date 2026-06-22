"""Vector similarity engine using OpenAI embeddings."""

from __future__ import annotations

from typing import Any

from app.embeddings import index_status, search_similar


def compute_originality(text: str, top_k: int = 10) -> dict[str, Any]:
    matches, max_sim, _ = search_similar(text, top_k=top_k)

    # Higher gap from prior art => higher originality premium (0.0 to 0.30)
    originality_score = round(max(0.0, min(0.30, 0.30 * (1.0 - max_sim))), 4)
    status = index_status()

    return {
        "max_cosine_similarity": round(max_sim, 4),
        "originality_premium_s": originality_score,
        "top_matches": matches,
        "embedding_dimensions": status["embedding_dimensions"],
        "embedding_model": status["model"],
        "patent_corpus_size": status["patent_count"],
    }
