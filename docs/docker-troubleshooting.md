# Docker Troubleshooting

## RPC auth falhando

Sintoma:

```text
ThreadRPCServer incorrect password attempt from 127.0.0.1
```

Verifique:

```bash
cat .env
docker compose exec bitcoind bitcoin-cli -regtest \
  -rpcuser="${BTC_RPC_USER:-user}" \
  -rpcpassword="${BTC_RPC_PASSWORD:-password}" \
  getblockchaininfo
```

O `infra/bitcoin/bitcoin.conf` usa `rpcauth`. O valor padrão corresponde a:

```bash
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
```

Se alterar usuário ou senha, gere um novo `rpcauth` com o script oficial do Bitcoin Core e atualize `BTC_RPC_AUTH` no `.env.example` e o `rpcauth=` em `infra/bitcoin/bitcoin.conf`.

## Backend unhealthy

Use os endpoints diretos:

```bash
curl -sS http://localhost:8001/health
curl -sS http://localhost:8002/health
curl -sS http://localhost:8003/health
```

Se `/health` responde mas as rotas Bitcoin retornam 503, o backend está vivo e a falha está na comunicação RPC com o `bitcoind`.

## ZMQ sem eventos

A Atividade 2 pode iniciar com:

```json
{"status":"waiting_for_zmq_block"}
```

Isso é esperado até o primeiro bloco ou transação chegar via ZMQ. Gere atividade:

```bash
make mine
docker compose logs -f atividade-2
```

Confirme que o `bitcoin.conf` contém:

```ini
zmqpubrawblock=tcp://0.0.0.0:28332
zmqpubrawtx=tcp://0.0.0.0:28333
```

O listener da Atividade 2 reconecta automaticamente em caso de erro de socket.

## Caddy não abre as interfaces

Confirme a saúde dos serviços:

```bash
docker compose ps
docker compose logs caddy
```

URLs esperadas:

- `http://localhost/atividade-1/`
- `http://localhost/atividade-2/`
- `http://localhost/atividade-3/`

As portas diretas continuam úteis para isolar proxy vs backend:

- `http://localhost:8001`
- `http://localhost:8002`
- `http://localhost:8003`

## Rebuild limpo

```bash
docker compose down -v
docker compose up --build
```

`down -v` apaga o volume regtest. Use quando quiser recriar wallets, saldo inicial e estado do nó do zero.
