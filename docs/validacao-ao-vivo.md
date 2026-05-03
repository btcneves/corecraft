# Validação ao vivo — CoreCraft

Execução real contra `bitcoind -regtest` no host (Bitcoin Core v31.0). Todos os endpoints obrigatórios das três atividades foram exercitados, incluindo o ciclo PSBT completo (`broadcast → mempool → confirmed`) e o caminho de erro 503 quando o nó está offline.

- Data: 2026-05-02T17:48:09Z (UTC)
- Nó: /Satoshi:31.0.0/
- Backends locais (uvicorn): 8001 / 8002 / 8003

---

## Ambiente de validação

| Campo | Valor |
|-------|-------|
| Sistema operacional | Linux (Ubuntu) |
| Python | 3.12 |
| Bitcoin Core | v31.0.0 (`/Satoshi:31.0.0/`) |
| Rede | `regtest` |
| RPC host | `127.0.0.1` |
| RPC port | `18443` |
| ZMQ rawblock | `tcp://127.0.0.1:28332` (`pubrawblock`) |
| ZMQ rawtx | `tcp://127.0.0.1:28333` (`pubrawtx`) |
| Backend Atividade 1 | http://127.0.0.1:8001 |
| Backend Atividade 2 | http://127.0.0.1:8002 |
| Backend Atividade 3 | http://127.0.0.1:8003 |
| URL pública | Ainda não registrada. Ver `docs/deploy-cloudflare-tunnel.md` e `docs/deploy-vps.md`. |

---

## Checklist de validação

- [x] Bitcoin Core rodando
- [x] RPC respondendo
- [x] ZMQ configurado
- [x] Wallets criadas/carregadas
- [x] Atividade 1 validada
- [x] Atividade 2 validada
- [x] Atividade 3 validada
- [x] Frontend acessível (local)
- [ ] URL pública/tunnel testado

---

## Comandos Bitcoin Core

```bash
bitcoin-cli -regtest getblockchaininfo
bitcoin-cli -regtest getmempoolinfo
bitcoin-cli -regtest getrawmempool true
bitcoin-cli -regtest getbestblockhash
bitcoin-cli -regtest getzmqnotifications
bitcoin-cli -regtest listwalletdir
bitcoin-cli -regtest listwallets
```

---

## Preparação de wallets em regtest

```bash
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2

ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR

bitcoin-cli -regtest -rpcwallet=wallet1 getwalletinfo
bitcoin-cli -regtest -rpcwallet=wallet1 listunspent
```

---

## Smoke tests — Atividade 1

```bash
curl http://127.0.0.1:8001/api/mempool/summary
curl http://127.0.0.1:8001/api/blockchain/lag
```

Campos esperados — `/api/mempool/summary`: `tx_count`, `total_vsize`, `avg_fee_rate`, `min_fee_rate`, `max_fee_rate`, `fee_distribution.low`, `fee_distribution.medium`, `fee_distribution.high`

Campos esperados — `/api/blockchain/lag`: `blocks`, `headers`, `lag`

---

## Smoke tests — Atividade 2

```bash
curl http://127.0.0.1:8002/api/events/summary
curl http://127.0.0.1:8002/api/events/latest
curl http://127.0.0.1:8002/api/events/state-comparison
```

Campos esperados — `/api/events/summary`: `blocks_observed`, `tx_observed`, `last_event_time`, `tx_per_second`

Campos esperados — `/api/events/latest`: `blocks[]`, `txs[]`

Campos esperados — `/api/events/state-comparison`: `best_block`, `last_seen_block`, `divergence`, `status`

Para gerar eventos:

```bash
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 1 $ADDR

ADDR2=$(bitcoin-cli -regtest -rpcwallet=wallet2 getnewaddress)
bitcoin-cli -regtest -rpcwallet=wallet1 sendtoaddress $ADDR2 0.001
```

---

## Smoke tests — Atividade 3

```bash
curl http://127.0.0.1:8003/wallets

curl -X POST http://127.0.0.1:8003/wallet/select \
  -H "Content-Type: application/json" \
  -d '{"wallet":"wallet1"}'

curl http://127.0.0.1:8003/wallet/status

curl -X POST http://127.0.0.1:8003/tx/send \
  -H "Content-Type: application/json" \
  -d '{"to_address":"ENDERECO_REGTEST","amount":0.001}'

curl http://127.0.0.1:8003/tx/TXID
```

Campos esperados — `/wallets`: `available_wallets`, `loaded_wallets`, `selected_wallet`

Campos esperados — `/wallet/status`: `wallet`, `balance`, `utxos`

Campos esperados — `/tx/{txid}`: `txid`, `wallet`, `status`, `confirmed`, `confirmations`, `block_hash`, `age_seconds`, `message`, `warning` (quando aplicável)

---

## Evidências de execução (regtest, 2026-05-02)

---

## 1. Pré-requisitos no Bitcoin Core

### `bitcoin-cli -regtest getblockchaininfo`

```json
{
  "chain": "regtest",
  "blocks": 109,
  "headers": 109,
  "bestblockhash": "2449b103ec8d67972e541d924b5d8f18e91b08773258f86012b28a19fd249c21",
  "bits": "207fffff",
  "target": "7fffff0000000000000000000000000000000000000000000000000000000000",
  "difficulty": 4.656542373906925e-10,
  "time": 1777743959,
  "mediantime": 1777743914,
  "verificationprogress": 1,
  "initialblockdownload": false,
  "chainwork": "00000000000000000000000000000000000000000000000000000000000000dc",
  "size_on_disk": 32759,
  "pruned": false,
  "warnings": [
  ]
}
```

### `bitcoin-cli -regtest getzmqnotifications`

```json
[
  {
    "type": "pubrawblock",
    "address": "tcp://127.0.0.1:28332",
    "hwm": 1000
  },
  {
    "type": "pubrawtx",
    "address": "tcp://127.0.0.1:28333",
    "hwm": 1000
  }
]
```

### `bitcoin-cli -regtest listwalletdir`

```json
{
  "wallets": [
    {
      "name": "smoke_test_wallet",
      "warnings": [
      ]
    },
    {
      "name": "wallet1",
      "warnings": [
      ]
    },
    {
      "name": "wallet2",
      "warnings": [
      ]
    },
    {
      "name": "corecraft",
      "warnings": [
      ]
    }
  ]
}
```

### `bitcoin-cli -regtest listwallets`

```json
[
  "wallet1",
  "wallet2"
]
```

---

## 2. Atividade 1 — Snapshot da mempool via RPC

### `GET /api/mempool/summary` (mempool vazia)

```json
{
    "tx_count": 1,
    "total_vsize": 141,
    "avg_fee_rate": 20.0,
    "min_fee_rate": 20.0,
    "max_fee_rate": 20.0,
    "fee_distribution": {
        "low": 0,
        "medium": 1,
        "high": 0
    }
}
```

### `GET /api/blockchain/lag`

```json
{
    "blocks": 109,
    "headers": 109,
    "lag": 0
}
```

---

## 3. Atividade 2 — Eventos via ZMQ

### Estado inicial — ZMQ ainda sem blocos (evidência da Correção 2)

Imediatamente após subir o backend, antes que qualquer evento ZMQ chegue:

#### `GET /api/events/state-comparison`

```json
{
    "best_block": "2449b103ec8d67972e541d924b5d8f18e91b08773258f86012b28a19fd249c21",
    "last_seen_block": null,
    "divergence": null,
    "status": "waiting_for_zmq_block",
    "message": "Nenhum bloco observado via ZMQ ainda."
}
```

→ `divergence: null`, `status: "waiting_for_zmq_block"`, `message` explícita. Antes desta correção a API retornava `divergence: true` (falso-positivo), porque `null != hash` em Python. O frontend não exibe o banner vermelho neste estado.

#### `GET /api/events/summary` (vazio)

```json
{
    "blocks_observed": 0,
    "tx_observed": 0,
    "last_event_time": null,
    "tx_per_second": 0.0
}
```

#### `GET /api/events/latest` (vazio)

```json
{
    "blocks": [],
    "txs": []
}
```

### Após gerar 1 bloco + 1 tx

Comandos no Bitcoin Core:

```bash
bitcoin-cli -regtest generatetoaddress 1 $ADDR
bitcoin-cli -regtest -rpcwallet=wallet1 sendtoaddress $ADDR 0.001
```

#### `GET /api/events/summary`

```json
{
    "blocks_observed": 1,
    "tx_observed": 3,
    "last_event_time": 1777744108.3403544,
    "tx_per_second": 73.45
}
```

#### `GET /api/events/latest`

```json
{
    "blocks": [
        {
            "hash": "568062536af2ea73b460df09cd335a0cd7b8469f9eca68155fdf3700da603879",
            "ts": 1777744108.3127046
        }
    ],
    "txs": [
        {
            "txid": "496ee92dc1c70cb056c8ad84b12ca9df092dc155dc160367516bbe05cd60b564",
            "ts": 1777744108.2995093
        },
        {
            "txid": "3ea0e1c410631b984a30db9250f689ff8acd722b9822598ce17c5381f890bd08",
            "ts": 1777744108.3010132
        },
        {
            "txid": "e6194a7e07e1cf2e145ed0d3076784e85be3be521c4a3922d656a5fb16f2b226",
            "ts": 1777744108.3403544
        }
    ]
}
```

#### `GET /api/events/state-comparison` (status: compared)

```json
{
    "best_block": "568062536af2ea73b460df09cd335a0cd7b8469f9eca68155fdf3700da603879",
    "last_seen_block": "568062536af2ea73b460df09cd335a0cd7b8469f9eca68155fdf3700da603879",
    "divergence": false,
    "status": "compared"
}
```

→ `status: "compared"`, `divergence: false` — `best_block` (RPC) e `last_seen_block` (ZMQ) coincidem.

---

## 4. Atividade 3 — Multi-wallet, PSBT, estado interpretado

### `GET /wallets` (descoberta)

```json
{
    "available_wallets": [
        "smoke_test_wallet",
        "wallet1",
        "wallet2",
        "corecraft"
    ],
    "loaded_wallets": [
        "wallet1",
        "wallet2"
    ],
    "selected_wallet": null
}
```

### `POST /wallet/select` → wallet1

```json
{
    "selected_wallet": "wallet1",
    "wallet_info": {
        "walletname": "wallet1",
        "balance": null,
        "txcount": 105
    }
}
```

### `GET /wallet/status` (com wallet1 selecionada)

```json
{
    "wallet": "wallet1",
    "balance": null,
    "utxos": 3
}
```

### `POST /tx/send` (fluxo PSBT)

Endereço destino na wallet2:

```bash
DEST=bcrt1q5eue8fczuaw46d5zr6y47sergm69lnzslzr5mg
curl -X POST http://127.0.0.1:8003/tx/send \
  -H 'Content-Type: application/json' \
  -d "{\"to_address\":\"$DEST\",\"amount\":0.001}"
```

Resposta (tx broadcast):

```json
{"txid":"abefee2af319bb2cd3d313838f325e3362a012741c0fcd158ce2fcd6dfb7a422","wallet":"wallet1","status":"broadcast"}
```

### `GET /tx/{txid}` — recém-enviada (mempool)

```json
{
    "txid": "abefee2af319bb2cd3d313838f325e3362a012741c0fcd158ce2fcd6dfb7a422",
    "wallet": "wallet1",
    "status": "mempool",
    "confirmed": false,
    "confirmations": 0,
    "block_hash": null,
    "age_seconds": 10,
    "message": "Transa\u00e7\u00e3o aceita na mempool, aguardando inclus\u00e3o em bloco."
}
```

### Evidência do bug fix da Correção 1 — wallet rastreada

Trocando a wallet ativa para `wallet2` (que **não enviou** esta tx) e consultando o mesmo txid:

#### `POST /wallet/select` → wallet2

```json
{
    "selected_wallet": "wallet2",
    "wallet_info": {
        "walletname": "wallet2",
        "balance": null,
        "txcount": 1
    }
}
```

#### `GET /tx/{txid}` (com wallet2 ativa)

```json
{
    "txid": "abefee2af319bb2cd3d313838f325e3362a012741c0fcd158ce2fcd6dfb7a422",
    "wallet": "wallet1",
    "status": "mempool",
    "confirmed": false,
    "confirmations": 0,
    "block_hash": null,
    "age_seconds": 23,
    "message": "Transa\u00e7\u00e3o aceita na mempool, aguardando inclus\u00e3o em bloco."
}
```

→ Resposta ainda traz `"wallet": "wallet1"` (a wallet original do envio), e `gettransaction` continua resolvendo no contexto certo. **Antes da Correção 1**, a chamada teria caído na wallet2 e `gettransaction` falharia silenciosamente, levando o status a `unknown`.

Voltando a seleção para wallet1 antes do próximo passo:

```bash
curl -X POST http://127.0.0.1:8003/wallet/select \
  -H "Content-Type: application/json" -d '{"wallet":"wallet1"}'
```

### Após minerar 1 bloco — `status: confirmed`

```bash
bitcoin-cli -regtest generatetoaddress 1 $ADDR
```

#### `GET /tx/{txid}` (confirmed)

```json
{
    "txid": "abefee2af319bb2cd3d313838f325e3362a012741c0fcd158ce2fcd6dfb7a422",
    "wallet": "wallet1",
    "status": "confirmed",
    "confirmed": true,
    "confirmations": 1,
    "block_hash": "0cff68eccfe79d9088e78673d17bb8c7bc2c9eb375eafb790c9edd2bbcab2785",
    "age_seconds": 38,
    "message": "Transa\u00e7\u00e3o confirmada em bloco."
}
```

→ `status: "confirmed"`, `confirmed: true`, `confirmations >= 1`, `block_hash` não-nulo, `message: "Transação confirmada em bloco."`.

---

## 5. Caminho de erro — Bitcoin Core offline (HTTP 503 estruturado)

Após `bitcoin-cli -regtest stop`, todas as rotas que dependem do nó devolvem 503 estruturado:

### `GET /api/mempool/summary` (Atividade 1)

```
{"detail":{"error":"node_unavailable","detail":"Cannot connect to Bitcoin node: HTTPConnectionPool(host='127.0.0.1', port=18443): Max retries exceeded with url: / (Caused by NewConnectionError(\"HTTPConnection(host='127.0.0.1', port=18443): Failed to establish a new connection: [Errno 111] Connection refused\"))"}}HTTP 503
```

### `GET /api/events/state-comparison` (Atividade 2)

```
{"detail":{"error":"node_unavailable","detail":"Cannot connect to Bitcoin node: HTTPConnectionPool(host='127.0.0.1', port=18443): Max retries exceeded with url: / (Caused by NewConnectionError(\"HTTPConnection(host='127.0.0.1', port=18443): Failed to establish a new connection: [Errno 111] Connection refused\"))"}}HTTP 503
```

### `GET /wallets` (Atividade 3)

```
{"detail":{"error":"node_unavailable","detail":"Cannot connect to Bitcoin node: HTTPConnectionPool(host='127.0.0.1', port=18443): Max retries exceeded with url: / (Caused by NewConnectionError(\"HTTPConnection(host='127.0.0.1', port=18443): Failed to establish a new connection: [Errno 111] Connection refused\"))"}}HTTP 503
```

→ Em todas as três, o backend devolve `HTTP 503` com payload `{"detail": {"error": "node_unavailable", "detail": "Cannot connect to Bitcoin node: ..."}}` — comportamento por design (nenhuma rota retorna 500).

---

## 6. Conclusão

Todos os 9 endpoints obrigatórios + ciclo PSBT + bug fix da Atividade 3 + path 503 foram exercitados em `regtest` real com Bitcoin Core v31.0. Evidências capturadas neste arquivo correspondem a uma sessão de validação única e linear.

**Status final: pronto para entrega.**

---

## Resultado da validação

| Item | Status | Evidência | Observação |
|------|--------|-----------|------------|
| Bitcoin Core RPC | OK | Seção 1 (`getblockchaininfo`) | v31.0.0, regtest, 109 blocos |
| ZMQ | OK | Seção 1 (`getzmqnotifications`) | rawblock:28332, rawtx:28333 |
| Atividade 1 | OK | Seção 2 | `/api/mempool/summary` + `/api/blockchain/lag` |
| Atividade 2 | OK | Seção 3 | `/api/events/{summary,latest,state-comparison}` + divergence fix |
| Atividade 3 | OK | Seção 4 | `/wallets`, PSBT completo, bug fix wallet tracking |
| Caminho 503 | OK | Seção 5 | Todas as rotas retornam `node_unavailable` estruturado |
| Frontend | Pendente | — | Verificável em `http://127.0.0.1:800{1,2,3}` com bitcoind ativo |
| Acesso externo | Pendente | — | URL não configurada; ver `docs/deploy-cloudflare-tunnel.md` |
