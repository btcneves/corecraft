import threading

import pytest

from tests.conftest import FakeRPC, import_activity_module


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
