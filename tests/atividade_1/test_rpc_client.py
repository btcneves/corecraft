from typing import Any

import pytest
import requests

from tests.conftest import import_activity_module


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def json(self) -> dict[str, Any]:
        return self.payload


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
