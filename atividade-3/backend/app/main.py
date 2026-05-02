from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .rpc_client import RPCConnectionError, RPCError, rpc_node
from .tx_service import get_tx, send_tx
from .wallet_service import list_wallets, select_wallet, wallet_status

load_dotenv()

app = FastAPI(title="CoreCraft Atividade 3 — Multi-Wallet + PSBT")

FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# ── In-memory state ──────────────────────────────────────────────────────────
state: dict = {
    "selected_wallet": None,
    "tracked_txs": {},  # txid -> {wallet, broadcast_ts}
}


# ── Models ────────────────────────────────────────────────────────────────────
class SelectWalletRequest(BaseModel):
    wallet: str


class SendTxRequest(BaseModel):
    to_address: str
    amount: float


# ── Helpers ───────────────────────────────────────────────────────────────────
def _node():
    return rpc_node()


def _require_wallet() -> str:
    w = state.get("selected_wallet")
    if not w:
        raise HTTPException(status_code=409, detail="No wallet selected. POST /wallet/select first.")
    return w


def _handle_rpc(exc: Exception):
    if isinstance(exc, RPCConnectionError):
        raise HTTPException(status_code=503, detail={"error": "node_unavailable", "detail": str(exc)})
    if isinstance(exc, RPCError):
        raise HTTPException(status_code=503, detail={"error": "rpc_error", "detail": str(exc)})
    raise exc


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/wallets")
def wallets():
    try:
        return list_wallets(_node(), state)
    except (RPCConnectionError, RPCError) as exc:
        _handle_rpc(exc)


@app.post("/wallet/select")
def wallet_select(body: SelectWalletRequest):
    try:
        return select_wallet(body.wallet, _node(), state)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except (RPCConnectionError, RPCError) as exc:
        _handle_rpc(exc)


@app.get("/wallet/status")
def wallet_status_route():
    name = _require_wallet()
    try:
        return wallet_status(name)
    except (RPCConnectionError, RPCError) as exc:
        _handle_rpc(exc)


@app.post("/tx/send")
def tx_send(body: SendTxRequest):
    name = _require_wallet()
    try:
        return send_tx(body.to_address, body.amount, name, state["tracked_txs"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except (RPCConnectionError, RPCError) as exc:
        _handle_rpc(exc)


@app.get("/tx/{txid}")
def tx_status(txid: str):
    wallet = state.get("selected_wallet")
    try:
        return get_tx(txid, wallet, state["tracked_txs"])
    except (RPCConnectionError, RPCError) as exc:
        _handle_rpc(exc)
