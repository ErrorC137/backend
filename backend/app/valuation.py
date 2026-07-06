"""Deterministic financial valuation engine with full audit trail."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_DATA_DIR = Path(__file__).parent / "data"


def _audit_entry(
    entry_id: str,
    label: str,
    amount_usd: float,
    formula: str,
    explanation: str,
    steps: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    *,
    parent_id: str | None = None,
) -> dict[str, Any]:
    return {
        "id": entry_id,
        "parent_id": parent_id,
        "label": label,
        "amount_usd": round(amount_usd, 2),
        "formula": formula,
        "explanation": explanation,
        "calculation_steps": steps,
        "evidence": evidence,
    }


def calculate_valuation(
    ipc_code: str,
    originality_premium: float,
    r_fto: float,
    expert_consultation_required: bool,
    *,
    classification: dict[str, Any] | None = None,
    originality: dict[str, Any] | None = None,
    fto: dict[str, Any] | None = None,
) -> dict[str, Any]:
    with open(_DATA_DIR / "industry_baselines.json", encoding="utf-8") as f:
        baselines = json.load(f)

    classification = classification or {}
    originality = originality or {}
    fto = fto or {}

    baseline = baselines.get(ipc_code, baselines["DEFAULT"])
    v_baseline = baseline["v_baseline_usd"]
    floor_cost = baseline["floor_cost_usd"]

    s_originality = max(0.0, min(0.30, originality_premium))
    r_fto_clamped = max(0.0, min(0.50, r_fto))
    max_sim = originality.get("max_cosine_similarity", 0.0)
    top_match = (originality.get("top_matches") or [{}])[0]

    v_after_originality = v_baseline * (1 + s_originality)
    v_after_fto = v_after_originality * (1 - r_fto_clamped)
    expert_cap_factor = 0.85 if expert_consultation_required else 1.0
    v_target = v_after_fto * expert_cap_factor
    tokenization_anchor = v_target * 0.70
    valuation_floor = max(floor_cost, v_target * 0.35)

    audit_trail: list[dict[str, Any]] = []

    audit_trail.append(
        _audit_entry(
            "v_baseline",
            "Sector Baseline (V_baseline)",
            v_baseline,
            "Industry benchmark for detected IPC/CPC sector",
            (
                f"The baseline reflects typical M&A/licensing exit values for "
                f"{baseline['sector_name']} (IPC {ipc_code}, NACE {baseline['nace']}). "
                f"Sourced from open deep-tech valuation benchmarks in industry_baselines.json."
            ),
            [
                {"step": 1, "operation": "IPC classification", "value": ipc_code},
                {"step": 2, "operation": "Sector lookup", "value": baseline["sector_name"]},
                {"step": 3, "operation": "Baseline USD", "value": v_baseline},
            ],
            [
                {"type": "ipc_classification", "ref": ipc_code, "detail": classification.get("sector_name", "")},
                {"type": "nace_code", "ref": baseline["nace"], "detail": "Statistical sector mapping"},
                {"type": "data_source", "ref": "industry_baselines.json", "detail": "Hardcoded open benchmark"},
            ],
        )
    )

    audit_trail.append(
        _audit_entry(
            "s_originality_premium",
            "Originality Premium Multiplier",
            v_after_originality - v_baseline,
            f"V_baseline × S_originality = {v_baseline:,.0f} × {s_originality:.4f}",
            (
                f"Semantic distance from prior art drives novelty premium. Max patent similarity was "
                f"{max_sim * 100:.1f}% (OpenAI embeddings vs {originality.get('patent_corpus_size', 'N/A')} patents). "
                f"Lower overlap → higher premium, capped at +30%."
            ),
            [
                {"step": 1, "operation": "Max cosine similarity", "value": round(max_sim, 4)},
                {"step": 2, "operation": "S_originality (0–0.30)", "value": s_originality},
                {"step": 3, "operation": "Premium USD added", "value": round(v_after_originality - v_baseline, 2)},
                {"step": 4, "operation": "Value after premium", "value": round(v_after_originality, 2)},
            ],
            [
                {
                    "type": "patent_match",
                    "ref": top_match.get("patent_id", "N/A"),
                    "detail": top_match.get("title", "Closest prior art"),
                },
                {"type": "embedding_model", "ref": originality.get("embedding_model", "text-embedding-3-small"), "detail": "1536-dim"},
            ],
            parent_id="v_baseline",
        )
    )

    audit_trail.append(
        _audit_entry(
            "r_fto_haircut",
            "FTO Risk Haircut",
            -(v_after_originality - v_after_fto),
            f"V × R_fto = {v_after_originality:,.0f} × {r_fto_clamped:.4f}",
            (
                f"Freedom-to-operate analysis flagged {fto.get('flagged_patent_count', 0)} patents with "
                f"structural claim overlap (source: {fto.get('analysis_source', 'rule_based')}). "
                f"Risk tier {fto.get('risk_tier_pct', 0):.1f}% maps to a haircut capped at −50%."
            ),
            [
                {"step": 1, "operation": "R_fto (0–0.50)", "value": r_fto_clamped},
                {"step": 2, "operation": "Haircut USD", "value": round(v_after_originality - v_after_fto, 2)},
                {"step": 3, "operation": "Value after FTO", "value": round(v_after_fto, 2)},
            ],
            [
                {
                    "type": "fto_patent",
                    "ref": fto.get("high_risk_patent_group") or "none",
                    "detail": f"{fto.get('flagged_patent_count', 0)} overlapping patents",
                },
            ],
            parent_id="s_originality_premium",
        )
    )

    if expert_consultation_required:
        audit_trail.append(
            _audit_entry(
                "expert_consultation_cap",
                "High-Risk FTO Cap (−15%)",
                -(v_after_fto - v_target),
                f"V × 0.85 (risk tier > 35%)",
                (
                    "FTO risk tier exceeded 35%. Automated valuation is capped pending patent attorney review "
                    "before tokenization minting, per platform policy."
                ),
                [
                    {"step": 1, "operation": "Pre-cap value", "value": round(v_after_fto, 2)},
                    {"step": 2, "operation": "Cap multiplier", "value": 0.85},
                    {"step": 3, "operation": "Post-cap V_target", "value": round(v_target, 2)},
                ],
                [{"type": "policy", "ref": "FTO_TIER_35", "detail": "Expert consultation required"}],
                parent_id="r_fto_haircut",
            )
        )

    audit_trail.append(
        _audit_entry(
            "v_target",
            "Target Valuation (V_target)",
            v_target,
            "V_baseline × (1 + S_originality) × (1 − R_fto)" + (" × 0.85" if expert_consultation_required else ""),
            "Fully adjusted pre-tokenization enterprise value anchor before the 70/30 human-in-the-loop split.",
            [
                {"step": 1, "operation": "V_baseline", "value": v_baseline},
                {"step": 2, "operation": "× (1 + S_originality)", "value": round(1 + s_originality, 4)},
                {"step": 3, "operation": "× (1 − R_fto)", "value": round(1 - r_fto_clamped, 4)},
                {"step": 4, "operation": "= V_target", "value": round(v_target, 2)},
            ],
            [],
            parent_id="v_baseline",
        )
    )

    audit_trail.append(
        _audit_entry(
            "valuation_floor",
            "Valuation Floor (Cost Approach)",
            valuation_floor,
            f"max(floor_cost={floor_cost:,.0f}, V_target × 0.35)",
            (
                f"Minimum price floor ensures the asset is not tokenized below estimated development cost "
                f"for {baseline['sector_name']}. Includes lab equipment, researcher hours, and grant baselines."
            ),
            [
                {"step": 1, "operation": "Sector floor_cost", "value": floor_cost},
                {"step": 2, "operation": "35% of V_target", "value": round(v_target * 0.35, 2)},
                {"step": 3, "operation": "Floor (max of above)", "value": round(valuation_floor, 2)},
            ],
            [{"type": "cost_approach", "ref": ipc_code, "detail": baseline["sector_name"]}],
            parent_id="v_target",
        )
    )

    audit_trail.append(
        _audit_entry(
            "tokenization_anchor",
            "AI Tokenization Anchor (70%)",
            tokenization_anchor,
            f"V_target × 0.70 = {v_target:,.0f} × 0.70",
            (
                "The 70% automated baseline is hard-locked per the 70/30 rule. "
                "The remaining 30% is reserved for human expert modifiers (team pedigree, trade secrets, partnerships)."
            ),
            [
                {"step": 1, "operation": "V_target", "value": round(v_target, 2)},
                {"step": 2, "operation": "Automated anchor %", "value": 70},
                {"step": 3, "operation": "Anchor USD", "value": round(tokenization_anchor, 2)},
            ],
            [{"type": "policy", "ref": "70_30_RULE", "detail": "Non-editable AI baseline guardrail"}],
            parent_id="v_target",
        )
    )

    # Calculate narrower valuation range based on confidence
    confidence_interval = 0.10  # ±10% for high confidence
    if max_sim > 0.5:
        confidence_interval = 0.15  # ±15% for medium confidence (higher similarity = more uncertainty)
    if expert_consultation_required:
        confidence_interval = 0.20  # ±20% for low confidence
    
    valuation_range_low = round(v_target * (1 - confidence_interval), 2)
    valuation_range_high = round(v_target * (1 + confidence_interval), 2)
    
    return {
        "v_baseline_usd": v_baseline,
        "valuation_range_usd": {
            "low": valuation_range_low,
            "mid": round(v_target, 2),
            "high": valuation_range_high,
            "confidence_interval": confidence_interval
        },
        "s_originality": s_originality,
        "r_fto": r_fto_clamped,
        "v_target_usd": round(v_target, 2),
        "valuation_floor_usd": round(valuation_floor, 2),
        "tokenization_anchor_usd": round(tokenization_anchor, 2),
        "royalty_rate_baseline": baseline["royalty_rate"],
        "sector_name": baseline["sector_name"],
        "formula": "V_target = V_baseline × (1 + S_originality) × (1 - R_fto)",
        "hitl_reserved_pct": 30,
        "automated_anchor_pct": 70,
        "audit_trail": audit_trail,
    }
