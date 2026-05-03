# Demo Pública — CoreCraft (2026-05-03)

Demonstração via Cloudflare Tunnel dos três backends em execução local expostos pela internet. Bitcoin Core v31.0.0 em regtest, 215 blocos no momento do registro.

---

## Ambiente

| Campo | Valor |
|-------|-------|
| Data | 2026-05-03 |
| Bitcoin Core | v31.0.0 |
| Rede | regtest |
| Blocos / Headers | 215 / 215 (lag = 0) |
| ZMQ rawblock | tcp://127.0.0.1:28332 |
| ZMQ rawtx | tcp://127.0.0.1:28333 |
| Wallets | wallet1, wallet2, smoke_test_wallet, corecraft |
| Tunnel | Cloudflare Tunnel (`cloudflared tunnel --url`) |

---

## URLs públicas

| Atividade | URL |
|-----------|-----|
| Atividade 1 | https://administrators-humanitarian-define-author.trycloudflare.com |
| Atividade 2 | https://dice-garcia-hub-particular.trycloudflare.com |
| Atividade 3 | https://move-after-salaries-kde.trycloudflare.com |

> Tunnels temporários (trycloudflare.com) — gerados sem conta e válidos enquanto o processo `cloudflared` estava ativo.

---

## Atividade 1 — Snapshot da Mempool via RPC

**URL base:** https://administrators-humanitarian-define-author.trycloudflare.com

### `GET /api/blockchain/lag`

```json
{"blocks":215,"headers":215,"lag":0}
```

Nó sincronizado: `blocks == headers`, `lag == 0`. Bitcoin Core v31.0 em regtest com 215 blocos minerados.

---

## Atividade 2 — Eventos em Tempo Real via ZMQ

**URL base:** https://dice-garcia-hub-particular.trycloudflare.com

### `GET /api/events/summary`

```json
{
  "blocks_observed": 1,
  "tx_observed": 4,
  "last_event_time": 1777837956.2590888,
  "tx_per_second": 0.7
}
```

ZMQ ativo: 1 bloco e 4 transações observados via `rawblock`/`rawtx` no momento da captura.

---

## Atividade 3 — Multi-wallet, PSBT e Estado Interpretado

**URL base:** https://move-after-salaries-kde.trycloudflare.com

### `GET /wallets`

```json
{
  "available_wallets": ["smoke_test_wallet", "wallet1", "wallet2", "corecraft"],
  "loaded_wallets": ["wallet1", "wallet2", "smoke_test_wallet", "corecraft"],
  "selected_wallet": "wallet1"
}
```

Quatro wallets detectadas via `listwalletdir`, todas carregadas. Wallet ativa: `wallet1`.

### `GET /wallet/status`

```json
{
  "wallet": "wallet1",
  "balance": null,
  "utxos": 109
}
```

109 UTXOs disponíveis na wallet1.

---

## Conclusão

| Item | Status |
|------|--------|
| Atividade 1 — acesso externo | OK |
| Atividade 2 — acesso externo | OK |
| Atividade 3 — acesso externo | OK |
| Frontend servido via HTTPS | OK |
| ZMQ ativo e recebendo eventos | OK |
| Múltiplas wallets funcionais | OK |

Todos os três backends foram acessíveis publicamente via HTTPS (Cloudflare Tunnel) com Bitcoin Core v31.0 em regtest, retornando dados reais do nó.
