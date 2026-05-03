# Atividade 1 — Snapshot Inteligente da Mempool via RPC

> Backend FastAPI + frontend React/Vite que consulta o Bitcoin Core via JSON-RPC e expõe um snapshot enriquecido da mempool e do status de sincronização do nó.

---

## Objetivo

Construir uma camada de **interpretação** sobre o estado bruto do nó: em vez de apenas devolver o JSON do `getmempoolinfo`, a aplicação calcula taxa média/mínima/máxima de fee, distribui as transações em faixas (low / medium / high) e expõe lag de sincronização entre `headers` e `blocks`.

## Restrições obrigatórias

- **Apenas RPC.** Sem ZMQ.
- **Sem banco de dados.** Tudo é calculado on-demand.
- **Sem libs Bitcoin de alto nível.** Cliente JSON-RPC próprio (`requests` + `HTTPBasicAuth`).
- Cálculo de fee rate sempre em sat/vB, com a fórmula:

  ```
  fee_rate = (fee_btc × 100_000_000) / vsize
  ```

## Arquitetura

```
atividade-1/
├── backend/
│   ├── app/
│   │   ├── main.py        rotas FastAPI + serve build React
│   │   ├── mempool.py     summary() e lag() — toda a lógica de cálculo
│   │   └── rpc_client.py  JSON-RPC (RPCError, RPCConnectionError, BitcoinRPC)
│   └── requirements.txt
├── frontend/              dashboard React/Vite com polling 5s
├── .env.example
└── README.md
```

## Endpoints

| Método | Rota | Descrição | RPC consumido |
|:------:|------|-----------|---------------|
| GET | `/api/mempool/summary` | Snapshot da mempool com distribuição de fee rate | `getmempoolinfo`, `getrawmempool true` |
| GET | `/api/blockchain/lag` | Lag de sincronização do nó | `getblockchaininfo` |

### Exemplo — `GET /api/mempool/summary`

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

| Faixa | Fee rate (sat/vB) |
|-------|-------------------|
| `low` | `< 10` |
| `medium` | `10 – 50` (inclusive) |
| `high` | `> 50` |

### Exemplo — `GET /api/blockchain/lag`

```json
{
  "blocks": 572061,
  "headers": 572120,
  "lag": 59
}
```

## Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste:

```env
BTC_RPC_HOST=127.0.0.1
BTC_RPC_PORT=18443        # regtest=18443 · mainnet=8332 · testnet=18332
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
```

## Como rodar

```bash
cd atividade-1/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Frontend disponível em [http://localhost:8001](http://localhost:8001) — polling automático a cada 5 s.

## Frontend

Dois cards lado a lado:

- **Mempool Intelligence** — total de transações, fee média/mínima/máxima e barra de distribuição low/medium/high.
- **Node Sync Status** — `blocks`, `headers` e `lag` em blocos.

Estados de loading e erro são tratados; quando o nó está offline, o card exibe a mensagem do 503 estruturado.

## Smoke tests com `bitcoin-cli`

```bash
# Iniciar nó
bitcoind -regtest -daemon

# Criar wallet e gerar saldo
bitcoin-cli -regtest createwallet wallet1
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR

# Endpoints
curl -s http://127.0.0.1:8001/api/mempool/summary | python3 -m json.tool
curl -s http://127.0.0.1:8001/api/blockchain/lag | python3 -m json.tool
```

## Comportamento sem nó

Quando o `bitcoind` não está acessível, todas as rotas devolvem **HTTP 503** com payload estruturado:

```json
{ "detail": { "error": "node_unavailable", "detail": "Cannot connect to Bitcoin node: ..." } }
```

## Checklist desta atividade

- [x] `GET /api/mempool/summary` com todos os campos exigidos
- [x] Usa `getmempoolinfo` e `getrawmempool true`
- [x] Cálculo de `avg_fee_rate`, `min_fee_rate`, `max_fee_rate` em sat/vB
- [x] `fee_distribution.{low,medium,high}` com classificação correta
- [x] Proteção contra `vsize == 0`
- [x] `GET /api/blockchain/lag` com `blocks`, `headers`, `lag`
- [x] Frontend exibe os dois cards
- [x] Tratamento de erro (503 estruturado)
- [x] **Não usa** ZMQ
- [x] **Não usa** banco de dados
- [x] **Não usa** libs Bitcoin de alto nível
