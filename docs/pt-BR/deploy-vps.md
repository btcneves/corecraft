# Deploy em VPS

[Versao em ingles](../en-US/deploy-vps.md)

## Requisitos

- Ubuntu 22.04+ ou Debian 12+
- 2 GB de RAM ou mais
- Portas dos backends liberadas no firewall
- Docker Engine com Docker Compose v2 para o fluxo recomendado de producao

## Instalacao Base

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl wget tmux
```

## Bitcoin Core

```bash
BTC_VERSION=27.0
wget https://bitcoincore.org/bin/bitcoin-core-${BTC_VERSION}/bitcoin-${BTC_VERSION}-x86_64-linux-gnu.tar.gz
tar -xzf bitcoin-${BTC_VERSION}-x86_64-linux-gnu.tar.gz
sudo install -m 0755 -o root -g root -t /usr/local/bin bitcoin-${BTC_VERSION}/bin/*
```

Configure `~/.bitcoin/bitcoin.conf` conforme [`setup-bitcoin-core.md`](setup-bitcoin-core.md). Use uma senha forte para `rpcpassword`.

## Backends

```bash
git clone https://github.com/btcneves/CoreCraft.git
cd CoreCraft
```

Para cada atividade:

```bash
cd atividade-1/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Repita para as portas `8002` e `8003`.

## tmux

```bash
tmux new-session -d -s activity1 "cd ~/CoreCraft/atividade-1/backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8001"
tmux new-session -d -s activity2 "cd ~/CoreCraft/atividade-2/backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8002"
tmux new-session -d -s activity3 "cd ~/CoreCraft/atividade-3/backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8003"
```

## Firewall

```bash
sudo ufw allow 8001/tcp
sudo ufw allow 8002/tcp
sudo ufw allow 8003/tcp
```

Nao exponha a porta RPC `18443` publicamente.

## Deploy via GitHub Actions

O CoreCraft inclui um workflow manual de deploy: [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml).

Use em GitHub Actions → **Deploy** → **Run workflow**.

### Secrets obrigatorios

| Secret | Descricao |
|--------|-----------|
| `VPS_HOST` | Hostname ou IP da VPS |
| `VPS_USER` | Usuario SSH usado para deploy |
| `VPS_SSH_KEY` | Chave privada SSH com acesso a VPS |

### Secrets opcionais

| Secret | Descricao |
|--------|-----------|
| `VPS_PORT` | Porta SSH. Padrao: `22` |
| `DEPLOY_PATH` | Caminho remoto. Padrao: `~/corecraft` |
| `VPS_ENV_FILE` | Conteudo completo do `.env` para gravar na VPS |
| `CLOUDFLARE_TUNNEL_TOKEN` | Obrigatorio apenas para o target `vps-cloudflare` |

### Targets

| Target | Comportamento |
|--------|---------------|
| `vps` | Faz deploy da stack Docker Compose completa na VPS |
| `vps-cloudflare` | Faz deploy da stack e do sidecar `cloudflared` definido em `docker-compose.cloudflare.yml` |

O workflow valida o Compose, executa `docker compose --profile all up -d --build` e pode rodar `./scripts/smoke-test.sh --timeout 120` apos o deploy.

> Mantenha `VPS_SSH_KEY`, `VPS_ENV_FILE` e `CLOUDFLARE_TUNNEL_TOKEN` apenas em GitHub Secrets. Nunca commite esses valores.
