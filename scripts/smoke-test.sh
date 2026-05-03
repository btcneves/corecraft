#!/usr/bin/env bash
set -euo pipefail

echo "=== Atividade 1 (porta 8001) ==="
curl -s http://127.0.0.1:8001/api/mempool/summary | python3 -m json.tool
curl -s http://127.0.0.1:8001/api/blockchain/lag | python3 -m json.tool

echo "=== Atividade 2 (porta 8002) ==="
curl -s http://127.0.0.1:8002/api/events/summary | python3 -m json.tool
curl -s http://127.0.0.1:8002/api/events/latest | python3 -m json.tool
curl -s http://127.0.0.1:8002/api/events/state-comparison | python3 -m json.tool

echo "=== Atividade 3 (porta 8003) ==="
curl -s http://127.0.0.1:8003/wallets | python3 -m json.tool
curl -s http://127.0.0.1:8003/wallet/status | python3 -m json.tool
