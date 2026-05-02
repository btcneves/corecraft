# Setup Bitcoin Core (regtest)

## bitcoin.conf

Localização padrão:
- Linux: `~/.bitcoin/bitcoin.conf`
- macOS: `~/Library/Application Support/Bitcoin/bitcoin.conf`

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

> **Nota:** `zmqpubrawblock` e `zmqpubrawtx` são obrigatórios para a Atividade 2.

## Iniciar o daemon

```bash
bitcoind -regtest -daemon
```

## Verificar status

```bash
bitcoin-cli -regtest getblockchaininfo
bitcoin-cli -regtest getzmqnotifications   # deve listar rawblock e rawtx
```

## Criar wallets

```bash
bitcoin-cli -regtest createwallet wallet1
bitcoin-cli -regtest createwallet wallet2
```

## Listar wallets

```bash
bitcoin-cli -regtest listwalletdir   # wallets disponíveis em disco
bitcoin-cli -regtest listwallets     # wallets carregadas em memória
```

## Carregar wallet

```bash
bitcoin-cli -regtest loadwallet wallet1
```

## Gerar endereço

```bash
ADDR=$(bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress)
echo $ADDR
```

## Minerar saldo (regtest)

```bash
# Minerar 101 blocos para a wallet1 (maturidade de 100 blocos)
bitcoin-cli -regtest generatetoaddress 101 $ADDR
```

## Verificar saldo

```bash
bitcoin-cli -regtest -rpcwallet=wallet1 getwalletinfo
bitcoin-cli -regtest -rpcwallet=wallet1 listunspent
```

## Gerar transação de teste

```bash
DEST=$(bitcoin-cli -regtest -rpcwallet=wallet2 getnewaddress)
bitcoin-cli -regtest -rpcwallet=wallet1 sendtoaddress $DEST 0.001
```

## Gerar bloco para confirmar

```bash
bitcoin-cli -regtest generatetoaddress 1 $ADDR
```

## Parar o daemon

```bash
bitcoin-cli -regtest stop
```
