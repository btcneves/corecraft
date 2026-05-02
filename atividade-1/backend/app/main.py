import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .mempool import lag, summary
from .rpc_client import RPCConnectionError, RPCError, rpc_from_env

load_dotenv()

app = FastAPI(title="CoreCraft Atividade 1 — Mempool Snapshot")

FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


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
