# Setup do Bitcoin Core em Regtest

[Versao em ingles](../en-US/setup-bitcoin-core.md)

## Instalacao

### Linux

```bash
sudo apt-get update
sudo apt-get install -y bitcoind bitcoin-qt
```

Ou use o pacote oficial em [bitcoincore.org/en/download](https://bitcoincore.org/en/download/).

### macOS

```bash
brew install bitcoin
```

### Windows

Baixe o instalador em [bitcoincore.org/en/download](https://bitcoincore.org/en/download/) e adicione `C:\Program Files\Bitcoin\daemon` ao PATH.

Para desenvolvimento, WSL 2 com Ubuntu costuma ser a opcao mais simples.

## Configuracao

Crie `bitcoin.conf`.

Linux/macOS/WSL:

```bash
mkdir -p ~/.bitcoin
nano ~/.bitcoin/bitcoin.conf
```

Conteudo recomendado:

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

## Inicializacao

```bash
bitcoind -regtest -daemon
bitcoin-cli -regtest getblockchaininfo
bitcoin-cli -regtest getzmqnotifications
```

## Wallets e Saldo

```bash
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
bitcoin-cli -regtest generatetoaddress 101 $ADDR
bitcoin-cli -regtest -rpcwallet=wallet1 getbalances
```

Em regtest, 101 blocos tornam o primeiro coinbase gastavel.

