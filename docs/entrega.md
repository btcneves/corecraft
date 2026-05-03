# Entrega — CoreCraft

## Escopo

Três micro-serviços independentes de integração com Bitcoin Core (regtest):

- Atividade 1 (porta 8001): Snapshot da mempool via RPC
- Atividade 2 (porta 8002): Eventos em tempo real via ZMQ
- Atividade 3 (porta 8003): Multi-wallet + PSBT + estado interpretado

## Checklist de entrega

- [x] Código funcional nas três atividades
- [x] Frontends servidos pelo próprio FastAPI
- [x] Documentação técnica em `docs/`
- [x] Validação ao vivo executada (2026-05-02, Bitcoin Core v31.0, regtest)
- [x] `CHANGELOG.md` atualizado
- [x] URL pública configurada e testada (2026-05-03, Cloudflare Tunnel)

## URLs públicas (demo 2026-05-03)

| Atividade | URL pública |
|-----------|-------------|
| Atividade 1 | https://administrators-humanitarian-define-author.trycloudflare.com |
| Atividade 2 | https://dice-garcia-hub-particular.trycloudflare.com |
| Atividade 3 | https://move-after-salaries-kde.trycloudflare.com |

> Tunnels Cloudflare temporários gerados em 2026-05-03. Evidências completas em [`docs/demo-publica.md`](demo-publica.md).

## Respostas reais dos endpoints (acesso externo)

| Atividade | Endpoint | Resposta observada |
|-----------|----------|--------------------|
| 1 | `GET /api/blockchain/lag` | `{"blocks":215,"headers":215,"lag":0}` |
| 2 | `GET /api/events/summary` | `{"blocks_observed":1,"tx_observed":4,"last_event_time":1777837956.2590888,"tx_per_second":0.7}` |
| 3 | `GET /wallets` | `{"available_wallets":["smoke_test_wallet","wallet1","wallet2","corecraft"],"loaded_wallets":["wallet1","wallet2","smoke_test_wallet","corecraft"],"selected_wallet":"wallet1"}` |
| 3 | `GET /wallet/status` | `{"wallet":"wallet1","balance":null,"utxos":109}` |

## Ambiente no momento da demo

| Campo | Valor |
|-------|-------|
| Bitcoin Core | v31.0.0 |
| Rede | regtest |
| Blocos | 215 (headers=215, lag=0) |
| Wallets disponíveis | wallet1, wallet2, smoke_test_wallet, corecraft |
| ZMQ rawblock | tcp://127.0.0.1:28332 |
| ZMQ rawtx | tcp://127.0.0.1:28333 |

## Validação antes do envio

```bash
# Verificar se o nó está respondendo
bitcoin-cli -regtest getblockchaininfo

# Smoke tests rápidos (todas as três atividades)
./scripts/smoke-test.sh
```

Evidências completas de validação local: [`docs/validacao-ao-vivo.md`](validacao-ao-vivo.md)
Evidências de demo pública: [`docs/demo-publica.md`](demo-publica.md)

---

## Bloco de envio

```
Nome: Pedro Neves
GitHub: https://github.com/btcneves/corecraft

Atividade 1:
https://github.com/btcneves/corecraft/tree/main/atividade-1

Atividade 2:
https://github.com/btcneves/corecraft/tree/main/atividade-2

Atividade 3:
https://github.com/btcneves/corecraft/tree/main/atividade-3

Observações:
Repositório único organizado conforme exigido, com backend, frontend,
documentação, integração Bitcoin Core via RPC/ZMQ quando aplicável e
validação real em Bitcoin Core v31.0.0 no modo regtest.

Demonstração pública:
Atividade 1: https://administrators-humanitarian-define-author.trycloudflare.com
Atividade 2: https://dice-garcia-hub-particular.trycloudflare.com
Atividade 3: https://move-after-salaries-kde.trycloudflare.com
```

> As URLs trycloudflare.com são temporárias e dependem da máquina local ligada, dos backends FastAPI nas portas 8001, 8002 e 8003, do bitcoind ativo e dos processos cloudflared ativos.
