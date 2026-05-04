# Docker Stack

CoreCraft agora pode subir a stack completa com um comando:

```bash
cp .env.example .env
docker compose up --build
```

Serviços iniciados:

| Serviço | Função | Porta |
|---|---|---:|
| `bitcoind` | Bitcoin Core em `regtest`, RPC e ZMQ | `18443`, `28332`, `28333` |
| `bitcoin-init` | Cria/carrega `wallet1` e `wallet2`, minera saldo inicial | interno |
| `atividade-1` | Backend FastAPI + frontend React | `8001` |
| `atividade-2` | Backend FastAPI + frontend React + WebSocket | `8002` |
| `atividade-3` | Backend FastAPI + frontend React | `8003` |
| `caddy` | Proxy HTTP para as três atividades | `80` |

URLs pelo Caddy:

- `http://localhost/atividade-1/`
- `http://localhost/atividade-2/`
- `http://localhost/atividade-3/`

As portas diretas continuam disponíveis para smoke tests:

- `http://localhost:8001`
- `http://localhost:8002`
- `http://localhost:8003`

Comandos úteis:

```bash
make up
make logs
make bitcoin-cli
make mine
make smoke
make down
```

Variáveis principais:

```bash
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
BTC_RPC_AUTH=user:corecraft$55eef9f3661634839386ead63a2e72d60d0ef27470547ec7b4b12d0e9dce8db2
LOG_LEVEL=INFO
```

`bitcoin.conf` usa `rpcauth`, não `rpcuser/rpcpassword`. O par `BTC_RPC_USER`/`BTC_RPC_PASSWORD` precisa corresponder ao `rpcauth` configurado para que `bitcoin-cli`, `bitcoin-init` e os backends autentiquem corretamente.

Dentro do Docker, os backends usam `bitcoind` como host RPC e ZMQ:

```bash
BTC_RPC_HOST=bitcoind
BTC_RPC_PORT=18443
ZMQ_RAWBLOCK_ENDPOINT=tcp://bitcoind:28332
ZMQ_RAWTX_ENDPOINT=tcp://bitcoind:28333
```

Healthchecks:

- `bitcoind`: `bitcoin-cli -regtest getblockchaininfo`
- `atividade-1`: `GET /health` em `8001`
- `atividade-2`: `GET /health` em `8002`
- `atividade-3`: `GET /health` em `8003`

Qualidade local:

```bash
PYTHON=./.venv/bin/python make ci
```

O target `ci` executa format, lint, type checking, testes com cobertura, build/audit dos frontends, `pip-audit` e validação do Compose.
