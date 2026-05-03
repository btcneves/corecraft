# Docker Stack

CoreCraft agora pode subir a stack completa com um comando:

```bash
cp .env.example .env
docker compose up --build
```

Servicos iniciados:

| Servico | Funcao | Porta |
|---|---|---:|
| `bitcoind` | Bitcoin Core em `regtest`, RPC e ZMQ | `18443`, `28332`, `28333` |
| `bitcoin-init` | Cria/carrega `wallet1` e `wallet2`, minera saldo inicial | interno |
| `atividade-1` | Backend FastAPI + frontend React | `8001` |
| `atividade-2` | Backend FastAPI + frontend React + WebSocket | `8002` |
| `atividade-3` | Backend FastAPI + frontend React | `8003` |
| `caddy` | Proxy HTTP para as tres atividades | `80` |

URLs pelo Caddy:

- `http://localhost/atividade-1/`
- `http://localhost/atividade-2/`
- `http://localhost/atividade-3/`

As portas diretas continuam disponiveis para smoke tests:

- `http://localhost:8001`
- `http://localhost:8002`
- `http://localhost:8003`

Comandos uteis:

```bash
make up
make logs
make bitcoin-cli
make mine
make smoke
make down
```

Variaveis principais:

```bash
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
LOG_LEVEL=INFO
```

Dentro do Docker, os backends usam `bitcoind` como host RPC e ZMQ:

```bash
BTC_RPC_HOST=bitcoind
BTC_RPC_PORT=18443
ZMQ_RAWBLOCK_ENDPOINT=tcp://bitcoind:28332
ZMQ_RAWTX_ENDPOINT=tcp://bitcoind:28333
```
