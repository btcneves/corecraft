# Atividade 2 — Eventos em Tempo Real via ZMQ

## Objetivo
Construir uma camada de processamento orientada a eventos: **evento → interpretação → estado derivado**.

O sistema assina notificações ZMQ do Bitcoin Core (`rawblock` e `rawtx`), mantém o estado em memória (deques com limite de tamanho) e expõe os dados via API REST + frontend com polling.

## RPC vs ZMQ

| Característica | RPC (JSON-RPC HTTP) | ZMQ (PUB/SUB) |
|---|---|---|
| Modelo | Pull (request/response síncrono) | Push (eventos assíncronos) |
| Iniciativa | A aplicação faz o pedido | O nó publica quando algo acontece |
| Latência | Limitada pela frequência de polling | Praticamente em tempo real |
| Uso ideal | Consultar estado, enviar tx | Detectar novos blocos/txs |

## Configuração do bitcoin.conf (regtest)

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

## Variáveis de ambiente

Copie `.env.example` → `.env`:

```env
BTC_RPC_HOST=127.0.0.1
BTC_RPC_PORT=18443
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
ZMQ_RAWBLOCK_ENDPOINT=tcp://127.0.0.1:28332
ZMQ_RAWTX_ENDPOINT=tcp://127.0.0.1:28333
```

## Como rodar o bitcoind

```bash
bitcoind -regtest -daemon
bitcoin-cli -regtest getzmqnotifications   # deve listar rawblock e rawtx
```

## Como rodar o backend

```bash
cd atividade-2/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## Como abrir o frontend

[http://localhost:8002](http://localhost:8002) — polling automático a cada 2 s.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/events/summary` | Contadores e taxa de eventos do buffer |
| GET | `/api/events/latest` | Últimos blocos e txs recebidos via ZMQ |
| GET | `/api/events/state-comparison` | Compara bestblockhash (RPC) vs último bloco (ZMQ) |

### Exemplo: `/api/events/summary`
```json
{
  "blocks_observed": 3,
  "tx_observed": 120,
  "last_event_time": 1712345678,
  "tx_per_second": 4.2
}
```

### Exemplo: `/api/events/latest`
```json
{
  "blocks": [{"hash": "abc...", "ts": 1712345600}],
  "txs":    [{"txid": "tx1...", "ts": 1712345670}]
}
```

### Exemplo: `/api/events/state-comparison`
```json
{
  "best_block":      "abc123...",
  "last_seen_block": "abc123...",
  "divergence": false
}
```

`divergence: true` quando `best_block != last_seen_block` (ex.: nó minerou bloco mas ZMQ ainda não processou).

## Como gerar eventos (regtest)

```bash
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 1 $ADDR   # gera 1 bloco
bitcoin-cli -regtest -rpcwallet=wallet1 sendtoaddress $ADDR 0.001  # gera tx
```

## Decisões de design

- **Hash do bloco**: calculado localmente com `sha256(sha256(header[:80]))[::-1]` — sem RPC extra.
- **txid**: resolvido via `decoderawtransaction` (RPC). Evita implementar parser de serialização witness. Trade-off: 1 RPC por tx recebida. Mitigado pelo buffer limitado (`maxlen=200`).
- **Buffers**: `deque(maxlen=20)` para blocos, `deque(maxlen=200)` para txs — sem crescimento ilimitado.

## Limitações conhecidas

- A taxa `tx_per_second` é baseada no buffer (não em janela deslizante real). Em redes movimentadas, pode subestimar a taxa.
- Se ZMQ não estiver configurado no `bitcoin.conf`, o listener conecta mas não recebe eventos (sem erro visível). Verificar com `bitcoin-cli getzmqnotifications`.
- Ao reiniciar o backend, o estado em memória é zerado (por design).

## Exposição externa (Cloudflare Tunnel)

```bash
cloudflared tunnel --url http://localhost:8002
```

Ver `docs/deploy-cloudflare-tunnel.md` para instruções completas.
