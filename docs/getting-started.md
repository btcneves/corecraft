# Guia de Início — CoreCraft

Este guia leva qualquer utilizador, em qualquer sistema operativo, do zero até às três atividades a correr.

---

## TL;DR — Já tens Docker? Começa aqui

> Três comandos e a stack está a correr.

```bash
git clone https://github.com/btcneves/corecraft.git
cd corecraft
./scripts/quickstart.sh        # Linux / macOS
# scripts\setup-windows.bat   # Windows
```

Depois de concluído:

```bash
docker compose up              # inicia tudo
./scripts/smoke-test.sh        # confirma que está a funcionar
```

Acede a [http://localhost:8001](http://localhost:8001) (Atividade 1), [http://localhost:8002](http://localhost:8002) (Atividade 2) e [http://localhost:8003](http://localhost:8003) (Atividade 3).

> Não tens Docker? Segue o [Caminho B — Manual, sem Docker](#caminho-b--manual-sem-docker).

---

## Sumário

- [Pré-requisitos](#pré-requisitos)
- [Caminho A — Docker (recomendado)](#caminho-a--docker-recomendado)
- [Caminho B — Manual, sem Docker](#caminho-b--manual-sem-docker)
  - [1. Instalar Bitcoin Core](#1-instalar-bitcoin-core)
  - [2. Instalar Python 3.11+](#2-instalar-python-311)
  - [3. Instalar Node.js 18+](#3-instalar-nodejs-18)
  - [4. Clonar o repositório](#4-clonar-o-repositório)
  - [5. Configurar Bitcoin Core](#5-configurar-bitcoin-core)
  - [6. Iniciar o nó e criar wallets](#6-iniciar-o-nó-e-criar-wallets)
  - [7. Executar as atividades](#7-executar-as-atividades)
  - [8. Verificar com smoke tests](#8-verificar-com-smoke-tests)
- [Windows — Notas específicas](#windows--notas-específicas)
- [Resolução de problemas comuns](#resolução-de-problemas-comuns)

---

## Pré-requisitos

| Dependência | Versão mínima | Caminho A (Docker) | Caminho B (Manual) |
|-------------|--------------|:------------------:|:------------------:|
| Git | qualquer | ✅ | ✅ |
| Docker Engine / Docker Desktop | 24+ | ✅ | — |
| Bitcoin Core | 26+ | incluído na stack | ✅ |
| Python | 3.11+ | incluído na imagem | ✅ |
| Node.js | 18+ | incluído na imagem | só para dev do frontend |

---

## Caminho A — Docker (recomendado)

O Docker Compose sobe Bitcoin Core, inicializa as wallets, minera saldo inicial e inicia os três backends + Caddy. É a opção mais simples em qualquer OS.

### 1. Instalar Docker

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Permitir usar docker sem sudo (requer logout/login)
sudo usermod -aG docker $USER
```

Verificar instalação:

```bash
docker --version
docker compose version
```

</details>

<details>
<summary><b>Linux (Fedora/RHEL/CentOS)</b></summary>

```bash
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo \
  https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

</details>

<details>
<summary><b>macOS</b></summary>

Instalar Docker Desktop:

```bash
# Via Homebrew (recomendado)
brew install --cask docker
```

Ou descarregar o instalador em [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).

Após instalar, abrir o Docker Desktop e aguardar o ícone da baleia aparecer na barra de menus.

</details>

<details>
<summary><b>Windows</b></summary>

1. Descarregar **Docker Desktop para Windows** em [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
2. Executar o instalador; activar a opção **Use WSL 2 based engine** quando solicitado.
3. Reiniciar o computador se pedido.
4. Abrir o Docker Desktop e aguardar até o ícone da baleia ficar estável na barra de tarefas.

Verificar num terminal (PowerShell ou Prompt de Comando):

```cmd
docker --version
docker compose version
```

> **Nota:** No Windows, todos os comandos `docker` e `make` abaixo funcionam no terminal do WSL 2, no Git Bash ou no PowerShell. Se preferir o PowerShell, substitua `./scripts/setup-linux.sh` por `scripts\setup-windows.bat`.

</details>

---

### 2. Clonar o repositório

```bash
git clone https://github.com/btcneves/corecraft.git
cd corecraft
```

### 3. Executar o script de setup

<details>
<summary><b>Linux</b></summary>

```bash
chmod +x scripts/setup-linux.sh
./scripts/setup-linux.sh
```

</details>

<details>
<summary><b>macOS</b></summary>

```bash
chmod +x scripts/setup-mac.sh
./scripts/setup-mac.sh
```

</details>

<details>
<summary><b>Windows (PowerShell ou Prompt de Comando)</b></summary>

```cmd
scripts\setup-windows.bat
```

</details>

O script verifica Docker, cria o `.env` a partir do `.env.example` e constrói as imagens.

### 4. Iniciar a stack completa

```bash
docker compose up --build
```

> Primeira execução demora 3–5 min enquanto o Docker constrói as imagens e baixa Bitcoin Core.

Quando a stack estiver pronta, verá no log:

```
atividade-1  | INFO: Application startup complete.
atividade-2  | INFO: Application startup complete.
atividade-3  | INFO: Application startup complete.
```

### 5. Aceder às interfaces

| URL | Descrição |
|-----|-----------|
| `http://localhost:8001` | Atividade 1 — Mempool Snapshot |
| `http://localhost:8002` | Atividade 2 — Eventos ZMQ |
| `http://localhost:8003` | Atividade 3 — Multi-Wallet PSBT |
| `http://localhost/atividade-1/` | Atividade 1 via Caddy |
| `http://localhost/atividade-2/` | Atividade 2 via Caddy |
| `http://localhost/atividade-3/` | Atividade 3 via Caddy |

### 6. Verificar com smoke tests (Docker)

Com a stack a correr, num terminal separado:

```bash
# Linux / macOS / WSL2
./scripts/smoke-test.sh

# Alternativa (qualquer OS)
make smoke
```

### 7. Iniciar apenas uma atividade

Para iniciar somente a Atividade 1 (com Bitcoin Core como dependência automática):

```bash
# Linux / macOS
docker compose --profile atividade-1 up --build

# Alternativa via Makefile
make up-atividade-1
```

Substitua `atividade-1` por `atividade-2` ou `atividade-3` conforme necessário.

### Comandos Make úteis (Docker)

```bash
make up              # Iniciar todos os serviços (com build)
make up-detached     # Em background
make down            # Parar todos os serviços
make logs            # Ver logs em tempo real
make ps              # Ver estado dos contentores
make mine            # Minerar 1 bloco para wallet1
make mine-10         # Minerar 10 blocos
make wallet-balance  # Verificar saldo da wallet1
make clean           # Parar e apagar volumes (reinício limpo)
```

---

## Caminho B — Manual, sem Docker

Use este caminho quando pretende desenvolver, depurar ou não tem Docker disponível.

### 1. Instalar Bitcoin Core

Ver o guia completo: [**`docs/setup-bitcoin-core.md`**](setup-bitcoin-core.md)

Resumo rápido por OS:

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
sudo add-apt-repository ppa:bitcoin/bitcoin
sudo apt-get update
sudo apt-get install -y bitcoind bitcoin-qt
```

Ou via tarball (sem PPA):

```bash
# Substituir pela versão mais recente em https://bitcoincore.org/en/download/
VERSION=27.0
wget https://bitcoincore.org/bin/bitcoin-core-${VERSION}/bitcoin-${VERSION}-x86_64-linux-gnu.tar.gz
tar xzf bitcoin-${VERSION}-x86_64-linux-gnu.tar.gz
sudo install -m 0755 -t /usr/local/bin \
  bitcoin-${VERSION}/bin/bitcoind \
  bitcoin-${VERSION}/bin/bitcoin-cli
```

</details>

<details>
<summary><b>macOS</b></summary>

```bash
brew install bitcoin
```

Ou descarregar o `.dmg` em [bitcoincore.org/en/download](https://bitcoincore.org/en/download/).

</details>

<details>
<summary><b>Windows</b></summary>

1. Descarregar o instalador `.exe` em [bitcoincore.org/en/download](https://bitcoincore.org/en/download/).
2. Executar o instalador e seguir os passos.
3. Adicionar o diretório de instalação ao PATH (tipicamente `C:\Program Files\Bitcoin\daemon\`):
   - Painel de Controlo → Sistema → Variáveis de Ambiente → PATH → Editar → Adicionar.
4. Verificar num novo terminal:

```cmd
bitcoind --version
bitcoin-cli --version
```

> **Alternativa recomendada para desenvolvimento:** usar WSL 2 com Ubuntu e seguir as instruções Linux. O Bitcoin Core no WSL 2 tem acesso completo à rede e aos ficheiros do Windows.

</details>

---

### 2. Instalar Python 3.11+

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
sudo apt-get install -y python3 python3-pip python3-venv
python3 --version   # deve mostrar 3.11 ou superior
```

Se a versão for inferior a 3.11:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv
```

</details>

<details>
<summary><b>macOS</b></summary>

```bash
brew install python@3.12
python3 --version
```

</details>

<details>
<summary><b>Windows</b></summary>

Descarregar o instalador em [python.org/downloads](https://www.python.org/downloads/).  
Activar a opção **Add Python to PATH** durante a instalação.

Verificar:

```cmd
python --version
```

> **WSL 2:** usar as instruções Linux acima.

</details>

---

### 3. Instalar Node.js 18+

Necessário apenas para compilar ou modificar os frontends React. Se só pretende correr os backends, ignore este passo (o `dist/` já está pré-compilado).

<details>
<summary><b>Linux — via nvm (recomendado)</b></summary>

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc   # ou ~/.zshrc
nvm install 22
nvm use 22
node --version
```

</details>

<details>
<summary><b>macOS</b></summary>

```bash
brew install node@22
node --version
```

</details>

<details>
<summary><b>Windows</b></summary>

Descarregar o instalador LTS em [nodejs.org](https://nodejs.org/).  
Ou, usando winget:

```cmd
winget install OpenJS.NodeJS
```

</details>

---

### 4. Clonar o repositório

```bash
git clone https://github.com/btcneves/corecraft.git
cd corecraft
```

---

### 5. Configurar Bitcoin Core

#### 5a. Criar o ficheiro `bitcoin.conf`

Localize (ou crie) o diretório de dados do Bitcoin Core:

| OS | Caminho padrão |
|----|----------------|
| Linux | `~/.bitcoin/` |
| macOS | `~/Library/Application Support/Bitcoin/` |
| Windows | `%APPDATA%\Bitcoin\` |

Criar o ficheiro de configuração:

**Linux / macOS:**

```bash
mkdir -p ~/.bitcoin
cat > ~/.bitcoin/bitcoin.conf << 'EOF'
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
EOF
```

**Windows (PowerShell):**

```powershell
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Bitcoin" | Out-Null
@"
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
"@ | Set-Content "$env:APPDATA\Bitcoin\bitcoin.conf"
```

> A secção `[regtest]` isola as configurações de RPC e ZMQ ao modo regtest. As linhas `zmqpub*` são obrigatórias para a Atividade 2.

---

### 6. Iniciar o nó e criar wallets

**Linux / macOS:**

```bash
bitcoind -regtest -daemon
sleep 3

# Verificar que está a correr
bitcoin-cli -regtest getblockchaininfo

# Verificar ZMQ (deve listar rawblock e rawtx)
bitcoin-cli -regtest getzmqnotifications

# Criar wallets
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2

# Gerar 101 blocos para wallet1 (mínimo para ter saldo maduro)
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR

# Confirmar saldo
bitcoin-cli -regtest -rpcwallet=wallet1 getbalances
```

**Windows (Prompt de Comando):**

```cmd
bitcoind -regtest -daemon
timeout /t 3 /nobreak > nul

bitcoin-cli -regtest getblockchaininfo
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2

for /f %a in ('bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress') do set ADDR=%a
bitcoin-cli -regtest generatetoaddress 101 %ADDR%
bitcoin-cli -regtest -rpcwallet=wallet1 getbalances
```

---

### 7. Executar as atividades

Cada atividade é independente. Abrir um terminal por atividade.

#### 7a. Configurar as variáveis de ambiente

Em cada diretório `atividade-N/backend`, copiar o `.env.example`:

```bash
# Linux / macOS
cp atividade-1/backend/../.env.example atividade-1/backend/.env
cp atividade-2/backend/../.env.example atividade-2/backend/.env
cp atividade-3/backend/../.env.example atividade-3/backend/.env
```

**Windows (PowerShell):**

```powershell
Copy-Item atividade-1\.env.example atividade-1\backend\.env
Copy-Item atividade-2\.env.example atividade-2\backend\.env
Copy-Item atividade-3\.env.example atividade-3\backend\.env
```

Conteúdo padrão (já correto para regtest local):

```env
BTC_RPC_HOST=127.0.0.1
BTC_RPC_PORT=18443
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
# Atividade 2 também precisa de:
ZMQ_RAWBLOCK_ENDPOINT=tcp://127.0.0.1:28332
ZMQ_RAWTX_ENDPOINT=tcp://127.0.0.1:28333
```

#### 7b. Atividade 1 — Mempool Snapshot (porta 8001)

**Linux / macOS:**

```bash
cd atividade-1/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Windows (PowerShell):**

```powershell
cd atividade-1\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Windows (Prompt de Comando):**

```cmd
cd atividade-1\backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Abrir [http://localhost:8001](http://localhost:8001).

#### 7c. Atividade 2 — Eventos ZMQ (porta 8002)

Verificar que o `bitcoin.conf` tem as linhas `zmqpubrawblock` e `zmqpubrawtx` (ver passo 5) e que o nó foi reiniciado com essas configurações.

**Linux / macOS:**

```bash
cd atividade-2/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

**Windows:**

```powershell
cd atividade-2\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

Gerar eventos ZMQ num terminal separado:

```bash
# Linux / macOS
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 1 $ADDR
```

```cmd
REM Windows
for /f %a in ('bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress') do set ADDR=%a
bitcoin-cli -regtest generatetoaddress 1 %ADDR%
```

Abrir [http://localhost:8002](http://localhost:8002).

#### 7d. Atividade 3 — Multi-Wallet PSBT (porta 8003)

```bash
# Linux / macOS
cd atividade-3/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

```powershell
# Windows
cd atividade-3\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

Abrir [http://localhost:8003](http://localhost:8003).

---

### 8. Verificar com smoke tests

Com os três backends e o nó a correr:

```bash
# Linux / macOS
./scripts/smoke-test.sh

# Ou manualmente, por atividade:
curl -s http://127.0.0.1:8001/api/mempool/summary | python3 -m json.tool
curl -s http://127.0.0.1:8001/api/blockchain/lag   | python3 -m json.tool

curl -s http://127.0.0.1:8002/api/events/summary   | python3 -m json.tool
curl -s http://127.0.0.1:8002/api/events/state-comparison | python3 -m json.tool

curl -s http://127.0.0.1:8003/wallets              | python3 -m json.tool
```

**Windows (PowerShell — requer curl ≥ 7.71 ou Invoke-WebRequest):**

```powershell
# curl existe por default no Windows 10/11
curl -s http://127.0.0.1:8001/api/mempool/summary
curl -s http://127.0.0.1:8001/api/blockchain/lag

curl -s http://127.0.0.1:8003/wallets
```

Guia completo de smoke tests: [**`docs/smoke-tests.md`**](smoke-tests.md)

---

## Windows — Notas específicas

### Activar scripts no PowerShell

Se o PowerShell bloquear a activação do venv com `Activate.ps1`:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Separador de caminho

Nos comandos Windows, substituir `/` por `\` nos caminhos de ficheiros.

### WSL 2 — Opção recomendada para desenvolvimento

WSL 2 (Windows Subsystem for Linux) permite correr um ambiente Linux nativo no Windows. Todos os comandos Linux deste guia funcionam dentro do WSL 2 sem modificação.

Instalar WSL 2 com Ubuntu:

```powershell
# PowerShell como Administrador
wsl --install -d Ubuntu
```

Após instalar e configurar o utilizador Ubuntu, seguir as instruções **Linux** deste guia dentro do terminal WSL.

> O Docker Desktop detecta automaticamente o WSL 2. Pode correr `docker compose` tanto no PowerShell como no terminal WSL.

### Caminhos bitcoin.conf no Windows

| Variante | Caminho |
|----------|---------|
| Windows nativo | `%APPDATA%\Bitcoin\bitcoin.conf` |
| WSL 2 | `~/.bitcoin/bitcoin.conf` |

Para editar o ficheiro diretamente no Windows nativo, pode usar o Notepad:

```cmd
notepad %APPDATA%\Bitcoin\bitcoin.conf
```

### Parar o daemon no Windows

```cmd
bitcoin-cli -regtest stop
```

---

## Resolução de problemas comuns

### `Cannot connect to Bitcoin node`

Verificar se o daemon está a correr:

```bash
bitcoin-cli -regtest getblockchaininfo
```

Se falhar, iniciar:

```bash
bitcoind -regtest -daemon
```

### `No wallet selected` (Atividade 3)

A Atividade 3 exige seleccionar uma wallet via `POST /wallet/select` antes de enviar transações. Usar o selector no dashboard ou via curl:

```bash
curl -s -X POST http://127.0.0.1:8003/wallet/select \
  -H "Content-Type: application/json" \
  -d '{"wallet":"wallet1"}'
```

### ZMQ não recebe eventos (Atividade 2)

Verificar se o `bitcoin.conf` tem as linhas ZMQ e se o nó foi reiniciado após adicioná-las:

```bash
bitcoin-cli -regtest getzmqnotifications
# Deve listar: zmqpubrawblock e zmqpubrawtx
```

Se a lista estiver vazia, editar o `bitcoin.conf`, parar e reiniciar o daemon.

### `Insufficient funds` ao enviar transação

Em regtest, os coinbases demoram 100 blocos a maturar. Minerar pelo menos 101 blocos:

```bash
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR
```

### Portas já em uso

Verificar qual processo ocupa a porta (ex.: 8001):

```bash
# Linux
ss -tlnp | grep 8001

# macOS
lsof -i :8001

# Windows
netstat -ano | findstr :8001
```

### Docker: `port is already allocated`

Parar a stack e remover contentores:

```bash
docker compose down
docker compose up --build
```

Se o problema persistir: `docker compose down -v` para remover volumes também.

---

## Próximos passos

- Guia de contribuição e testes: [**`CONTRIBUTING.md`**](../CONTRIBUTING.md)
- Arquitetura e decisões de design: [**`docs/architecture.md`**](architecture.md)
- Deploy em VPS Ubuntu: [**`docs/deploy-vps.md`**](deploy-vps.md)
- Exposição pública via Cloudflare Tunnel: [**`docs/deploy-cloudflare-tunnel.md`**](deploy-cloudflare-tunnel.md)
- Stack Docker completa: [**`docs/docker-stack.md`**](docker-stack.md)
- Troubleshooting Docker: [**`docs/docker-troubleshooting.md`**](docker-troubleshooting.md)
