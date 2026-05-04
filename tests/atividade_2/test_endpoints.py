import pytest
from fastapi import HTTPException

from tests.conftest import FakeRPC, import_activity_module


def test_activity_2_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    main = import_activity_module("atividade-2", "app.main", monkeypatch)
    main.store.add_tx("tx1")

    monkeypatch.setattr(
        main,
        "rpc_from_env",
        lambda: FakeRPC({"getbestblockhash": "best"}),
    )

    assert main.events_summary()["tx_observed"] == 1
    assert main.events_latest()["txs"][0]["txid"] == "tx1"
    comparison = main.events_state_comparison()
    assert comparison["status"] == "waiting_for_zmq_block"
    assert main.health()["service"] == "atividade-2"
    assert "corecraft_service_up" in main.metrics()


def test_activity_2_state_comparison_rpc_error(monkeypatch: pytest.MonkeyPatch) -> None:
    main = import_activity_module("atividade-2", "app.main", monkeypatch)
    monkeypatch.setattr(
        main,
        "rpc_from_env",
        lambda: FakeRPC({"getbestblockhash": main.RPCConnectionError("offline")}),
    )

    with pytest.raises(HTTPException) as exc_info:
        main.events_state_comparison()

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail["error"] == "node_unavailable"
