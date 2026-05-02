# RPC vs ZMQ — Conceitos e Uso no CoreCraft

## JSON-RPC (HTTP)

**Modelo:** Pull — a aplicação faz o pedido, o node responde.

```
Aplicação ──── POST /  ──→  Bitcoin Core
Aplicação ←── resposta ───  Bitcoin Core
```

**Características:**
- Síncrono: você pergunta, ele responde imediatamente.
- Stateless: cada chamada é independente.
- Ideal para: consultar estado, enviar transações, listar UTXOs.

**Exemplo:**
```python
rpc.call("getmempoolinfo")          # snapshot da mempool
rpc.call("sendrawtransaction", hex) # broadcast de tx
```

## ZMQ (PUB/SUB)

**Modelo:** Push — o node publica eventos, a aplicação assina.

```
Bitcoin Core ──── publica ──→  ZMQ endpoint
Aplicação    ←── recebe  ────  ZMQ endpoint
```

**Características:**
- Assíncrono: o node envia quando algo acontece.
- Baixa latência: praticamente em tempo real.
- Ideal para: detectar novos blocos, novas transações na mempool.

**Tópicos disponíveis:**
| Tópico | Conteúdo | Porta (default) |
|--------|----------|----------------|
| `rawblock` | Bloco completo serializado | 28332 |
| `rawtx` | Transação serializada | 28333 |
| `hashblock` | Hash do novo bloco | 28332 |
| `hashtx` | Hash de nova tx | 28333 |

**Exemplo:**
```python
sock.setsockopt(zmq.SUBSCRIBE, b"rawblock")
sock.setsockopt(zmq.SUBSCRIBE, b"rawtx")
topic, body, seq = sock.recv_multipart()
```

## Quando usar cada um — decisões no CoreCraft

| Atividade | Tecnologia | Justificativa |
|-----------|-----------|---------------|
| 1 | RPC only | Snapshot pontual não precisa de tempo real |
| 2 | RPC + ZMQ | ZMQ para detectar eventos; RPC para `bestblockhash` e `decoderawtransaction` |
| 3 | RPC only | Operações de wallet (PSBT, UTXOs) são stateful e síncronas por natureza |

## Configuração necessária no bitcoin.conf

```ini
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
```

Verificar:
```bash
bitcoin-cli -regtest getzmqnotifications
```
