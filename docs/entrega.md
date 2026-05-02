# Smoke Tests — Entrega CoreCraft

## Pré-requisito: Bitcoin Core em regtest

```bash
# 1. Iniciar daemon
bitcoind -regtest -daemon
sleep 2

# 2. Criar wallets
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2

# 3. Gerar saldo na wallet1
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR

# 4. Verificar
bitcoin-cli -regtest -rpcwallet=wallet1 getwalletinfo
```

## Pré-requisito: backends rodando

```bash
# Terminal 1
cd atividade-1/backend && source .venv/bin/activate
uvicorn app.main:app --port 8001

# Terminal 2
cd atividade-2/backend && source .venv/bin/activate
uvicorn app.main:app --port 8002

# Terminal 3
cd atividade-3/backend && source .venv/bin/activate
uvicorn app.main:app --port 8003
```

---

## Atividade 1 — Smoke Tests

```bash
# Snapshot da mempool
curl -s http://127.0.0.1:8001/api/mempool/summary | python3 -m json.tool

# Lag de sincronização
curl -s http://127.0.0.1:8001/api/blockchain/lag | python3 -m json.tool

# Frontend
curl -s http://127.0.0.1:8001/ | head -5
```

**Resultado esperado (`/api/mempool/summary`):**
```json
{
  "tx_count": 0,
  "total_vsize": 0,
  "avg_fee_rate": 0.0,
  "min_fee_rate": 0.0,
  "max_fee_rate": 0.0,
  "fee_distribution": {"low": 0, "medium": 0, "high": 0}
}
```

**Resultado esperado (`/api/blockchain/lag`):**
```json
{"blocks": 101, "headers": 101, "lag": 0}
```

---

## Atividade 2 — Smoke Tests

```bash
# Resumo de eventos (começa vazio)
curl -s http://127.0.0.1:8002/api/events/summary | python3 -m json.tool

# Últimos eventos (começa vazio)
curl -s http://127.0.0.1:8002/api/events/latest | python3 -m json.tool

# Comparação de estado
curl -s http://127.0.0.1:8002/api/events/state-comparison | python3 -m json.tool

# Gerar eventos ZMQ (em outro terminal):
bitcoin-cli -regtest generatetoaddress 1 $ADDR
bitcoin-cli -regtest -rpcwallet=wallet1 sendtoaddress $ADDR 0.001

# Aguardar ~2s e consultar novamente
curl -s http://127.0.0.1:8002/api/events/latest | python3 -m json.tool
```

**Resultado esperado (`/api/events/state-comparison`):**
```json
{
  "best_block": "abc123...",
  "last_seen_block": "abc123...",
  "divergence": false
}
```

---

## Atividade 3 — Smoke Tests

```bash
# Listar wallets
curl -s http://127.0.0.1:8003/wallets | python3 -m json.tool

# Selecionar wallet1
curl -s -X POST http://127.0.0.1:8003/wallet/select \
  -H "Content-Type: application/json" \
  -d '{"wallet":"wallet1"}' | python3 -m json.tool

# Status da wallet selecionada
curl -s http://127.0.0.1:8003/wallet/status | python3 -m json.tool

# Obter endereço destino
DEST=$(bitcoin-cli -regtest -rpcwallet=wallet2 getnewaddress)

# Enviar transação
TXID=$(curl -s -X POST http://127.0.0.1:8003/tx/send \
  -H "Content-Type: application/json" \
  -d "{\"to_address\":\"$DEST\",\"amount\":0.001}" | python3 -c "import sys,json; print(json.load(sys.stdin)['txid'])")
echo "TXID: $TXID"

# Consultar status (deve ser broadcast ou mempool)
curl -s http://127.0.0.1:8003/tx/$TXID | python3 -m json.tool

# Confirmar (minerar 1 bloco)
bitcoin-cli -regtest generatetoaddress 1 $ADDR

# Consultar novamente (deve ser confirmed)
curl -s http://127.0.0.1:8003/tx/$TXID | python3 -m json.tool
```

---

## Teste com node offline (503 esperado)

```bash
# Parar bitcoind
bitcoin-cli -regtest stop
sleep 2

# Todas as rotas devem retornar 503 com JSON estruturado
curl -s http://127.0.0.1:8001/api/mempool/summary
curl -s http://127.0.0.1:8002/api/events/state-comparison
curl -s http://127.0.0.1:8003/wallets
```

**Resultado esperado:**
```json
{"detail": {"error": "node_unavailable", "detail": "Cannot connect to Bitcoin node: ..."}}
```

---

## Texto de entrega (canal)

```
Nome: Pedro Neves
GitHub: https://github.com/btcneves/corecraft

Atividade 1:
https://github.com/btcneves/corecraft/tree/main/atividade-1

Atividade 2:
https://github.com/btcneves/corecraft/tree/main/atividade-2

Atividade 3:
https://github.com/btcneves/corecraft/tree/main/atividade-3

Observações:
Repositório único organizado conforme exigido, com backend, frontend, documentação,
integração Bitcoin Core via RPC/ZMQ quando aplicável e instruções de execução local/externa.
```
