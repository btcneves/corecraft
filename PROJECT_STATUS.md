# Project Status — CoreCraft

**Última atualização:** 2026-05-03

## Status geral

Entrega concluída. As três atividades estão implementadas, validadas ao vivo (2026-05-02) e demonstradas publicamente via Cloudflare Tunnel (2026-05-03) contra Bitcoin Core v31.0 em regtest.

## Status por atividade

| Atividade | Implementação | Validação local | Demo pública |
|-----------|--------------|-----------------|--------------|
| 1 — Mempool RPC | Concluída | OK (2026-05-02) | OK (2026-05-03) |
| 2 — ZMQ Events | Concluída | OK (2026-05-02) | OK (2026-05-03) |
| 3 — Multi-wallet PSBT | Concluída | OK (2026-05-02) | OK (2026-05-03) |

## URLs públicas (demo 2026-05-03)

| Atividade | URL |
|-----------|-----|
| Atividade 1 | https://administrators-humanitarian-define-author.trycloudflare.com |
| Atividade 2 | https://dice-garcia-hub-particular.trycloudflare.com |
| Atividade 3 | https://move-after-salaries-kde.trycloudflare.com |

> Tunnels Cloudflare temporários gerados em 2026-05-03. Evidências completas em [`docs/demo-publica.md`](docs/demo-publica.md).

## Pendências

Nenhuma pendência em aberto.

## Arquivos de validação

| Arquivo | Conteúdo |
|---------|----------|
| `docs/validacao-ao-vivo.md` | Evidências reais de execução local (2026-05-02) |
| `docs/demo-publica.md` | Evidências de acesso externo via Cloudflare Tunnel (2026-05-03) |
| `docs/smoke-tests.md` | Smoke tests manuais com curl por atividade |
| `scripts/smoke-test.sh` | Script automatizado de smoke tests |
| `docs/entrega.md` | Checklist de entrega + URLs públicas + respostas reais |
