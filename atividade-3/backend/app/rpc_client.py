import os
import requests
from requests.auth import HTTPBasicAuth


class RPCError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"RPC error {code}: {message}")


class RPCConnectionError(Exception):
    pass


class BitcoinRPC:
    def __init__(self, host: str, port: int, user: str, password: str, wallet: str | None = None):
        base = f"http://{host}:{port}"
        self._url = f"{base}/wallet/{wallet}" if wallet else f"{base}/"
        self._auth = HTTPBasicAuth(user, password)

    def call(self, method: str, *params):
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


def _base_params() -> dict:
    return {
        "host": os.getenv("BTC_RPC_HOST", "127.0.0.1"),
        "port": int(os.getenv("BTC_RPC_PORT", "18443")),
        "user": os.getenv("BTC_RPC_USER", "user"),
        "password": os.getenv("BTC_RPC_PASSWORD", "password"),
    }


def rpc_node() -> BitcoinRPC:
    return BitcoinRPC(**_base_params())


def rpc_wallet(wallet_name: str) -> BitcoinRPC:
    return BitcoinRPC(**_base_params(), wallet=wallet_name)
