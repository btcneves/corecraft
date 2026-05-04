import pytest
from fastapi import HTTPException

from tests.conftest import import_activity_module


def test_activity_1_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    main = import_activity_module("atividade-1", "app.main", monkeypatch)

    monkeypatch.setattr(main, "rpc_from_env", lambda: object())
    monkeypatch.setattr(
        main,
        "summary",
        lambda rpc: {"tx_count": 1, "total_vsize": 141, "fee_distribution": {}},
    )
    monkeypatch.setattr(main, "lag", lambda rpc: {"blocks": 10, "headers": 11, "lag": 1})

    assert main.mempool_summary()["tx_count"] == 1
    assert main.blockchain_lag()["lag"] == 1
    assert main.health() == {"status": "ok", "service": "atividade-1"}
    assert "corecraft_service_up" in main.metrics()


def test_activity_1_rpc_error_returns_503(monkeypatch: pytest.MonkeyPatch) -> None:
    main = import_activity_module("atividade-1", "app.main", monkeypatch)

    def raise_rpc_error(rpc: object) -> None:
        raise main.RPCError(-1, "boom")

    monkeypatch.setattr(main, "rpc_from_env", lambda: object())
    monkeypatch.setattr(main, "summary", raise_rpc_error)

    with pytest.raises(HTTPException) as exc_info:
        main.mempool_summary()

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail["error"] == "rpc_error"
