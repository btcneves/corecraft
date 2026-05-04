from typing import Any

from corecraft import (
    BlockchainLag,
    GetMempoolInfoResponse,
    MempoolSummary,
)

from .rpc_client import BitcoinRPC


def summary(rpc: BitcoinRPC) -> MempoolSummary:
    info: GetMempoolInfoResponse = rpc.call("getmempoolinfo")
    tx_count = info["size"]
    total_vsize = info.get("bytes", 0)

    raw: dict[str, Any] = rpc.call("getrawmempool", True)

    fee_rates: list[float] = []
    dist: dict[str, int] = {"low": 0, "medium": 0, "high": 0}

    for entry_raw in raw.values():
        entry: dict[str, Any] = entry_raw
        fees: dict[str, Any] = entry.get("fees", {})
        fee_btc: float = fees.get("base", entry.get("fee", 0))
        vsize: int = entry.get("vsize", entry.get("size", 1))
        if vsize == 0:
            continue
        rate = (fee_btc * 100_000_000) / vsize
        fee_rates.append(rate)
        if rate < 10:
            dist["low"] += 1
        elif rate <= 50:
            dist["medium"] += 1
        else:
            dist["high"] += 1

    if fee_rates:
        avg = round(sum(fee_rates) / len(fee_rates), 2)
        min_rate = round(min(fee_rates), 2)
        max_rate = round(max(fee_rates), 2)
    else:
        avg = min_rate = max_rate = 0.0

    return {
        "tx_count": tx_count,
        "total_vsize": total_vsize,
        "avg_fee_rate": avg,
        "min_fee_rate": min_rate,
        "max_fee_rate": max_rate,
        "fee_distribution": dist,
    }


def lag(rpc: BitcoinRPC) -> BlockchainLag:
    info: dict[str, Any] = rpc.call("getblockchaininfo")
    blocks = info["blocks"]
    headers = info["headers"]
    return {
        "blocks": blocks,
        "headers": headers,
        "lag": headers - blocks,
    }
