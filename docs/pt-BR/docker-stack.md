# Stack Docker

[Versao em ingles](../en-US/docker-stack.md)

O Docker Compose sobe o ambiente completo do CoreCraft: Bitcoin Core em `regtest`, inicializacao de wallets, tres backends, frontends e Caddy.

## Inicio Rapido

```bash
cp .env.example .env
docker compose --profile all up --build
```

## Servicos

| Servico | Funcao | Porta |
|---------|--------|-------|
| `bitcoind` | no Bitcoin Core em regtest | 18443, 28332, 28333 |
| `bitcoin-init` | cria wallets e minera saldo inicial | interno |
| `atividade-1` | mempool snapshot | 8001 |
| `atividade-2` | eventos ZMQ | 8002 |
| `atividade-3` | wallets, PSBT e transacoes | 8003 |
| `caddy` | proxy reverso | 80 |

## Acesso

```text
http://localhost:8001
http://localhost:8002
http://localhost:8003
http://localhost/atividade-1/
http://localhost/atividade-2/
http://localhost/atividade-3/
```

## Comandos Uteis

```bash
make up
make down
make logs
make ps
make mine
make mine-10
make smoke
make clean
```

## Variaveis

O arquivo `.env` deve manter credenciais consistentes com o Bitcoin Core:

```env
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
COMPOSE_PROFILES=all
```

Para detalhes de diagnostico, veja [`docker-troubleshooting.md`](docker-troubleshooting.md).
