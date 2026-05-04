from typing import Any

import pytest

from tests.conftest import FakeRPC, import_activity_module


def test_wallet_service_lists_and_selects_wallet(monkeypatch: pytest.MonkeyPatch) -> None:
    service = import_activity_module("atividade-3", "app.wallet_service", monkeypatch)
    node_rpc = FakeRPC(
        {
            "listwalletdir": {"wallets": [{"name": "wallet1"}]},
            "listwallets": [],
            "loadwallet": {},
        }
    )
    wallet_rpc = FakeRPC({"getwalletinfo": {"walletname": "wallet1", "balance": 2.0, "txcount": 4}})
    monkeypatch.setattr(service, "rpc_wallet", lambda name: wallet_rpc)
    state: dict[str, Any] = {}

    assert service.list_wallets(node_rpc, state)["available_wallets"] == ["wallet1"]
    selected = service.select_wallet("wallet1", node_rpc, state)

    assert selected["selected_wallet"] == "wallet1"
    assert state["selected_wallet"] == "wallet1"
    assert ("loadwallet", ("wallet1",)) in node_rpc.calls


def test_wallet_status_uses_getbalances_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    service = import_activity_module("atividade-3", "app.wallet_service", monkeypatch)
    wallet_rpc = FakeRPC(
        {
            "getwalletinfo": {"walletname": "wallet1"},
            "listunspent": [{}, {}],
            "getbalances": {
                "mine": {
                    "trusted": 1.5,
                    "untrusted_pending": 0.2,
                    "immature": 0.0,
                }
            },
        }
    )
    monkeypatch.setattr(service, "rpc_wallet", lambda name: wallet_rpc)

    status = service.wallet_status("wallet1")

    assert status["balance"] == 1.5
    assert status["utxos"] == 2
    assert status["untrusted_pending"] == 0.2


def test_tx_service_sends_psbt_and_tracks_tx(monkeypatch: pytest.MonkeyPatch) -> None:
    service = import_activity_module("atividade-3", "app.tx_service", monkeypatch)
    wallet_rpc = FakeRPC(
        {
            "walletcreatefundedpsbt": {"psbt": "base64-psbt"},
            "walletprocesspsbt": {"psbt": "signed-psbt"},
            "finalizepsbt": {"complete": True, "hex": "deadbeef"},
        }
    )
    node_rpc = FakeRPC({"sendrawtransaction": "txid"})
    monkeypatch.setattr(service, "rpc_wallet", lambda name: wallet_rpc)
    monkeypatch.setattr(service, "rpc_node", lambda: node_rpc)
    tracked: dict[str, Any] = {}

    result = service.send_tx("bcrt1qtest", 0.001, "wallet1", tracked)

    assert result == {"txid": "txid", "wallet": "wallet1", "status": "broadcast"}
    assert tracked["txid"]["wallet"] == "wallet1"


def test_tx_service_rejects_incomplete_psbt(monkeypatch: pytest.MonkeyPatch) -> None:
    service = import_activity_module("atividade-3", "app.tx_service", monkeypatch)
    wallet_rpc = FakeRPC(
        {
            "walletcreatefundedpsbt": {"psbt": "base64-psbt"},
            "walletprocesspsbt": {"psbt": "signed-psbt"},
            "finalizepsbt": {"complete": False},
        }
    )
    monkeypatch.setattr(service, "rpc_wallet", lambda name: wallet_rpc)
    monkeypatch.setattr(service, "rpc_node", lambda: FakeRPC({}))

    with pytest.raises(ValueError, match="PSBT finalization incomplete"):
        service.send_tx("bcrt1qtest", 0.001, "wallet1", {})


def test_tx_service_gets_wallet_and_mempool_state(monkeypatch: pytest.MonkeyPatch) -> None:
    service = import_activity_module("atividade-3", "app.tx_service", monkeypatch)
    wallet_rpc = FakeRPC({"gettransaction": {"confirmations": 0}})
    node_rpc = FakeRPC({"getmempoolentry": {"fees": {"base": 0.00001}, "vsize": 100}})
    monkeypatch.setattr(service, "rpc_wallet", lambda name: wallet_rpc)
    monkeypatch.setattr(service, "rpc_node", lambda: node_rpc)

    result = service.get_tx("txid", "wallet1", {"txid": {"wallet": "wallet1", "broadcast_ts": 1.0}})

    assert result["wallet"] == "wallet1"
    assert result["confirmed"] is False
    assert result["status"] == "mempool"
