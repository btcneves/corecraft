SHELL := /bin/sh
COMPOSE := docker compose
PYTHON ?= python3

# Default activity for single-activity targets
ACTIVITY ?= atividade-1

.PHONY: help up down build logs ps restart clean bitcoin-cli mine smoke config \
         format-check lint type test security frontend audit ci \
         up-atividade-1 up-atividade-2 up-atividade-3 \
         logs-atividade-1 logs-atividade-2 logs-atividade-3 \
         shell-atividade-1 shell-atividade-2 shell-atividade-3 \
         shell-bitcoind test-local

help:
	@echo "CoreCraft Makefile - Available Targets"
	@echo "======================================="
	@echo ""
	@echo "Docker Compose:"
	@echo "  make up              Start all services (build first)"
	@echo "  make up-detached     Start all services in background"
	@echo "  make down            Stop all services"
	@echo "  make build           Build all images"
	@echo "  make logs            View all logs"
	@echo "  make ps              Check service status"
	@echo "  make restart         Restart all services"
	@echo "  make clean           Stop and remove volumes (fresh start)"
	@echo "  make config          Validate docker-compose.yml"
	@echo ""
	@echo "Single Activity (with dependencies):"
	@echo "  make up-atividade-1  Start only Atividade 1 (Mempool)"
	@echo "  make up-atividade-2  Start only Atividade 2 (ZMQ Events)"
	@echo "  make up-atividade-3  Start only Atividade 3 (Tx Interpreter)"
	@echo ""
	@echo "Individual Logs:"
	@echo "  make logs-atividade-1  View Atividade 1 logs"
	@echo "  make logs-atividade-2  View Atividade 2 logs"
	@echo "  make logs-atividade-3  View Atividade 3 logs"
	@echo ""
	@echo "Interactive Shells:"
	@echo "  make shell-atividade-1  Open shell in Atividade 1"
	@echo "  make shell-atividade-2  Open shell in Atividade 2"
	@echo "  make shell-atividade-3  Open shell in Atividade 3"
	@echo "  make shell-bitcoind     Open bitcoin-cli shell"
	@echo ""
	@echo "Bitcoin:"
	@echo "  make bitcoin-cli     Interactive bitcoin-cli shell"
	@echo "  make mine            Mine one block to wallet1"
	@echo "  make mine-10         Mine 10 blocks to wallet1"
	@echo "  make wallet-balance  Check wallet1 balance"
	@echo ""
	@echo "Testing:"
	@echo "  make smoke           Run smoke tests"
	@echo "  make test-local      Run local tests (without Docker)"
	@echo ""
	@echo "Development:"
	@echo "  make format-check    Check code formatting"
	@echo "  make lint            Run linter"
	@echo "  make type            Run type checker"
	@echo "  make test            Run unit tests"
	@echo "  make security        Run security audit"
	@echo "  make frontend        Build all frontends"
	@echo "  make audit           Audit npm packages"
	@echo "  make ci              Run full CI pipeline"

# ==============================================================================
# Docker Compose
# ==============================================================================

up:
	$(COMPOSE) up --build

up-detached:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

logs:
	$(COMPOSE) logs -f

logs-atividade-1:
	$(COMPOSE) logs -f atividade-1

logs-atividade-2:
	$(COMPOSE) logs -f atividade-2

logs-atividade-3:
	$(COMPOSE) logs -f atividade-3

ps:
	$(COMPOSE) ps

restart:
	$(COMPOSE) restart

clean:
	$(COMPOSE) down -v
	$(COMPOSE) rm -f

config:
	$(COMPOSE) config

# ==============================================================================
# Single Activity (using profiles)
# ==============================================================================

up-atividade-1:
	$(COMPOSE) --profile atividade-1 up --build

up-atividade-2:
	$(COMPOSE) --profile atividade-2 up --build

up-atividade-3:
	$(COMPOSE) --profile atividade-3 up --build

# ==============================================================================
# Interactive Shells
# ==============================================================================

shell-atividade-1:
	$(COMPOSE) exec atividade-1 /bin/sh

shell-atividade-2:
	$(COMPOSE) exec atividade-2 /bin/sh

shell-atividade-3:
	$(COMPOSE) exec atividade-3 /bin/sh

shell-bitcoind:
	$(COMPOSE) exec bitcoind bitcoin-cli -regtest -rpcuser=$${BTC_RPC_USER:-user} -rpcpassword=$${BTC_RPC_PASSWORD:-password}

# ==============================================================================
# Bitcoin Operations
# ==============================================================================

bitcoin-cli:
	$(COMPOSE) exec bitcoind bitcoin-cli -regtest -rpcuser=$${BTC_RPC_USER:-user} -rpcpassword=$${BTC_RPC_PASSWORD:-password}

mine:
	$(COMPOSE) exec bitcoind sh -c 'ADDR=$$(bitcoin-cli -regtest -rpcuser=$${BTC_RPC_USER:-user} -rpcpassword=$${BTC_RPC_PASSWORD:-password} -rpcwallet=wallet1 getnewaddress) && bitcoin-cli -regtest -rpcuser=$${BTC_RPC_USER:-user} -rpcpassword=$${BTC_RPC_PASSWORD:-password} generatetoaddress 1 "$$ADDR"'

mine-10:
	$(COMPOSE) exec bitcoind sh -c 'ADDR=$$(bitcoin-cli -regtest -rpcuser=$${BTC_RPC_USER:-user} -rpcpassword=$${BTC_RPC_PASSWORD:-password} -rpcwallet=wallet1 getnewaddress) && bitcoin-cli -regtest -rpcuser=$${BTC_RPC_USER:-user} -rpcpassword=$${BTC_RPC_PASSWORD:-password} generatetoaddress 10 "$$ADDR"'

wallet-balance:
	$(COMPOSE) exec bitcoind bitcoin-cli -regtest -rpcuser=$${BTC_RPC_USER:-user} -rpcpassword=$${BTC_RPC_PASSWORD:-password} -rpcwallet=wallet1 getbalances

# ==============================================================================
# Testing
# ==============================================================================

smoke:
	./scripts/smoke-test.sh

test-local:
	$(PYTHON) -m pytest tests/ -v

# ==============================================================================
# Development (CI targets)
# ==============================================================================

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