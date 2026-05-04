import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from corecraft import BlockchainLag, MempoolSummary

from .logging_config import configure_logging
from .mempool import lag, summary
from .observability import correlation_middleware, health_payload, metrics_text
from .rpc_client import RPCConnectionError, RPCError, rpc_from_env

load_dotenv()
configure_logging()

app = FastAPI(title="CoreCraft Atividade 1 — Mempool Snapshot")
app.middleware("http")(correlation_middleware)

FRONTEND_CANDIDATES = [
    Path(os.getenv("FRONTEND_DIR", "")) if os.getenv("FRONTEND_DIR") else None,
    Path("/app/frontend/dist"),
    Path("/app/frontend"),
    Path(__file__).parent.parent.parent / "frontend" / "dist",
    Path(__file__).parent.parent.parent / "frontend",
]
FRONTEND_DIR = next(path for path in FRONTEND_CANDIDATES if path and (path / "index.html").exists())
FRONTEND_SOURCE_DIR = FRONTEND_DIR.parent if FRONTEND_DIR.name == "dist" else FRONTEND_DIR

if (FRONTEND_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
if (FRONTEND_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
elif FRONTEND_SOURCE_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_SOURCE_DIR)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/health")
def health() -> dict[str, str]:
    return health_payload()


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    return metrics_text()


@app.get("/api/mempool/summary")
def mempool_summary() -> MempoolSummary:
    rpc = rpc_from_env()
    try:
        result: MempoolSummary = summary(rpc)
        return result
    except RPCConnectionError as exc:
        raise HTTPException(
            status_code=503, detail={"error": "node_unavailable", "detail": str(exc)}
        ) from exc
    except RPCError as exc:
        raise HTTPException(
            status_code=503, detail={"error": "rpc_error", "detail": str(exc)}
        ) from exc


@app.get("/api/blockchain/lag")
def blockchain_lag() -> BlockchainLag:
    rpc = rpc_from_env()
    try:
        result: BlockchainLag = lag(rpc)
        return result
    except RPCConnectionError as exc:
        raise HTTPException(
            status_code=503, detail={"error": "node_unavailable", "detail": str(exc)}
        ) from exc
    except RPCError as exc:
        raise HTTPException(
            status_code=503, detail={"error": "rpc_error", "detail": str(exc)}
        ) from exc


@app.get("/{path:path}")
def spa_fallback(path: str) -> FileResponse:
    return FileResponse(str(FRONTEND_DIR / "index.html"))
