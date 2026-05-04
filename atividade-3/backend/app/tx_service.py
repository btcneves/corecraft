import time
from typing import Any

from .rpc_client import RPCError, rpc_node, rpc_wallet
from .tx_interpreter import interpret

JsonDict = dict[str, Any]


def send_tx(to_address: str, amount: float, wallet_name: str, tracked_txs: JsonDict) -> JsonDict:
    """
    Build, sign and broadcast a transaction using PSBT flow:
    walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction
    """
    w_rpc = rpc_wallet(wallet_name)
    n_rpc = rpc_node()

    outputs = [{to_address: amount}]

    psbt_result = w_rpc.call("walletcreatefundedpsbt", [], outputs, 0, {})
    psbt = psbt_result["psbt"]

    processed = w_rpc.call("walletprocesspsbt", psbt)
    signed_psbt = processed["psbt"]

    finalized = w_rpc.call("finalizepsbt", signed_psbt)
    if not finalized.get("complete", False):
        raise ValueError("PSBT finalization incomplete — wallet may lack signing keys")

    raw_hex = finalized["hex"]
    txid = n_rpc.call("sendrawtransaction", raw_hex)

    tracked_txs[txid] = {"wallet": wallet_name, "broadcast_ts": time.time()}

    return {"txid": txid, "wallet": wallet_name, "status": "broadcast"}


def get_tx(txid: str, wallet_name: str | None, tracked_txs: JsonDict) -> JsonDict:
    n_rpc = rpc_node()
    tracked = tracked_txs.get(txid)

    # Prioriza a wallet original que enviou a tx; cai para a wallet
    # selecionada apenas quando a tx nunca passou por este backend.
    effective_wallet = tracked["wallet"] if tracked else wallet_name

    gettx_result = None
    if effective_wallet:
        try:
            gettx_result = rpc_wallet(effective_wallet).call("gettransaction", txid)
        except RPCError:
            pass

    mempool_entry = None
    try:
        mempool_entry = n_rpc.call("getmempoolentry", txid)
    except RPCError:
        pass

    return interpret(txid, effective_wallet, gettx_result, mempool_entry, tracked)
