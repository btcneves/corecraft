# Smoke Tests

End-to-end validation of all three activities against a live `bitcoind -regtest` node.

## Prerequisites — Bitcoin Core

```bash
# Start daemon
bitcoind -regtest -daemon
sleep 2

# Create wallets
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2

# Fund wallet1 (101 blocks to mature coinbase)
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR

# Verify
bitcoin-cli -regtest -rpcwallet=wallet1 getwalletinfo
```

## Prerequisites — running backends

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

## Activity 1

```bash
# Mempool snapshot
curl -s http://127.0.0.1:8001/api/mempool/summary | python3 -m json.tool

# Blockchain sync lag
curl -s http://127.0.0.1:8001/api/blockchain/lag | python3 -m json.tool

# Frontend served
curl -s http://127.0.0.1:8001/ | head -5
```

**Expected (`/api/mempool/summary`):**
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

**Expected (`/api/blockchain/lag`):**
```json
{"blocks": 101, "headers": 101, "lag": 0}
```

---

## Activity 2

```bash
# Event summary (starts empty)
curl -s http://127.0.0.1:8002/api/events/summary | python3 -m json.tool

# Latest events (starts empty)
curl -s http://127.0.0.1:8002/api/events/latest | python3 -m json.tool

# State comparison
curl -s http://127.0.0.1:8002/api/events/state-comparison | python3 -m json.tool

# Generate ZMQ events (in another terminal)
bitcoin-cli -regtest generatetoaddress 1 $ADDR
bitcoin-cli -regtest -rpcwallet=wallet1 sendtoaddress $ADDR 0.001

# Wait ~2s, then re-query
curl -s http://127.0.0.1:8002/api/events/latest | python3 -m json.tool
```

**Expected (`/api/events/state-comparison`) after ZMQ events:**
```json
{
  "best_block": "abc123...",
  "last_seen_block": "abc123...",
  "divergence": false,
  "status": "compared"
}
```

> Before the ZMQ listener receives its first block, the response will have `"divergence": null` and `"status": "waiting_for_zmq_block"`. The frontend does not show the divergence banner in this state.

---

## Activity 3

```bash
# List wallets
curl -s http://127.0.0.1:8003/wallets | python3 -m json.tool

# Select wallet1
curl -s -X POST http://127.0.0.1:8003/wallet/select \
  -H "Content-Type: application/json" \
  -d '{"wallet":"wallet1"}' | python3 -m json.tool

# Wallet status
curl -s http://127.0.0.1:8003/wallet/status | python3 -m json.tool

# Get a destination address from wallet2
DEST=$(bitcoin-cli -regtest -rpcwallet=wallet2 getnewaddress)

# Send a transaction (PSBT flow)
TXID=$(curl -s -X POST http://127.0.0.1:8003/tx/send \
  -H "Content-Type: application/json" \
  -d "{\"to_address\":\"$DEST\",\"amount\":0.001}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['txid'])")
echo "TXID: $TXID"

# Query status (should be broadcast or mempool)
curl -s http://127.0.0.1:8003/tx/$TXID | python3 -m json.tool

# Mine 1 block to confirm
bitcoin-cli -regtest generatetoaddress 1 $ADDR

# Query again (should be confirmed)
curl -s http://127.0.0.1:8003/tx/$TXID | python3 -m json.tool
```

---

## Node offline (expected HTTP 503)

```bash
bitcoin-cli -regtest stop
sleep 2

curl -s http://127.0.0.1:8001/api/mempool/summary
curl -s http://127.0.0.1:8002/api/events/state-comparison
curl -s http://127.0.0.1:8003/wallets
```

**Expected response (all three):**
```json
{"detail": {"error": "node_unavailable", "detail": "Cannot connect to Bitcoin node: ..."}}
```

---

## Live validation evidence

Full session output with real Bitcoin Core v31.0 responses: [`docs/validacao-ao-vivo.md`](validacao-ao-vivo.md)
