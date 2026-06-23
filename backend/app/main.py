import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.embeddings import ensure_index, index_status
from app.pipeline import run_analysis

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_PORT = int(os.environ.get("PORT", os.environ.get("API_PORT", "8765")))


def _cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    if origins:
        return origins
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]


app = FastAPI(
    title="MatDAO IP Valuation & FTO Engine",
    description="Automated deep tech IP valuation and freedom-to-operate analysis",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    status = index_status()
    return {
        "status": "ok" if status["ready"] else "warming",
        "service": "matdao-ip-engine",
        "port": API_PORT,
        "embedding_model": status["model"],
        "embedding_provider": status.get("provider", "openai"),
        "patent_corpus_size": status["patent_count"],
        "index_ready": status["ready"],
    }


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        ensure_index()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Patent index unavailable: {exc}") from exc

    if not index_status()["ready"]:
        raise HTTPException(status_code=503, detail="Patent vector index is still loading. Retry shortly.")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    allowed = (".pdf", ".docx", ".txt")
    if not file.filename.lower().endswith(allowed):
        raise HTTPException(status_code=400, detail=f"Supported formats: {', '.join(allowed)}")

    content = await file.read()
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 15MB)")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        result = await run_analysis(file.filename, content)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
    finally:
        del content

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
