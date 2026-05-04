"""
Integration tests for Activity 3 — full PSBT end-to-end flow via HTTP.

These tests validate the complete lifecycle: wallet selection, status check,
PSBT transaction send, and transaction status tracking through the HTTP API.
"""

import importlib
from typing import Any

import pytest
from starlette.testclient import TestClient

from tests.conftest import FakeRPC, prepare_activity_import


def _setup(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pytest.TempPathFactory,
) -> object:
    (tmp_path / "index.html").write_text("<html></html>")  # type: ignore[attr-defined]
    monkeypatch.setenv("FRONTEND_DIR", str(tmp_path))
    prepare_activity_import("atividade-3", monkeypatch)
    main = importlib.import_module("app.main")
    # Reset module-level state for test isolation
    main.state["selected_wallet"] = None  # type: ignore[attr-defined]
    main.state["tracked_txs"] = {}  # type: ignore[attr-defined]
    return main


def _node_rpc(extra: dict[str, Any] | None = None) -> FakeRPC:
    # Import RPCError lazily (module loaded after prepare_activity_import)
    try:
        _rpc_err = importlib.import_module("app.tx_service").RPCError
    except Exception:
        _rpc_err = Exception  # fallback before module is loaded

    base: dict[str, Any] = {
        "listwalletdir": {"wallets": [{"name": "wallet1"}, {"name": "wallet2"}]},
        "listwallets": [],
        "loadwallet": {},
        "getwalletinfo": {"walletname": "wallet1", "balance": 10.0, "txcount": 5},
        "getbalances": {"mine": {"trusted": 10.0, "untrusted_pending": 0.0, "immature": 0.0}},
        "listunspent": [{}, {}],
        "walletcreatefundedpsbt": {"psbt": "base64-psbt"},
        "walletprocesspsbt": {"psbt": "signed-psbt"},
        "finalizepsbt": {"complete": True, "hex": "deadbeef01"},
        "sendrawtransaction": "abc123txid",
        # Used by get_tx — tx in mempool, no confirmations yet
        "gettransaction": {"confirmations": 0},
        "getmempoolentry": {"fees": {"base": 0.00001}, "vsize": 141, "time": 1700000000},
    }
    if extra:
        base.update(extra)
    return FakeRPC(base)


# ── Basic endpoints ───────────────────────────────────────────────────────────


def test_health(monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory) -> None:
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "atividade-3"


def test_metrics_includes_psbt_counter(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "corecraft_psbt_sent_total" in resp.text


# ── Wallet flow ───────────────────────────────────────────────────────────────


def test_list_wallets_returns_available(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    monkeypatch.setattr(main, "_node", lambda: _node_rpc())
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/wallets")
    assert resp.status_code == 200
    data = resp.json()
    assert "wallet1" in data["available_wallets"]
    assert "wallet2" in data["available_wallets"]


def test_list_wallets_503_on_rpc_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    RPCConnectionError = importlib.import_module("app.rpc_client").RPCConnectionError
    monkeypatch.setattr(
        main,
        "_node",
        lambda: FakeRPC({"listwalletdir": RPCConnectionError("offline")}),
    )
    with TestClient(main.app, raise_server_exceptions=False) as client:  # type: ignore[attr-defined]
        resp = client.get("/wallets")
    assert resp.status_code == 503


def test_select_wallet_updates_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    wallet_service = importlib.import_module("app.wallet_service")
    node = _node_rpc()
    monkeypatch.setattr(main, "_node", lambda: node)
    monkeypatch.setattr(wallet_service, "rpc_wallet", lambda name: node)

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.post("/wallet/select", json={"wallet": "wallet1"})
    assert resp.status_code == 200
    assert resp.json()["selected_wallet"] == "wallet1"
    assert main.state["selected_wallet"] == "wallet1"  # type: ignore[attr-defined]


def test_select_missing_wallet_returns_404(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    wallet_service = importlib.import_module("app.wallet_service")
    node = _node_rpc()
    monkeypatch.setattr(main, "_node", lambda: node)
    monkeypatch.setattr(wallet_service, "rpc_wallet", lambda name: node)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.post("/wallet/select", json={"wallet": "nonexistent"})
    assert resp.status_code == 404


def test_wallet_status_after_selection(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    wallet_service = importlib.import_module("app.wallet_service")
    monkeypatch.setattr(main, "_node", lambda: _node_rpc())
    monkeypatch.setattr(
        wallet_service,
        "rpc_wallet",
        lambda name: _node_rpc(),
    )
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        client.post("/wallet/select", json={"wallet": "wallet1"})
        resp = client.get("/wallet/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["balance"] == 10.0


def test_wallet_status_409_when_no_wallet_selected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/wallet/status")
    assert resp.status_code == 409


# ── PSBT transaction flow ─────────────────────────────────────────────────────


def test_send_without_wallet_returns_409(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.post("/tx/send", json={"to_address": "bcrt1qtest", "amount": 0.001})
    assert resp.status_code == 409


def test_full_psbt_flow(monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory) -> None:
    """
    End-to-end PSBT flow:
    POST /wallet/select → POST /tx/send → GET /tx/{txid}
    Validates state transitions through the HTTP layer.
    """
    main = _setup(monkeypatch, tmp_path)
    tx_service = importlib.import_module("app.tx_service")
    wallet_service = importlib.import_module("app.wallet_service")

    node = _node_rpc()
    monkeypatch.setattr(main, "_node", lambda: node)
    monkeypatch.setattr(wallet_service, "rpc_wallet", lambda name: node)
    monkeypatch.setattr(tx_service, "rpc_wallet", lambda name: node)
    monkeypatch.setattr(tx_service, "rpc_node", lambda: node)

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        # Step 1: select wallet
        r1 = client.post("/wallet/select", json={"wallet": "wallet1"})
        assert r1.status_code == 200
        assert r1.json()["selected_wallet"] == "wallet1"

        # Step 2: send PSBT transaction
        r2 = client.post("/tx/send", json={"to_address": "bcrt1qtest", "amount": 0.001})
        assert r2.status_code == 200
        txid = r2.json()["txid"]
        assert txid == "abc123txid"
        assert r2.json()["status"] == "broadcast"

        # Step 3: get tx status — in tracked_txs but not confirmed yet
        r3 = client.get(f"/tx/{txid}")
        assert r3.status_code == 200
        tx_data = r3.json()
        assert tx_data["txid"] == txid
        assert tx_data["wallet"] == "wallet1"
        # status depends on RPC state; broadcast or mempool are valid


def test_psbt_finalization_failure_returns_400(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    tx_service = importlib.import_module("app.tx_service")
    wallet_service = importlib.import_module("app.wallet_service")

    bad_node = FakeRPC(
        {
            "listwalletdir": {"wallets": [{"name": "wallet1"}]},
            "listwallets": [],
            "loadwallet": {},
            "getwalletinfo": {"walletname": "wallet1", "balance": 1.0, "txcount": 0},
            "walletcreatefundedpsbt": {"psbt": "base64-psbt"},
            "walletprocesspsbt": {"psbt": "signed-psbt"},
            "finalizepsbt": {"complete": False},  # ← finalization fails
        }
    )
    monkeypatch.setattr(main, "_node", lambda: bad_node)
    monkeypatch.setattr(wallet_service, "rpc_wallet", lambda name: bad_node)
    monkeypatch.setattr(tx_service, "rpc_wallet", lambda name: bad_node)
    monkeypatch.setattr(tx_service, "rpc_node", lambda: bad_node)

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        client.post("/wallet/select", json={"wallet": "wallet1"})
        resp = client.post("/tx/send", json={"to_address": "bcrt1qtest", "amount": 0.001})
    assert resp.status_code == 400
    assert "finalization" in resp.json()["detail"].lower()


def test_tx_status_confirmed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    tx_service = importlib.import_module("app.tx_service")
    wallet_service = importlib.import_module("app.wallet_service")

    confirmed_node = _node_rpc(
        {
            "gettransaction": {"confirmations": 3, "blockhash": "blockabc"},
            "getmempoolentry": tx_service.RPCError(-5, "not in mempool"),
        }
    )
    monkeypatch.setattr(main, "_node", lambda: confirmed_node)
    monkeypatch.setattr(wallet_service, "rpc_wallet", lambda name: confirmed_node)
    monkeypatch.setattr(tx_service, "rpc_wallet", lambda name: confirmed_node)
    monkeypatch.setattr(tx_service, "rpc_node", lambda: confirmed_node)

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        # Pre-populate state so /tx/{txid} knows the wallet
        main.state["selected_wallet"] = "wallet1"  # type: ignore[attr-defined]
        main.state["tracked_txs"]["abc123txid"] = {  # type: ignore[attr-defined]
            "wallet": "wallet1",
            "broadcast_ts": 1700000000.0,
        }
        resp = client.get("/tx/abc123txid")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "confirmed"
    assert data["confirmed"] is True
    assert data["confirmations"] == 3


def test_psbt_counter_increments_in_metrics(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    """After a successful PSBT send, /metrics reflects the incremented counter."""
    main = _setup(monkeypatch, tmp_path)
    tx_service = importlib.import_module("app.tx_service")
    wallet_service = importlib.import_module("app.wallet_service")
    node = _node_rpc()
    monkeypatch.setattr(main, "_node", lambda: node)
    monkeypatch.setattr(wallet_service, "rpc_wallet", lambda name: node)
    monkeypatch.setattr(tx_service, "rpc_wallet", lambda name: node)
    monkeypatch.setattr(tx_service, "rpc_node", lambda: node)

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        client.post("/wallet/select", json={"wallet": "wallet1"})
        client.post("/tx/send", json={"to_address": "bcrt1qtest", "amount": 0.001})
        resp = client.get("/metrics")

    import re

    match = re.search(r"corecraft_psbt_sent_total\{[^}]+\} (\d+)", resp.text)
    assert match and int(match.group(1)) >= 1
