SHELL := /bin/sh
COMPOSE := docker compose
PYTHON ?= python3

.PHONY: up down build logs ps restart clean bitcoin-cli mine smoke config format-check lint type test security frontend audit ci

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

format-check:
	$(PYTHON) -m ruff format --check .

lint:
	$(PYTHON) -m ruff check .

type:
	$(PYTHON) -m mypy --no-incremental --config-file mypy-atividade-1.ini
	$(PYTHON) -m mypy --no-incremental --config-file mypy-atividade-2.ini
	$(PYTHON) -m mypy --no-incremental --config-file mypy-atividade-3.ini

test:
	$(PYTHON) -m pytest

security:
	$(PYTHON) -m pip_audit -r atividade-1/backend/requirements.txt -r atividade-2/backend/requirements.txt -r atividade-3/backend/requirements.txt

frontend:
	cd atividade-1/frontend && npm ci && npm run build
	cd atividade-2/frontend && npm ci && npm run build
	cd atividade-3/frontend && npm ci && npm run build

audit:
	cd atividade-1/frontend && npm audit --audit-level=moderate
	cd atividade-2/frontend && npm audit --audit-level=moderate
	cd atividade-3/frontend && npm audit --audit-level=moderate

ci: format-check lint type test frontend security audit config
