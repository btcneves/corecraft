import hashlib

import pytest

from tests.conftest import import_activity_module


def test_event_store_tracks_blocks_txs_and_limits(monkeypatch: pytest.MonkeyPatch) -> None:
    event_store = import_activity_module("atividade-2", "app.event_store", monkeypatch)
    store = event_store.EventStore(max_blocks=1, max_txs=2)

    raw_block = bytes(range(80))
    expected_hash = hashlib.sha256(hashlib.sha256(raw_block).digest()).digest()[::-1].hex()

    store.add_block(raw_block)
    store.add_tx("tx1")
    store.add_tx("tx2")
    store.add_tx("tx3")
    snapshot = store.snapshot()

    assert store.last_block_hash() == expected_hash
    assert snapshot["blocks_observed"] == 1
    assert snapshot["tx_observed"] == 2
    assert [tx["txid"] for tx in snapshot["txs"]] == ["tx2", "tx3"]
    assert snapshot["last_event_time"] is not None


def test_event_store_tx_rate(monkeypatch: pytest.MonkeyPatch) -> None:
    event_store = import_activity_module("atividade-2", "app.event_store", monkeypatch)
    times = iter([100.0, 102.0])
    monkeypatch.setattr(event_store.time, "time", lambda: next(times))

    store = event_store.EventStore()
    store.add_tx("tx1")
    store.add_tx("tx2")

    assert store.snapshot()["tx_per_second"] == 1.0
