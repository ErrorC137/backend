import logging
import os
import time
from collections import defaultdict
from threading import Lock

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.embeddings import ensure_index, index_status
from app.pipeline import run_analysis

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Render sets PORT automatically; use API_PORT for local dev only
API_PORT = int(os.environ.get("PORT", os.environ.get("API_PORT", "8765")))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# Simple in-memory rate limiter
_rate_limit_store = defaultdict(list)
_rate_limit_lock = Lock()


def _check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit."""
    current_time = time.time()
    
    with _rate_limit_lock:
        # Clean old requests outside the window
        _rate_limit_store[client_ip] = [
            req_time for req_time in _rate_limit_store[client_ip]
            if current_time - req_time < RATE_LIMIT_WINDOW
        ]
        
        # Check if under limit
        if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for {client_ip}: {len(_rate_limit_store[client_ip])} requests in {RATE_LIMIT_WINDOW}s")
            return False
        
        # Add current request
        _rate_limit_store[client_ip].append(current_time)
        return True


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
async def analyze(file: UploadFile = File(...), client_ip: str = "0.0.0.0"):
    # Check rate limit
    if not _check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429, 
            detail=f"Rate limit exceeded: maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds"
        )
    
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
        import traceback
        error_detail = f"Analysis failed: {str(exc)}"
        print(f"Analysis error: {error_detail}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_detail) from exc
    finally:
        del content

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
