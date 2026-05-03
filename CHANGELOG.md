# Changelog

All notable changes to CoreCraft are documented here.

## [1.0.1] — 2026-05-03

### Fixed

- **Activity 3 — `wallet_service.py`**: `wallet_status()` now falls back to
  `getbalances()` when `getwalletinfo` does not expose a `balance` field
  (behaviour observed with Bitcoin Core v31). `/wallet/status` now returns a
  numeric balance via `mine.trusted` instead of `null`. The response also
  includes `trusted_balance`, `untrusted_pending`, and `immature_balance`.

## [1.0.0] — 2026-05-02

### Added

- **Activity 1**: mempool snapshot via RPC
  - `GET /api/mempool/summary` — tx count, total vsize, avg/min/max fee rate, fee distribution buckets
  - `GET /api/blockchain/lag` — difference between `headers` and `blocks` from `getblockchaininfo`
- **Activity 2**: real-time event stream via ZMQ (`rawblock` + `rawtx`)
  - `GET /api/events/summary` — block/tx counters and throughput from the ZMQ buffer
  - `GET /api/events/latest` — last 20 blocks and 200 transactions observed
  - `GET /api/events/state-comparison` — compares `getbestblockhash` (RPC pull) with the latest block hash received over ZMQ (push)
- **Activity 3**: multi-wallet management, PSBT transaction flow, interpreted transaction state
  - `GET /wallets` — lists available, loaded, and selected wallets
  - `POST /wallet/select` — selects and loads a wallet
  - `GET /wallet/status` — balance and UTXO count for the active wallet
  - `POST /tx/send` — creates, signs, and broadcasts a transaction via the PSBT flow
  - `GET /tx/{txid}` — interpreted transaction state: `broadcast → mempool → confirmed → unknown`
- Frontend dashboards for all three activities (plain HTML/CSS/JS, polling-based)
- Docker Compose configuration to run all three backends simultaneously
- Documentation: `docs/setup-bitcoin-core.md`, `docs/rpc-zmq.md`, `docs/deploy-vps.md`, `docs/deploy-cloudflare-tunnel.md`, `docs/smoke-tests.md`, `docs/validacao-ao-vivo.md`
- MIT licence

### Fixed

- **All activities — `rpc_client.py`**: JSON-RPC version changed from `"1.1"` to `"2.0"`. Bitcoin Core ≥ 31 rejects `"1.1"` with error `-32600: JSON-RPC version not supported`; all endpoints were returning 503 before this fix.
- **Activity 3 — `tx_service.py`**: `get_tx()` now uses the wallet stored at send time rather than the currently selected wallet. Querying a past transaction no longer fails after switching wallets.
- **Activity 2 — `event_service.py`**: returns `divergence: null` and `status: "waiting_for_zmq_block"` before the ZMQ listener receives its first block, eliminating a false-positive divergence flag at startup.
- **Activity 2 — frontend**: divergence banner is only shown when `status === "compared" && divergence === true`.
- **Docker Compose**: added `extra_hosts: ["host.docker.internal:host-gateway"]` to each service so containers can reach the host's `bitcoind`.
