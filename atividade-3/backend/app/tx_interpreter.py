import time


def interpret(txid: str, wallet_name: str | None, gettx_result: dict | None,
              mempool_entry: dict | None, tracked: dict | None) -> dict:
    """
    Build an interpreted transaction state dict.

    gettx_result: result of gettransaction (wallet RPC), or None if not found / no wallet
    mempool_entry: result of getmempoolentry (node RPC), or None if not in mempool
    tracked: dict with {wallet, broadcast_ts} from in-memory store, or None
    """
    now = time.time()

    confirmations = 0
    block_hash = None
    age_seconds = None
    message = None
    warning = None

    if gettx_result is not None:
        confirmations = gettx_result.get("confirmations", 0)
        block_hash = gettx_result.get("blockhash")

    if tracked:
        age_seconds = round(now - tracked["broadcast_ts"])

    if confirmations > 0:
        status = "confirmed"
        message = "Transação confirmada em bloco."
    elif mempool_entry is not None:
        status = "mempool"
        message = "Transação aceita na mempool, aguardando inclusão em bloco."
        # Try to get a better age from mempool entry
        if age_seconds is None:
            entry_time = mempool_entry.get("time")
            if entry_time:
                age_seconds = round(now - entry_time)
        if age_seconds is not None and age_seconds > 120:
            warning = "Transação está na mempool há mais de 2 minutos."
    elif tracked is not None:
        status = "broadcast"
        message = "Transação enviada ao node, aguardando aceitação na mempool."
    else:
        status = "unknown"
        warning = "Transação não localizada na wallet selecionada."

    result = {
        "txid": txid,
        "wallet": wallet_name,
        "status": status,
        "confirmed": confirmations > 0,
        "confirmations": confirmations,
        "block_hash": block_hash,
        "age_seconds": age_seconds,
        "message": message,
    }
    if warning:
        result["warning"] = warning
    return result
