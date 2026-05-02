# CoreCraft

Repositório do programa CoreCraft com as três atividades obrigatórias de integração com Bitcoin Core.

---

## Texto de entrega

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
Repositório único organizado conforme exigido, com backend, frontend, documentação,
integração Bitcoin Core via RPC/ZMQ quando aplicável e instruções de execução local/externa.
```

---

## Estrutura

```
corecraft/
├── atividade-1/    # Snapshot inteligente da mempool via RPC
├── atividade-2/    # Eventos em tempo real via ZMQ
├── atividade-3/    # Múltiplas wallets + PSBT + estado interpretado
├── docs/           # Setup, deploy e smoke tests
├── README.md
├── CLAUDE.md
├── .gitignore
└── docker-compose.yml
```

## Atividade 1 — Snapshot da Mempool (RPC)

**Stack:** Python + FastAPI + Uvicorn. Sem ZMQ, sem banco de dados.

**Endpoints:**
- `GET /api/mempool/summary` — snapshot com distribuição de fee rate (low/medium/high)
- `GET /api/blockchain/lag` — lag de sincronização do nó

**Rodar:**
```bash
cd atividade-1/backend
cp ../.env.example .env  # ajuste com suas credenciais RPC
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
# Acesse: http://localhost:8001
```

## Atividade 2 — Eventos em Tempo Real (ZMQ)

**Stack:** Python + FastAPI + pyzmq. Estado em memória (`collections.deque`).

**Requer:** `zmqpubrawblock` e `zmqpubrawtx` configurados no `bitcoin.conf`.

**Endpoints:**
- `GET /api/events/summary` — contadores e taxa de eventos
- `GET /api/events/latest` — últimos blocos e txs recebidos via ZMQ
- `GET /api/events/state-comparison` — divergência entre ZMQ e RPC

**Rodar:**
```bash
cd atividade-2/backend
cp ../.env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002
# Acesse: http://localhost:8002
```

## Atividade 3 — Multi-Wallet + PSBT

**Stack:** Python + FastAPI. Fluxo PSBT completo. Estado de txs em memória.

**Endpoints:**
- `GET /wallets` — lista wallets disponíveis/carregadas/selecionada
- `POST /wallet/select` — seleciona e carrega wallet
- `GET /wallet/status` — saldo e UTXOs da wallet ativa
- `POST /tx/send` — cria, assina e transmite via PSBT
- `GET /tx/{txid}` — estado interpretado (`broadcast → mempool → confirmed`)

**Rodar:**
```bash
cd atividade-3/backend
cp ../.env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003
# Acesse: http://localhost:8003
```

## Documentação

| Arquivo | Conteúdo |
|---------|----------|
| [`docs/setup-bitcoin-core.md`](docs/setup-bitcoin-core.md) | bitcoin.conf + wallets + regtest |
| [`docs/rpc-zmq.md`](docs/rpc-zmq.md) | Conceitos: RPC vs ZMQ |
| [`docs/deploy-cloudflare-tunnel.md`](docs/deploy-cloudflare-tunnel.md) | Exposição via Cloudflare Tunnel |
| [`docs/deploy-vps.md`](docs/deploy-vps.md) | Deploy em VPS Ubuntu |
| [`docs/entrega.md`](docs/entrega.md) | Smoke tests completos com curl |

## Docker (opcional)

```bash
docker compose up --build
# Atividade 1: http://localhost:8001
# Atividade 2: http://localhost:8002
# Atividade 3: http://localhost:8003
```

> Requer `.env` preenchido em cada atividade. O Bitcoin Core deve rodar no host.

## Pré-requisitos gerais

- Python 3.11+
- Bitcoin Core com regtest configurado ([instruções](docs/setup-bitcoin-core.md))
- `.env` em cada atividade (copiar de `.env.example`)
