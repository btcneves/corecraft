<div align="center">

# CoreCraft

**Integração com Bitcoin Core via JSON-RPC e ZMQ — três aplicações web evolutivas.**

`Python 3.12` · `FastAPI` · `Uvicorn` · `pyzmq` · `HTML/CSS/JS puro`

</div>

---

## Visão geral

CoreCraft é o repositório das três atividades obrigatórias do programa CoreCraft. Cada atividade é um **micro-serviço independente** (backend FastAPI + frontend estático) que se comunica com um nó Bitcoin Core local em `regtest` e expõe uma camada interpretada do estado da rede.

A evolução entre as atividades segue um arco claro:

| # | Foco | Origem dos dados |
|---|------|------------------|
| 1 | Snapshot inteligente da mempool e do nó | Apenas RPC |
| 2 | Eventos em tempo real e divergência estado×fluxo | RPC + ZMQ |
| 3 | Múltiplas wallets, PSBT e estado interpretado de transações | RPC global + RPC por wallet |

---

## Status da entrega

| Atividade | Status | Porta | Principais recursos |
|-----------|:------:|:-----:|---------------------|
| [Atividade 1](atividade-1/) | Concluída | `8001` | `getmempoolinfo` · `getrawmempool` · distribuição de fee rate (low/medium/high) · `getblockchaininfo` · lag de sincronização |
| [Atividade 2](atividade-2/) | Concluída | `8002` | Listener `pyzmq` (rawblock + rawtx) · buffer em `deque` · taxa de eventos · comparação `bestblockhash` × último ZMQ |
| [Atividade 3](atividade-3/) | Concluída | `8003` | Carregamento de wallets · PSBT (`walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction`) · interpretação `broadcast → mempool → confirmed` |

Os três backends seguem o mesmo padrão estrutural: `app/main.py` (rotas FastAPI) + `app/rpc_client.py` (cliente JSON-RPC dedicado) + módulos de domínio + frontend estático servido pelo próprio FastAPI.

---

## Estrutura do repositório

```
corecraft/
├── atividade-1/                  Snapshot da mempool via RPC
│   ├── backend/                  FastAPI (porta 8001)
│   │   ├── app/
│   │   │   ├── main.py           rotas /api/mempool/summary, /api/blockchain/lag
│   │   │   ├── mempool.py        cálculo de fee rate e distribuição
│   │   │   └── rpc_client.py     JSON-RPC com tratamento de erro
│   │   └── requirements.txt
│   ├── frontend/                 dashboard polling 5s (HTML/CSS/JS)
│   ├── .env.example
│   └── README.md
│
├── atividade-2/                  Eventos em tempo real via ZMQ
│   ├── backend/                  FastAPI (porta 8002)
│   │   ├── app/
│   │   │   ├── main.py           rotas /api/events/{summary,latest,state-comparison}
│   │   │   ├── zmq_listener.py   thread daemon assina rawblock + rawtx
│   │   │   ├── event_store.py    deque(maxlen=20) blocos · deque(maxlen=200) txs
│   │   │   ├── event_service.py  agregadores
│   │   │   └── rpc_client.py
│   │   └── requirements.txt
│   ├── frontend/                 dashboard polling 2s + banner de divergência
│   ├── .env.example
│   └── README.md
│
├── atividade-3/                  Multi-wallet + PSBT + estado interpretado
│   ├── backend/                  FastAPI (porta 8003)
│   │   ├── app/
│   │   │   ├── main.py           rotas /wallets, /wallet/{select,status}, /tx/send, /tx/{txid}
│   │   │   ├── wallet_service.py listwalletdir/listwallets/loadwallet/getwalletinfo
│   │   │   ├── tx_service.py     fluxo PSBT completo
│   │   │   ├── tx_interpreter.py broadcast → mempool → confirmed → unknown
│   │   │   └── rpc_client.py     RPC global + RPC por wallet (/wallet/<nome>)
│   │   └── requirements.txt
│   ├── frontend/                 seletor de wallet, formulário de envio, tabela de tx
│   ├── .env.example
│   └── README.md
│
├── docs/
│   ├── setup-bitcoin-core.md     bitcoin.conf, regtest, wallets, ZMQ
│   ├── rpc-zmq.md                conceitos RPC vs ZMQ
│   ├── deploy-vps.md             Ubuntu 22.04 + tmux + ufw
│   ├── deploy-cloudflare-tunnel.md  exposição pública
│   └── entrega.md                smoke tests + texto de envio
│
├── docker-compose.yml            (opcional) sobe os 3 backends
├── CLAUDE.md                     decisões de design
├── LICENSE                       MIT
├── .gitignore
└── README.md
```

---

## Pré-requisitos

| Dependência | Versão mínima | Observação |
|-------------|---------------|------------|
| Python | 3.11+ (testado em 3.12) | `python3 -m venv` |
| Bitcoin Core | 26.0+ | Modo `regtest`, com RPC habilitado |
| ZMQ | — | Apenas Atividade 2 (`zmqpubrawblock` e `zmqpubrawtx` no `bitcoin.conf`) |
| `pip` | atualizado | Instala `fastapi`, `uvicorn`, `requests`, `python-dotenv`, `pyzmq` |

> Setup completo do Bitcoin Core: [`docs/setup-bitcoin-core.md`](docs/setup-bitcoin-core.md)

---

## Quickstart

### 1. Configurar o Bitcoin Core (uma única vez)

```bash
# bitcoin.conf — ver docs/setup-bitcoin-core.md para o conteúdo completo
bitcoind -regtest -daemon
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR    # gera saldo maturado
bitcoin-cli -regtest getzmqnotifications            # deve listar rawblock e rawtx
```

### 2. Rodar uma atividade

Cada atividade é independente. O fluxo é o mesmo nas três (apenas troque o número):

```bash
cd atividade-1/backend
cp ../.env.example .env                              # ajuste credenciais RPC
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Frontend disponível em `http://localhost:8001` (servido pelo próprio FastAPI).

### 3. Rodar as três simultaneamente (Docker Compose)

```bash
docker compose up --build
# Atividade 1: http://localhost:8001
# Atividade 2: http://localhost:8002
# Atividade 3: http://localhost:8003
```

> Requer `.env` preenchido em cada `atividade-*/`. O Bitcoin Core continua rodando no host.

---

## Endpoints (resumo)

| Método | Rota | Atividade | Descrição |
|:------:|------|:---------:|-----------|
| GET | `/api/mempool/summary` | 1 | Snapshot da mempool com distribuição de fee rate |
| GET | `/api/blockchain/lag` | 1 | Lag de sincronização (`headers - blocks`) |
| GET | `/api/events/summary` | 2 | Contadores e taxa de eventos do buffer ZMQ |
| GET | `/api/events/latest` | 2 | Últimos blocos e txs recebidos via ZMQ |
| GET | `/api/events/state-comparison` | 2 | Compara `getbestblockhash` (RPC) × último bloco (ZMQ) |
| GET | `/wallets` | 3 | Lista wallets disponíveis, carregadas e selecionada |
| POST | `/wallet/select` | 3 | Seleciona e carrega wallet ativa |
| GET | `/wallet/status` | 3 | Saldo e UTXOs da wallet ativa |
| POST | `/tx/send` | 3 | Cria, assina e transmite tx via PSBT |
| GET | `/tx/{txid}` | 3 | Estado interpretado da transação |

Smoke tests completos com `curl`: [`docs/entrega.md`](docs/entrega.md).

---

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [`docs/setup-bitcoin-core.md`](docs/setup-bitcoin-core.md) | `bitcoin.conf`, regtest, wallets, ZMQ, geração de saldo |
| [`docs/rpc-zmq.md`](docs/rpc-zmq.md) | Conceitos: pull (RPC) vs push (ZMQ) e justificativa por atividade |
| [`docs/deploy-vps.md`](docs/deploy-vps.md) | Deploy em VPS Ubuntu 22.04 com `tmux` e `ufw` |
| [`docs/deploy-cloudflare-tunnel.md`](docs/deploy-cloudflare-tunnel.md) | Exposição pública via Cloudflare Tunnel ou ngrok |
| [`docs/entrega.md`](docs/entrega.md) | Smoke tests `curl` por atividade + texto de envio |

Cada atividade tem seu próprio README detalhado:

- [`atividade-1/README.md`](atividade-1/README.md) — objetivo, restrições, endpoints, exemplos
- [`atividade-2/README.md`](atividade-2/README.md) — fluxo `evento → estado`, ZMQ, divergência
- [`atividade-3/README.md`](atividade-3/README.md) — multi-wallet, PSBT, interpretação de tx

---

## Decisões de design (resumo)

- **Sem libs Bitcoin de alto nível.** Cada atividade tem seu `rpc_client.py` próprio (`requests` + `HTTPBasicAuth`). Hash de bloco é calculado localmente em Python.
- **Sem banco de dados.** Estado em memória (`deque` na Atividade 2, `dict` na Atividade 3). Estado zera ao reiniciar — comportamento esperado.
- **PSBT na Atividade 3.** Fluxo `walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction` para o Core cuidar de seleção de UTXO e fee.
- **Erro 503 estruturado.** Quando o nó está offline, todas as rotas que dependem dele retornam `{"detail": {"error": "node_unavailable", "detail": "..."}}` com HTTP 503.
- **Frontend isolado.** Cada atividade tem HTML/CSS/JS próprios; nenhum framework. URLs relativas — funciona com tunnel sem alterar JS.
- **Decisões completas em [`CLAUDE.md`](CLAUDE.md).**

---

## Limitações conhecidas

- O nó Bitcoin Core (`bitcoind -regtest`) precisa estar rodando para qualquer rota retornar dados — caso contrário, todas devolvem **HTTP 503** estruturado.
- A Atividade 2 só recebe eventos se `zmqpubrawblock` e `zmqpubrawtx` estiverem ativos no `bitcoin.conf`. Sem ZMQ habilitado, o listener conecta mas não recebe nada (verificar com `bitcoin-cli -regtest getzmqnotifications`).
- A Atividade 3 só envia transações se a wallet selecionada tiver UTXOs maduros. Em regtest novo, é necessário minerar pelo menos 101 blocos para a wallet receber saldo gastável.
- O estado das três aplicações é **em memória**. Reiniciar o uvicorn zera o buffer ZMQ e a lista de transações enviadas (txid permanece consultável via RPC do nó).
- A taxa `tx_per_second` da Atividade 2 é calculada sobre a janela do buffer interno (`deque(maxlen=200)`); em redes muito ativas pode subestimar a taxa real.
- O txid da Atividade 2 é resolvido via RPC `decoderawtransaction` — se o nó estiver offline, txs ZMQ chegam mas o txid não é registrado (loga warning).

---

## Acesso externo

Para tornar qualquer das três atividades acessível pela internet:

```bash
# Cloudflare Tunnel (sem expor portas no roteador)
cloudflared tunnel --url http://localhost:8001
cloudflared tunnel --url http://localhost:8002
cloudflared tunnel --url http://localhost:8003

# Alternativa: ngrok
ngrok http 8001
```

Detalhes (instalação, deploy permanente em VPS, firewall): [`docs/deploy-cloudflare-tunnel.md`](docs/deploy-cloudflare-tunnel.md) e [`docs/deploy-vps.md`](docs/deploy-vps.md).

---

## Licença

[MIT](LICENSE) © 2026 Pedro Neves
