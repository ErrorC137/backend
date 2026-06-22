#!/usr/bin/env python3
"""Build or rebuild the OpenAI embedding vector index from Google Patents export."""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Allow running as `python scripts/build_patent_index.py` from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.embeddings import build_index  # noqa: E402


def main() -> None:
    os.environ["REBUILD_PATENT_INDEX"] = "1"
    info = build_index(force=True)
    print("Patent index rebuilt successfully:")
    for key, value in info.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
