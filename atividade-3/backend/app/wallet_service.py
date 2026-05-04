from corecraft import (
    AppState,
    GetBalancesResponse,
    GetWalletInfoResponse,
    ListUnspentEntry,
    ListWalletDirResponse,
    MineBalances,
    SelectWalletResponse,
    WalletInfo,
    WalletsResponse,
    WalletStatus,
)

from .rpc_client import BitcoinRPC, RPCError, rpc_wallet


def list_wallets(node_rpc: BitcoinRPC, state: AppState) -> WalletsResponse:
    raw_dir: ListWalletDirResponse = node_rpc.call("listwalletdir")
    wallets_raw = raw_dir.get("wallets", [])
    available: list[str] = [w["name"] if isinstance(w, dict) else str(w) for w in wallets_raw]
    loaded: list[str] = node_rpc.call("listwallets")
    return WalletsResponse(
        available_wallets=available,
        loaded_wallets=loaded,
        selected_wallet=state.get("selected_wallet"),
    )


def select_wallet(name: str, node_rpc: BitcoinRPC, state: AppState) -> SelectWalletResponse:
    raw_dir: ListWalletDirResponse = node_rpc.call("listwalletdir")
    available: list[str] = [
        w["name"] if isinstance(w, dict) else str(w) for w in raw_dir.get("wallets", [])
    ]
    if name not in available:
        raise ValueError(f"Wallet '{name}' not found in listwalletdir")

    loaded: list[str] = node_rpc.call("listwallets")
    if name not in loaded:
        try:
            node_rpc.call("loadwallet", name)
        except RPCError as exc:
            if exc.code != -35:
                raise

    state["selected_wallet"] = name
    info: GetWalletInfoResponse = rpc_wallet(name).call("getwalletinfo")
    return SelectWalletResponse(
        selected_wallet=name,
        wallet_info=WalletInfo(
            walletname=info.get("walletname", name),
            balance=info.get("balance", 0.0),
            txcount=info.get("txcount", 0),
        ),
    )


def wallet_status(name: str) -> WalletStatus:
    """Get detailed wallet status including balance and UTXO count."""
    w_rpc = rpc_wallet(name)
    info: GetWalletInfoResponse = w_rpc.call("getwalletinfo")
    utxos: list[ListUnspentEntry] = w_rpc.call("listunspent")

    balance: float | None = info.get("balance")
    trusted_balance: float | None = None
    untrusted_pending: float | None = None
    immature_balance: float | None = None

    if balance is None:
        balances: GetBalancesResponse = w_rpc.call("getbalances")
        mine: MineBalances = balances.get("mine", {})
        trusted_balance = mine.get("trusted", 0.0)
        untrusted_pending = mine.get("untrusted_pending", 0.0)
        immature_balance = mine.get("immature", 0.0)
        balance = trusted_balance

    return WalletStatus(
        wallet=info.get("walletname", name),
        balance=balance if balance is not None else 0.0,
        utxos=len(utxos),
        trusted_balance=trusted_balance if trusted_balance is not None else balance,
        untrusted_pending=untrusted_pending if untrusted_pending is not None else 0.0,
        immature_balance=immature_balance if immature_balance is not None else 0.0,
    )
