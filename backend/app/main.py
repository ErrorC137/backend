import logging
import os
import time
from collections import defaultdict
from threading import Lock

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware

from app.embeddings import ensure_index, index_status
from app.ingestion import DocumentExtractionError
from app.pipeline import run_analysis
from app.ai_services.rate_limiter import get_rate_limiter, get_cost_monitor, RateLimitConfig

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Render sets PORT automatically; use API_PORT for local dev only
API_PORT = int(os.environ.get("PORT", os.environ.get("API_PORT", "8765")))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# Advanced rate limiting configuration
ENABLE_ADVANCED_RATE_LIMITING = os.getenv("ENABLE_ADVANCED_RATE_LIMITING", "true").lower() == "true"
DAILY_BUDGET_USD = float(os.getenv("DAILY_BUDGET_USD", "100.0"))
HOURLY_BUDGET_USD = float(os.getenv("HOURLY_BUDGET_USD", "10.0"))

# Simple in-memory rate limiter (fallback)
_rate_limit_store = defaultdict(list)
_rate_limit_lock = Lock()

# Initialize advanced rate limiter and cost monitor
if ENABLE_ADVANCED_RATE_LIMITING:
    rate_limit_config = RateLimitConfig(
        requests_per_minute=RATE_LIMIT_REQUESTS,
        requests_per_hour=int(RATE_LIMIT_REQUESTS * 60),
        tokens_per_minute=100000,
        cost_per_hour_usd=HOURLY_BUDGET_USD,
    )
    _advanced_rate_limiter = get_rate_limiter(rate_limit_config)
    _cost_monitor = get_cost_monitor(
        daily_budget_usd=DAILY_BUDGET_USD,
        hourly_budget_usd=HOURLY_BUDGET_USD,
        alert_threshold_percent=0.8,
    )
else:
    _advanced_rate_limiter = None
    _cost_monitor = None


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
    health_data = {
        "status": "ok" if status["ready"] else "warming",
        "service": "matdao-ip-engine",
        "port": API_PORT,
        "embedding_model": status["model"],
        "embedding_provider": status.get("provider", "openai"),
        "patent_corpus_size": status["patent_count"],
        "index_ready": status["ready"],
    }
    
    # Add rate limiting and cost monitoring stats if enabled
    if ENABLE_ADVANCED_RATE_LIMITING and _advanced_rate_limiter and _cost_monitor:
        health_data["rate_limiting"] = {
            "enabled": True,
            "requests_per_minute": RATE_LIMIT_REQUESTS,
            "tokens_per_minute": 100000,
            "cost_per_hour_usd": HOURLY_BUDGET_USD,
        }
        health_data["usage_stats"] = _advanced_rate_limiter.get_usage_stats()
        health_data["cost_stats"] = _cost_monitor.get_cost_stats()
    
    return health_data


@app.get("/api/stats")
async def get_stats():
    """Get detailed usage and cost statistics."""
    if not ENABLE_ADVANCED_RATE_LIMITING or not _advanced_rate_limiter or not _cost_monitor:
        return {
            "enabled": False,
            "message": "Advanced rate limiting and cost monitoring not enabled"
        }
    
    return {
        "enabled": True,
        "rate_limiting": {
            "config": {
                "requests_per_minute": RATE_LIMIT_REQUESTS,
                "requests_per_hour": int(RATE_LIMIT_REQUESTS * 60),
                "tokens_per_minute": 100000,
                "cost_per_hour_usd": HOURLY_BUDGET_USD,
            },
            "stats": _advanced_rate_limiter.get_usage_stats(),
        },
        "cost_monitoring": {
            "config": {
                "daily_budget_usd": DAILY_BUDGET_USD,
                "hourly_budget_usd": HOURLY_BUDGET_USD,
                "alert_threshold_percent": 0.8,
            },
            "stats": _cost_monitor.get_cost_stats(),
        },
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
        
        # Record cost if advanced monitoring is enabled
        if ENABLE_ADVANCED_RATE_LIMITING and _cost_monitor:
            api_cost = result.get("api_usage", {}).get("total_analysis_time", 0) * 0.01  # Estimate cost based on time
            _cost_monitor.record_cost(api_cost)
            
    except DocumentExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
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
