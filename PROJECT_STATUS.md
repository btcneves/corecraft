# Project Status — CoreCraft

**Última atualização:** 2026-05-03

## Status geral

Pronto para entrega. As três atividades estão implementadas e validadas ao vivo contra Bitcoin Core v31.0 em regtest (2026-05-02). Nenhuma pendência bloqueia a entrega — apenas a URL pública opcional está em aberto.

## Status por atividade

| Atividade | Implementação | Validação | Observação |
|-----------|--------------|-----------|------------|
| 1 — Mempool RPC | Concluída | OK (2026-05-02) | 2 endpoints validados com saída real |
| 2 — ZMQ Events | Concluída | OK (2026-05-02) | 3 endpoints + bug fix divergence null |
| 3 — Multi-wallet PSBT | Concluída | OK (2026-05-02) | 5 endpoints + ciclo PSBT completo + bug fix wallet tracking |

## Pendências

- [ ] URL pública (VPS/tunnel) não configurada
- [ ] Frontend não validado via acesso externo (apenas local)

## Próximos passos

1. Configurar Cloudflare Tunnel ou VPS seguindo `docs/deploy-cloudflare-tunnel.md`
2. Registrar URLs em `docs/entrega.md`
3. Re-executar `./scripts/smoke-test.sh` via URL pública
4. Marcar `[ ] URL pública/tunnel testado` no checklist de `docs/validacao-ao-vivo.md`

## Arquivos de validação

| Arquivo | Conteúdo |
|---------|----------|
| `docs/validacao-ao-vivo.md` | Evidências reais de execução (saídas JSON reais do regtest) |
| `docs/smoke-tests.md` | Smoke tests manuais com curl por atividade |
| `scripts/smoke-test.sh` | Script automatizado de smoke tests (requer backends ativos) |
| `docs/entrega.md` | Checklist de entrega + campo para URL pública |
