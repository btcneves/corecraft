SHELL := /bin/sh
COMPOSE := docker compose

.PHONY: up down build logs ps restart clean bitcoin-cli mine smoke config

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

restart:
	$(COMPOSE) restart

clean:
	$(COMPOSE) down -v

bitcoin-cli:
	$(COMPOSE) exec bitcoind bitcoin-cli -regtest -rpcuser=$${BTC_RPC_USER:-user} -rpcpassword=$${BTC_RPC_PASSWORD:-password}

mine:
	$(COMPOSE) exec bitcoind sh -c 'ADDR=$$(bitcoin-cli -regtest -rpcuser=$${BTC_RPC_USER:-user} -rpcpassword=$${BTC_RPC_PASSWORD:-password} -rpcwallet=wallet1 getnewaddress) && bitcoin-cli -regtest -rpcuser=$${BTC_RPC_USER:-user} -rpcpassword=$${BTC_RPC_PASSWORD:-password} generatetoaddress 1 "$$ADDR"'

smoke:
	./scripts/smoke-test.sh

config:
	$(COMPOSE) config
