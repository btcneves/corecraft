# Atividade 1 — Snapshot Inteligente da Mempool via RPC

## Objetivo
Consultar o Bitcoin Core via JSON-RPC e expor um snapshot enriquecido da mempool e do status de sincronização do nó através de uma API REST + frontend web.

## Restrições
- **Apenas RPC** (sem ZMQ, sem banco de dados, sem libs Bitcoin de alto nível).
- Todo cálculo de fee rate é feito na aplicação: `fee_rate = (fee_btc × 1e8) / vsize`.

## Variáveis de ambiente

Copie `.env.example` → `.env` e preencha:

```env
BTC_RPC_HOST=127.0.0.1
BTC_RPC_PORT=18443       # regtest=18443, mainnet=8332, testnet=18332
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
```

## Como rodar o backend

```bash
cd atividade-1/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Como abrir o frontend

Com o backend rodando, acesse: [http://localhost:8001](http://localhost:8001)

O frontend é servido diretamente pelo FastAPI. Polling automático a cada 5 s.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/mempool/summary` | Snapshot da mempool com distribuição de fee rate |
| GET | `/api/blockchain/lag` | Lag de sincronização do nó |

### Exemplo: `/api/mempool/summary`
```json
{
  "tx_count": 12345,
  "total_vsize": 3456789,
  "avg_fee_rate": 42.3,
  "min_fee_rate": 5.1,
  "max_fee_rate": 120.8,
  "fee_distribution": {
    "low": 3200,
    "medium": 7000,
    "high": 2145
  }
}
```

Classificação:
- `low`: fee rate < 10 sat/vB
- `medium`: fee rate entre 10 e 50 sat/vB
- `high`: fee rate > 50 sat/vB

### Exemplo: `/api/blockchain/lag`
```json
{
  "blocks": 572061,
  "headers": 572120,
  "lag": 59
}
```

## Como testar com Bitcoin Core (regtest)

```bash
# Iniciar bitcoind
bitcoind -regtest -daemon

# Criar wallet e gerar saldo
bitcoin-cli -regtest createwallet wallet1
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR

# Smoke tests
curl http://127.0.0.1:8001/api/mempool/summary
curl http://127.0.0.1:8001/api/blockchain/lag
```

## Erros esperados (sem node)

Quando o Bitcoin Core não está acessível, todas as rotas retornam:
```json
HTTP 503
{"detail": {"error": "node_unavailable", "detail": "Cannot connect to Bitcoin node: ..."}}
```
