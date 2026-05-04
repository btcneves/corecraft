from typing import Any

import pytest
import requests

from tests.conftest import FakeResponse, import_activity_module


def test_rpc_client_sends_jsonrpc_2_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-1", "app.rpc_client", monkeypatch)
    captured: dict[str, Any] = {}

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        captured.update({"url": url, "json": json, "auth": auth, "timeout": timeout})
        return FakeResponse({"result": {"chain": "regtest"}, "error": None})

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.BitcoinRPC("node", 18443, "user", "password")

    assert rpc.call("getblockchaininfo") == {"chain": "regtest"}
    assert captured["url"] == "http://node:18443/"
    assert captured["json"] == {
        "jsonrpc": "2.0",
        "id": "getblockchaininfo",
        "method": "getblockchaininfo",
        "params": [],
    }
    assert captured["timeout"] == 10


def test_rpc_client_raises_rpc_error(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-1", "app.rpc_client", monkeypatch)

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        return FakeResponse({"result": None, "error": {"code": -32601, "message": "missing"}})

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.BitcoinRPC("node", 18443, "user", "password")

    with pytest.raises(rpc_client.RPCError) as exc:
        rpc.call("missing")
    assert exc.value.code == -32601


def test_rpc_client_wraps_connection_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-1", "app.rpc_client", monkeypatch)

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        raise requests.exceptions.ConnectionError("offline")

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.BitcoinRPC("node", 18443, "user", "password")

    with pytest.raises(rpc_client.RPCConnectionError):
        rpc.call("getblockchaininfo")


def test_rpc_client_wraps_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-1", "app.rpc_client", monkeypatch)

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        raise requests.exceptions.Timeout("timed out")

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.BitcoinRPC("node", 18443, "user", "password")

    with pytest.raises(rpc_client.RPCConnectionError, match="timed out"):
        rpc.call("getblockchaininfo")


def test_rpc_error_from_data(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-1", "app.rpc_client", monkeypatch)
    err = rpc_client.RPCError.from_data({"code": -5, "message": "invalid address"})
    assert err.code == -5
    assert err.message == "invalid address"
    assert "RPC error -5" in str(err)


def test_rpc_from_env_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-1", "app.rpc_client", monkeypatch)
    monkeypatch.delenv("BTC_RPC_HOST", raising=False)
    monkeypatch.delenv("BTC_RPC_PORT", raising=False)
    monkeypatch.delenv("BTC_RPC_USER", raising=False)
    monkeypatch.delenv("BTC_RPC_PASSWORD", raising=False)

    rpc = rpc_client.rpc_from_env()
    assert rpc._url == "http://127.0.0.1:18443/"


def test_rpc_from_env_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-1", "app.rpc_client", monkeypatch)
    monkeypatch.setenv("BTC_RPC_HOST", "mynode")
    monkeypatch.setenv("BTC_RPC_PORT", "8332")

    rpc = rpc_client.rpc_from_env()
    assert rpc._url == "http://mynode:8332/"
