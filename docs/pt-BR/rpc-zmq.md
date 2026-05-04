# RPC vs ZMQ

[Versao em ingles](../en-US/rpc-zmq.md)

## JSON-RPC

JSON-RPC e o modelo de requisicao e resposta do Bitcoin Core. A aplicacao pergunta, o no responde.

Usos no CoreCraft:

- consultar mempool;
- consultar altura da blockchain;
- listar wallets e UTXOs;
- criar, assinar e transmitir transacoes.

Exemplo:

```python
rpc.call("getmempoolinfo")
rpc.call("sendrawtransaction", raw_tx)
```

## ZMQ

ZMQ e o modelo de eventos. O Bitcoin Core publica mensagens, e a aplicacao se inscreve nos topicos desejados.

Topicos usados:

| Topico | Conteudo |
|--------|----------|
| `rawblock` | bloco serializado |
| `rawtx` | transacao serializada |

Exemplo:

```python
sock.setsockopt(zmq.SUBSCRIBE, b"rawblock")
sock.setsockopt(zmq.SUBSCRIBE, b"rawtx")
```

## Decisao por Atividade

| Atividade | Tecnologia | Motivo |
|-----------|------------|--------|
| 1 | RPC | snapshot pontual |
| 2 | RPC + ZMQ | eventos em tempo real com verificacao de estado |
| 3 | RPC | operacoes de wallet sao sincronas e stateful |

