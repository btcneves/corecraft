import os
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import zmq_listener
from .event_service import get_latest, get_state_comparison, get_summary
from .event_store import EventStore
from .logging_config import configure_logging
from .rpc_client import RPCConnectionError, RPCError, rpc_from_env

load_dotenv()
configure_logging()

store = EventStore()

FRONTEND_CANDIDATES = [
    Path(os.getenv("FRONTEND_DIR", "")) if os.getenv("FRONTEND_DIR") else None,
    Path("/app/frontend/dist"),
    Path("/app/frontend"),
    Path(__file__).parent.parent.parent / "frontend" / "dist",
    Path(__file__).parent.parent.parent / "frontend",
]
FRONTEND_DIR = next(path for path in FRONTEND_CANDIDATES if path and (path / "index.html").exists())
FRONTEND_SOURCE_DIR = FRONTEND_DIR.parent if FRONTEND_DIR.name == "dist" else FRONTEND_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    rpc = rpc_from_env()
    zmq_listener.start(store, rpc)
    yield
    zmq_listener.stop()


app = FastAPI(title="CoreCraft Atividade 2 — Eventos em Tempo Real", lifespan=lifespan)

if (FRONTEND_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
if (FRONTEND_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
elif FRONTEND_SOURCE_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_SOURCE_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/api/events/summary")
def events_summary():
    return get_summary(store)


@app.get("/api/events/latest")
def events_latest():
    return get_latest(store)


@app.get("/api/events/state-comparison")
def events_state_comparison():
    rpc = rpc_from_env()
    try:
        return get_state_comparison(store, rpc)
    except RPCConnectionError as exc:
        raise HTTPException(status_code=503, detail={"error": "node_unavailable", "detail": str(exc)})
    except RPCError as exc:
        raise HTTPException(status_code=503, detail={"error": "rpc_error", "detail": str(exc)})


@app.websocket("/ws/events")
async def events_ws(websocket: WebSocket):
    await websocket.accept()
    rpc = rpc_from_env()
    try:
        while True:
            payload = {
                "summary": get_summary(store),
                "latest": get_latest(store),
            }
            try:
                payload["state_comparison"] = get_state_comparison(store, rpc)
            except (RPCConnectionError, RPCError) as exc:
                payload["state_comparison"] = {
                    "error": "node_unavailable" if isinstance(exc, RPCConnectionError) else "rpc_error",
                    "detail": str(exc),
                }
            await websocket.send_json(payload)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return


@app.get("/{path:path}")
def spa_fallback(path: str):
    return FileResponse(str(FRONTEND_DIR / "index.html"))
