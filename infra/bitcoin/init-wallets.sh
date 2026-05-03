#!/bin/sh
set -eu

RPC_HOST="${BTC_RPC_HOST:-bitcoind}"
RPC_PORT="${BTC_RPC_PORT:-18443}"
RPC_USER="${BTC_RPC_USER:-user}"
RPC_PASSWORD="${BTC_RPC_PASSWORD:-password}"

bitcoin_cli() {
  bitcoin-cli \
    -regtest \
    -rpcconnect="${RPC_HOST}" \
    -rpcport="${RPC_PORT}" \
    -rpcuser="${RPC_USER}" \
    -rpcpassword="${RPC_PASSWORD}" \
    "$@"
}

echo "Waiting for Bitcoin Core RPC..."
until bitcoin_cli getblockchaininfo >/dev/null 2>&1; do
  sleep 1
done

ensure_wallet() {
  wallet="$1"
  if ! bitcoin_cli listwalletdir | grep -q "\"name\": \"${wallet}\""; then
    bitcoin_cli createwallet "${wallet}" >/dev/null
  fi

  if ! bitcoin_cli listwallets | grep -q "\"${wallet}\""; then
    bitcoin_cli loadwallet "${wallet}" >/dev/null || true
  fi
}

ensure_wallet wallet1
ensure_wallet wallet2

balance="$(bitcoin_cli -rpcwallet=wallet1 getbalances | awk '/trusted/ { gsub(/[,]/, "", $2); print $2; exit }')"
balance="${balance:-0}"

if awk "BEGIN { exit !(${balance} <= 0) }"; then
  address="$(bitcoin_cli -rpcwallet=wallet1 getnewaddress)"
  bitcoin_cli generatetoaddress 101 "${address}" >/dev/null
  echo "wallet1 funded with 101 regtest blocks"
else
  echo "wallet1 already has spendable balance: ${balance} BTC"
fi

bitcoin_cli getzmqnotifications
