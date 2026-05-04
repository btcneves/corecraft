import hashlib
import time
from collections import deque
from threading import Lock

from corecraft import BlockEvent, EventStoreSnapshot, TxEvent


def _block_hash(raw: bytes) -> str:
    header = raw[:80]
    h = hashlib.sha256(hashlib.sha256(header).digest()).digest()
    return h[::-1].hex()


class EventStore:
    """Thread-safe store for blockchain events (blocks and transactions)."""

    def __init__(self, max_blocks: int = 20, max_txs: int = 200) -> None:
        self._lock = Lock()
        self.blocks: deque[BlockEvent] = deque(maxlen=max_blocks)
        self.txs: deque[TxEvent] = deque(maxlen=max_txs)
        self.last_event_time: float | None = None
        self._total_tx_count: int = 0

    def add_block(self, raw: bytes) -> None:
        """Add a block event to the store."""
        ts: float = time.time()
        block_hash: str = _block_hash(raw)
        with self._lock:
            self.blocks.append(BlockEvent(hash=block_hash, ts=ts))
            self.last_event_time = ts

    def add_tx(self, txid: str) -> None:
        """Add a transaction event to the store."""
        ts: float = time.time()
        with self._lock:
            self.txs.append(TxEvent(txid=txid, ts=ts))
            self.last_event_time = ts
            self._total_tx_count += 1

    def snapshot(self) -> EventStoreSnapshot:
        with self._lock:
            blocks: list[BlockEvent] = list(self.blocks)
            txs: list[TxEvent] = list(self.txs)
            last_event_time: float | None = self.last_event_time

        tx_per_second: float = 0.0
        if len(txs) >= 2:
            window: float = txs[-1]["ts"] - txs[0]["ts"]
            if window > 0:
                tx_per_second = round(len(txs) / window, 2)

        return EventStoreSnapshot(
            blocks=blocks,
            txs=txs,
            blocks_observed=len(blocks),
            tx_observed=len(txs),
            last_event_time=last_event_time,
            tx_per_second=tx_per_second,
        )

    def last_block_hash(self) -> str | None:
        """Get the hash of the last observed block."""
        with self._lock:
            if self.blocks:
                block_hash: str = self.blocks[-1]["hash"]
                return block_hash
        return None
