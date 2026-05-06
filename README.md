<div align="center">

# CoreCraft

**Integração com Bitcoin Core via JSON-RPC e ZMQ — três aplicações web evolutivas.**

`Python 3.12` · `FastAPI` · `Uvicorn` · `pyzmq` · `React` · `Vite` · `TypeScript` · `Docker Compose`

[![Português do Brasil](https://img.shields.io/badge/idioma-PT--BR-009739?style=flat-square)](README.md)
[![English US](https://img.shields.io/badge/language-EN--US-3C3B6E?style=flat-square)](README.en-US.md)

[![GitHub Release](https://img.shields.io/github/v/release/btcneves/CoreCraft?sort=semver&style=flat-square&label=release&cacheSeconds=3600)](https://github.com/btcneves/CoreCraft/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/btcneves/CoreCraft/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/btcneves/CoreCraft/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/docker-ghcr.io%2Fbtcneves%2Fcorecraft--suite-blue?style=flat-square&logo=docker)](https://github.com/btcneves/CoreCraft/pkgs/container/corecraft-suite-atividade-1)

</div>

---

> **Início rápido — com Docker:**
>
> ```bash
> git clone https://github.com/btcneves/CoreCraft.git && cd CoreCraft
> ./scripts/quickstart.sh        # Linux / macOS
> docker compose --profile all up
> ```
>
> No Windows PowerShell, use `.\scripts\setup-windows.ps1` no lugar de `./scripts/quickstart.sh`.
>
> Acesse as atividades em `http://localhost:8001`, `8002` e `8003`.  
> Guia completo (incluindo sem Docker): [**docs/pt-BR/getting-started.md**](docs/pt-BR/getting-started.md)

### O que você verá após `docker compose --profile all up`

```
✔ Container corecraft-bitcoind       Healthy
✔ Container corecraft-bitcoin-init   Exited (0)
✔ Container corecraft-suite-atividade-1    Healthy
✔ Container corecraft-suite-atividade-2    Healthy
✔ Container corecraft-suite-atividade-3    Healthy
✔ Container corecraft-caddy          Started
```

| URL | Descrição |
|-----|-----------|
| `http://localhost:8001` | Atividade 1 — Mempool Snapshot (RPC) |
| `http://localhost:8002` | Atividade 2 — Eventos ZMQ em tempo real |
| `http://localhost:8003` | Atividade 3 — Multi-wallet + PSBT |
| `http://localhost/atividade-1/` | Atividade 1 via Caddy (proxy reverso) |

Verificar que tudo funciona:

```bash
./scripts/smoke-test.sh
# ══════════════════════════════════════
#   CoreCraft — Smoke Tests
# ══════════════════════════════════════
# Activity 1 — Mempool Snapshot (port 8001)
#   ✔  GET /api/mempool/summary  (200)
#   ✔  GET /api/blockchain/lag   (200)
# Activity 2 — ZMQ Events (port 8002)
#   ✔  GET /api/events/summary   (200)
# ...
#   RESULT: 7/7 endpoints OK
```

---

## Visão geral

CoreCraft é o repositório das três atividades obrigatórias do programa CoreCraft. Cada atividade é um **micro-serviço independente** (backend FastAPI + frontend React) que se comunica com um nó Bitcoin Core em `regtest` e expõe uma camada interpretada do estado da rede.

A evolução entre as atividades segue um arco claro:

| # | Foco | Origem dos dados |
|---|------|------------------|
| 1 | Snapshot inteligente da mempool e do nó | Apenas RPC |
| 2 | Eventos em tempo real e divergência estado×fluxo | RPC + ZMQ |
| 3 | Múltiplas wallets, PSBT e estado interpretado de transações | RPC global + RPC por wallet |

### Arquitetura em alto nível

```mermaid
flowchart LR
    user[Browser] --> caddy[Caddy reverse proxy]
    caddy --> a1["Atividade 1<br/>FastAPI + React<br/>Mempool Snapshot"]
    caddy --> a2["Atividade 2<br/>FastAPI + React<br/>ZMQ Events"]
    caddy --> a3["Atividade 3<br/>FastAPI + React<br/>Wallets + PSBT"]

    a1 -->|JSON-RPC| bitcoind["Bitcoin Core<br/>regtest"]
    a2 -->|JSON-RPC| bitcoind
    bitcoind -->|ZMQ rawblock/rawtx| a2
    a3 -->|Global RPC| bitcoind
    a3 -->|Wallet RPC| wallets[("wallet1 / wallet2")]
    bitcoind --- wallets
```

Diagramas técnicos completos: [`docs/pt-BR/architecture.md`](docs/pt-BR/architecture.md).

---

## Status da entrega

| Atividade | Status | Principais recursos |
|-----------|--------|---------------------|
| [Atividade 1](atividade-1/) | Concluída e validada | RPC, mempool summary, blockchain lag |
| [Atividade 2](atividade-2/) | Concluída e validada, requer ZMQ ativo | rawtx/rawblock, eventos recentes, comparação RPC/ZMQ |
| [Atividade 3](atividade-3/) | Concluída e validada, requer wallets em regtest | múltiplas wallets, PSBT, tx interpretada, wallet status |

Portas locais (uvicorn): Atividade 1 → `8001` · Atividade 2 → `8002` · Atividade 3 → `8003`.

Os três backends seguem o mesmo padrão estrutural: `app/main.py` (rotas FastAPI) + `app/rpc_client.py` (cliente JSON-RPC dedicado) + módulos de domínio + build React servido pelo próprio FastAPI.

Todos os backends expõem `/health`, `/metrics` e logs JSON com `correlation_id`. O CI executa `ruff`, `mypy --strict`, `pytest --cov`, `npm audit`, `pip-audit`, Trivy e validação do Compose.

---

## Conceitos principais

| Conceito | Onde aparece | Resumo |
|----------|--------------|--------|
| `regtest` | Todas as atividades | Rede local e controlada do Bitcoin Core. Permite minerar blocos sob demanda, criar wallets de teste e validar fluxos sem tocar em testnet/mainnet. |
| JSON-RPC | Atividades 1, 2 e 3 | Interface síncrona usada para consultar estado do nó, mempool, blockchain, wallets, UTXOs e transmitir transações. |
| ZMQ | Atividade 2 | Canal assíncrono PUB/SUB do Bitcoin Core. Publica eventos `rawblock` e `rawtx` quase em tempo real para detectar novos blocos e transações. |
| Mempool | Atividades 1 e 2 | Conjunto de transações válidas ainda não confirmadas. A Atividade 1 interpreta snapshots via RPC; a Atividade 2 observa eventos relacionados via ZMQ. |
| UTXO | Atividade 3 | Saída não gasta que pode financiar uma nova transação. A wallet selecionada precisa ter UTXOs maduros para enviar fundos. |
| PSBT | Atividade 3 | Partially Signed Bitcoin Transaction. O backend usa `walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction` para criar, assinar e transmitir transações com Bitcoin Core. |
| Wallet-scoped RPC | Atividade 3 | Chamadas feitas em `/wallet/<nome>` para manter operações de saldo, UTXO, assinatura e histórico isoladas por wallet. |
| Estado interpretado | Atividade 3 | Camada de domínio que traduz respostas do nó em estados como `broadcast`, `mempool`, `confirmed` e `unknown`. |

Referências aprofundadas: [`docs/pt-BR/rpc-zmq.md`](docs/pt-BR/rpc-zmq.md), [`docs/pt-BR/architecture.md`](docs/pt-BR/architecture.md) e [`docs/pt-BR/setup-bitcoin-core.md`](docs/pt-BR/setup-bitcoin-core.md).

---

## Estrutura do repositório

```
CoreCraft/
├── atividade-1/                  Snapshot da mempool via RPC
│   ├── backend/                  FastAPI (porta 8001)
│   │   ├── app/
│   │   │   ├── main.py           rotas /api/mempool/summary, /api/blockchain/lag
│   │   │   ├── mempool.py        cálculo de fee rate e distribuição
│   │   │   └── rpc_client.py     JSON-RPC com tratamento de erro
│   │   └── requirements.txt
│   ├── frontend/                 dashboard React/Vite polling 5s
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
│   ├── frontend/                 dashboard React/Vite com WebSocket + fallback polling
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
│   ├── frontend/                 React/Vite: seletor de wallet, envio PSBT, tabela de tx
│   ├── .env.example
│   └── README.md
│
├── src/
│   └── corecraft/                pacote Python partilhado
│       ├── __init__.py           re-exporta todos os tipos públicos
│       └── types.py              38 TypedDicts — respostas RPC e tipos de domínio
│
├── tests/
│   ├── conftest.py               FakeRPC, FakeResponse, import_activity_module
│   ├── atividade_1/              testes unitários da Atividade 1
│   ├── atividade_2/              testes unitários da Atividade 2
│   └── atividade_3/              testes unitários da Atividade 3
│
├── docs/
│   ├── README.md                 índice bilíngue da documentação
│   ├── pt-BR/                    documentação em Português do Brasil
│   │   ├── getting-started.md    comece aqui (Docker + manual)
│   │   ├── architecture.md       arquitetura e decisões técnicas
│   │   ├── setup-bitcoin-core.md setup do Bitcoin Core
│   │   ├── docker-stack.md       referência da stack Docker
│   │   └── smoke-tests.md        validação dos endpoints
│   ├── en-US/                    documentação em Inglês (US)
│   │   ├── getting-started.md
│   │   ├── architecture.md
│   │   ├── setup-bitcoin-core.md
│   │   ├── docker-stack.md
│   │   └── smoke-tests.md
│   └── assets/                   screenshots e evidências visuais
│
├── CHANGELOG.md                  histórico de versões e correções
├── CONTRIBUTING.md               guia de contribuição
├── SECURITY.md                   política de segurança
├── docker-compose.yml            (opcional) sobe os 3 backends
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
| Node.js | 18+ local, 22.12 no CI/Docker | Frontends React/Vite |

> Setup completo do Bitcoin Core: [`docs/pt-BR/setup-bitcoin-core.md`](docs/pt-BR/setup-bitcoin-core.md)

---

## Início rápido

### 1. Configurar o Bitcoin Core (uma única vez)

```bash
# bitcoin.conf — ver docs/pt-BR/setup-bitcoin-core.md para o conteúdo completo
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

### 3. Rodar a stack completa (Docker Compose)

```bash
cp .env.example .env
docker compose --profile all up --build
# Caddy:
#   http://localhost/atividade-1/
#   http://localhost/atividade-2/
#   http://localhost/atividade-3/
# Portas diretas:
#   http://localhost:8001
#   http://localhost:8002
#   http://localhost:8003
```

Sinais esperados quando a stack estiver pronta:

```text
corecraft-bitcoind             | Bitcoin Core starting
corecraft-bitcoin-init         | Initial funding complete
corecraft-suite-atividade-1    | INFO: Application startup complete.
corecraft-suite-atividade-2    | INFO: Application startup complete.
corecraft-suite-atividade-3    | INFO: Application startup complete.
corecraft-caddy                | serving initial configuration
```

O Compose sobe `bitcoind` em regtest, inicializa wallets, minera saldo inicial para `wallet1`, executa os três backends e expõe as interfaces pelo Caddy. Detalhes em [`docs/pt-BR/docker-stack.md`](docs/pt-BR/docker-stack.md).

Variáveis principais:

```bash
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
BTC_RPC_AUTH=user:corecraft$55eef9f3661634839386ead63a2e72d60d0ef27470547ec7b4b12d0e9dce8db2
LOG_LEVEL=INFO
```

`BTC_RPC_AUTH` é o valor `rpcauth` usado pelo Bitcoin Core. `BTC_RPC_USER` e `BTC_RPC_PASSWORD` continuam sendo usados por `bitcoin-cli`, `bitcoin-init` e pelos backends para autenticar via HTTP Basic Auth.

---

## Endpoints (resumo)

| Método | Rota | Atividade | Descrição |
|:------:|------|:---------:|-----------|
| GET | `/api/mempool/summary` | 1 | Snapshot da mempool com distribuição de fee rate |
| GET | `/api/blockchain/lag` | 1 | Lag de sincronização (`headers - blocks`) |
| GET | `/health` | 1-3 | Healthcheck simples do backend |
| GET | `/metrics` | 1-3 | Métricas Prometheus text básicas |
| GET | `/api/events/summary` | 2 | Contadores e taxa de eventos do buffer ZMQ |
| GET | `/api/events/latest` | 2 | Últimos blocos e txs recebidos via ZMQ |
| GET | `/api/events/state-comparison` | 2 | Compara `getbestblockhash` (RPC) × último bloco (ZMQ) |
| GET | `/wallets` | 3 | Lista wallets disponíveis, carregadas e selecionada |
| POST | `/wallet/select` | 3 | Seleciona e carrega wallet ativa |
| GET | `/wallet/status` | 3 | Saldo e UTXOs da wallet ativa |
| POST | `/tx/send` | 3 | Cria, assina e transmite tx via PSBT |
| GET | `/tx/{txid}` | 3 | Estado interpretado da transação |

Smoke tests completos com `curl`: [`docs/pt-BR/smoke-tests.md`](docs/pt-BR/smoke-tests.md).

---

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [`docs/pt-BR/architecture.md`](docs/pt-BR/architecture.md) | Decisões de design, padrões de implementação e trade-offs |
| [`docs/pt-BR/setup-bitcoin-core.md`](docs/pt-BR/setup-bitcoin-core.md) | `bitcoin.conf`, regtest, wallets, ZMQ, geração de saldo |
| [`docs/pt-BR/rpc-zmq.md`](docs/pt-BR/rpc-zmq.md) | Conceitos: pull (RPC) vs push (ZMQ) e justificativa por atividade |
| [`docs/pt-BR/deploy-vps.md`](docs/pt-BR/deploy-vps.md) | Deploy em VPS Ubuntu 22.04 com `tmux` e `ufw` |
| [`docs/pt-BR/deploy-cloudflare-tunnel.md`](docs/pt-BR/deploy-cloudflare-tunnel.md) | Exposição pública via Cloudflare Tunnel ou ngrok |
| [`docs/pt-BR/smoke-tests.md`](docs/pt-BR/smoke-tests.md) | Smoke tests `curl` por atividade |
| [`docs/pt-BR/docker-stack.md`](docs/pt-BR/docker-stack.md) | Stack Docker completa, variáveis e comandos Make |
| [`docs/pt-BR/docker-troubleshooting.md`](docs/pt-BR/docker-troubleshooting.md) | Diagnóstico de RPC auth, healthchecks, ZMQ e Caddy |
| [`docs/pt-BR/live-validation.md`](docs/pt-BR/live-validation.md) | Resumo da validação contra Bitcoin Core v31.0 |
| [`docs/pt-BR/public-demo.md`](docs/pt-BR/public-demo.md) | Resumo da demo pública via Cloudflare Tunnel (2026-05-03) |

Deploy automatizado: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) executa deploy manual para VPS ou VPS + Cloudflare Tunnel usando GitHub Secrets.

Cada atividade tem seu próprio README detalhado:

- [`atividade-1/README.md`](atividade-1/README.md) — objetivo, restrições, endpoints, exemplos
- [`atividade-2/README.md`](atividade-2/README.md) — fluxo `evento → estado`, ZMQ, divergência
- [`atividade-3/README.md`](atividade-3/README.md) — multi-wallet, PSBT, interpretação de tx

---

## Testes

O projeto usa **pytest** com cobertura mínima de 70% (atualmente 85%).

```bash
# instalar dependências de desenvolvimento
pip install -e ".[dev]"

# executar suite completa com cobertura
pytest tests/ --cov

# type-checking estrito nas 3 atividades
python -m mypy --config-file mypy-atividade-1.ini atividade-1/backend/app/
python -m mypy --config-file mypy-atividade-2.ini atividade-2/backend/app/
python -m mypy --config-file mypy-atividade-3.ini atividade-3/backend/app/
```

Saídas esperadas:

```text
pytest: tests passed, coverage >= 70%
mypy: Success: no issues found
```

| Módulo coberto | Cobertura |
|---|---|
| `rpc_client.py` (3 atividades) | 95–96% |
| `zmq_listener.py` | 84% |
| `tx_service.py` / `tx_interpreter.py` | 96–98% |
| `event_service.py` | 100% |
| **Total** | **85%** |

Os testes usam `monkeypatch` para isolar cada módulo de domínio. `FakeRPC` simula o cliente Bitcoin RPC sem rede real. `import_activity_module` garante que cada atividade é importada num namespace limpo.

---

## Decisões de design (resumo)

- **Sem libs Bitcoin de alto nível.** Cada atividade tem seu `rpc_client.py` próprio (`requests` + `HTTPBasicAuth`). Hash de bloco é calculado localmente em Python.
- **Sem banco de dados.** Estado em memória (`deque` na Atividade 2, `dict` na Atividade 3). Estado zera ao reiniciar — comportamento esperado.
- **PSBT na Atividade 3.** Fluxo `walletcreatefundedpsbt → walletprocesspsbt → finalizepsbt → sendrawtransaction` para o Core cuidar de seleção de UTXO e fee.
- **Erro 503 estruturado.** Quando o nó está offline, todas as rotas que dependem dele retornam `{"detail": {"error": "node_unavailable", "detail": "..."}}` com HTTP 503.
- **Observabilidade mínima.** Logs são emitidos em JSON com `service` e `correlation_id`; cada backend expõe `/health` e `/metrics`.
- **Frontend isolado.** Cada atividade tem frontend React/Vite/TypeScript próprio. URLs relativas e Caddy com prefixos permitem acesso direto (`:8001`/`:8002`/`:8003`) ou por `/atividade-N/`.
- **Decisões de arquitetura completas em [`docs/pt-BR/architecture.md`](docs/pt-BR/architecture.md).**

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

Detalhes (instalação, deploy permanente em VPS, firewall): [`docs/pt-BR/deploy-cloudflare-tunnel.md`](docs/pt-BR/deploy-cloudflare-tunnel.md) e [`docs/pt-BR/deploy-vps.md`](docs/pt-BR/deploy-vps.md).

---

## Validação e demonstração

O projeto foi validado ao vivo contra Bitcoin Core v31.0 em `regtest` em 2026-05-02. A validação completa — incluindo saídas reais dos endpoints, ciclo PSBT e caminho de erro 503 — está documentada em [`docs/pt-BR/live-validation.md`](docs/pt-BR/live-validation.md).

Para reproduzir localmente (requer `bitcoind -regtest` nas portas padrão):

```bash
./scripts/smoke-test.sh
```

Demo pública executada em 2026-05-03 via Cloudflare Tunnel:

### Screenshots dos dashboards

Placeholders versionados para evidências visuais estão em [`docs/assets/README.md`](docs/assets/README.md). Ao gerar novos screenshots/GIFs dos dashboards React, salve-os como:

- `docs/assets/activity-1-dashboard.png`
- `docs/assets/activity-2-events.png`
- `docs/assets/activity-3-wallet.png`

| Atividade | URL | Endpoint validado | Resposta |
|-----------|-----|-------------------|----------|
| 1 | https://administrators-humanitarian-define-author.trycloudflare.com | `/api/blockchain/lag` | `{"blocks":215,"headers":215,"lag":0}` |
| 2 | https://dice-garcia-hub-particular.trycloudflare.com | `/api/events/summary` | `{"blocks_observed":1,"tx_observed":4,...}` |
| 3 | https://move-after-salaries-kde.trycloudflare.com | `/wallets` | `{"available_wallets":[...],"selected_wallet":"wallet1"}` |

> URLs temporárias (trycloudflare.com) — ativas enquanto os processos `cloudflared` estavam rodando. Evidências completas: [`docs/pt-BR/public-demo.md`](docs/pt-BR/public-demo.md).

---

## Releases

O badge de release usa `shields.io/github/v/release/btcneves/CoreCraft` com ordenação SemVer. Para evitar `release: invalid`, a tag publicada no GitHub deve ser limpa e válida, como `v1.0.0`; não use textos como `CoreCraft v1.0.0` no nome da tag. Se necessário, mantenha `CoreCraft v1.0.0` apenas como título da release no GitHub.

---

## Licença

[MIT](LICENSE) © 2026 Pedro Neves
