# CLAUDE.md — CoreCraft

## Estado inicial
Projeto criado do zero em 2026-05-02. Diretório estava vazio.

## Decisões de design

- **Stack**: Python 3.12 + FastAPI + Uvicorn. Frontend HTML/CSS/JS puro servido pelo FastAPI.
- **RPC**: módulo `rpc_client.py` próprio em cada atividade, usando `requests`. Sem libs Bitcoin de alto nível.
- **ZMQ**: apenas na Atividade 2. Thread daemon com `pyzmq`, buffers via `collections.deque`.
- **Atividade 3 — assinatura**: PSBT (`walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction`). Escolha: mais robusto, Core cuida de seleção de UTXO e cálculo de fee.
- **Atividade 3 — RPC global × wallet**: dois construtores no `rpc_client.py` (`rpc_node()` e `rpc_wallet(name)`); chamadas globais e específicas nunca se misturam.
- **Atividade 2 — txid via RPC**: `decoderawtransaction` (evita parser de serialização witness). Trade-off documentado.
- **Atividade 2 — divergência inicial**: quando `last_seen_block` é `null` (ZMQ ainda não recebeu blocos), o frontend exibe estado neutro em vez do banner vermelho — banner só aparece em divergência **real** (ambos hashes existem e diferem).
- **Estado em memória**: sem banco de dados. Atividade 3 usa `dict` em memória para rastrear txs enviadas; Atividade 2 usa `deque` com `maxlen`.
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
├── LICENSE
└── README.md (com tabela de status, sem texto de entrega)
```

> O texto de entrega para o canal vive **apenas** em `docs/entrega.md` (seção final). O `README.md` raiz é puramente apresentação técnica do projeto.

## Pendências / validação ao vivo
- Todas as 3 atividades precisam de `bitcoind -regtest` rodando para funcionar.
- Atividade 2 precisa de `zmqpubrawblock` e `zmqpubrawtx` no `bitcoin.conf`.
- Atividade 3 precisa de wallets criadas (`createwallet`) e saldo maturado (101 blocos minerados).
- Ver `docs/setup-bitcoin-core.md` e `docs/entrega.md` para instruções completas.

## Histórico de auditoria
- **2026-05-02 (auditoria final)**: relatório técnico completo confirmou aderência aos enunciados das 3 atividades. Aplicadas correções pós-auditoria:
  - README raiz reescrito em formato profissional (tabela de status, tecnologias, limitações conhecidas, sem texto de entrega na home).
  - `.gitignore` passou a ignorar `.claude/` e `.codex` (tooling local).
  - Frontend Atividade 2: banner de divergência só aparece em divergência real; estado inicial (ZMQ vazio) tratado.
  - `LICENSE` MIT adicionado.
  - READMEs por atividade padronizados (cabeçalho, objetivo, arquitetura, endpoints, exemplos, limitações, checklist).

## Checklist final
- [x] README.md profissional na raiz (sem texto de entrega na home)
- [x] Tabela de status no README raiz
- [x] Seção "Limitações conhecidas" no README raiz
- [x] LICENSE MIT
- [x] atividade-1/ — backend + frontend + README polido
- [x] atividade-2/ — backend + frontend + README polido
- [x] atividade-3/ — backend + frontend + README polido
- [x] Atividade 1 NÃO usa ZMQ
- [x] Atividade 1 tem /api/mempool/summary
- [x] Atividade 1 tem /api/blockchain/lag
- [x] Atividade 2 usa ZMQ real (rawblock + rawtx)
- [x] Atividade 2 tem /api/events/summary
- [x] Atividade 2 tem /api/events/latest
- [x] Atividade 2 tem /api/events/state-comparison
- [x] Atividade 2 banner de divergência trata estado inicial corretamente
- [x] Atividade 3 separa RPC global e RPC por wallet
- [x] Atividade 3 tem /wallets, /wallet/select, /wallet/status
- [x] Atividade 3 tem /tx/send (fluxo PSBT)
- [x] Atividade 3 tem /tx/{txid} enriquecido (broadcast → mempool → confirmed → unknown)
- [x] Atividade 3 frontend com seleção de wallet
- [x] .env protegido no .gitignore
- [x] .env.example existe em cada atividade
- [x] .claude/ e .codex no .gitignore
- [x] CLAUDE.md atualizado
- [x] docs/setup-bitcoin-core.md
- [x] docs/rpc-zmq.md
- [x] docs/deploy-vps.md
- [x] docs/deploy-cloudflare-tunnel.md
- [x] docs/entrega.md (texto de envio + smoke tests)
- [ ] Validação ao vivo registrada (depende de execução com `bitcoind`)
