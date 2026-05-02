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
        return result.get("txid")
    except (RPCError, RPCConnectionError) as exc:
        logger.warning("decoderawtransaction failed: %s", exc)
        return None


def _run(store: EventStore, rpc: BitcoinRPC) -> None:
    block_ep = os.getenv("ZMQ_RAWBLOCK_ENDPOINT", "tcp://127.0.0.1:28332")
    tx_ep    = os.getenv("ZMQ_RAWTX_ENDPOINT",    "tcp://127.0.0.1:28333")

    ctx = zmq.Context.instance()
    sock = ctx.socket(zmq.SUB)
    sock.connect(block_ep)
    sock.connect(tx_ep)
    sock.setsockopt(zmq.SUBSCRIBE, b"rawblock")
    sock.setsockopt(zmq.SUBSCRIBE, b"rawtx")
    sock.setsockopt(zmq.RCVTIMEO, 500)

    logger.info("ZMQ listener started (%s | %s)", block_ep, tx_ep)

    poller = zmq.Poller()
    poller.register(sock, zmq.POLLIN)

    while not _stop_event.is_set():
        try:
            socks = dict(poller.poll(500))
        except zmq.ZMQError:
            break

        if sock not in socks:
            continue

        try:
            parts = sock.recv_multipart()
        except zmq.ZMQError as exc:
            logger.warning("ZMQ recv error: %s", exc)
            continue

        if len(parts) < 2:
            continue

        topic = parts[0]
        body  = parts[1]

        if topic == b"rawblock":
            store.add_block(body)
            logger.debug("block received, hash=%s", store.last_block_hash())
        elif topic == b"rawtx":
            txid = _decode_txid(body, rpc)
            if txid:
                store.add_tx(txid)
                logger.debug("tx received: %s", txid)

    sock.close()
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
