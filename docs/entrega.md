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
- [ ] URL pública configurada (pendente — ver seção abaixo)

## Validação antes do envio

Antes de enviar, execute os comandos abaixo com `bitcoind -regtest` rodando:

```bash
# Verificar se o nó está respondendo
bitcoin-cli -regtest getblockchaininfo

# Smoke tests rápidos (todas as três atividades)
./scripts/smoke-test.sh

# Ou individualmente:
curl http://127.0.0.1:8001/api/mempool/summary
curl http://127.0.0.1:8002/api/events/state-comparison
curl http://127.0.0.1:8003/wallets
```

Evidências completas de validação: [`docs/validacao-ao-vivo.md`](validacao-ao-vivo.md)

## URL pública

**Status: pendente.**

O projeto ainda não possui URL pública registrada. Para expor via tunnel:

```bash
# Cloudflare Tunnel (sem abrir portas no roteador)
cloudflared tunnel --url http://localhost:8001
cloudflared tunnel --url http://localhost:8002
cloudflared tunnel --url http://localhost:8003

# Alternativa: ngrok
ngrok http 8001
```

Guias completos: [`deploy-cloudflare-tunnel.md`](deploy-cloudflare-tunnel.md) e [`deploy-vps.md`](deploy-vps.md).

Quando disponível, registrar aqui:

| Atividade | URL pública |
|-----------|-------------|
| Atividade 1 | `https://____________` |
| Atividade 2 | `https://____________` |
| Atividade 3 | `https://____________` |
