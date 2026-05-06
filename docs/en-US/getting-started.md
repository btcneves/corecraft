# Getting Started Guide — CoreCraft

This guide takes any user, on any operating system, from zero to running three activities.

---

## TL;DR — Do you already have Docker? Start here

> Three commands and the stack is running.

```bash
git clone https://github.com/btcneves/CoreCraft.git
cd CoreCraft
./scripts/quickstart.sh        # Linux / macOS
# powershell -ExecutionPolicy Bypass -File scripts\setup-windows.ps1  # Windows
```

Once completed:

```bash
docker compose --profile all up  # starts everything
./scripts/smoke-test.sh        # confirms it is working
```

Open [http://localhost:8001](http://localhost:8001) (Activity 1), [http://localhost:8002](http://localhost:8002) (Activity 2), and [http://localhost:8003](http://localhost:8003) (Activity 3).

> No Docker available? Follow [Path B — Manual, without Docker](#path-b--manual-without-docker).

---

## Summary

- [Prerequisites](#prerequisites)
- [Path A — Docker (recommended)](#path-a--docker-recommended)
- [Path B — Manual, without Docker](#path-b--manual-without-docker)
  - [1. Install Bitcoin Core](#1-install-bitcoin-core)
  - [2. Install Python 3.11+](#2-install-python-311)
  - [3. Install Node.js 18+](#3-install-nodejs-18)
  - [4. Clone the repository](#4-clone-the-repository)
  - [5. Configure Bitcoin Core](#5-configure-bitcoin-core)
  - [6. Launch the node and create wallets](#6-launch-the-node-and-create-wallets)
  - [7. Run the activities](#7-run-the-activities)
  - [8. Check with smoke tests](#8-check-with-smoke-tests)
- [Windows — Specific notes](#windows--specific-notes)
- [Troubleshooting common problems](#troubleshooting-common-problems)

---

## Prerequisites

| Dependency | Minimum version | Path A (Docker) | Path B (Manual) |
|-------------|--------------|:------------------:|:------------------:|
| Git | any | ✅ | ✅ |
| Docker Engine / Docker Desktop | 24+ | ✅ | — |
| Bitcoin Core | 26+ | included in the stack | ✅ |
| Python | 3.11+ | included in the image | ✅ |
| Node.js | 18+ | included in the image | only for frontend dev |

---

## Path A — Docker (recommended)

Docker Compose starts Bitcoin Core, initializes the wallets, mines the initial balance, and launches the three backends plus Caddy. It is the simplest option on any OS.

### 1. Install Docker

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

# Allow using docker without sudo (requires logout/login)
sudo usermod -aG docker $USER
```

Check installation:

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

Install Docker Desktop:

```bash
# Via Homebrew (recommended)
brew install --cask docker
```

Or download the installer at [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).

After installing, open Docker Desktop and wait for the whale icon to appear in the menu bar.

</details>

<details>
<summary><b>Windows</b></summary>

1. Download **Docker Desktop for Windows** at [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
2. Run the installer; activate the **Use WSL 2 based engine** option when prompted.
3. Restart the computer if prompted.
4. Open Docker Desktop and wait until the whale icon becomes stable on the taskbar.

Check in a terminal (PowerShell or Command Prompt):

```cmd
docker --version
docker compose version
```

> **Note:** On Windows, all of the `docker` and `make` commands below work in the WSL 2 terminal, Git Bash, or PowerShell. If you prefer PowerShell, replace `./scripts/setup-linux.sh` with `powershell -ExecutionPolicy Bypass -File scripts\setup-windows.ps1`.

</details>

---

### 2. Clone the repository

```bash
git clone https://github.com/btcneves/CoreCraft.git
cd CoreCraft
```

### 3. Run the setup script

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
<summary><b>Windows (PowerShell or Command Prompt)</b></summary>

```cmd
powershell -ExecutionPolicy Bypass -File scripts\setup-windows.ps1
```

</details>

The script checks Docker, creates `.env` from `.env.example` and builds the images.

### 4. Start full stack

```bash
docker compose --profile all up --build
```

> First run takes 3–5 min while Docker builds the images and downloads Bitcoin Core.

When the stack is ready, you will see in the log:

```text
corecraft-bitcoind             | Bitcoin Core starting
corecraft-bitcoin-init         | Initial funding complete
corecraft-suite-atividade-1    | INFO: Application startup complete.
corecraft-suite-atividade-2    | INFO: Application startup complete.
corecraft-suite-atividade-3    | INFO: Application startup complete.
corecraft-caddy                | serving initial configuration
```

In another terminal, `docker compose ps` should show healthy services:

```text
NAME                            STATUS
corecraft-bitcoind              Up ... (healthy)
corecraft-bitcoin-init          Exited (0)
corecraft-suite-atividade-1     Up ... (healthy)
corecraft-suite-atividade-2     Up ... (healthy)
corecraft-suite-atividade-3     Up ... (healthy)
corecraft-caddy                 Up ...
```

### 5. Access the interfaces

| URL | Description |
|-----|-----------|
| `http://localhost:8001` | Activity 1 — Mempool Snapshot |
| `http://localhost:8002` | Activity 2 — ZMQ Events |
| `http://localhost:8003` | Activity 3 — PSBT Multi-Wallet |
| `http://localhost/atividade-1/` | Activity 1 via Caddy |
| `http://localhost/atividade-2/` | Activity 2 via Caddy |
| `http://localhost/atividade-3/` | Activity 3 via Caddy |

### 6. Check with smoke tests (Docker)

With the stack running, in a separate terminal:

```bash
# Linux / macOS / WSL2
./scripts/smoke-test.sh

# Alternative (any OS)
make smoke
```

Expected result:

```text
CoreCraft — Smoke Tests
Activity 1 — Mempool Snapshot      2/2 OK
Activity 2 — ZMQ Events            3/3 OK
Activity 3 — Multi-Wallet PSBT     2/2 OK
RESULT: 7/7 endpoints OK
```

### 7. Start just one activity

To start only Activity 1 (with Bitcoin Core as automatic dependency):

```bash
# Linux / macOS
docker compose --profile atividade-1 up --build

# Makefile alternative
make up-atividade-1
```

Replace `atividade-1` with `atividade-2` or `atividade-3` as needed.

### Useful Make Commands (Docker)

```bash
make up              # Start all services (with build)
make up-detached     # Run in the background
make down            # Stop all services
make logs            # View real-time logs
make ps              # View container status
make mine            # Mine 1 block for wallet1
make mine-10         # Mine 10 blocks
make wallet-balance  # Check wallet1 balance
make clean           # Stop and delete volumes (clean restart)
```

---

## Path B — Manual, without Docker

Use this path when you want to develop, debug, or do not have Docker available.

### 1. Install Bitcoin Core

See the complete guide: [**`setup-bitcoin-core.md`**](setup-bitcoin-core.md)

Quick summary by OS:

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
sudo add-apt-repository ppa:bitcoin/bitcoin
sudo apt-get update
sudo apt-get install -y bitcoind bitcoin-qt
```

Or via tarball (no PPA):

```bash
# Replace with the latest version from https://bitcoincore.org/en/download/
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

Or download `.dmg` at [bitcoincore.org/en/download](https://bitcoincore.org/en/download/).

</details>

<details>
<summary><b>Windows</b></summary>

1. Download the `.exe` installer on [bitcoincore.org/en/download](https://bitcoincore.org/en/download/).
2. Run the installer and follow the steps.
3. Add the installation directory to the PATH (typically `C:\Program Files\Bitcoin\daemon\`):
   - Control Panel → System → Environment Variables → PATH → Edit → Add.
4. Check on a new terminal:

```cmd
bitcoind --version
bitcoin-cli --version
```

> **Recommended alternative for development:** use WSL 2 with Ubuntu and follow the Linux instructions. Bitcoin Core on WSL 2 has full access to the Windows network and files.

</details>

---

### 2. Install Python 3.11+

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
sudo apt-get install -y python3 python3-pip python3-venv
python3 --version   # should show 3.11 or higher
```

If the version is lower than 3.11:

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

Download the installer at [python.org/downloads](https://www.python.org/downloads/).
Enable the **Add Python to PATH** option during installation.

To check:

```cmd
python --version
```

> **WSL 2:** use the Linux instructions above.

</details>

---

### 3. Install Node.js 18+

Only needed to compile or modify React frontends. If you only want to run the backends, skip this step (`dist/` is already pre-compiled).

<details>
<summary><b>Linux — via nvm (recommended)</b></summary>

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc   # or ~/.zshrc
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

Download the LTS installer at [nodejs.org](https://nodejs.org/).
Or, using winget:

```cmd
winget install OpenJS.NodeJS
```

</details>

---

### 4. Clone the repository

```bash
git clone https://github.com/btcneves/CoreCraft.git
cd CoreCraft
```

---

### 5. Configure Bitcoin Core

#### 5a. Create the file `bitcoin.conf`

Locate (or create) the Bitcoin Core data directory:

| OS | Default path |
|----|----------------|
| Linux | `~/.bitcoin/` |
| macOS | `~/Library/Application Support/Bitcoin/` |
| Windows | `%APPDATA%\Bitcoin\` |

Create the configuration file:

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

> The `[regtest]` section isolates RPC and ZMQ configurations to regtest mode. Lines `zmqpub*` are mandatory for Activity 2.

---

### 6. Launch the node and create wallets

**Linux / macOS:**

```bash
bitcoind -regtest -daemon
sleep 3

# Check that it is running
bitcoin-cli -regtest getblockchaininfo

# Check ZMQ (should list rawblock and rawtx)
bitcoin-cli -regtest getzmqnotifications

# Create wallets
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2

# Generate 101 blocks for wallet1 (minimum required for mature balance)
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR

# Confirm balance
bitcoin-cli -regtest -rpcwallet=wallet1 getbalances
```

Expected output highlights:

```json
{
  "chain": "regtest",
  "blocks": 101,
  "headers": 101,
  "verificationprogress": 1
}
```

```json
[
  { "type": "pubrawblock", "address": "tcp://127.0.0.1:28332", "hwm": 1000 },
  { "type": "pubrawtx", "address": "tcp://127.0.0.1:28333", "hwm": 1000 }
]
```

```json
{
  "mine": {
    "trusted": 50.00000000,
    "untrusted_pending": 0.00000000,
    "immature": 5000.00000000
  }
}
```

**Windows (Command Prompt):**

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

### 7. Run the activities

Each activity is independent. Open a terminal per activity.

#### 7a. Configure environment variables

In each `atividade-N/backend` directory, copy the `.env.example`:

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

Default content (already correct for local regtest):

```env
BTC_RPC_HOST=127.0.0.1
BTC_RPC_PORT=18443
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
# Activity 2 also needs:
ZMQ_RAWBLOCK_ENDPOINT=tcp://127.0.0.1:28332
ZMQ_RAWTX_ENDPOINT=tcp://127.0.0.1:28333
```

#### 7b. Activity 1 — Mempool Snapshot (port 8001)

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

**Windows (Command Prompt):**

```cmd
cd atividade-1\backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Open [http://localhost:8001](http://localhost:8001).

#### 7c. Activity 2 — ZMQ Events (port 8002)

Check that `bitcoin.conf` has the lines `zmqpubrawblock` and `zmqpubrawtx` (see step 5) and that the node has been restarted with these settings.

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

Generate ZMQ events on a separate terminal:

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

Open [http://localhost:8002](http://localhost:8002).

#### 7d. Activity 3 — PSBT Multi-Wallet (port 8003)

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

Open [http://localhost:8003](http://localhost:8003).

---

### 8. Check with smoke tests

With the three backends and the node running:

```bash
# Linux / macOS
./scripts/smoke-test.sh

# Or manually, per activity:
curl -s http://127.0.0.1:8001/api/mempool/summary | python3 -m json.tool
curl -s http://127.0.0.1:8001/api/blockchain/lag   | python3 -m json.tool

curl -s http://127.0.0.1:8002/api/events/summary   | python3 -m json.tool
curl -s http://127.0.0.1:8002/api/events/state-comparison | python3 -m json.tool

curl -s http://127.0.0.1:8003/wallets              | python3 -m json.tool
```

Expected output highlights:

```json
{"tx_count": 0, "fee_distribution": {"low": 0, "medium": 0, "high": 0}}
```

```json
{"blocks": 101, "headers": 101, "lag": 0}
```

```json
{"available_wallets": ["wallet1", "wallet2"], "selected_wallet": "wallet1"}
```

**Windows (PowerShell — requires curl ≥ 7.71 or Invoke-WebRequest):**

```powershell
# curl is available by default on Windows 10/11
curl -s http://127.0.0.1:8001/api/mempool/summary
curl -s http://127.0.0.1:8001/api/blockchain/lag

curl -s http://127.0.0.1:8003/wallets
```

Complete smoke testing guide: [**`smoke-tests.md`**](smoke-tests.md)

---

## Windows — Specific notes

### Enable scripts in PowerShell

If PowerShell blocks venv activation with `Activate.ps1`:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Path Separator

In Windows commands, replace `/` with `\` in the file paths.

### WSL 2 — Recommended option for development

WSL 2 (Windows Subsystem for Linux) allows you to run a native Linux environment on Windows. All Linux commands in this guide work within WSL 2 without modification.

Install WSL 2 with Ubuntu:

```powershell
# PowerShell as Administrator
wsl --install -d Ubuntu
```

After installing and configuring the Ubuntu user, follow the **Linux** instructions in this guide within the WSL terminal.

> Docker Desktop automatically detects WSL 2. You can run `docker compose` in both PowerShell and the WSL terminal.

### bitcoin.conf Paths on Windows

| Variant | Path |
|----------|---------|
| Native Windows | `%APPDATA%\Bitcoin\bitcoin.conf` |
| WSL 2 | `~/.bitcoin/bitcoin.conf` |

To edit the file directly in native Windows, you can use Notepad:

```cmd
notepad %APPDATA%\Bitcoin\bitcoin.conf
```

### Stop the daemon on Windows

```cmd
bitcoin-cli -regtest stop
```

---

## Troubleshooting common problems

### `Cannot connect to Bitcoin node`

Check if the daemon is running:

```bash
bitcoin-cli -regtest getblockchaininfo
```

If it fails, start:

```bash
bitcoind -regtest -daemon
```

### `No wallet selected` (Activity 3)

Activity 3 requires selecting a wallet via `POST /wallet/select` before sending transactions. Use the selector on the dashboard or via curl:

```bash
curl -s -X POST http://127.0.0.1:8003/wallet/select \
  -H "Content-Type: application/json" \
  -d '{"wallet":"wallet1"}'
```

### ZMQ does not receive events (Activity 2)

Verify that `bitcoin.conf` has the ZMQ lines and that the node was restarted after adding them:

```bash
bitcoin-cli -regtest getzmqnotifications
# Should list: zmqpubrawblock and zmqpubrawtx
```

If the list is empty, edit `bitcoin.conf`, stop and restart the daemon.

### `Insufficient funds` when sending transaction

In regtest, coinbases take 100 blocks to mature. Mine at least 101 blocks:

```bash
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR
```

### Ports already in use

Check which process occupies the port (e.g.: 8001):

```bash
# Linux
ss -tlnp | grep 8001

# macOS
lsof -i :8001

# Windows
netstat -ano | findstr :8001
```

### Docker: `port is already allocated`

Stop the stack and remove containers:

```bash
docker compose down
docker compose --profile all up --build
```

If the problem persists: `docker compose down -v` to remove volumes as well.

---

## Next steps

- Contribution and testing guide: [**`CONTRIBUTING.md`**](../../CONTRIBUTING.md)
- Architecture and design decisions: [**`architecture.md`**](architecture.md)
- Deploy on Ubuntu VPS: [**`deploy-vps.md`**](deploy-vps.md)
- Public exposure via Cloudflare Tunnel: [**`deploy-cloudflare-tunnel.md`**](deploy-cloudflare-tunnel.md)
- Complete Docker Stack: [**`docker-stack.md`**](docker-stack.md)
- Troubleshooting Docker: [**`docker-troubleshooting.md`**](docker-troubleshooting.md)
