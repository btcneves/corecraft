# CLAUDE.md — CoreCraft

## Estado inicial
Projeto criado do zero em 2026-05-02. Diretório estava vazio.

## Decisões de design

- **Stack**: Python 3.12 + FastAPI + Uvicorn. Frontend HTML/CSS/JS puro servido pelo FastAPI.
- **RPC**: módulo `rpc_client.py` próprio em cada atividade, usando `requests`. Sem libs Bitcoin de alto nível.
- **ZMQ**: apenas na Atividade 2. Thread daemon com `pyzmq`, buffers via `collections.deque`.
- **Atividade 3 — assinatura**: PSBT (`walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction`). Escolha: mais robusto, Core cuida de seleção de UTXO e cálculo de fee.
- **Atividade 3 — txid via ZMQ**: `decoderawtransaction` via RPC (evita parser de serialização witness). Trade-off documentado.
- **Estado em memória**: sem banco de dados. Atividade 3 usa `dict` em memória para rastrear txs enviadas.
- **Portas**: Atividade 1 → 8001, Atividade 2 → 8002, Atividade 3 → 8003.
- **Sem bitcoind durante dev**: toda validação ao vivo fica para o usuário seguir `docs/entrega.md`.
- **Erro 503**: rotas que dependem do node retornam 503 estruturado quando node offline.

## Estrutura
```
corecraft/
├── atividade-1/  backend (port 8001) + frontend
├── atividade-2/  backend (port 8002) + frontend + ZMQ
├── atividade-3/  backend (port 8003) + frontend + multi-wallet
├── docs/
└── README.md (bloco de entrega)
```

## Pendências / validação ao vivo
- Todas as 3 atividades precisam de `bitcoind -regtest` rodando para funcionar.
- Atividade 2 precisa de `zmqpubrawblock` e `zmqpubrawtx` no `bitcoin.conf`.
- Ver `docs/setup-bitcoin-core.md` e `docs/entrega.md` para instruções completas.

## Checklist final
- [x] README.md na raiz
- [x] atividade-1/
- [x] atividade-2/
- [x] atividade-3/
- [x] Cada atividade tem backend
- [x] Cada atividade tem frontend
- [x] Cada atividade tem README
- [x] Atividade 1 NÃO usa ZMQ
- [x] Atividade 1 tem /api/mempool/summary
- [x] Atividade 1 tem /api/blockchain/lag
- [x] Atividade 2 usa ZMQ
- [x] Atividade 2 tem /api/events/summary
- [x] Atividade 2 tem /api/events/latest
- [x] Atividade 2 tem /api/events/state-comparison
- [x] Atividade 3 tem /wallets
- [x] Atividade 3 tem /wallet/select
- [x] Atividade 3 tem /wallet/status
- [x] Atividade 3 tem /tx/{txid} enriquecido
- [x] Atividade 3 tem seleção de wallet no frontend
- [x] README principal tem bloco de entrega
- [x] .env protegido no .gitignore
- [x] .env.example existe em cada atividade
- [x] CLAUDE.md atualizado
- [x] docs/entrega.md existe
- [x] docs/setup-bitcoin-core.md existe
- [x] docs/deploy-cloudflare-tunnel.md existe
