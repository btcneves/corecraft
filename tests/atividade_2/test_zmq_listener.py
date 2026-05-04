import importlib
import threading
from typing import Any
from unittest.mock import MagicMock

import pytest

from tests.conftest import FakeRPC, import_activity_module, prepare_activity_import


def test_decode_txid_uses_decoderawtransaction(monkeypatch: pytest.MonkeyPatch) -> None:
    listener = import_activity_module("atividade-2", "app.zmq_listener", monkeypatch)
    rpc = FakeRPC({"decoderawtransaction": {"txid": "abc"}})

    assert listener._decode_txid(b"\x01\x02", rpc) == "abc"
    assert rpc.calls == [("decoderawtransaction", ("0102",))]


def test_decode_txid_returns_none_on_rpc_error(monkeypatch: pytest.MonkeyPatch) -> None:
    listener = import_activity_module("atividade-2", "app.zmq_listener", monkeypatch)
    rpc = FakeRPC({"decoderawtransaction": listener.RPCConnectionError("offline")})

    assert listener._decode_txid(b"\x01", rpc) is None


def test_start_and_stop_manage_listener_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    listener = import_activity_module("atividade-2", "app.zmq_listener", monkeypatch)
    started = threading.Event()

    def fake_run(store: object, rpc: object) -> None:
        started.set()
        listener._stop_event.wait(1)

    monkeypatch.setattr(listener, "_run", fake_run)

    listener.start(object(), object())
    assert started.wait(1)
    listener.stop()
    assert listener._thread is not None
    assert not listener._thread.is_alive()


def _make_zmq_mocks(listener: Any, messages: list[list[bytes]]) -> tuple[Any, Any]:
    """Build fake ZMQ context/socket/poller that delivers `messages` then stops."""
    msg_iter = iter(messages)
    fake_sock = MagicMock()

    def fake_poll(timeout: int) -> dict[Any, Any]:
        try:
            fake_sock.recv_multipart.return_value = next(msg_iter)
            return {fake_sock: listener.zmq.POLLIN}
        except StopIteration:
            listener._stop_event.set()
            return {}

    fake_poller = MagicMock()
    fake_poller.poll.side_effect = fake_poll

    fake_ctx = MagicMock()
    fake_ctx.socket.return_value = fake_sock

    return fake_ctx, fake_poller


def _run_listener(
    listener: Any, store: Any, rpc: Any, fake_ctx: Any, fake_poller: Any, monkeypatch: Any
) -> threading.Thread:
    monkeypatch.setattr(listener.zmq.Context, "instance", lambda: fake_ctx)
    monkeypatch.setattr(listener.zmq, "Poller", lambda: fake_poller)
    listener._stop_event.clear()
    t = threading.Thread(target=listener._run, args=(store, rpc), daemon=True)
    t.start()
    t.join(timeout=3)
    return t


def test_run_processes_rawblock(monkeypatch: pytest.MonkeyPatch) -> None:
    prepare_activity_import("atividade-2", monkeypatch)
    listener = importlib.import_module("app.zmq_listener")
    store = importlib.import_module("app.event_store").EventStore()
    rpc = FakeRPC({})

    fake_ctx, fake_poller = _make_zmq_mocks(listener, [[b"rawblock", bytes(80)]])
    t = _run_listener(listener, store, rpc, fake_ctx, fake_poller, monkeypatch)

    assert not t.is_alive()
    assert store.snapshot()["blocks_observed"] == 1


def test_run_processes_rawtx(monkeypatch: pytest.MonkeyPatch) -> None:
    prepare_activity_import("atividade-2", monkeypatch)
    listener = importlib.import_module("app.zmq_listener")
    store = importlib.import_module("app.event_store").EventStore()
    rpc = FakeRPC({"decoderawtransaction": {"txid": "deadbeef"}})

    fake_ctx, fake_poller = _make_zmq_mocks(listener, [[b"rawtx", b"\xde\xad"]])
    t = _run_listener(listener, store, rpc, fake_ctx, fake_poller, monkeypatch)

    assert not t.is_alive()
    assert store.snapshot()["tx_observed"] == 1
    assert store.snapshot()["txs"][0]["txid"] == "deadbeef"


def test_run_skips_short_multipart(monkeypatch: pytest.MonkeyPatch) -> None:
    prepare_activity_import("atividade-2", monkeypatch)
    listener = importlib.import_module("app.zmq_listener")
    store = importlib.import_module("app.event_store").EventStore()
    rpc = FakeRPC({})

    # Only one part — malformed message, should be silently skipped
    fake_ctx, fake_poller = _make_zmq_mocks(listener, [[b"rawblock"]])
    t = _run_listener(listener, store, rpc, fake_ctx, fake_poller, monkeypatch)

    assert not t.is_alive()
    assert store.snapshot()["blocks_observed"] == 0


def test_run_skips_rawtx_with_null_txid(monkeypatch: pytest.MonkeyPatch) -> None:
    prepare_activity_import("atividade-2", monkeypatch)
    listener = importlib.import_module("app.zmq_listener")
    store = importlib.import_module("app.event_store").EventStore()
    rpc = FakeRPC({"decoderawtransaction": {"txid": None}})

    fake_ctx, fake_poller = _make_zmq_mocks(listener, [[b"rawtx", b"\x00"]])
    t = _run_listener(listener, store, rpc, fake_ctx, fake_poller, monkeypatch)

    assert not t.is_alive()
    assert store.snapshot()["tx_observed"] == 0
