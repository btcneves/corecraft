# Troubleshooting Docker

[Versao em ingles](../en-US/docker-troubleshooting.md)

## Diagnostico Rapido

```bash
docker compose ps
docker compose logs --tail=50 bitcoind
docker compose logs --tail=50 atividade-1
curl -s http://localhost:8001/health
curl -s http://localhost:8002/health
curl -s http://localhost:8003/health
```

## Problemas Comuns

### RPC authentication failed

Confirme se `.env` e `bitcoin.conf` usam as mesmas credenciais.

```bash
docker compose exec bitcoind bitcoin-cli -regtest getblockchaininfo
```

### `bitcoind` unhealthy

Na primeira execucao, aguarde alguns minutos. Depois verifique:

```bash
docker compose logs -f bitcoind
docker compose exec bitcoind bitcoin-cli -regtest getblockchaininfo
```

### Backend unhealthy

```bash
docker compose logs atividade-1
docker compose restart atividade-1
```

Troque `atividade-1` por `atividade-2` ou `atividade-3` conforme necessario.

### ZMQ sem eventos

Confirme se ZMQ esta ativo:

```bash
docker compose exec bitcoind bitcoin-cli -regtest getzmqnotifications
```

Depois mine um bloco:

```bash
make mine
```

### Porta em uso

```bash
ss -tuln | grep -E ':(80|8001|8002|8003|18443|28332|28333)'
```

Pare o processo conflitante ou altere as portas em `docker-compose.yml`.

### Reset completo

```bash
docker compose down -v
docker system prune -a --volumes
docker compose --profile all up --build
```

