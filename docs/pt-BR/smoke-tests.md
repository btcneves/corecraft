# Smoke Tests

[Versao em ingles](../en-US/smoke-tests.md)

Os smoke tests validam os endpoints principais das tres atividades contra um Bitcoin Core em `regtest`.

## Pre-requisitos

```bash
bitcoind -regtest -daemon
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR
```

Inicie os tres backends ou use Docker Compose.

## Execucao Automatizada

```bash
./scripts/smoke-test.sh
```

Resultado esperado:

```text
RESULT: 7/7 endpoints OK
```

## Testes Manuais

Atividade 1:

```bash
curl -s http://127.0.0.1:8001/api/mempool/summary | python3 -m json.tool
curl -s http://127.0.0.1:8001/api/blockchain/lag | python3 -m json.tool
```

Atividade 2:

```bash
curl -s http://127.0.0.1:8002/api/events/summary | python3 -m json.tool
curl -s http://127.0.0.1:8002/api/events/latest | python3 -m json.tool
curl -s http://127.0.0.1:8002/api/events/state-comparison | python3 -m json.tool
```

Atividade 3:

```bash
curl -s http://127.0.0.1:8003/wallets | python3 -m json.tool
curl -s http://127.0.0.1:8003/wallet/status | python3 -m json.tool
```

Para validar confirmacao, envie uma transacao pela Atividade 3 e mine um bloco.
