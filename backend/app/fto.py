"""Light FTO & claim overlap analysis."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx


def _tokenize_claim(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z]{4,}", text.lower())
    stop = {
        "wherein", "comprising", "method", "system", "device", "configured",
        "according", "present", "invention", "embodiment", "includes",
    }
    return {t for t in tokens if t not in stop}


def _rule_based_overlap(methodology: str, patent_claims: list[str]) -> list[dict[str, Any]]:
    method_tokens = _tokenize_claim(methodology)
    overlaps = []

    for i, claim in enumerate(patent_claims):
        claim_tokens = _tokenize_claim(claim)
        if not claim_tokens:
            continue
        intersection = method_tokens & claim_tokens
        overlap_ratio = len(intersection) / max(len(claim_tokens), 1)
        flagged_elements = sorted(intersection)[:8]
        overlaps.append(
            {
                "patent_index": i,
                "overlap_ratio": round(overlap_ratio, 4),
                "flagged_elements": flagged_elements,
                "structural_overlap": overlap_ratio >= 0.18,
            }
        )
    return overlaps


async def _llm_overlap(methodology: str, patents: list[dict[str, Any]]) -> list[dict[str, Any]] | None:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return None

    base_url = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")

    patent_block = "\n\n".join(
        f"Patent {p['patent_id']} claims: {p['claims']}" for p in patents[:3]
    )
    prompt = (
        "Compare the user methodology against each patent's independent claims. "
        "Return JSON array with objects: patent_id, overlap_elements (string[]), "
        "overlap_score (0-1). Only JSON, no markdown.\n\n"
        f"Methodology:\n{methodology[:3000]}\n\n{patent_block}"
    )

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a patent claim analyst. Output strict JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "results" in parsed:
                return parsed["results"]
            if isinstance(parsed, list):
                return parsed
            return parsed.get("overlaps", [])
    except Exception:
        return None


def _compute_risk(overlap_results: list[dict[str, Any]], top_matches: list[dict[str, Any]]) -> dict[str, Any]:
    flagged = [o for o in overlap_results if o.get("structural_overlap") or o.get("overlap_ratio", 0) >= 0.18]
    overlap_count = len(flagged)

    # R_fto scaled 0.0 to 0.50
    r_fto = min(0.50, overlap_count * 0.08 + sum(o.get("overlap_ratio", 0) for o in flagged) * 0.15)
    r_fto = round(r_fto, 4)

    risk_tier_pct = round(r_fto * 100 / 0.50, 1)
    high_risk_group = None
    if risk_tier_pct > 35 and top_matches:
        high_risk_group = top_matches[0].get("patent_id")

    overlap_matrix = []
    for i, match in enumerate(top_matches[:10]):
        overlap = next((o for o in overlap_results if o.get("patent_index") == i), None)
        overlap_matrix.append(
            {
                "patent_id": match["patent_id"],
                "title": match["title"],
                "cosine_similarity": match["cosine_similarity"],
                "overlap_ratio": overlap.get("overlap_ratio", 0) if overlap else 0,
                "flagged_elements": overlap.get("flagged_elements", []) if overlap else [],
                "structural_overlap": overlap.get("structural_overlap", False) if overlap else False,
            }
        )

    return {
        "r_fto": r_fto,
        "risk_tier_pct": risk_tier_pct,
        "high_risk_patent_group": high_risk_group,
        "expert_consultation_required": risk_tier_pct > 35,
        "overlap_matrix": overlap_matrix,
        "flagged_patent_count": overlap_count,
    }


async def analyze_fto(methodology: str, top_matches: list[dict[str, Any]]) -> dict[str, Any]:
    claims = [m["claims"] for m in top_matches[:10]]
    llm_result = await _llm_overlap(methodology, top_matches[:3])

    if llm_result:
        overlap_results = []
        for i, item in enumerate(llm_result):
            score = float(item.get("overlap_score", 0))
            overlap_results.append(
                {
                    "patent_index": i,
                    "overlap_ratio": score,
                    "flagged_elements": item.get("overlap_elements", []),
                    "structural_overlap": score >= 0.18,
                }
            )
        source = "llm"
    else:
        overlap_results = _rule_based_overlap(methodology, claims)
        source = "rule_based_token_matching"

    risk = _compute_risk(overlap_results, top_matches)
    risk["analysis_source"] = source
    return risk
