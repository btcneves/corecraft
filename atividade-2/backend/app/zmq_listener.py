import logging
import os
import threading

import zmq

from .event_store import EventStore
from .rpc_client import BitcoinRPC, RPCConnectionError, RPCError

logger = logging.getLogger(__name__)

_stop_event = threading.Event()
_thread: threading.Thread | None = None


def _decode_txid(raw: bytes, rpc: BitcoinRPC) -> str | None:
    """Resolve txid via RPC decoderawtransaction (handles witness serialization correctly)."""
    try:
        result = rpc.call("decoderawtransaction", raw.hex())
        if isinstance(result, dict):
            txid = result.get("txid")
            return str(txid) if txid is not None else None
        return None
    except (RPCError, RPCConnectionError) as exc:
        logger.warning("decoderawtransaction failed: %s", exc)
        return None


def _run(store: EventStore, rpc: BitcoinRPC) -> None:
    block_ep = os.getenv("ZMQ_RAWBLOCK_ENDPOINT", "tcp://127.0.0.1:28332")
    tx_ep = os.getenv("ZMQ_RAWTX_ENDPOINT", "tcp://127.0.0.1:28333")
    reconnect_delay = 1.0

    ctx = zmq.Context.instance()
    logger.info("ZMQ listener started (%s | %s)", block_ep, tx_ep)

    while not _stop_event.is_set():
        sock = ctx.socket(zmq.SUB)
        poller = zmq.Poller()

        try:
            sock.setsockopt(zmq.SUBSCRIBE, b"rawblock")
            sock.setsockopt(zmq.SUBSCRIBE, b"rawtx")
            sock.setsockopt(zmq.RCVTIMEO, 500)
            sock.connect(block_ep)
            sock.connect(tx_ep)
            poller.register(sock, zmq.POLLIN)
            reconnect_delay = 1.0

            while not _stop_event.is_set():
                try:
                    socks = dict(poller.poll(500))
                except zmq.ZMQError as exc:
                    logger.warning("ZMQ poll error: %s", exc)
                    break

                if sock not in socks:
                    continue

                try:
                    parts = sock.recv_multipart()
                except zmq.ZMQError as exc:
                    logger.warning("ZMQ recv error: %s", exc)
                    break

                if len(parts) < 2:
                    continue

                topic = parts[0]
                body = parts[1]

                if topic == b"rawblock":
                    store.add_block(body)
                    logger.debug("block received, hash=%s", store.last_block_hash())
                elif topic == b"rawtx":
                    txid = _decode_txid(body, rpc)
                    if txid:
                        store.add_tx(txid)
                        logger.debug("tx received: %s", txid)
        finally:
            try:
                poller.unregister(sock)
            except (KeyError, zmq.ZMQError):
                pass
            sock.close(linger=0)

        if not _stop_event.is_set():
            logger.info("Reconnecting ZMQ listener in %.1fs", reconnect_delay)
            _stop_event.wait(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 30.0)

    logger.info("ZMQ listener stopped")


def start(store: EventStore, rpc: BitcoinRPC) -> None:
    global _thread
    _stop_event.clear()
    _thread = threading.Thread(target=_run, args=(store, rpc), daemon=True, name="zmq-listener")
    _thread.start()


def stop() -> None:
    _stop_event.set()
    if _thread:
        _thread.join(timeout=3)
