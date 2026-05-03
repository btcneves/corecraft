# Atividade 2 — Eventos em Tempo Real via ZMQ

> Backend FastAPI + frontend React/Vite que assina notificações ZMQ do Bitcoin Core, mantém o estado em memória e expõe a divergência entre o **fluxo** (eventos ZMQ) e o **estado** (RPC).

---

## Objetivo

Sair do modelo "consultar quando precisar" (RPC puro da Atividade 1) e introduzir um pipeline orientado a eventos:

```
evento ZMQ ──→ interpretação ──→ estado derivado em memória ──→ API REST + WebSocket
```

A aplicação assina `rawblock` e `rawtx`, mantém buffers limitados e expõe um endpoint de **comparação** que detecta inconsistências entre o que foi observado via ZMQ e o `bestblockhash` retornado por RPC.

## RPC vs ZMQ

| Característica | RPC (JSON-RPC HTTP) | ZMQ (PUB/SUB) |
|----------------|---------------------|---------------|
| Modelo | Pull (request/response síncrono) | Push (eventos assíncronos) |
| Iniciativa | A aplicação faz o pedido | O nó publica quando algo acontece |
| Latência | Limitada pela frequência de polling | Praticamente em tempo real |
| Uso ideal | Consultar estado, enviar tx | Detectar novos blocos/txs |

Mais detalhes: [`docs/rpc-zmq.md`](../docs/rpc-zmq.md).

## Arquitetura

```
atividade-2/
├── backend/
│   ├── app/
│   │   ├── main.py            rotas FastAPI + lifespan que inicia o listener
│   │   ├── zmq_listener.py    thread daemon assina rawblock + rawtx
│   │   ├── event_store.py     deque(maxlen=20) blocos · deque(maxlen=200) txs
│   │   ├── event_service.py   agregadores (summary, latest, state-comparison)
│   │   └── rpc_client.py      JSON-RPC para getbestblockhash + decoderawtransaction
│   └── requirements.txt
├── frontend/                  dashboard polling 2s + banner de divergência
├── .env.example
└── README.md
```

### Fluxo do listener

1. `lifespan` do FastAPI dispara `zmq_listener.start(store, rpc)`.
2. Thread daemon abre socket SUB conectado a `tcp://127.0.0.1:28332` (rawblock) e `tcp://127.0.0.1:28333` (rawtx).
3. Para cada `rawblock`, calcula o hash localmente (`sha256d(header[:80])`) e enfileira no deque.
4. Para cada `rawtx`, resolve o `txid` via RPC `decoderawtransaction` (evita implementar parser de witness) e enfileira.
5. Buffers são thread-safe via `Lock`.

## Configuração obrigatória do `bitcoin.conf`

```ini
regtest=1
server=1
txindex=1
fallbackfee=0.0001

[regtest]
rpcuser=user
rpcpassword=password
rpcbind=127.0.0.1
rpcallowip=127.0.0.1
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
```

> Sem `zmqpubrawblock` e `zmqpubrawtx`, o listener conecta mas não recebe eventos. Verifique com:
>
> ```bash
> bitcoin-cli -regtest getzmqnotifications
> ```

## Endpoints

| Método | Rota | Descrição | Origem |
|:------:|------|-----------|--------|
| GET | `/api/events/summary` | Contadores e taxa de eventos do buffer | Buffer ZMQ |
| GET | `/api/events/latest` | Últimos blocos e txs recebidos | Buffer ZMQ |
| GET | `/api/events/state-comparison` | Compara `bestblockhash` (RPC) × último bloco visto via ZMQ | RPC + Buffer |

### Exemplo — `GET /api/events/summary`

```json
{
  "blocks_observed": 3,
  "tx_observed": 120,
  "last_event_time": 1712345678,
  "tx_per_second": 4.2
}
```

`tx_per_second` é calculado sobre a janela do buffer — em redes muito ativas pode subestimar a taxa real.

### Exemplo — `GET /api/events/latest`

```json
{
  "blocks": [
    { "hash": "abc...", "ts": 1712345600 },
    { "hash": "def...", "ts": 1712345678 }
  ],
  "txs": [
    { "txid": "tx1...", "ts": 1712345670 },
    { "txid": "tx2...", "ts": 1712345675 }
  ]
}
```

### Exemplo — `GET /api/events/state-comparison`

```json
{
  "best_block": "abc123...",
  "last_seen_block": "abc123...",
  "divergence": false
}
```

`divergence: true` quando `best_block != last_seen_block` (ex.: o nó já minerou um bloco mas o ZMQ ainda não o entregou). Quando `last_seen_block` é `null` (ZMQ ainda não recebeu nenhum bloco), o frontend mostra estado inicial em vez de banner de divergência.

## Variáveis de ambiente

```env
BTC_RPC_HOST=127.0.0.1
BTC_RPC_PORT=18443
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
ZMQ_RAWBLOCK_ENDPOINT=tcp://127.0.0.1:28332
ZMQ_RAWTX_ENDPOINT=tcp://127.0.0.1:28333
```

## Como rodar

```bash
cd atividade-2/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

Frontend em [http://localhost:8002](http://localhost:8002) — polling 2 s.

## Frontend

- **Event Activity** — txs recebidas, blocos recebidos, taxa de eventos, timestamp do último evento.
- **State Comparison** — `best_block` (RPC) e `last_seen_block` (ZMQ) lado a lado.
- **Últimos Eventos** — duas listas (blocos e txs) com hash truncado e timestamp.
- **Banner de divergência** — barra vermelha no topo quando ambos os hashes existem e diferem; oculto enquanto o ZMQ ainda não recebeu blocos.

## Como gerar eventos (regtest)

```bash
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 1 $ADDR                  # 1 bloco → rawblock
bitcoin-cli -regtest -rpcwallet=wallet1 sendtoaddress $ADDR 0.001  # 1 tx → rawtx
```

## Smoke tests

```bash
curl -s http://127.0.0.1:8002/api/events/summary | python3 -m json.tool
curl -s http://127.0.0.1:8002/api/events/latest | python3 -m json.tool
curl -s http://127.0.0.1:8002/api/events/state-comparison | python3 -m json.tool
```

## Decisões de design

- **Hash do bloco** calculado localmente com `sha256(sha256(header[:80]))[::-1]` — sem RPC extra.
- **txid resolvido via RPC** (`decoderawtransaction`) — evita parser de serialização witness. Trade-off: 1 RPC por tx recebida; mitigado pelo buffer limitado (`maxlen=200`).
- **Buffers limitados** em `deque(maxlen=20)` (blocos) e `deque(maxlen=200)` (txs) — sem crescimento ilimitado.
- **Listener desacoplado** — roda em thread daemon; falhas de ZMQ logam warning sem derrubar a API.

## Limitações conhecidas

- `tx_per_second` é baseado na janela do buffer (não em janela deslizante real). Em redes movimentadas, pode subestimar a taxa.
- Reiniciar o backend zera o estado em memória (por design).
- Se o nó estiver offline, o listener continua tentando, mas `decoderawtransaction` falha e txs ZMQ não são registradas.

## Acesso externo

```bash
cloudflared tunnel --url http://localhost:8002
```

Detalhes em [`docs/deploy-cloudflare-tunnel.md`](../docs/deploy-cloudflare-tunnel.md) e [`docs/deploy-vps.md`](../docs/deploy-vps.md).

## Checklist desta atividade

- [x] Listener ZMQ assina `rawblock` e `rawtx`
- [x] Buffer limitado (`deque`) com timestamp por evento
- [x] Sistema não quebra se ZMQ estiver indisponível
- [x] `GET /api/events/summary` com `blocks_observed`, `tx_observed`, `last_event_time`, `tx_per_second`
- [x] `GET /api/events/latest` com `blocks[].{hash,ts}` e `txs[].{txid,ts}`
- [x] `GET /api/events/state-comparison` compara `getbestblockhash` × último ZMQ
- [x] Frontend tem cards Event Activity, State Comparison e Últimos Eventos
- [x] Indicador visual de divergência (banner) com tratamento do estado inicial
- [x] Documentação de acesso externo (Cloudflare Tunnel + VPS + ngrok)
