from typing import Any

from .event_store import EventStore
from .rpc_client import BitcoinRPC

JsonDict = dict[str, Any]


def get_summary(store: EventStore) -> JsonDict:
    snap = store.snapshot()
    return {
        "blocks_observed": snap["blocks_observed"],
        "tx_observed": snap["tx_observed"],
        "last_event_time": snap["last_event_time"],
        "tx_per_second": snap["tx_per_second"],
    }


def get_latest(store: EventStore) -> JsonDict:
    snap = store.snapshot()
    return {
        "blocks": snap["blocks"][-20:],
        "txs": snap["txs"][-20:],
    }


def get_state_comparison(store: EventStore, rpc: BitcoinRPC) -> JsonDict:
    best_block = rpc.call("getbestblockhash")
    last_seen = store.last_block_hash()

    if last_seen is None:
        return {
            "best_block": best_block,
            "last_seen_block": None,
            "divergence": None,
            "status": "waiting_for_zmq_block",
            "message": "Nenhum bloco observado via ZMQ ainda.",
        }

    return {
        "best_block": best_block,
        "last_seen_block": last_seen,
        "divergence": best_block != last_seen,
        "status": "compared",
    }
