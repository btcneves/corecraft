from .rpc_client import BitcoinRPC, RPCError, rpc_wallet


def list_wallets(node_rpc: BitcoinRPC, state: dict) -> dict:
    raw_dir = node_rpc.call("listwalletdir")
    wallets_raw = raw_dir.get("wallets", [])
    available = [
        w["name"] if isinstance(w, dict) else str(w)
        for w in wallets_raw
    ]
    loaded = node_rpc.call("listwallets")
    return {
        "available_wallets": available,
        "loaded_wallets": loaded,
        "selected_wallet": state.get("selected_wallet"),
    }


def select_wallet(name: str, node_rpc: BitcoinRPC, state: dict) -> dict:
    # Confirm wallet exists
    raw_dir = node_rpc.call("listwalletdir")
    available = [
        w["name"] if isinstance(w, dict) else str(w)
        for w in raw_dir.get("wallets", [])
    ]
    if name not in available:
        raise ValueError(f"Wallet '{name}' not found in listwalletdir")

    # Load if necessary
    loaded = node_rpc.call("listwallets")
    if name not in loaded:
        try:
            node_rpc.call("loadwallet", name)
        except RPCError as exc:
            # -35 = already loaded (race condition); ignore
            if exc.code != -35:
                raise

    state["selected_wallet"] = name
    info = rpc_wallet(name).call("getwalletinfo")
    return {
        "selected_wallet": name,
        "wallet_info": {
            "walletname": info.get("walletname"),
            "balance": info.get("balance"),
            "txcount": info.get("txcount"),
        },
    }


def wallet_status(name: str) -> dict:
    w_rpc = rpc_wallet(name)
    info = w_rpc.call("getwalletinfo")
    utxos = w_rpc.call("listunspent")
    return {
        "wallet": info.get("walletname"),
        "balance": info.get("balance"),
        "utxos": len(utxos),
    }
