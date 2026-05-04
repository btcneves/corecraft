# Setup Bitcoin Core (regtest)

Este documento cobre a instalação e configuração do Bitcoin Core para uso com o CoreCraft em todos os sistemas operativos suportados.

---

## Sumário

- [Instalação](#instalação)
  - [Linux (Ubuntu/Debian)](#linux-ubuntudebian)
  - [Linux (Fedora/RHEL)](#linux-fedorarhel)
  - [Linux — a partir do tarball oficial](#linux--a-partir-do-tarball-oficial)
  - [macOS — Homebrew](#macos--homebrew)
  - [macOS — Instalador DMG](#macos--instalador-dmg)
  - [Windows — Instalador oficial](#windows--instalador-oficial)
  - [Windows via WSL 2](#windows-via-wsl-2)
- [Configuração (bitcoin.conf)](#configuração-bitcoinconf)
- [Iniciar e parar o daemon](#iniciar-e-parar-o-daemon)
- [Verificar estado e ZMQ](#verificar-estado-e-zmq)
- [Criar wallets e gerar saldo](#criar-wallets-e-gerar-saldo)
- [Operações frequentes](#operações-frequentes)

---

## Instalação

### Linux (Ubuntu/Debian)

**Opção 1 — PPA oficial (recomendado, mais simples):**

```bash
sudo add-apt-repository ppa:bitcoin/bitcoin
sudo apt-get update
sudo apt-get install -y bitcoind bitcoin-qt
```

**Opção 2 — apt direto (versão do repositório oficial Ubuntu, pode ser mais antiga):**

```bash
sudo apt-get update
sudo apt-get install -y bitcoind
```

Verificar a versão instalada:

```bash
bitcoind --version
```

---

### Linux (Fedora/RHEL)

```bash
sudo dnf install -y bitcoin-core
```

Se o pacote não estiver disponível no repositório padrão, usar o tarball oficial (ver abaixo).

---

### Linux — a partir do tarball oficial

Use este método para instalar qualquer versão específica ou em distribuições sem PPA.

```bash
# Substituir pela versão desejada (ver https://bitcoincore.org/en/download/)
VERSION=27.0

# Descarregar e verificar integridade
wget https://bitcoincore.org/bin/bitcoin-core-${VERSION}/bitcoin-${VERSION}-x86_64-linux-gnu.tar.gz
wget https://bitcoincore.org/bin/bitcoin-core-${VERSION}/SHA256SUMS

sha256sum --check --ignore-missing SHA256SUMS

# Extrair e instalar
tar xzf bitcoin-${VERSION}-x86_64-linux-gnu.tar.gz
sudo install -m 0755 -t /usr/local/bin \
  bitcoin-${VERSION}/bin/bitcoind \
  bitcoin-${VERSION}/bin/bitcoin-cli

# Verificar
bitcoind --version
bitcoin-cli --version
```

> Para ARM (Raspberry Pi, etc.), substituir `x86_64-linux-gnu` por `aarch64-linux-gnu`.

---

### macOS — Homebrew

```bash
brew install bitcoin
```

O Homebrew instala `bitcoind` e `bitcoin-cli` em `/usr/local/bin/` (Intel) ou `/opt/homebrew/bin/` (Apple Silicon).

```bash
bitcoind --version
```

---

### macOS — Instalador DMG

1. Descarregar o `.dmg` em [bitcoincore.org/en/download](https://bitcoincore.org/en/download/).
2. Abrir o `.dmg` e arrastar `Bitcoin-Qt.app` para `Applications`.
3. O `bitcoind` e o `bitcoin-cli` ficam em `/Applications/Bitcoin-Qt.app/Contents/MacOS/`:

```bash
# Adicionar ao PATH (colocar no ~/.zshrc ou ~/.bash_profile)
export PATH="/Applications/Bitcoin-Qt.app/Contents/MacOS:$PATH"

source ~/.zshrc   # ou source ~/.bash_profile
bitcoind --version
```

---

### Windows — Instalador oficial

1. Descarregar o instalador `.exe` (64-bit) em [bitcoincore.org/en/download](https://bitcoincore.org/en/download/).
2. Executar o instalador como administrador; seguir os passos do assistente.
3. O instalador cria por padrão `C:\Program Files\Bitcoin\`.
4. Adicionar o diretório `daemon` ao PATH do sistema:
   - Painel de Controlo → Sistema → Definições avançadas do sistema → Variáveis de Ambiente
   - Em "Variáveis de sistema", selecionar `Path` → Editar → Novo
   - Adicionar: `C:\Program Files\Bitcoin\daemon`
5. Abrir um **novo** Prompt de Comando ou PowerShell e verificar:

```cmd
bitcoind --version
bitcoin-cli --version
```

> O diretório de dados padrão no Windows é `%APPDATA%\Bitcoin\` (tipicamente `C:\Users\<utilizador>\AppData\Roaming\Bitcoin\`).

---

### Windows via WSL 2

WSL 2 é a opção **recomendada para desenvolvimento** no Windows: permite usar Bitcoin Core e todas as ferramentas do projeto num ambiente Linux nativo.

**Instalar WSL 2:**

```powershell
# PowerShell como Administrador
wsl --install -d Ubuntu
# Reiniciar quando solicitado
```

Após o reinício, configurar o utilizador Ubuntu e, no terminal Ubuntu, seguir as instruções [Linux (Ubuntu/Debian)](#linux-ubuntudebian) acima.

> O Docker Desktop detecta automaticamente o WSL 2. O `bitcoind` a correr no WSL 2 é acessível pelo host Windows em `127.0.0.1:18443`.

---

## Configuração (bitcoin.conf)

### Caminhos por sistema operativo

| OS | Caminho do bitcoin.conf |
|----|------------------------|
| Linux | `~/.bitcoin/bitcoin.conf` |
| macOS | `~/Library/Application Support/Bitcoin/bitcoin.conf` |
| Windows (nativo) | `%APPDATA%\Bitcoin\bitcoin.conf` |
| Windows (WSL 2) | `~/.bitcoin/bitcoin.conf` (dentro do WSL) |

### Criar/editar o ficheiro

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

### Conteúdo do bitcoin.conf

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

> **Nota:** As linhas `zmqpub*` são **obrigatórias para a Atividade 2**. Se não pretende usar a Atividade 2, pode omiti-las — o daemon inicia igualmente.

> **Nota:** `txindex=1` constrói um índice completo de transações. Na primeira iniciação com este flag, o nó indexa a chain (em regtest com poucos blocos, é instantâneo).

---

## Iniciar e parar o daemon

### Linux / macOS

```bash
# Iniciar em background
bitcoind -regtest -daemon

# Parar
bitcoin-cli -regtest stop
```

### Windows (Prompt de Comando)

```cmd
REM Iniciar em background
start /B bitcoind -regtest -daemon

REM Parar
bitcoin-cli -regtest stop
```

### Windows (PowerShell)

```powershell
# Iniciar em background
Start-Process bitcoind -ArgumentList "-regtest", "-daemon" -WindowStyle Hidden

# Parar
bitcoin-cli -regtest stop
```

### Iniciar como serviço no Linux (systemd)

Para manter o daemon ativo entre reinícios:

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

## Verificar estado e ZMQ

```bash
# Estado da chain
bitcoin-cli -regtest getblockchaininfo

# Verificar ZMQ (deve listar rawblock e rawtx se configurado)
bitcoin-cli -regtest getzmqnotifications

# Listar wallets carregadas
bitcoin-cli -regtest listwallets

# Listar wallets em disco
bitcoin-cli -regtest listwalletdir
```

Saída esperada de `getzmqnotifications` com ZMQ configurado:

```json
[
  { "type": "pubrawblock", "address": "tcp://127.0.0.1:28332", "hwm": 1000 },
  { "type": "pubrawtx",    "address": "tcp://127.0.0.1:28333", "hwm": 1000 }
]
```

---

## Criar wallets e gerar saldo

### Criar wallets (necessário para Atividades 2 e 3)

```bash
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2
```

### Gerar endereço e minerar saldo

```bash
# Obter endereço da wallet1
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
echo "Endereço: $ADDR"

# Minerar 101 blocos (os primeiros 100 coinbases ficam imaturos;
# o 101.º bloco torna o saldo do bloco 1 gastável)
bitcoin-cli -regtest generatetoaddress 101 $ADDR
```

**Windows (Prompt de Comando):**

```cmd
for /f %a in ('bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress') do set ADDR=%a
bitcoin-cli -regtest generatetoaddress 101 %ADDR%
```

### Verificar saldo

```bash
# Saldo detalhado (trusted / pending / immature)
bitcoin-cli -regtest -rpcwallet=wallet1 getbalances

# Informação geral da wallet
bitcoin-cli -regtest -rpcwallet=wallet1 getwalletinfo

# Lista de UTXOs disponíveis
bitcoin-cli -regtest -rpcwallet=wallet1 listunspent
```

---

## Operações frequentes

### Minerar blocos adicionais

```bash
# Minerar 1 bloco
bitcoin-cli -regtest generatetoaddress 1 $ADDR

# Minerar 10 blocos
bitcoin-cli -regtest generatetoaddress 10 $ADDR
```

### Enviar transação entre wallets (para teste)

```bash
DEST=$(bitcoin-cli -regtest -rpcwallet=wallet2 getnewaddress)
bitcoin-cli -regtest -rpcwallet=wallet1 sendtoaddress $DEST 0.001
```

### Ver transações recentes

```bash
bitcoin-cli -regtest -rpcwallet=wallet1 listtransactions
```

### Carregar wallet que não está em memória

```bash
bitcoin-cli -regtest loadwallet wallet2
```

### Descarregar wallet

```bash
bitcoin-cli -regtest unloadwallet wallet2
```

### Reiniciar o daemon (após editar bitcoin.conf)

```bash
bitcoin-cli -regtest stop
sleep 2
bitcoind -regtest -daemon
```

---

## Referências

- [Bitcoin Core Downloads](https://bitcoincore.org/en/download/)
- [bitcoin.conf reference (bitcoin/bitcoin GitHub)](https://github.com/bitcoin/bitcoin/blob/master/doc/bitcoin-conf.md)
- [JSON-RPC API reference](https://developer.bitcoin.org/reference/rpc/)
- [ZMQ notifications](https://github.com/bitcoin/bitcoin/blob/master/doc/zmq.md)
