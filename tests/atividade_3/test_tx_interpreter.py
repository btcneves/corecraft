import pytest

from tests.conftest import import_activity_module


def test_tx_interpreter_confirmed(monkeypatch: pytest.MonkeyPatch) -> None:
    tx_interpreter = import_activity_module("atividade-3", "app.tx_interpreter", monkeypatch)
    result = tx_interpreter.interpret(
        "txid",
        "wallet1",
        {"confirmations": 2, "blockhash": "block"},
        None,
        {"wallet": "wallet1", "broadcast_ts": 90.0},
    )
    assert result["status"] == "confirmed"
    assert result["confirmed"] is True
    assert result["block_hash"] == "block"


def test_tx_interpreter_mempool_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    tx_interpreter = import_activity_module("atividade-3", "app.tx_interpreter", monkeypatch)
    monkeypatch.setattr(tx_interpreter.time, "time", lambda: 300.0)

    result = tx_interpreter.interpret("txid", "wallet1", None, {"time": 100.0}, None)

    assert result["status"] == "mempool"
    assert result["age_seconds"] == 200
    assert "warning" in result


def test_tx_interpreter_broadcast_and_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    tx_interpreter = import_activity_module("atividade-3", "app.tx_interpreter", monkeypatch)

    broadcast = tx_interpreter.interpret(
        "txid", "wallet1", None, None, {"wallet": "wallet1", "broadcast_ts": 1.0}
    )
    unknown = tx_interpreter.interpret("txid", None, None, None, None)

    assert broadcast["status"] == "broadcast"
    assert unknown["status"] == "unknown"
