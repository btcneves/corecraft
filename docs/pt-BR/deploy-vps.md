# Deploy em VPS

[Versao em ingles](../en-US/deploy-vps.md)

## Requisitos

- Ubuntu 22.04+ ou Debian 12+
- 2 GB de RAM ou mais
- Portas dos backends liberadas no firewall

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

