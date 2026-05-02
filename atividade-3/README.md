# Atividade 3 — Múltiplas Wallets, PSBT e Estado Interpretado

> Backend FastAPI + frontend estático que carrega e seleciona wallets do Bitcoin Core, monta transações via fluxo PSBT, transmite ao nó e expõe o ciclo de vida interpretado de cada transação (`broadcast → mempool → confirmed`).

---

## Objetivo

Evoluir o sistema para suportar:

1. **Múltiplas wallets** com seleção dinâmica (descoberta via `listwalletdir`, carregamento via `loadwallet`).
2. **Envio real** de transação via fluxo PSBT (`walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction`).
3. **Interpretação** do estado da transação ao longo do tempo, com mensagens em português e warning de demora na mempool.

## RPC global × RPC de wallet

A separação entre contexto global do nó e contexto específico da wallet é **estrutural** no código:

| Chamada | Contexto | URL final |
|---------|----------|-----------|
| `sendrawtransaction`, `getblockchaininfo`, `getmempoolentry`, `getbestblockhash`, `listwalletdir`, `listwallets`, `loadwallet` | Global (nó) | `http://host:18443/` |
| `listunspent`, `getrawchangeaddress`, `walletcreatefundedpsbt`, `walletprocesspsbt`, `finalizepsbt`, `signrawtransactionwithwallet`, `gettransaction`, `getwalletinfo` | Wallet específica | `http://host:18443/wallet/<NOME>` |

No código, isto é representado por dois construtores:

```python
rpc_node()                   # cliente sem prefixo de wallet
rpc_wallet("wallet1")        # cliente com /wallet/wallet1 no path
```

## Arquitetura

```
atividade-3/
├── backend/
│   ├── app/
│   │   ├── main.py             rotas FastAPI + state em memória
│   │   ├── wallet_service.py   list_wallets, select_wallet, wallet_status
│   │   ├── tx_service.py       send_tx (PSBT) + get_tx
│   │   ├── tx_interpreter.py   broadcast → mempool → confirmed → unknown
│   │   └── rpc_client.py       BitcoinRPC com suporte opcional a /wallet/<nome>
│   └── requirements.txt
├── frontend/                   seletor de wallet, formulário de envio, tabela de tx
├── .env.example
└── README.md
```

## Fluxo de envio — PSBT

```
walletcreatefundedpsbt  ──┐
walletprocesspsbt        ─┤  → wallet ativa (RPC com /wallet/<nome>)
finalizepsbt             ─┘
sendrawtransaction        ──→ nó (RPC global)
```

**Por que PSBT?** O Bitcoin Core cuida de seleção de UTXO, cálculo de fee e adição de troco automaticamente — mais robusto do que montar a raw transaction manualmente.

## Endpoints

| Método | Rota | Body | Descrição |
|:------:|------|------|-----------|
| GET  | `/wallets` | — | Lista wallets disponíveis, carregadas e a selecionada |
| POST | `/wallet/select` | `{ "wallet": "<nome>" }` | Seleciona (e carrega se necessário) a wallet ativa |
| GET  | `/wallet/status` | — | Saldo e UTXOs da wallet ativa |
| POST | `/tx/send` | `{ "to_address": "...", "amount": 0.001 }` | Cria, assina e transmite tx via PSBT |
| GET  | `/tx/{txid}` | — | Estado interpretado da transação |

### Exemplo — `GET /wallets`

```json
{
  "available_wallets": ["wallet1", "wallet2"],
  "loaded_wallets": ["wallet1"],
  "selected_wallet": "wallet1"
}
```

### Exemplo — `POST /wallet/select`

```json
// Request
{ "wallet": "wallet2" }

// Response
{
  "selected_wallet": "wallet2",
  "wallet_info": {
    "walletname": "wallet2",
    "balance": 0.001,
    "txcount": 4
  }
}
```

### Exemplo — `GET /wallet/status`

```json
{ "wallet": "wallet1", "balance": 0.0012, "utxos": 3 }
```

### Exemplo — `POST /tx/send`

```json
// Request
{ "to_address": "bcrt1q...", "amount": 0.001 }

// Response
{ "txid": "abc...", "wallet": "wallet1", "status": "broadcast" }
```

### Exemplo — `GET /tx/{txid}`

```json
{
  "txid": "abc...",
  "wallet": "wallet1",
  "status": "mempool",
  "confirmed": false,
  "confirmations": 0,
  "block_hash": null,
  "age_seconds": 145,
  "message": "Transação aceita na mempool, aguardando inclusão em bloco.",
  "warning": "Transação está na mempool há mais de 2 minutos."
}
```

## Interpretação do estado da transação

| Condição | `status` | `message` / `warning` |
|----------|---------|-----------------------|
| `confirmations > 0` | `confirmed` | "Transação confirmada em bloco." |
| Está na mempool | `mempool` | "Transação aceita na mempool, aguardando inclusão em bloco." |
| Mempool há mais de 2 min | `mempool` | + warning: "Transação está na mempool há mais de 2 minutos." |
| Enviada mas ainda propagando | `broadcast` | "Transação enviada ao node, aguardando aceitação na mempool." |
| Não localizada na wallet | `unknown` | warning: "Transação não localizada na wallet selecionada." |

A idade é calculada a partir do `broadcast_ts` armazenado na tabela em memória `tracked_txs`; quando indisponível, cai no `time` do `getmempoolentry`.

## Variáveis de ambiente

```env
BTC_RPC_HOST=127.0.0.1
BTC_RPC_PORT=18443
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
```

## Como rodar

```bash
cd atividade-3/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

Frontend em [http://localhost:8003](http://localhost:8003).

## Frontend

- **Seleção de Wallet** — `<select>` preenchido por `GET /wallets`. Auto-seleciona quando há apenas uma; troca chama `POST /wallet/select`.
- **Status da Wallet** — saldo e UTXOs da wallet ativa, polling 10 s.
- **Enviar Transação** — formulário com endereço destino e valor; nota explícita "Transação criada e assinada com a wallet selecionada via PSBT".
- **Transações Enviadas** — tabela com TXID, wallet, status (badge colorido), confirmações, idade e mensagem; polling 5 s reavalia o estado de cada txid.

## Setup completo de regtest

```bash
# 1. Iniciar nó
bitcoind -regtest -daemon

# 2. Criar 2 wallets
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2

# 3. Gerar saldo na wallet1
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR

# 4. Conferir saldo
bitcoin-cli -regtest -rpcwallet=wallet1 getwalletinfo
```

## Smoke tests via curl

```bash
# Listar wallets
curl -s http://127.0.0.1:8003/wallets | python3 -m json.tool

# Selecionar wallet1
curl -s -X POST http://127.0.0.1:8003/wallet/select \
  -H "Content-Type: application/json" \
  -d '{"wallet":"wallet1"}' | python3 -m json.tool

# Status
curl -s http://127.0.0.1:8003/wallet/status | python3 -m json.tool

# Enviar 0.001 BTC para um endereço da wallet2
DEST=$(bitcoin-cli -regtest -rpcwallet=wallet2 getnewaddress)
TXID=$(curl -s -X POST http://127.0.0.1:8003/tx/send \
  -H "Content-Type: application/json" \
  -d "{\"to_address\":\"$DEST\",\"amount\":0.001}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['txid'])")
echo "TXID: $TXID"

# Estado (broadcast / mempool)
curl -s http://127.0.0.1:8003/tx/$TXID | python3 -m json.tool

# Confirmar minerando 1 bloco
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 1 $ADDR

# Estado (confirmed)
curl -s http://127.0.0.1:8003/tx/$TXID | python3 -m json.tool
```

## Acesso externo

```bash
cloudflared tunnel --url http://localhost:8003
```

Detalhes em [`docs/deploy-cloudflare-tunnel.md`](../docs/deploy-cloudflare-tunnel.md) e [`docs/deploy-vps.md`](../docs/deploy-vps.md).

## Limitações conhecidas

- O `tracked_txs` é em memória — reiniciar o backend zera a tabela. O estado consegue ser reconstruído em parte porque `gettransaction` continua respondendo enquanto o txid existir na wallet.
- `POST /wallet/select` retorna **404** se a wallet não existir em `listwalletdir`, e **503** se o nó estiver indisponível.
- `POST /tx/send` exige wallet selecionada (**409 Conflict** caso contrário) e UTXOs gastáveis na wallet (regtest precisa de 101 blocos minerados antes que o coinbase fique maduro).

## Checklist desta atividade

- [x] RPC global do nó separado de RPC por wallet (`rpc_node()` × `rpc_wallet(name)`)
- [x] `GET /wallets` usa `listwalletdir` e `listwallets`
- [x] `POST /wallet/select` carrega via `loadwallet` quando necessário
- [x] `GET /wallet/status` consulta `getwalletinfo` e `listunspent` no contexto da wallet
- [x] `POST /tx/send` implementa fluxo PSBT completo
- [x] `GET /tx/{txid}` retorna estado interpretado com mensagem e warning
- [x] Interpretação cobre `broadcast`, `mempool`, `confirmed` e `unknown`
- [x] Warning quando tx está na mempool há mais de 2 minutos
- [x] Frontend tem `<select>` de wallet preenchido por API
- [x] Lista de transações exibe a wallet usada em cada linha
- [x] Documentação de acesso externo (Cloudflare Tunnel + VPS)
