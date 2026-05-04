from typing import Any

import pytest
import requests

from tests.conftest import FakeResponse, import_activity_module


def test_rpc_call_returns_result(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-2", "app.rpc_client", monkeypatch)

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        return FakeResponse({"result": "bestblockhash", "error": None})

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.BitcoinRPC("node", 18443, "user", "password")
    assert rpc.call("getbestblockhash") == "bestblockhash"


def test_rpc_raises_rpc_error(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-2", "app.rpc_client", monkeypatch)

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        return FakeResponse({"result": None, "error": {"code": -28, "message": "warming up"}})

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.BitcoinRPC("node", 18443, "user", "password")

    with pytest.raises(rpc_client.RPCError) as exc:
        rpc.call("getbestblockhash")
    assert exc.value.code == -28


def test_rpc_wraps_connection_error(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-2", "app.rpc_client", monkeypatch)

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        raise requests.exceptions.ConnectionError("down")

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.BitcoinRPC("node", 18443, "user", "password")
    with pytest.raises(rpc_client.RPCConnectionError):
        rpc.call("getbestblockhash")


def test_rpc_wraps_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-2", "app.rpc_client", monkeypatch)

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        raise requests.exceptions.Timeout("timed out")

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.BitcoinRPC("node", 18443, "user", "password")
    with pytest.raises(rpc_client.RPCConnectionError, match="timed out"):
        rpc.call("getbestblockhash")


def test_rpc_error_from_data(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-2", "app.rpc_client", monkeypatch)
    err = rpc_client.RPCError.from_data({"code": -4, "message": "insufficient funds"})
    assert err.code == -4
    assert "insufficient funds" in str(err)


def test_rpc_from_env_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-2", "app.rpc_client", monkeypatch)
    monkeypatch.delenv("BTC_RPC_HOST", raising=False)
    monkeypatch.delenv("BTC_RPC_PORT", raising=False)
    monkeypatch.delenv("BTC_RPC_USER", raising=False)
    monkeypatch.delenv("BTC_RPC_PASSWORD", raising=False)

    rpc = rpc_client.rpc_from_env()
    assert rpc._url == "http://127.0.0.1:18443/"


def test_rpc_from_env_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-2", "app.rpc_client", monkeypatch)
    monkeypatch.setenv("BTC_RPC_HOST", "bitcoind")
    monkeypatch.setenv("BTC_RPC_PORT", "18443")

    rpc = rpc_client.rpc_from_env()
    assert "bitcoind" in rpc._url
