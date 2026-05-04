import pytest
from fastapi import HTTPException

from tests.conftest import import_activity_module


def test_activity_3_wallet_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    main = import_activity_module("atividade-3", "app.main", monkeypatch)

    monkeypatch.setattr(
        main,
        "list_wallets",
        lambda rpc, state: {
            "available_wallets": ["wallet1"],
            "loaded_wallets": ["wallet1"],
            "selected_wallet": state.get("selected_wallet"),
        },
    )
    monkeypatch.setattr(
        main,
        "select_wallet",
        lambda wallet, rpc, state: state.update({"selected_wallet": wallet})
        or {"selected_wallet": wallet, "wallet_info": {"walletname": wallet}},
    )
    monkeypatch.setattr(
        main,
        "wallet_status",
        lambda name: {"wallet": name, "balance": 1.0, "utxos": 1},
    )
    monkeypatch.setattr(main, "rpc_node", lambda: object())

    assert main.wallets()["available_wallets"] == ["wallet1"]
    assert (
        main.wallet_select(main.SelectWalletRequest(wallet="wallet1"))["selected_wallet"]
        == "wallet1"
    )
    assert main.wallet_status_route()["balance"] == 1.0
    assert main.health()["service"] == "atividade-3"
    assert "corecraft_service_up" in main.metrics()


def test_activity_3_tx_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    main = import_activity_module("atividade-3", "app.main", monkeypatch)
    main.state["selected_wallet"] = "wallet1"

    monkeypatch.setattr(
        main,
        "send_tx",
        lambda address, amount, wallet, tracked: tracked.update(
            {"txid": {"wallet": wallet, "broadcast_ts": 1.0}}
        )
        or {"txid": "txid", "wallet": wallet, "status": "broadcast"},
    )
    monkeypatch.setattr(
        main,
        "get_tx",
        lambda txid, wallet, tracked: {
            "txid": txid,
            "wallet": wallet,
            "status": "mempool",
            "confirmed": False,
        },
    )

    sent = main.tx_send(main.SendTxRequest(to_address="bcrt1qtest", amount=0.001))
    assert sent["status"] == "broadcast"
    assert main.tx_status("txid")["status"] == "mempool"


def test_activity_3_requires_wallet(monkeypatch: pytest.MonkeyPatch) -> None:
    main = import_activity_module("atividade-3", "app.main", monkeypatch)
    main.state["selected_wallet"] = None

    with pytest.raises(HTTPException) as exc_info:
        main.wallet_status_route()

    assert exc_info.value.status_code == 409
