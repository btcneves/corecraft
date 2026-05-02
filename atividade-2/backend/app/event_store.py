import hashlib
import time
from collections import deque
from threading import Lock


def _block_hash(raw: bytes) -> str:
    header = raw[:80]
    h = hashlib.sha256(hashlib.sha256(header).digest()).digest()
    return h[::-1].hex()


class EventStore:
    def __init__(self, max_blocks: int = 20, max_txs: int = 200):
        self._lock = Lock()
        self.blocks: deque = deque(maxlen=max_blocks)
        self.txs: deque = deque(maxlen=max_txs)
        self.last_event_time: float | None = None
        self._total_tx_count: int = 0

    def add_block(self, raw: bytes) -> None:
        ts = time.time()
        block_hash = _block_hash(raw)
        with self._lock:
            self.blocks.append({"hash": block_hash, "ts": ts})
            self.last_event_time = ts

    def add_tx(self, txid: str) -> None:
        ts = time.time()
        with self._lock:
            self.txs.append({"txid": txid, "ts": ts})
            self.last_event_time = ts
            self._total_tx_count += 1

    def snapshot(self) -> dict:
        with self._lock:
            blocks = list(self.blocks)
            txs = list(self.txs)
            last_event_time = self.last_event_time

        tx_per_second = 0.0
        if len(txs) >= 2:
            window = txs[-1]["ts"] - txs[0]["ts"]
            if window > 0:
                tx_per_second = round(len(txs) / window, 2)

        return {
            "blocks": blocks,
            "txs": txs,
            "blocks_observed": len(blocks),
            "tx_observed": len(txs),
            "last_event_time": last_event_time,
            "tx_per_second": tx_per_second,
        }

    def last_block_hash(self) -> str | None:
        with self._lock:
            if self.blocks:
                return self.blocks[-1]["hash"]
        return None
