# Architecture

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + FastAPI + Uvicorn |
| Frontend | React + Vite + TypeScript |
| Bitcoin Core integration | Custom `rpc_client.py` per activity using `requests` + `HTTPBasicAuth` |
| Event stream | `pyzmq` daemon thread (Activity 2 only) |
| Local orchestration | Docker Compose + Caddy + Bitcoin Core regtest |

## Service overview

Each activity is an independent microservice with its own backend and frontend.

| Activity | Port | Key modules |
|----------|------|-------------|
| 1 — Mempool snapshot | 8001 | `mempool.py`, `rpc_client.py` |
| 2 — ZMQ event stream | 8002 | `zmq_listener.py`, `event_store.py`, `event_service.py`, `rpc_client.py` |
| 3 — Multi-wallet + PSBT | 8003 | `wallet_service.py`, `tx_service.py`, `tx_interpreter.py`, `rpc_client.py` |

All three share the same structural pattern:

```
atividade-N/
├── backend/app/
│   ├── main.py          FastAPI routes + static file serving
│   ├── rpc_client.py    JSON-RPC 2.0 client
│   └── <domain>.py      Business logic modules
└── frontend/            React/Vite/TypeScript dashboard
```

## Design decisions

### No Bitcoin libraries
Each activity has its own `rpc_client.py` that calls `requests.post` with `HTTPBasicAuth` and JSON-RPC 2.0 payloads. This keeps the dependency surface minimal and makes the Bitcoin Core protocol explicit. Block hashes, when needed, are computed locally in Python (double SHA-256 + byte reversal).

### No database
State is in-memory only:

- **Activity 2**: `collections.deque(maxlen=20)` for blocks, `deque(maxlen=200)` for transactions
- **Activity 3**: Python `dict` tracking sent transactions `{txid: {wallet, timestamp}}`

State resets on process restart. Transaction IDs remain queryable via Bitcoin Core RPC (`gettransaction`) after a restart because the node holds the authoritative state.

### PSBT transaction flow (Activity 3)
Transaction signing uses Partially Signed Bitcoin Transactions (PSBT) so Bitcoin Core handles UTXO selection and fee calculation:

```
walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction
```

### Global vs wallet-scoped RPC (Activity 3)
`rpc_client.py` exposes two constructors:

- `rpc_node()` — calls the global endpoint (`http://host:port/`)
- `rpc_wallet(name)` — calls the wallet endpoint (`http://host:port/wallet/<name>`)

Global and wallet-scoped calls never mix. When querying a transaction, the service uses the wallet recorded at send time (from the in-memory tracker), not the currently selected wallet — so switching wallets does not break historical lookups.

### ZMQ divergence detection (Activity 2)
When the ZMQ listener has not yet received a block (e.g., immediately after startup), `last_seen_block` is `null`. The API returns `divergence: null` and `status: "waiting_for_zmq_block"` rather than comparing null against the RPC best block hash. The frontend only shows the divergence banner when `status === "compared" && divergence === true`.

### txid resolution in Activity 2
Transaction IDs are resolved via `decoderawtransaction` RPC, which avoids writing a local witness-serialisation parser. If the node is offline when a ZMQ transaction arrives, the txid is not registered and a warning is logged.

### HTTP 503 for node unavailability
All routes that depend on Bitcoin Core return a structured 503 response when the node is unreachable. No route returns HTTP 500 for a connectivity failure:

```json
{"detail": {"error": "node_unavailable", "detail": "..."}}
```

### Frontend design
Each activity has a self-contained React/Vite/TypeScript frontend. Docker builds the frontend and copies `dist/` into the FastAPI runtime image, where it is served by `app/main.py`. API URLs are prefix-aware, so each frontend works directly on `:8001`/`:8002`/`:8003` and through Caddy at `/atividade-1/`, `/atividade-2/`, and `/atividade-3/`.

### Docker orchestration
`docker compose up --build` starts Bitcoin Core in regtest, initializes `wallet1` and `wallet2`, mines spendable funds, starts the three activity services, and exposes them through Caddy. RPC credentials are supplied to `bitcoind` through command-line flags and to the backends through `BTC_RPC_USER`/`BTC_RPC_PASSWORD`; `bitcoin.conf` does not rely on environment-variable interpolation.

### JSON-RPC version
All `rpc_client.py` modules send `"jsonrpc": "2.0"`. Bitcoin Core ≥ 31 rejects `"1.1"` with error `-32600: JSON-RPC version not supported`.

## Known limitations

See [Known Limitations](../README.md#limitações-conhecidas) in the root README.
