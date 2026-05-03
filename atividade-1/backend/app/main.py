import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .logging_config import configure_logging
from .mempool import lag, summary
from .rpc_client import RPCConnectionError, RPCError, rpc_from_env

load_dotenv()
configure_logging()

app = FastAPI(title="CoreCraft Atividade 1 — Mempool Snapshot")

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
def index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/api/mempool/summary")
def mempool_summary():
    rpc = rpc_from_env()
    try:
        return summary(rpc)
    except RPCConnectionError as exc:
        raise HTTPException(status_code=503, detail={"error": "node_unavailable", "detail": str(exc)})
    except RPCError as exc:
        raise HTTPException(status_code=503, detail={"error": "rpc_error", "detail": str(exc)})


@app.get("/api/blockchain/lag")
def blockchain_lag():
    rpc = rpc_from_env()
    try:
        return lag(rpc)
    except RPCConnectionError as exc:
        raise HTTPException(status_code=503, detail={"error": "node_unavailable", "detail": str(exc)})
    except RPCError as exc:
        raise HTTPException(status_code=503, detail={"error": "rpc_error", "detail": str(exc)})


@app.get("/{path:path}")
def spa_fallback(path: str):
    return FileResponse(str(FRONTEND_DIR / "index.html"))
