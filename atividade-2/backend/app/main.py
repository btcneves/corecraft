from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import zmq_listener
from .event_service import get_latest, get_state_comparison, get_summary
from .event_store import EventStore
from .rpc_client import RPCConnectionError, RPCError, rpc_from_env

load_dotenv()

store = EventStore()

FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    rpc = rpc_from_env()
    zmq_listener.start(store, rpc)
    yield
    zmq_listener.stop()


app = FastAPI(title="CoreCraft Atividade 2 — Eventos em Tempo Real", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


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
