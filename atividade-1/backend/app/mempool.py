from typing import Any

from .rpc_client import BitcoinRPC

JsonDict = dict[str, Any]


def summary(rpc: BitcoinRPC) -> JsonDict:
    info = rpc.call("getmempoolinfo")
    tx_count = info["size"]
    total_vsize = info.get("bytes", 0)

    raw = rpc.call("getrawmempool", True)

    fee_rates = []
    dist = {"low": 0, "medium": 0, "high": 0}

    for entry in raw.values():
        fees = entry.get("fees", {})
        fee_btc = fees.get("base", entry.get("fee", 0))
        vsize = entry.get("vsize", entry.get("size", 1))
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


def lag(rpc: BitcoinRPC) -> JsonDict:
    info = rpc.call("getblockchaininfo")
    blocks = info["blocks"]
    headers = info["headers"]
    return {
        "blocks": blocks,
        "headers": headers,
        "lag": headers - blocks,
    }
