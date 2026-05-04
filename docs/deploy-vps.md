# Deploy — VPS

## Requirements

- Ubuntu 22.04+ (or Debian 12+)
- 2 GB RAM minimum (Bitcoin Core in regtest is light)
- Backend port released on firewall

## 1. Install dependencies

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git curl wget
```

## 2. Install Bitcoin Core

```bash
# Check the latest version at https://bitcoincore.org/en/download/
BTC_VERSION=27.0
wget https://bitcoincore.org/bin/bitcoin-core-${BTC_VERSION}/bitcoin-${BTC_VERSION}-x86_64-linux-gnu.tar.gz
tar -xzf bitcoin-${BTC_VERSION}-x86_64-linux-gnu.tar.gz
sudo install -m 0755 -o root -g root -t /usr/local/bin bitcoin-${BTC_VERSION}/bin/*
```

## 3. Configure bitcoin.conf

```bash
mkdir -p ~/.bitcoin
cat > ~/.bitcoin/bitcoin.conf << 'EOF'
regtest=1
server=1
txindex=1
fallbackfee=0.0001

[regtest]
rpcuser=user
rpcpassword=TROQUE_ESTA_SENHA
rpcbind=127.0.0.1
rpcallowip=127.0.0.1
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
EOF
```

> **Security:** Use a strong password for `rpcpassword`. Never expose the RPC port (18443) directly to the internet.

## 4. Start bitcoind

```bash
bitcoind -regtest -daemon
sleep 2
bitcoin-cli -regtest getblockchaininfo
```

## 5. Clone the repository

```bash
git clone https://github.com/btcneves/CoreCraft.git
cd corecraft
```

## 6. Create .env in each activity

```bash
cp atividade-1/.env.example atividade-1/.env
cp atividade-2/.env.example atividade-2/.env
cp atividade-3/.env.example atividade-3/.env
# Edit each .env with the correct RPC password
```

## 7. Install dependencies and run backends

### Activity 1

```bash
cd atividade-1/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Activity 2

```bash
cd atividade-2/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Activity 3

```bash
cd atividade-3/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## 8. Run with tmux (recommended for persistent sessions)

```bash
sudo apt install -y tmux
tmux new-session -d -s atividade1 "cd ~/corecraft/atividade-1/backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8001"
tmux new-session -d -s atividade2 "cd ~/corecraft/atividade-2/backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8002"
tmux new-session -d -s atividade3 "cd ~/corecraft/atividade-3/backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8003"
```

## 9. Release ports on the firewall

```bash
sudo ufw allow 8001/tcp
sudo ufw allow 8002/tcp
sudo ufw allow 8003/tcp
```

## 10. Point frontend to public IP

Frontends use relative URLs, so they work automatically when accessed through the backend's IP/port.

Access via browser:
```
http://<IP_DA_VPS>:8001  → Activity 1
http://<IP_DA_VPS>:8002  → Activity 2
http://<IP_DA_VPS>:8003  → Activity 3
```
