"""
Integration tests for Activity 2 — ZMQ → EventStore → HTTP API flow.

These tests validate the full pipeline: simulated ZMQ events populate the
EventStore, which is then reflected correctly in the HTTP API responses.
"""

import importlib

import pytest
from starlette.testclient import TestClient

from tests.conftest import FakeRPC, prepare_activity_import


def _setup(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pytest.TempPathFactory,
    fake_rpc: object | None = None,
) -> object:
    (tmp_path / "index.html").write_text("<html></html>")  # type: ignore[attr-defined]
    monkeypatch.setenv("FRONTEND_DIR", str(tmp_path))
    prepare_activity_import("atividade-2", monkeypatch)

    zmq_listener = importlib.import_module("app.zmq_listener")
    monkeypatch.setattr(zmq_listener, "start", lambda store, rpc: None)
    monkeypatch.setattr(zmq_listener, "stop", lambda: None)

    main = importlib.import_module("app.main")
    rpc = fake_rpc or FakeRPC({"getbestblockhash": "0000abc"})
    monkeypatch.setattr(main, "rpc_from_env", lambda: rpc)
    return main


_RAW_BLOCK = bytes(80)  # 80-byte header → deterministic hash


def test_health(monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory) -> None:
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "atividade-2"


def test_events_summary_empty_store(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/events/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["blocks_observed"] == 0
    assert data["tx_observed"] == 0


def test_events_summary_after_zmq_block(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    """Simulate ZMQ rawblock arriving → EventStore updated → API reflects it."""
    main = _setup(monkeypatch, tmp_path)
    main.store.add_block(_RAW_BLOCK)  # type: ignore[attr-defined]

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/events/summary")
    assert resp.status_code == 200
    assert resp.json()["blocks_observed"] == 1


def test_events_summary_after_zmq_tx(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    """Simulate ZMQ rawtx arriving → EventStore updated → API reflects it."""
    main = _setup(monkeypatch, tmp_path)
    main.store.add_tx("deadbeef01")  # type: ignore[attr-defined]
    main.store.add_tx("deadbeef02")  # type: ignore[attr-defined]

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/events/summary")
    assert resp.json()["tx_observed"] == 2


def test_events_latest_includes_txids(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    main.store.add_tx("txabc123")  # type: ignore[attr-defined]

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/events/latest")
    assert resp.status_code == 200
    txids = [t["txid"] for t in resp.json()["txs"]]
    assert "txabc123" in txids


def test_events_latest_includes_block_hash(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    main.store.add_block(_RAW_BLOCK)  # type: ignore[attr-defined]
    expected_hash = main.store.last_block_hash()  # type: ignore[attr-defined]

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/events/latest")
    blocks = resp.json()["blocks"]
    assert len(blocks) == 1
    assert blocks[0]["hash"] == expected_hash


def test_state_comparison_in_sync(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    """ZMQ block hash == RPC getbestblockhash → in_sync, no divergence."""
    main = _setup(monkeypatch, tmp_path)
    main.store.add_block(_RAW_BLOCK)  # type: ignore[attr-defined]
    zmq_hash = main.store.last_block_hash()  # type: ignore[attr-defined]

    monkeypatch.setattr(main, "rpc_from_env", lambda: FakeRPC({"getbestblockhash": zmq_hash}))

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/events/state-comparison")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "compared"
    assert data["divergence"] is False
    assert data["last_seen_block"] == zmq_hash


def test_state_comparison_divergence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    """ZMQ hash differs from RPC → divergence=True."""
    main = _setup(monkeypatch, tmp_path)
    main.store.add_block(_RAW_BLOCK)  # type: ignore[attr-defined]

    monkeypatch.setattr(
        main, "rpc_from_env", lambda: FakeRPC({"getbestblockhash": "totally_different_hash"})
    )

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/events/state-comparison")
    data = resp.json()
    assert data["status"] == "compared"
    assert data["divergence"] is True


def test_state_comparison_waiting_for_first_block(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    """No ZMQ blocks yet → waiting_for_zmq_block status."""
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/events/state-comparison")
    assert resp.json()["status"] == "waiting_for_zmq_block"


def test_state_comparison_503_on_rpc_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    main.store.add_block(_RAW_BLOCK)  # type: ignore[attr-defined]
    RPCConnectionError = importlib.import_module("app.rpc_client").RPCConnectionError
    monkeypatch.setattr(
        main,
        "rpc_from_env",
        lambda: FakeRPC({"getbestblockhash": RPCConnectionError("node offline")}),
    )

    with TestClient(main.app, raise_server_exceptions=False) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/events/state-comparison")
    assert resp.status_code == 503
    assert resp.json()["detail"]["error"] == "node_unavailable"


def test_metrics_includes_zmq_counters(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    """After ZMQ events, /metrics exposes block and tx counters."""
    main = _setup(monkeypatch, tmp_path)
    main.store.add_block(_RAW_BLOCK)  # type: ignore[attr-defined]
    main.store.add_tx("atx")  # type: ignore[attr-defined]

    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "corecraft_zmq_blocks_total" in resp.text
    assert "corecraft_zmq_tx_total" in resp.text
