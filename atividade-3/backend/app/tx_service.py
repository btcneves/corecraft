import time

from .rpc_client import BitcoinRPC, RPCError, rpc_node, rpc_wallet
from .tx_interpreter import interpret


def send_tx(to_address: str, amount: float, wallet_name: str, tracked_txs: dict) -> dict:
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


def get_tx(txid: str, wallet_name: str | None, tracked_txs: dict) -> dict:
    n_rpc = rpc_node()

    gettx_result = None
    if wallet_name:
        try:
            gettx_result = rpc_wallet(wallet_name).call("gettransaction", txid)
        except RPCError:
            pass

    mempool_entry = None
    try:
        mempool_entry = n_rpc.call("getmempoolentry", txid)
    except RPCError:
        pass

    tracked = tracked_txs.get(txid)

    return interpret(txid, wallet_name, gettx_result, mempool_entry, tracked)
