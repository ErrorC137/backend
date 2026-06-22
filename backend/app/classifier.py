"""Semantic IPC/CPC & NACE classification using OpenAI embeddings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from app.embeddings import encode_texts


_DATA_DIR = Path(__file__).parent / "data"


def _load_json(name: str) -> Any:
    with open(_DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def classify_document(text: str) -> dict[str, Any]:
    keywords_map = _load_json("classification_keywords.json")
    baselines = _load_json("industry_baselines.json")

    ipc_codes = list(keywords_map.keys())
    sector_descriptions = [
        f"{code}: {baselines.get(code, baselines['DEFAULT'])['sector_name']}. "
        f"Keywords: {', '.join(keywords_map[code])}"
        for code in ipc_codes
    ]

    vectors = encode_texts(sector_descriptions + [text[:4000]])
    doc_vec = vectors[-1]
    code_vecs = vectors[:-1]
    scores = code_vecs @ doc_vec

    best_idx = int(np.argmax(scores))
    best_ipc = ipc_codes[best_idx]
    confidence = float(scores[best_idx])

    baseline = baselines.get(best_ipc, baselines["DEFAULT"])
    cpc = f"{best_ipc}00/00"

    return {
        "ipc_primary": best_ipc,
        "cpc_primary": cpc,
        "nace_code": baseline["nace"],
        "sector_name": baseline["sector_name"],
        "classification_confidence": round(confidence, 4),
        "all_scores": {
            ipc_codes[i]: round(float(scores[i]), 4) for i in range(len(ipc_codes))
        },
        "classifier_model": "OpenAI text-embedding-3-small semantic sector matching",
    }
