from typing import Any

import pytest
import requests

from tests.conftest import FakeResponse, import_activity_module


def test_rpc_node_url_has_no_wallet(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-3", "app.rpc_client", monkeypatch)
    monkeypatch.setenv("BTC_RPC_HOST", "node")
    monkeypatch.setenv("BTC_RPC_PORT", "18443")

    rpc = rpc_client.rpc_node()
    assert rpc._url == "http://node:18443/"


def test_rpc_wallet_url_includes_wallet_name(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-3", "app.rpc_client", monkeypatch)
    monkeypatch.setenv("BTC_RPC_HOST", "node")
    monkeypatch.setenv("BTC_RPC_PORT", "18443")

    rpc = rpc_client.rpc_wallet("mywallet")
    assert rpc._url == "http://node:18443/wallet/mywallet"


def test_rpc_base_params_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-3", "app.rpc_client", monkeypatch)
    monkeypatch.setenv("BTC_RPC_HOST", "remotenode")
    monkeypatch.setenv("BTC_RPC_PORT", "8332")
    monkeypatch.setenv("BTC_RPC_USER", "admin")
    monkeypatch.setenv("BTC_RPC_PASSWORD", "secret")

    params = rpc_client._base_params()
    assert params == {"host": "remotenode", "port": 8332, "user": "admin", "password": "secret"}


def test_rpc_call_returns_result(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-3", "app.rpc_client", monkeypatch)

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        return FakeResponse({"result": {"txid": "abc"}, "error": None})

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.rpc_wallet("wallet1")
    assert rpc.call("gettransaction", "abc") == {"txid": "abc"}


def test_rpc_raises_rpc_error(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-3", "app.rpc_client", monkeypatch)

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        return FakeResponse({"result": None, "error": {"code": -5, "message": "invalid"}})

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.rpc_node()

    with pytest.raises(rpc_client.RPCError) as exc:
        rpc.call("sendrawtransaction", "hex")
    assert exc.value.code == -5


def test_rpc_wraps_connection_error(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-3", "app.rpc_client", monkeypatch)

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        raise requests.exceptions.ConnectionError("down")

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.rpc_node()
    with pytest.raises(rpc_client.RPCConnectionError):
        rpc.call("getblockchaininfo")


def test_rpc_wraps_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-3", "app.rpc_client", monkeypatch)

    def fake_post(url: str, json: dict[str, Any], auth: Any, timeout: int) -> FakeResponse:
        raise requests.exceptions.Timeout("timeout")

    monkeypatch.setattr(rpc_client.requests, "post", fake_post)
    rpc = rpc_client.rpc_node()
    with pytest.raises(rpc_client.RPCConnectionError, match="timeout"):
        rpc.call("getblockchaininfo")


def test_rpc_error_from_data(monkeypatch: pytest.MonkeyPatch) -> None:
    rpc_client = import_activity_module("atividade-3", "app.rpc_client", monkeypatch)
    err = rpc_client.RPCError.from_data({"code": -6, "message": "insufficient funds"})
    assert err.code == -6
    assert "insufficient funds" in str(err)
