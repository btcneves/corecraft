# Guia de Inicio Rapido — CoreCraft

[Versao em ingles](../en-US/getting-started.md)

Este guia leva o projeto do zero ate as tres atividades em execucao com Bitcoin Core em `regtest`.

## Caminho A — Docker

Use este caminho para validar o projeto rapidamente.

```bash
git clone https://github.com/btcneves/CoreCraft.git
cd CoreCraft
./scripts/quickstart.sh
docker compose up --build
```

No Windows, use:

```cmd
scripts\setup-windows.bat
docker compose up --build
```

Ao final, acesse:

| Atividade | URL |
|-----------|-----|
| Atividade 1 | `http://localhost:8001` |
| Atividade 2 | `http://localhost:8002` |
| Atividade 3 | `http://localhost:8003` |
| Caddy | `http://localhost/atividade-1/`, `/atividade-2/`, `/atividade-3/` |

Execute os smoke tests:

```bash
./scripts/smoke-test.sh
```

Resultado esperado: `7/7 endpoints OK`.

## Caminho B — Manual

Use este caminho para desenvolvimento local, depuracao ou ambientes sem Docker.

1. Instale Bitcoin Core 26+.
2. Configure `~/.bitcoin/bitcoin.conf` com `regtest=1`, RPC e ZMQ.
3. Inicie o daemon:

```bash
bitcoind -regtest -daemon
```

4. Crie wallets e gere saldo:

```bash
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR
```

5. Inicie cada backend em um terminal:

```bash
cd atividade-1/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Repita para `atividade-2/backend` na porta `8002` e `atividade-3/backend` na porta `8003`.

## Proximos Passos

- Arquitetura: [`architecture.md`](architecture.md)
- Setup Bitcoin Core: [`setup-bitcoin-core.md`](setup-bitcoin-core.md)
- Stack Docker: [`docker-stack.md`](docker-stack.md)
- Smoke tests: [`smoke-tests.md`](smoke-tests.md)

