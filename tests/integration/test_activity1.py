"""
Integration tests for Activity 1 — full HTTP stack via TestClient.

These tests exercise the complete request path: middleware → route handler →
service layer → response serialization, using mocked Bitcoin Core RPC.
"""

import importlib

import pytest
from starlette.testclient import TestClient

from tests.conftest import FakeRPC, prepare_activity_import


def _setup(monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory) -> object:
    (tmp_path / "index.html").write_text("<html></html>")  # type: ignore[attr-defined]
    monkeypatch.setenv("FRONTEND_DIR", str(tmp_path))
    prepare_activity_import("atividade-1", monkeypatch)
    return importlib.import_module("app.main")


_MEMPOOL_RPC = {
    "getmempoolinfo": {"size": 3, "bytes": 1500},
    "getrawmempool": ["tx1", "tx2", "tx3"],
    "getrawtransaction": {
        "txid": "tx1",
        "vsize": 141,
        "fees": {"base": 0.00001},
    },
    "getmempoolentry": {
        "vsize": 141,
        "fees": {"base": 0.00001},
        "fee": 0.00001,
        "time": 1700000000,
        "descendantcount": 1,
    },
    "getblockchaininfo": {"blocks": 200, "headers": 201},
}


def test_health_returns_ok(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "atividade-1"}


def test_metrics_prometheus_format(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.text
    assert "corecraft_service_up" in body
    assert "corecraft_requests_total" in body
    assert "corecraft_service_uptime_seconds" in body


def test_correlation_id_propagated(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/health", headers={"X-Correlation-ID": "test-corr-123"})
    assert resp.headers.get("X-Correlation-ID") == "test-corr-123"


def test_correlation_id_generated_when_absent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/health")
    assert "X-Correlation-ID" in resp.headers
    assert len(resp.headers["X-Correlation-ID"]) > 0


def test_mempool_summary_returns_200(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    monkeypatch.setattr(
        main,
        "rpc_from_env",
        lambda: FakeRPC({"getrawmempool": ["tx1"]}),
    )
    monkeypatch.setattr(
        main,
        "summary",
        lambda rpc: {
            "tx_count": 1,
            "total_vsize": 141,
            "avg_fee_rate": 70.9,
            "min_fee_rate": 70.9,
            "max_fee_rate": 70.9,
            "fee_distribution": {"1-5": 0, "5-10": 1},
        },
    )
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/mempool/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tx_count"] == 1
    assert "fee_distribution" in data


def test_blockchain_lag_returns_200(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    monkeypatch.setattr(main, "rpc_from_env", lambda: FakeRPC({}))
    monkeypatch.setattr(
        main,
        "lag",
        lambda rpc: {"blocks": 200, "headers": 201, "lag": 1},
    )
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/blockchain/lag")
    assert resp.status_code == 200
    assert resp.json()["lag"] == 1


def test_mempool_summary_503_on_rpc_connection_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    RPCConnectionError = main.RPCConnectionError  # type: ignore[attr-defined]
    monkeypatch.setattr(
        main,
        "rpc_from_env",
        lambda: FakeRPC({"getrawmempool": RPCConnectionError("node offline")}),
    )
    monkeypatch.setattr(
        main,
        "summary",
        lambda rpc: (_ for _ in ()).throw(RPCConnectionError("node offline")),
    )
    with TestClient(main.app, raise_server_exceptions=False) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/mempool/summary")
    assert resp.status_code == 503
    assert resp.json()["detail"]["error"] == "node_unavailable"


def test_mempool_summary_503_on_rpc_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    RPCError = main.RPCError  # type: ignore[attr-defined]
    monkeypatch.setattr(
        main,
        "summary",
        lambda rpc: (_ for _ in ()).throw(RPCError(-1, "method not found")),
    )
    monkeypatch.setattr(main, "rpc_from_env", lambda: object())
    with TestClient(main.app, raise_server_exceptions=False) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/mempool/summary")
    assert resp.status_code == 503
    assert resp.json()["detail"]["error"] == "rpc_error"


def test_blockchain_lag_503_on_rpc_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    RPCConnectionError = main.RPCConnectionError  # type: ignore[attr-defined]
    monkeypatch.setattr(
        main,
        "lag",
        lambda rpc: (_ for _ in ()).throw(RPCConnectionError("offline")),
    )
    monkeypatch.setattr(main, "rpc_from_env", lambda: object())
    with TestClient(main.app, raise_server_exceptions=False) as client:  # type: ignore[attr-defined]
        resp = client.get("/api/blockchain/lag")
    assert resp.status_code == 503


def test_requests_total_increments(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    main = _setup(monkeypatch, tmp_path)
    with TestClient(main.app) as client:  # type: ignore[attr-defined]
        for _ in range(3):
            client.get("/health")
        resp = client.get("/metrics")
    assert "corecraft_requests_total" in resp.text
    # At least 4 requests (3 health + 1 metrics)
    import re

    match = re.search(r"corecraft_requests_total\{[^}]+\} (\d+)", resp.text)
    assert match and int(match.group(1)) >= 4
