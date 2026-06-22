#!/usr/bin/env python3
"""Import a BigQuery CSV/JSON export into google_patents_public_export.json."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def row_to_publication(row: dict) -> dict:
    pub_num = row.get("publication_number") or row.get("patent_id") or row.get("id")
    title = row.get("title") or row.get("title_text") or ""
    abstract = row.get("abstract") or row.get("abstract_text") or ""
    claims = row.get("claims") or row.get("claims_text") or ""
    ipc_raw = row.get("ipc") or row.get("ipc_code") or ""

    ipc_codes = []
    for part in str(ipc_raw).replace(";", "|").split("|"):
        part = part.strip()
        if part:
            ipc_codes.append({"code": part})

    return {
        "publication_number": pub_num,
        "country_code": row.get("country_code", "US"),
        "publication_date": row.get("publication_date"),
        "title_localized": [{"text": title, "language": "en"}],
        "abstract_localized": [{"text": abstract, "language": "en"}],
        "claims_localized": [{"text": claims, "language": "en"}] if claims else [],
        "ipc": ipc_codes,
        "assignee": [row["assignee"]] if row.get("assignee") else [],
        "_source": "bigquery_csv_import",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Google Patents BigQuery export")
    parser.add_argument("input", type=Path, help="CSV or JSON file from BigQuery export")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "app" / "data" / "google_patents_public_export.json",
    )
    args = parser.parse_args()

    publications: list[dict] = []
    if args.input.suffix.lower() == ".json":
        with open(args.input, encoding="utf-8") as f:
            data = json.load(f)
        rows = data if isinstance(data, list) else data.get("publications", [])
        for row in rows:
            if "title_localized" in row:
                publications.append(row)
            else:
                publications.append(row_to_publication(row))
    else:
        with open(args.input, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                publications.append(row_to_publication(row))

    payload = {
        "dataset": "patents-public-data.patents.publications",
        "description": "Curated subset compatible with Google Patents Public Data BigQuery schema",
        "publications": publications,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Imported {len(publications)} publications -> {args.output}")


if __name__ == "__main__":
    main()
