# Delivery — CoreCraft

## Scope

Three independent microservices for integration with Bitcoin Core (regtest):

- Activity 1 (port 8001): Mempool snapshot via RPC
- Activity 2 (port 8002): Real-time events via ZMQ
- Activity 3 (port 8003): Multi-wallet + PSBT + interpreted state

## Delivery checklist

- [x] Functional code in the three activities
- [x] Frontends served by FastAPI itself
- [x] Technical documentation in `docs/`
- [x] Live validation performed (2026-05-02, Bitcoin Core v31.0, regtest)
- [x] `CHANGELOG.md` updated
- [x] Configured and tested public URL (2026-05-03, Cloudflare Tunnel)

## Public URLs (demo 2026-05-03)

| Activity | Public URL |
|-----------|-------------|
| Activity 1 | https://administrators-humanitarian-define-author.trycloudflare.com |
| Activity 2 | https://dice-garcia-hub-particular.trycloudflare.com |
| Activity 3 | https://move-after-salaries-kde.trycloudflare.com |

> Temporary Cloudflare Tunnels generated on 2026-05-03. Complete evidence in [`docs/demo-publica.md`](demo-publica.md).

## Actual endpoint responses (external access)

| Activity | Endpoint | Observed response |
|-----------|----------|--------------------|
| 1 | `GET /api/blockchain/lag` | `{"blocks":215,"headers":215,"lag":0}` |
| 2 | `GET /api/events/summary` | `{"blocks_observed":1,"tx_observed":4,"last_event_time":1777837956.2590888,"tx_per_second":0.7}` |
| 3 | `GET /wallets` | `{"available_wallets":["smoke_test_wallet","wallet1","wallet2","corecraft"],"loaded_wallets":["wallet1","wallet2","smoke_test_wallet","corecraft"],"selected_wallet":"wallet1"}` |
| 3 | `GET /wallet/status` | `{"wallet":"wallet1","balance":null,"utxos":109}` ¹ |

¹ The `balance` field displayed `null` at demo time because `getwalletinfo` in Bitcoin Core v31 no longer exposes this field directly. Fixed next (commit `5b9a925`): `/wallet/status` now uses `getbalances()` and returns numeric balance via `mine.trusted`.

## Environment at the time of the demo

| Field | Value |
|-------|-------|
| Bitcoin Core | v31.0.0 |
| Network | regtest |
| Blocks | 215 (headers=215, lag=0) |
| Wallets available | wallet1, wallet2, smoke_test_wallet, corecraft |
| ZMQ rawblock | tcp://127.0.0.1:28332 |
| ZMQ rawtx | tcp://127.0.0.1:28333 |

## Validation before shipping

```bash
# Check whether the node is responding
bitcoin-cli -regtest getblockchaininfo

# Quick smoke tests (all three activities)
./scripts/smoke-test.sh
```

Complete local validation evidence: [`docs/validacao-ao-vivo.md`](validacao-ao-vivo.md)
Public demo evidence: [`docs/demo-publica.md`](demo-publica.md)

---

## Send block

```
Name: Pedro Neves
GitHub: https://github.com/btcneves/CoreCraft

Activity 1:
https://github.com/btcneves/CoreCraft/tree/main/atividade-1

Activity 2:
https://github.com/btcneves/CoreCraft/tree/main/atividade-2

Activity 3:
https://github.com/btcneves/CoreCraft/tree/main/atividade-3

Notes:
Single repository organized as required, with backend, frontend,
documentation, Bitcoin Core integration through RPC/ZMQ where applicable,
and real validation against Bitcoin Core v31.0.0 in regtest mode.

Public demo:
Activity 1: https://administrators-humanitarian-define-author.trycloudflare.com
Activity 2: https://dice-garcia-hub-particular.trycloudflare.com
Activity 3: https://move-after-salaries-kde.trycloudflare.com
```

> The trycloudflare.com URLs are temporary and depend on the powered-on local machine, FastAPI backends on ports 8001, 8002, and 8003, active bitcoind, and active cloudflared processes.
