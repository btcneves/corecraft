# Changelog

All notable changes to CoreCraft are documented here.

## [1.3.0] — 2026-05-04

### Added

- Integration test suite (`tests/integration/`) — 34 tests covering full HTTP stack via TestClient: Activity 1 endpoints, ZMQ→EventStore→API pipeline (Activity 2), and PSBT end-to-end flow (Activity 3).
- Expanded Prometheus metrics: per-path request counters (`corecraft_requests_by_path_total`), last request latency gauge (`corecraft_last_request_latency_ms`), ZMQ event counters for Activity 2 (`corecraft_zmq_blocks_total`, `corecraft_zmq_tx_total`), and PSBT transaction counter for Activity 3 (`corecraft_psbt_sent_total`).
- `docs/en-US/docker-troubleshooting.md`: macOS Apple Silicon section (Rosetta 2, memory allocation, `exec format error`) and Windows WSL 2 section (integration, permissions, path issues).
- Bilingual documentation structure with `docs/pt-BR/`, `docs/en-US/`, and `docs/README.md`.
- README badges (GitHub Release, CI status, Docker/GHCR).
- README "O que você verá" section with expected `docker compose up` output and smoke test output.

### Changed

- Coverage threshold raised from 70% to 80% (current: 89%).

## [1.2.0] — 2026-05-04

### Added

- Release workflow (`.github/workflows/release.yml`): builds and pushes Docker images to `ghcr.io` and creates a GitHub Release with CHANGELOG excerpt on every `v*.*.*` tag.
- Docker images now tagged at `ghcr.io/btcneves/corecraft-suite-atividade-{1,2,3}`.
- `scripts/quickstart.sh`: single OS-detecting entry-point for Linux and macOS.
- `VERSION` file as single source of truth for the project version.
- Makefile `tag` and `release` targets to automate versioning.

### Changed

- `scripts/setup-mac.sh`: detects Apple Silicon vs Intel, checks Homebrew path, warns about Rosetta 2 overhead and recommends 4 GB RAM on arm64.
- `scripts/setup-windows.bat`: detects WSL 2, shows PowerShell execution policy note, adds bitcoin-cli PATH guidance.
- `scripts/smoke-test.sh`: rewritten with wait-for-services loop, per-endpoint PASS/FAIL, `--timeout` flag, and correct exit code.
- `README.md`: prominent 3-command quickstart block at the top; docs section now shows beginner-first ordering.
- `.env.example`: comments explaining each variable.
- `docs/en-US/getting-started.md`: TL;DR 3-step block at the top.

## [1.1.0] — 2026-05-03

### Added

- Full Docker stack with `bitcoind`, wallet initialization, Caddy, and the three activity services.
- React/Vite/TypeScript frontends for all activities.
- Activity 2 WebSocket endpoint (`/ws/events`) with HTTP polling endpoints preserved.
- Root tooling: `pyproject.toml`, per-activity Dockerfiles, setup scripts, Makefile, `.dockerignore`, and CI.
- Structured JSON logging for the FastAPI backends.

### Fixed

- Docker RPC authentication now passes `-rpcuser` and `-rpcpassword` to `bitcoind` via Compose command flags instead of relying on unsupported environment-variable expansion inside `bitcoin.conf`.
- FastAPI static serving now locates the Docker build output at `/app/frontend/dist`.

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
- Documentation: `docs/pt-BR/` and `docs/en-US/` language tracks, including setup, RPC/ZMQ, deploy, smoke tests, and validation evidence.
- MIT licence

### Fixed

- **All activities — `rpc_client.py`**: JSON-RPC version changed from `"1.1"` to `"2.0"`. Bitcoin Core ≥ 31 rejects `"1.1"` with error `-32600: JSON-RPC version not supported`; all endpoints were returning 503 before this fix.
- **Activity 3 — `tx_service.py`**: `get_tx()` now uses the wallet stored at send time rather than the currently selected wallet. Querying a past transaction no longer fails after switching wallets.
- **Activity 2 — `event_service.py`**: returns `divergence: null` and `status: "waiting_for_zmq_block"` before the ZMQ listener receives its first block, eliminating a false-positive divergence flag at startup.
- **Activity 2 — frontend**: divergence banner is only shown when `status === "compared" && divergence === true`.
- **Docker Compose**: added `extra_hosts: ["host.docker.internal:host-gateway"]` to each service so containers can reach the host's `bitcoind`.
