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


def test_tx_service_get_tx_unknown_when_not_in_mempool(monkeypatch: pytest.MonkeyPatch) -> None:
    service = import_activity_module("atividade-3", "app.tx_service", monkeypatch)
    # gettransaction raises RPCError (wallet doesn't know the tx)
    # getmempoolentry also raises RPCError (not in mempool)
    wallet_rpc = FakeRPC({"gettransaction": service.RPCError(-5, "not found")})
    node_rpc = FakeRPC({"getmempoolentry": service.RPCError(-5, "not in mempool")})
    monkeypatch.setattr(service, "rpc_wallet", lambda name: wallet_rpc)
    monkeypatch.setattr(service, "rpc_node", lambda: node_rpc)

    result = service.get_tx("txid", "wallet1", {})

    assert result["status"] == "unknown"
    assert result["confirmed"] is False


def test_tx_service_get_tx_confirmed(monkeypatch: pytest.MonkeyPatch) -> None:
    service = import_activity_module("atividade-3", "app.tx_service", monkeypatch)
    wallet_rpc = FakeRPC({"gettransaction": {"confirmations": 3, "blockhash": "abc123"}})
    node_rpc = FakeRPC({"getmempoolentry": service.RPCError(-5, "not in mempool")})
    monkeypatch.setattr(service, "rpc_wallet", lambda name: wallet_rpc)
    monkeypatch.setattr(service, "rpc_node", lambda: node_rpc)

    result = service.get_tx("txid", "wallet1", {})

    assert result["status"] == "confirmed"
    assert result["confirmed"] is True
    assert result["confirmations"] == 3


def test_wallet_service_select_already_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    service = import_activity_module("atividade-3", "app.wallet_service", monkeypatch)
    # wallet1 is already loaded — loadwallet should NOT be called
    node_rpc = FakeRPC(
        {
            "listwalletdir": {"wallets": [{"name": "wallet1"}]},
            "listwallets": ["wallet1"],
        }
    )
    wallet_rpc = FakeRPC({"getwalletinfo": {"walletname": "wallet1", "balance": 5.0, "txcount": 2}})
    monkeypatch.setattr(service, "rpc_wallet", lambda name: wallet_rpc)
    state: dict[str, Any] = {}

    result = service.select_wallet("wallet1", node_rpc, state)

    assert result["selected_wallet"] == "wallet1"
    assert ("loadwallet", ("wallet1",)) not in node_rpc.calls


def test_wallet_service_select_raises_for_missing_wallet(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = import_activity_module("atividade-3", "app.wallet_service", monkeypatch)
    node_rpc = FakeRPC(
        {
            "listwalletdir": {"wallets": [{"name": "wallet1"}]},
            "listwallets": [],
        }
    )
    monkeypatch.setattr(service, "rpc_wallet", lambda name: FakeRPC({}))
    state: dict[str, Any] = {}

    with pytest.raises(ValueError, match="not found"):
        service.select_wallet("nonexistent", node_rpc, state)


def test_wallet_status_with_direct_balance(monkeypatch: pytest.MonkeyPatch) -> None:
    service = import_activity_module("atividade-3", "app.wallet_service", monkeypatch)
    wallet_rpc = FakeRPC(
        {
            "getwalletinfo": {"walletname": "wallet1", "balance": 3.0},
            "listunspent": [{}],
        }
    )
    monkeypatch.setattr(service, "rpc_wallet", lambda name: wallet_rpc)

    status = service.wallet_status("wallet1")

    assert status["balance"] == 3.0
    assert status["utxos"] == 1
    assert status["trusted_balance"] == 3.0
