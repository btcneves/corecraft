# CLAUDE.md — CoreCraft

## Contexto do projeto

Três micro-serviços independentes de integração com Bitcoin Core (regtest):

| Atividade | Foco | Porta |
|-----------|------|-------|
| 1 | Snapshot da mempool via RPC | 8001 |
| 2 | Eventos em tempo real via ZMQ | 8002 |
| 3 | Multi-wallet + PSBT + estado interpretado | 8003 |

## Stack

- Python 3.12 + FastAPI + Uvicorn
- Frontend HTML/CSS/JS puro servido pelo FastAPI
- `rpc_client.py` próprio em cada atividade, usando `requests` — sem libs Bitcoin de alto nível
- ZMQ apenas na Atividade 2 (`pyzmq`, thread daemon)

## Estrutura

```
corecraft/
├── atividade-1/   backend (porta 8001) + frontend
├── atividade-2/   backend (porta 8002) + frontend + ZMQ
├── atividade-3/   backend (porta 8003) + frontend + multi-wallet
├── docs/          architecture.md, setup, rpc-zmq, deploy, smoke-tests, validacao
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
└── README.md
```

## Decisões-chave

- **PSBT (Atividade 3)**: `walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction`.
- **RPC global × wallet (Atividade 3)**: `rpc_node()` (global) e `rpc_wallet(name)` (por wallet) — nunca se misturam. `get_tx()` usa a wallet registrada no envio, não a wallet atualmente selecionada.
- **Estado em memória**: `deque` na Atividade 2, `dict` na Atividade 3. Zera ao reiniciar o processo.
- **Erro 503 estruturado**: `{"detail": {"error": "node_unavailable", "detail": "..."}}` quando o nó está offline.
- **JSON-RPC `"2.0"`**: Bitcoin Core ≥ 31 rejeita `"1.1"` com erro `-32600`.
- **Divergência ZMQ**: quando `last_seen_block` é `null`, a API retorna `divergence: null` + `status: "waiting_for_zmq_block"` — o frontend não exibe banner vermelho neste estado.
- **txid (Atividade 2)**: resolvido via `decoderawtransaction` (evita parser de serialização witness).

## Documentação de referência

- Decisões de arquitetura completas: `docs/architecture.md`
- Setup do Bitcoin Core: `docs/setup-bitcoin-core.md`
- Smoke tests: `docs/smoke-tests.md`
- Validação ao vivo: `docs/validacao-ao-vivo.md`
