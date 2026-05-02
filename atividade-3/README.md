# Atividade 3 — Múltiplas Wallets e Estado Interpretado

## Objetivo
Evoluir o sistema para suportar múltiplas wallets, criar e transmitir transações via PSBT e exibir o estado interpretado de cada transação (`broadcast → mempool → confirmed`).

## RPC global do node vs RPC da wallet

| Chamada | Contexto | URL |
|---------|----------|-----|
| `sendrawtransaction`, `getblockchaininfo`, `getmempoolentry`, `listwalletdir`, `listwallets`, `loadwallet` | Global (node) | `http://host:18443/` |
| `listunspent`, `getrawchangeaddress`, `walletcreatefundedpsbt`, `walletprocesspsbt`, `finalizepsbt`, `signrawtransactionwithwallet`, `gettransaction`, `getwalletinfo` | Wallet específica | `http://host:18443/wallet/NOME` |

## Fluxo de envio — PSBT

**Escolha de design:** `walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction`

O Bitcoin Core cuida da seleção de UTXOs, cálculo de fee e adição de troco automaticamente. Mais robusto que montar a raw transaction manualmente.

## Variáveis de ambiente

Copie `.env.example` → `.env`:

```env
BTC_RPC_HOST=127.0.0.1
BTC_RPC_PORT=18443
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
```

## Como criar wallets de teste

```bash
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2
```

## Como carregar wallets

```bash
bitcoin-cli -regtest loadwallet wallet1
```

## Como gerar saldo em regtest

```bash
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR
bitcoin-cli -regtest -rpcwallet=wallet1 getwalletinfo
```

## Como rodar o backend

```bash
cd atividade-3/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

## Como abrir o frontend

[http://localhost:8003](http://localhost:8003)

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/wallets` | Lista wallets disponíveis, carregadas e selecionada |
| POST | `/wallet/select` | Seleciona wallet ativa (carrega se necessário) |
| GET | `/wallet/status` | Saldo e UTXOs da wallet selecionada |
| POST | `/tx/send` | Cria, assina e transmite tx via PSBT |
| GET | `/tx/{txid}` | Estado interpretado da transação |

### Exemplo: `GET /wallets`
```json
{
  "available_wallets": ["wallet1", "wallet2"],
  "loaded_wallets": ["wallet1"],
  "selected_wallet": "wallet1"
}
```

### Exemplo: `POST /wallet/select`
```json
// Request body:
{"wallet": "wallet2"}

// Response:
{
  "selected_wallet": "wallet2",
  "wallet_info": {"walletname": "wallet2", "balance": 0.001, "txcount": 4}
}
```

### Exemplo: `GET /wallet/status`
```json
{"wallet": "wallet1", "balance": 0.0012, "utxos": 3}
```

### Exemplo: `POST /tx/send`
```json
// Request:
{"to_address": "bcrt1q...", "amount": 0.001}

// Response:
{"txid": "abc...", "wallet": "wallet1", "status": "broadcast"}
```

### Exemplo: `GET /tx/{txid}`
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

## Interpretação de status

| Condição | Status | Mensagem |
|----------|--------|----------|
| `confirmations > 0` | `confirmed` | "Transação confirmada em bloco." |
| Na mempool | `mempool` | "Transação aceita na mempool, aguardando inclusão em bloco." |
| Mempool há > 2 min | `mempool` | + warning de demora |
| Enviada mas ainda propagando | `broadcast` | "Transação enviada ao node, aguardando aceitação na mempool." |
| Não encontrada | `unknown` | (warning: "Transação não localizada na wallet selecionada.") |

## Como enviar transação via curl

```bash
# 1. Selecionar wallet
curl -X POST http://127.0.0.1:8003/wallet/select \
  -H "Content-Type: application/json" -d '{"wallet":"wallet1"}'

# 2. Obter endereço destino
DEST=$(bitcoin-cli -regtest -rpcwallet=wallet2 getnewaddress)

# 3. Enviar
curl -X POST http://127.0.0.1:8003/tx/send \
  -H "Content-Type: application/json" \
  -d "{\"to_address\":\"$DEST\",\"amount\":0.001}"

# 4. Consultar status
curl http://127.0.0.1:8003/tx/<txid>

# 5. Confirmar (minerar 1 bloco)
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 1 $ADDR

# 6. Consultar novamente — status deve ser "confirmed"
curl http://127.0.0.1:8003/tx/<txid>
```

## Exposição externa

```bash
cloudflared tunnel --url http://localhost:8003
```

Ver `docs/deploy-cloudflare-tunnel.md` para instruções completas.
