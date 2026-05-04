# Bitcoin Core Setup (regtest)

This document covers installing and configuring Bitcoin Core for use with CoreCraft on all supported operating systems.

---

## Summary

- [Installation](#installation)
  - [Linux (Ubuntu/Debian)](#linux-ubuntudebian)
  - [Linux (Fedora/RHEL)](#linux-fedorarhel)
  - [Linux — from the official tarball](#linux--from-the-official-tarball)
  - [macOS — Homebrew](#macos--homebrew)
  - [macOS — DMG Installer](#macos--dmg-installer)
  - [Windows — Official Installer](#windows--official-installer)
  - [Windows via WSL 2](#windows-via-wsl-2)
- [Configuration (bitcoin.conf)](#configuration-bitcoinconf)
- [Start and stop the daemon](#start-and-stop-the-daemon)
- [Check status and ZMQ](#check-status-and-zmq)
- [Create wallets and generate balance](#create-wallets-and-generate-balance)
- [Frequent operations](#frequent-operations)

---

## Installation

### Linux (Ubuntu/Debian)

**Option 1 — Official PPA (recommended, simpler):**

```bash
sudo add-apt-repository ppa:bitcoin/bitcoin
sudo apt-get update
sudo apt-get install -y bitcoind bitcoin-qt
```

**Option 2 — direct apt (official Ubuntu repository version, may be older):**

```bash
sudo apt-get update
sudo apt-get install -y bitcoind
```

Check the installed version:

```bash
bitcoind --version
```

---

### Linux (Fedora/RHEL)

```bash
sudo dnf install -y bitcoin-core
```

If the package is not available in the default repository, use the official tarball (see below).

---

### Linux — from the official tarball

Use this method to install any specific version or on PPA-free distributions.

```bash
# Replace with the desired version (see https://bitcoincore.org/en/download/)
VERSION=27.0

# Download and verify integrity
wget https://bitcoincore.org/bin/bitcoin-core-${VERSION}/bitcoin-${VERSION}-x86_64-linux-gnu.tar.gz
wget https://bitcoincore.org/bin/bitcoin-core-${VERSION}/SHA256SUMS

sha256sum --check --ignore-missing SHA256SUMS

# Extract and install
tar xzf bitcoin-${VERSION}-x86_64-linux-gnu.tar.gz
sudo install -m 0755 -t /usr/local/bin \
  bitcoin-${VERSION}/bin/bitcoind \
  bitcoin-${VERSION}/bin/bitcoin-cli

# Check
bitcoind --version
bitcoin-cli --version
```

> For ARM (Raspberry Pi, etc.), replace `x86_64-linux-gnu` with `aarch64-linux-gnu`.

---

### macOS — Homebrew

```bash
brew install bitcoin
```

Homebrew installs `bitcoind` and `bitcoin-cli` on `/usr/local/bin/` (Intel) or `/opt/homebrew/bin/` (Apple Silicon).

```bash
bitcoind --version
```

---

### macOS — DMG Installer

1. Download `.dmg` to [bitcoincore.org/en/download](https://bitcoincore.org/en/download/).
2. Open `.dmg` and drag `Bitcoin-Qt.app` to `Applications`.
3. `bitcoind` and `bitcoin-cli` are in `/Applications/Bitcoin-Qt.app/Contents/MacOS/`:

```bash
# Add to PATH (place in ~/.zshrc or ~/.bash_profile)
export PATH="/Applications/Bitcoin-Qt.app/Contents/MacOS:$PATH"

source ~/.zshrc   # ou source ~/.bash_profile
bitcoind --version
```

---

### Windows — Official Installer

1. Download the `.exe` (64-bit) installer on [bitcoincore.org/en/download](https://bitcoincore.org/en/download/).
2. Run the installer as administrator; Follow the wizard's steps.
3. The installer creates by default `C:\Program Files\Bitcoin\`.
4. Add the `daemon` directory to the system PATH:
   - Control Panel → System → Advanced system settings → Environment Variables
   - Under "System variables", select `Path` → Edit → New
   - Add: `C:\Program Files\Bitcoin\daemon`
5. Open a **new** Command Prompt or PowerShell and check:

```cmd
bitcoind --version
bitcoin-cli --version
```

> The default data directory in Windows is `%APPDATA%\Bitcoin\` (typically `C:\Users\<user>\AppData\Roaming\Bitcoin\`).

---

### Windows via WSL 2

WSL 2 is the **recommended option for development** on Windows: it allows you to use Bitcoin Core and all project tools in a native Linux environment.

**Install WSL 2:**

```powershell
# PowerShell as Administrator
wsl --install -d Ubuntu
# Restart when prompted
```

After restart, configure the Ubuntu user and, in the Ubuntu terminal, follow the [Linux (Ubuntu/Debian)](#linux-ubuntudebian) instructions above.

> Docker Desktop automatically detects WSL 2. `bitcoind` running on WSL 2 is accessible from the Windows host at `127.0.0.1:18443`.

---

## Configuration (bitcoin.conf)

### Paths by operating system

| OS | bitcoin.conf Path |
|----|------------------------|
| Linux | `~/.bitcoin/bitcoin.conf` |
| macOS | `~/Library/Application Support/Bitcoin/bitcoin.conf` |
| Windows (native) | `%APPDATA%\Bitcoin\bitcoin.conf` |
| Windows (WSL 2) | `~/.bitcoin/bitcoin.conf` (within WSL) |

### Create/edit the file

**Linux / macOS / WSL 2:**

```bash
mkdir -p ~/.bitcoin
nano ~/.bitcoin/bitcoin.conf
```

**Windows (PowerShell):**

```powershell
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Bitcoin" | Out-Null
notepad "$env:APPDATA\Bitcoin\bitcoin.conf"
```

### bitcoin.conf content

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

> **Note:** Lines `zmqpub*` are **required for Activity 2**. If you do not intend to use Activity 2, you can omit them — the daemon starts anyway.

> **Note:** `txindex=1` builds a complete index of transactions. On the first start with this flag, the node indexes the chain (in regtest with few blocks, it is instantaneous).

---

## Start and stop the daemon

### Linux/macOS

```bash
# Start in the background
bitcoind -regtest -daemon

# Stop
bitcoin-cli -regtest stop
```

### Windows (Command Prompt)

```cmd
REM Start in the background
start /B bitcoind -regtest -daemon

REM Stop
bitcoin-cli -regtest stop
```

### Windows (PowerShell)

```powershell
# Start in the background
Start-Process bitcoind -ArgumentList "-regtest", "-daemon" -WindowStyle Hidden

# Stop
bitcoin-cli -regtest stop
```

### Start as service in Linux (systemd)

To keep the daemon alive between restarts:

```bash
sudo tee /etc/systemd/system/bitcoind-regtest.service > /dev/null << 'EOF'
[Unit]
Description=Bitcoin Core Daemon (regtest)
After=network.target

[Service]
Type=forking
User=$USER
ExecStart=/usr/local/bin/bitcoind -regtest -daemon -conf=/home/$USER/.bitcoin/bitcoin.conf
ExecStop=/usr/local/bin/bitcoin-cli -regtest stop
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now bitcoind-regtest
```

---

## Check status and ZMQ

```bash
# Chain state
bitcoin-cli -regtest getblockchaininfo

# Check ZMQ (should list rawblock and rawtx if configured)
bitcoin-cli -regtest getzmqnotifications

# List loaded wallets
bitcoin-cli -regtest listwallets

# List wallets on disk
bitcoin-cli -regtest listwalletdir
```

Expected output highlights:

```json
{
  "chain": "regtest",
  "blocks": 0,
  "headers": 0,
  "initialblockdownload": false
}
```

Expected output of `getzmqnotifications` with ZMQ configured:

```json
[
  { "type": "pubrawblock", "address": "tcp://127.0.0.1:28332", "hwm": 1000 },
  { "type": "pubrawtx",    "address": "tcp://127.0.0.1:28333", "hwm": 1000 }
]
```

---

## Create wallets and generate balance

### Create wallets (required for Activities 2 and 3)

```bash
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2
```

Expected output:

```json
{
  "name": "wallet1",
  "warning": ""
}
```

### Generate address and mine balance

```bash
# Get wallet1 address
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
echo "Address: $ADDR"

# Mine 101 blocks (the first 100 coinbases remain immature;
# the 101st block makes the balance from block 1 spendable)
bitcoin-cli -regtest generatetoaddress 101 $ADDR
```

Expected output:

```text
Address: bcrt1...
[
  "block_hash_1",
  "...",
  "block_hash_101"
]
```

**Windows (Command Prompt):**

```cmd
for /f %a in ('bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress') do set ADDR=%a
bitcoin-cli -regtest generatetoaddress 101 %ADDR%
```

### Check balance

```bash
# Detailed balance (trusted / pending / immature)
bitcoin-cli -regtest -rpcwallet=wallet1 getbalances

# General wallet information
bitcoin-cli -regtest -rpcwallet=wallet1 getwalletinfo

# List available UTXOs
bitcoin-cli -regtest -rpcwallet=wallet1 listunspent
```

Expected output highlights:

```json
{
  "mine": {
    "trusted": 50.00000000,
    "untrusted_pending": 0.00000000,
    "immature": 5000.00000000
  }
}
```

```json
{
  "walletname": "wallet1",
  "txcount": 101,
  "balance": 50.00000000
}
```

---

## Frequent operations

### Mine additional blocks

```bash
# Mine 1 block
bitcoin-cli -regtest generatetoaddress 1 $ADDR

# Mine 10 blocks
bitcoin-cli -regtest generatetoaddress 10 $ADDR
```

### Send transaction between wallets (for testing)

```bash
DEST=$(bitcoin-cli -regtest -rpcwallet=wallet2 getnewaddress)
bitcoin-cli -regtest -rpcwallet=wallet1 sendtoaddress $DEST 0.001
```

### View recent transactions

```bash
bitcoin-cli -regtest -rpcwallet=wallet1 listtransactions
```

### Load wallet that is not in memory

```bash
bitcoin-cli -regtest loadwallet wallet2
```

### Download wallet

```bash
bitcoin-cli -regtest unloadwallet wallet2
```

### Restart the daemon (after editing bitcoin.conf)

```bash
bitcoin-cli -regtest stop
sleep 2
bitcoind -regtest -daemon
```

---

## References

- [Bitcoin Core Downloads](https://bitcoincore.org/en/download/)
- [bitcoin.conf reference (bitcoin/bitcoin GitHub)](https://github.com/bitcoin/bitcoin/blob/master/doc/bitcoin-conf.md)
- [JSON-RPC API reference](https://developer.bitcoin.org/reference/rpc/)
- [ZMQ notifications](https://github.com/bitcoin/bitcoin/blob/master/doc/zmq.md)
