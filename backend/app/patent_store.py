"""Patent corpus loader — Google Patents Public Data export format."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_DATA_DIR = Path(__file__).parent / "data"


def _localized_text(field: list[dict[str, str]] | None, lang: str = "en") -> str:
    if not field:
        return ""
    for item in field:
        if item.get("language") == lang and item.get("text"):
            return item["text"].strip()
    for item in field:
        if item.get("text"):
            return item["text"].strip()
    return ""


def _ipc_code(record: dict[str, Any]) -> str:
    ipc_list = record.get("ipc") or []
    if not ipc_list:
        return "DEFAULT"
    code = ipc_list[0].get("code", "")
    return code.split("/")[0][:4] if code else "DEFAULT"


def _normalize_bigquery_record(record: dict[str, Any]) -> dict[str, Any]:
    title = _localized_text(record.get("title_localized"))
    abstract = _localized_text(record.get("abstract_localized"))
    claims = _localized_text(record.get("claims_localized"))
    if not claims and record.get("claims"):
        claims = record["claims"]

    ipc = _ipc_code(record)
    return {
        "patent_id": record.get("publication_number") or record.get("patent_id", "UNKNOWN"),
        "publication_number": record.get("publication_number"),
        "country_code": record.get("country_code", "US"),
        "title": title or record.get("title", ""),
        "abstract": abstract or record.get("abstract", ""),
        "claims": claims,
        "ipc": ipc if ipc != "DEFAULT" else record.get("ipc", "G06F"),
        "cpc": record.get("cpc") or (f"{ipc}/00" if ipc != "DEFAULT" else "G06F00/00"),
        "publication_date": record.get("publication_date"),
        "assignee": record.get("assignee", []),
        "source": record.get("_source", "google_patents_public_data"),
    }


def _load_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "publications" in data:
        return data["publications"]
    if isinstance(data, list):
        return data
    return []


def load_patent_corpus() -> list[dict[str, Any]]:
    """Merge legacy samples with all Google Patents Public Data export files."""
    legacy = _load_json(_DATA_DIR / "sample_patents.json")
    export_records: list[dict[str, Any]] = []
    for path in sorted(_DATA_DIR.glob("google_patents*.json")):
        export_records.extend(_load_json(path))

    seen: set[str] = set()
    corpus: list[dict[str, Any]] = []

    for record in export_records + legacy:
        if "title_localized" in record or "abstract_localized" in record:
            normalized = _normalize_bigquery_record(record)
        else:
            normalized = {
                "patent_id": record.get("patent_id", "UNKNOWN"),
                "publication_number": record.get("patent_id"),
                "country_code": "US",
                "title": record.get("title", ""),
                "abstract": record.get("abstract", ""),
                "claims": record.get("claims", ""),
                "ipc": str(record.get("ipc", "G06F")).split("/")[0][:4],
                "cpc": record.get("cpc", record.get("ipc", "G06F")),
                "publication_date": None,
                "assignee": [],
                "source": "legacy_sample",
            }

        pid = normalized["patent_id"]
        if not normalized["abstract"] or pid in seen:
            continue
        seen.add(pid)
        corpus.append(normalized)

    return corpus
