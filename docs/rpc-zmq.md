# RPC vs ZMQ — Concepts and Usage in CoreCraft

## JSON-RPC (HTTP)

**Model:** Pull — the application makes the request, the node responds.

```
Application ──── POST /  ──→  Bitcoin Core
Application ←── response ───  Bitcoin Core
```

**Features:**
- Synchronous: the application requests data, and the node responds immediately.
- Stateless: each call is independent.
- Ideal for: querying status, sending transactions, listing UTXOs.

**Example:**
```python
rpc.call("getmempoolinfo")          # mempool snapshot
rpc.call("sendrawtransaction", hex) # tx broadcast
```

## ZMQ (PUB/SUB)

**Model:** Push — the node publishes events, the application subscribes.

```
Bitcoin Core ──── publishes ──→  ZMQ endpoint
Application     ←── receives  ───  ZMQ endpoint
```

**Features:**
- Asynchronous: the node sends when something happens.
- Low latency: practically in real time.
- Ideal for: detecting new blocks, new transactions in the mempool.

**Available topics:**
| Topic | Content | Port (default) |
|--------|----------|----------------|
| `rawblock` | Complete serialized block | 28332 |
| `rawtx` | Serialized transaction | 28333 |
| `hashblock` | Hash of new block | 28332 |
| `hashtx` | New tx hash | 28333 |

**Example:**
```python
sock.setsockopt(zmq.SUBSCRIBE, b"rawblock")
sock.setsockopt(zmq.SUBSCRIBE, b"rawtx")
topic, body, seq = sock.recv_multipart()
```

## When to use each — decisions in CoreCraft

| Activity | Technology | Justification |
|-----------|-----------|---------------|
| 1 | RPC only | Point-in-time snapshot doesn’t need real time |
| 2 | RPC + ZMQ | ZMQ to detect events; RPC for `bestblockhash` and `decoderawtransaction` |
| 3 | RPC only | Wallet operations (PSBT, UTXOs) are stateful and synchronous in nature |

## Configuration required in bitcoin.conf

```ini
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
```

To check:
```bash
bitcoin-cli -regtest getzmqnotifications
```
