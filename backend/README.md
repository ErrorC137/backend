# MatDAO IP Engine

Python FastAPI service powering AI Studio: TRL evaluation, IP valuation, FTO, and due diligence — all from one `/api/analyze` endpoint.

Embeddings use **OpenAI `text-embedding-3-small`** (no local transformer model — low RAM for Render).

## Local development

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env     # set OPENAI_API_KEY
uvicorn app.main:app --reload --port 8765
```

## Deploy on Render

1. Create a **Web Service** from this directory (or use root `render.yaml`).
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set env vars:
   - `OPENAI_API_KEY` (required)
   - `CORS_ALLOWED_ORIGINS` = your v0/Vercel frontend URL

## Rebuild patent index (optional)

```bash
python scripts/build_patent_index.py
```

Requires `OPENAI_API_KEY`. Index is cached under `app/data/vector_cache/`.
