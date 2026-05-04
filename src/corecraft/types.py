"""
Shared type definitions for CoreCraft activities.

This module defines TypedDicts and other type aliases for better type safety
when working with Bitcoin RPC responses and internal data structures.
"""

from typing import Any, TypedDict

# =============================================================================
# Bitcoin RPC Response Types
# =============================================================================


class RPCErrorData(TypedDict):
    """Structure of a JSON-RPC error response."""

    code: int
    message: str


class GetBlockchainInfoResponse(TypedDict):
    """Response from getblockchaininfo RPC call."""

    chain: str
    blocks: int
    headers: int
    bestblockhash: str
    difficulty: float
    mediantime: int
    verificationprogress: float
    initialblockdownload: bool
    chainwork: str
    size_on_disk: int
    pruned: bool
    softforks: dict[str, Any]
    warnings: str


class GetMempoolInfoResponse(TypedDict):
    """Response from getmempoolinfo RPC call."""

    size: int
    bytes: int
    usage: int
    total_fee: float
    maxmempool: int
    mempoolminfee: float
    minrelaytxfee: float
    unbroadcastcount: int


class MempoolEntryFees(TypedDict):
    """Fee breakdown for a mempool entry."""

    base: float
    modified: float
    ancestor: float
    descendant: float


class MempoolEntry(TypedDict, total=False):
    """Entry from getrawmempool(verbose=True) RPC call."""

    vsize: int
    size: int
    weight: int
    fee: float
    modifiedfee: float
    time: int
    height: int
    descendantcount: int
    descendantsize: int
    descendantfees: int
    ancestorcount: int
    ancestorsize: int
    ancestorfees: int
    wtxid: str
    fees: MempoolEntryFees
    depends: list[str]
    spentby: list[str]
    bip125_replaceable: bool
    unbroadcast: bool


class GetRawMempoolVerboseResponse(TypedDict):
    """Verbose mempool response keyed by txid."""

    # This is a dict[txid, MempoolEntry] but we define it for documentation
    pass


class GetTransactionResponse(TypedDict, total=False):
    """Response from gettransaction RPC call."""

    amount: float
    fee: float
    confirmations: int
    generated: bool
    blockhash: str
    blockheight: int
    blocktime: int
    txid: str
    walletconflicts: list[str]
    time: int
    timedetails: dict[str, Any]
    bip125_replaceable: str
    comment: str
    to: str
    abandomed: bool


class GetBalancesResponse(TypedDict):
    """Response from getbalances RPC call."""

    mine: dict[str, float]
    watchonly: dict[str, float]


class MineBalances(TypedDict):
    """Mine section of getbalances response."""

    trusted: float
    untrusted_pending: float
    immature: float


class ListUnspentEntry(TypedDict, total=False):
    """Entry from listunspent RPC call."""

    txid: str
    vout: int
    address: str
    label: str
    scriptPubKey: str
    amount: float
    confirmations: int
    spendable: bool
    solvable: bool
    desc: str
    safe: bool


class GetWalletInfoResponse(TypedDict, total=False):
    """Response from getwalletinfo RPC call."""

    walletname: str
    walletversion: int
    balance: float
    unconfirmed_balance: float
    immature_balance: float
    txcount: int
    keypoololdest: int
    keypoolsize: int
    keypoolsize_hd_internal: int
    unlocked_until: int
    paytxfee: float
    hdchainid: str
    hdaccountcount: int


class WalletCreateFundedPSBTResponse(TypedDict):
    """Response from walletcreatefundedpsbt RPC call."""

    psbt: str
    fee: float
    changepos: int


class WalletProcessPSBTResponse(TypedDict):
    """Response from walletprocesspsbt RPC call."""

    psbt: str
    complete: bool


class FinalizePSBTResponse(TypedDict, total=False):
    """Response from finalizepsbt RPC call."""

    psbt: str
    hex: str
    complete: bool
    errors: list[str]


class GetMempoolEntryResponse(TypedDict, total=False):
    """Response from getmempoolentry RPC call."""

    vsize: int
    fees: MempoolEntryFees
    time: int
    height: int
    descendantcount: int
    descendantsize: int
    descendantfees: float
    ancestorcount: int
    ancestorsize: int
    ancestorfees: float
    wtxid: str


class ListWalletDirResponse(TypedDict):
    """Response from listwalletdir RPC call."""

    wallets: list[dict[str, str]]


class LoadWalletResponse(TypedDict, total=False):
    """Response from loadwallet RPC call."""

    name: str
    warning: str


# =============================================================================
# Internal Application Types
# =============================================================================


class BlockEvent(TypedDict):
    """Internal representation of a block event."""

    hash: str
    ts: float


class TxEvent(TypedDict):
    """Internal representation of a transaction event."""

    txid: str
    ts: float


class EventStoreSnapshot(TypedDict):
    """Snapshot from EventStore."""

    blocks: list[BlockEvent]
    txs: list[TxEvent]
    blocks_observed: int
    tx_observed: int
    last_event_time: float | None
    tx_per_second: float


class TrackedTx(TypedDict):
    """Tracked transaction in memory store."""

    wallet: str
    broadcast_ts: float


class _TxInterpretationBase(TypedDict):
    """Required fields present in every TxInterpretation."""

    txid: str
    wallet: str | None
    status: str  # "confirmed", "mempool", "broadcast", "unknown"
    confirmed: bool
    confirmations: int
    block_hash: str | None
    age_seconds: int | None
    message: str | None


class TxInterpretation(_TxInterpretationBase, total=False):
    """Interpreted transaction state. `warning` is present only for stale-mempool cases."""

    warning: str


class WalletInfo(TypedDict):
    """Wallet information for API responses."""

    walletname: str
    balance: float
    txcount: int


class WalletStatus(TypedDict):
    """Wallet status API response."""

    wallet: str
    balance: float
    utxos: int
    trusted_balance: float
    untrusted_pending: float
    immature_balance: float


class MempoolSummary(TypedDict):
    """Mempool summary API response."""

    tx_count: int
    total_vsize: int
    avg_fee_rate: float
    min_fee_rate: float
    max_fee_rate: float
    fee_distribution: dict[str, int]


class BlockchainLag(TypedDict):
    """Blockchain lag API response."""

    blocks: int
    headers: int
    lag: int


class EventsSummary(TypedDict):
    """Events summary API response."""

    blocks_observed: int
    tx_observed: int
    last_event_time: float | None
    tx_per_second: float


class EventsLatest(TypedDict):
    """Latest events API response."""

    blocks: list[BlockEvent]
    txs: list[TxEvent]


class _StateComparisonBase(TypedDict):
    """Fields always present in a StateComparison."""

    best_block: str
    last_seen_block: str | None
    divergence: bool | None
    status: str


class StateComparison(_StateComparisonBase, total=False):
    """State comparison API response. `message` only present while waiting for first ZMQ block."""

    message: str


class SendTxResponse(TypedDict):
    """Send transaction API response."""

    txid: str
    wallet: str
    status: str


# =============================================================================
# Activity 3 application types
# =============================================================================


class WalletsResponse(TypedDict):
    """Response for GET /wallets."""

    available_wallets: list[str]
    loaded_wallets: list[str]
    selected_wallet: str | None


class SelectWalletResponse(TypedDict):
    """Response for POST /wallet/select."""

    selected_wallet: str
    wallet_info: WalletInfo


class AppState(TypedDict):
    """In-memory application state for activity 3."""

    selected_wallet: str | None
    tracked_txs: dict[str, TrackedTx]


# =============================================================================
# Fee Distribution Categories
# =============================================================================

FeeCategory = str  # "low", "medium", "high"
