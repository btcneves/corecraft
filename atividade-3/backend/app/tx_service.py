import time
from typing import Any

from corecraft import (
    FinalizePSBTResponse,
    GetMempoolEntryResponse,
    GetTransactionResponse,
    SendTxResponse,
    TrackedTx,
    TxInterpretation,
    WalletCreateFundedPSBTResponse,
    WalletProcessPSBTResponse,
)

from .rpc_client import RPCError, rpc_node, rpc_wallet
from .tx_interpreter import interpret


def send_tx(
    to_address: str, amount: float, wallet_name: str, tracked_txs: dict[str, TrackedTx]
) -> SendTxResponse:
    """
    Build, sign and broadcast a transaction using PSBT flow:
    walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction
    """
    w_rpc = rpc_wallet(wallet_name)
    n_rpc = rpc_node()

    outputs: list[dict[str, float]] = [{to_address: amount}]

    psbt_result: WalletCreateFundedPSBTResponse = w_rpc.call(
        "walletcreatefundedpsbt", [], outputs, 0, {}
    )
    psbt: str = psbt_result["psbt"]

    processed: WalletProcessPSBTResponse = w_rpc.call("walletprocesspsbt", psbt)
    signed_psbt: str = processed["psbt"]

    finalized: FinalizePSBTResponse = w_rpc.call("finalizepsbt", signed_psbt)
    if not finalized.get("complete", False):
        raise ValueError("PSBT finalization incomplete — wallet may lack signing keys")

    raw_hex: str = finalized["hex"]
    txid: str = n_rpc.call("sendrawtransaction", raw_hex)

    tracked_txs[txid] = TrackedTx(wallet=wallet_name, broadcast_ts=time.time())

    return SendTxResponse(txid=txid, wallet=wallet_name, status="broadcast")


def get_tx(
    txid: str, wallet_name: str | None, tracked_txs: dict[str, TrackedTx]
) -> TxInterpretation:
    """Get transaction status and interpretation."""
    n_rpc = rpc_node()
    tracked: TrackedTx | None = tracked_txs.get(txid)

    # Prioritize the original wallet that sent the tx; fall back to selected
    # wallet only when the tx never went through this backend.
    effective_wallet: str | None = tracked["wallet"] if tracked else wallet_name

    gettx_result: GetTransactionResponse | None = None
    if effective_wallet:
        try:
            gettx_result = rpc_wallet(effective_wallet).call("gettransaction", txid)
        except RPCError:
            pass

    mempool_entry: GetMempoolEntryResponse | None = None
    try:
        mempool_entry = n_rpc.call("getmempoolentry", txid)
    except RPCError:
        pass

    return interpret(txid, effective_wallet, gettx_result, mempool_entry, tracked)
