# Deploy — VPS

## Requisitos

- Ubuntu 22.04+ (ou Debian 12+)
- 2 GB RAM mínimo (Bitcoin Core em regtest é leve)
- Porta do backend liberada no firewall

## 1. Instalar dependências

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git curl wget
```

## 2. Instalar Bitcoin Core

```bash
# Verificar última versão em https://bitcoincore.org/en/download/
BTC_VERSION=27.0
wget https://bitcoincore.org/bin/bitcoin-core-${BTC_VERSION}/bitcoin-${BTC_VERSION}-x86_64-linux-gnu.tar.gz
tar -xzf bitcoin-${BTC_VERSION}-x86_64-linux-gnu.tar.gz
sudo install -m 0755 -o root -g root -t /usr/local/bin bitcoin-${BTC_VERSION}/bin/*
```

## 3. Configurar bitcoin.conf

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

> **Segurança:** Use uma senha forte para `rpcpassword`. Nunca exponha a porta RPC (18443) diretamente na internet.

## 4. Iniciar bitcoind

```bash
bitcoind -regtest -daemon
sleep 2
bitcoin-cli -regtest getblockchaininfo
```

## 5. Clonar o repositório

```bash
git clone https://github.com/btcneves/corecraft.git
cd corecraft
```

## 6. Criar .env em cada atividade

```bash
cp atividade-1/.env.example atividade-1/.env
cp atividade-2/.env.example atividade-2/.env
cp atividade-3/.env.example atividade-3/.env
# Editar cada .env com a senha RPC correta
```

## 7. Instalar dependências e rodar backends

### Atividade 1

```bash
cd atividade-1/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Atividade 2

```bash
cd atividade-2/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Atividade 3

```bash
cd atividade-3/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## 8. Rodar com tmux (recomendado para sessões persistentes)

```bash
sudo apt install -y tmux
tmux new-session -d -s atividade1 "cd ~/corecraft/atividade-1/backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8001"
tmux new-session -d -s atividade2 "cd ~/corecraft/atividade-2/backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8002"
tmux new-session -d -s atividade3 "cd ~/corecraft/atividade-3/backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8003"
```

## 9. Liberar portas no firewall

```bash
sudo ufw allow 8001/tcp
sudo ufw allow 8002/tcp
sudo ufw allow 8003/tcp
```

## 10. Apontar frontend para IP público

Os frontends usam URLs relativas, por isso funcionam automaticamente quando acessados pelo IP/porta do backend.

Acesse pelo navegador:
```
http://<IP_DA_VPS>:8001  → Atividade 1
http://<IP_DA_VPS>:8002  → Atividade 2
http://<IP_DA_VPS>:8003  → Atividade 3
```
