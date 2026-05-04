# Demo Publica — CoreCraft

[Versao em ingles](../en-US/public-demo.md)

Demonstracao dos tres backends locais expostos via Cloudflare Tunnel.

## Ambiente

| Campo | Valor |
|-------|-------|
| Data | 2026-05-03 |
| Bitcoin Core | v31.0.0 |
| Rede | `regtest` |
| Blocos / Headers | 215 / 215 |
| Wallets | wallet1, wallet2, smoke_test_wallet, corecraft |

## URLs Publicas

| Atividade | URL |
|-----------|-----|
| 1 | `https://administrators-humanitarian-define-author.trycloudflare.com` |
| 2 | `https://dice-garcia-hub-particular.trycloudflare.com` |
| 3 | `https://move-after-salaries-kde.trycloudflare.com` |

## Resultado

- Atividade 1 respondeu `/api/blockchain/lag` com `lag = 0`.
- Atividade 2 respondeu `/api/events/summary` com eventos ZMQ observados.
- Atividade 3 respondeu `/wallets` e `/wallet/status`.
- As tres interfaces foram servidas por HTTPS via tunnel temporario.

As URLs eram temporarias e validas enquanto os processos `cloudflared` estavam ativos.

