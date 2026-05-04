import os
from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from corecraft import RPCErrorData

JsonValue = Any


class RPCError(Exception):
    """Exception raised for Bitcoin RPC errors."""

    def __init__(self, code: int, message: str) -> None:
        self.code: int = code
        self.message: str = message
        super().__init__(f"RPC error {code}: {message}")

    @classmethod
    def from_data(cls, data: RPCErrorData) -> "RPCError":
        """Create an RPCError from RPC error data."""
        return cls(code=data["code"], message=data["message"])


class RPCConnectionError(Exception):
    pass


class BitcoinRPC:
    def __init__(self, host: str, port: int, user: str, password: str) -> None:
        self._url = f"http://{host}:{port}/"
        self._auth = HTTPBasicAuth(user, password)

    def call(self, method: str, *params: JsonValue) -> JsonValue:
        payload = {"jsonrpc": "2.0", "id": method, "method": method, "params": list(params)}
        try:
            resp = requests.post(self._url, json=payload, auth=self._auth, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            raise RPCConnectionError(f"Cannot connect to Bitcoin node: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            raise RPCConnectionError(f"Bitcoin node timed out: {exc}") from exc

        data = resp.json()
        if data.get("error"):
            err = data["error"]
            raise RPCError(err.get("code", -1), err.get("message", "unknown"))
        return data["result"]


def rpc_from_env() -> BitcoinRPC:
    return BitcoinRPC(
        host=os.getenv("BTC_RPC_HOST", "127.0.0.1"),
        port=int(os.getenv("BTC_RPC_PORT", "18443")),
        user=os.getenv("BTC_RPC_USER", "user"),
        password=os.getenv("BTC_RPC_PASSWORD", "password"),
    )
