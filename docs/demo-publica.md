# Public Demo — CoreCraft (2026-05-03)

Demonstration via Cloudflare Tunnel of the three backends running locally exposed over the internet. Bitcoin Core v31.0.0 in regtest, 215 blocks at time of registration.

---

## Environment

| Field | Value |
|-------|-------|
| Date | 2026-05-03 |
| Bitcoin Core | v31.0.0 |
| Network | regtest |
| Blocks / Headers | 215 / 215 (lag = 0) |
| ZMQ rawblock | tcp://127.0.0.1:28332 |
| ZMQ rawtx | tcp://127.0.0.1:28333 |
| Wallets | wallet1, wallet2, smoke_test_wallet, corecraft |
| Tunnel | Cloudflare Tunnel (`cloudflared tunnel --url`) |

---

## Public URLs

| Activity | URL |
|-----------|-----|
| Activity 1 | https://administrators-humanitarian-define-author.trycloudflare.com |
| Activity 2 | https://dice-garcia-hub-particular.trycloudflare.com |
| Activity 3 | https://move-after-salaries-kde.trycloudflare.com |

> Temporary Tunnels (trycloudflare.com) — generated without account and valid while process `cloudflared` was active.

---

## Activity 1 — Mempool Snapshot via RPC

**Base URL:** https://administrators-humanitarian-define-author.trycloudflare.com

### `GET /api/blockchain/lag`

```json
{"blocks":215,"headers":215,"lag":0}
```

Synchronized node: `blocks == headers`, `lag == 0`. Bitcoin Core v31.0 in regtest with 215 blocks mined.

---

## Activity 2 — Real-Time Events via ZMQ

**Base URL:** https://dice-garcia-hub-particular.trycloudflare.com

### `GET /api/events/summary`

```json
{
  "blocks_observed": 1,
  "tx_observed": 4,
  "last_event_time": 1777837956.2590888,
  "tx_per_second": 0.7
}
```

Active ZMQ: 1 block and 4 transactions observed via `rawblock`/`rawtx` at the time of capture.

---

## Activity 3 — Multi-wallet, PSBT and Interpreted State

**Base URL:** https://move-after-salaries-kde.trycloudflare.com

### `GET /wallets`

```json
{
  "available_wallets": ["smoke_test_wallet", "wallet1", "wallet2", "corecraft"],
  "loaded_wallets": ["wallet1", "wallet2", "smoke_test_wallet", "corecraft"],
  "selected_wallet": "wallet1"
}
```

Four wallets detected via `listwalletdir`, all loaded. Active wallet: `wallet1`.

### `GET /wallet/status`

```json
{
  "wallet": "wallet1",
  "balance": null,
  "utxos": 109
}
```

109 UTXOs available on wallet1.

> **Fix applied (commit `5b9a925`):** The field `balance` returned `null` in this demo because `getwalletinfo` in Bitcoin Core v31 no longer exposes this field directly. After correction, `/wallet/status` uses `getbalances()` and returns the numeric balance in `mine.trusted`. The corrected response includes the fields `balance` (numeric), `trusted_balance`, `untrusted_pending`, and `immature_balance`.

---

## Conclusion

| Item | Status |
|------|--------|
| Activity 1 — external access | OK |
| Activity 2 — external access | OK |
| Activity 3 — external access | OK |
| Frontend served via HTTPS | OK |
| ZMQ active and receiving events | OK |
| Multiple functional wallets | OK |

All three backends were publicly accessible via HTTPS (Cloudflare Tunnel) with Bitcoin Core v31.0 under regtest, returning real node data.
