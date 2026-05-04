#!/usr/bin/env bash
#
# CoreCraft Smoke Tests
# =====================
# Verifica se as três atividades estão a responder corretamente.
# Aguarda até os serviços ficarem prontos (útil logo após docker compose up).
#
# Uso:
#   ./scripts/smoke-test.sh              # testa tudo, aguarda até 60s
#   ./scripts/smoke-test.sh --no-wait    # falha imediatamente se não estiver pronto
#   ./scripts/smoke-test.sh --timeout 120
#

set -uo pipefail

# ── Cores ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# ── Opções ───────────────────────────────────────────────────────────────────
WAIT=true
TIMEOUT=60

while [[ $# -gt 0 ]]; do
  case $1 in
    --no-wait)   WAIT=false; shift ;;
    --timeout)   TIMEOUT="$2"; shift 2 ;;
    -h|--help)
      echo "Uso: $0 [--no-wait] [--timeout SEGUNDOS]"
      exit 0 ;;
    *) echo -e "${RED}Opção desconhecida: $1${NC}"; exit 1 ;;
  esac
done

# ── Helpers ──────────────────────────────────────────────────────────────────
PASS=0
FAIL=0

check() {
  local label="$1"
  local url="$2"

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")

  if [[ "$http_code" =~ ^2 ]]; then
    echo -e "  ${GREEN}✔${NC}  $label ${BLUE}($http_code)${NC}"
    (( PASS++ )) || true
  else
    echo -e "  ${RED}✘${NC}  $label ${RED}($http_code)${NC}"
    (( FAIL++ )) || true
  fi
}

wait_for_port() {
  local port="$1"
  local label="$2"
  local elapsed=0

  while ! curl -s --max-time 2 "http://127.0.0.1:$port/health" -o /dev/null 2>/dev/null &&
        ! curl -s --max-time 2 "http://127.0.0.1:$port/" -o /dev/null 2>/dev/null; do
    if (( elapsed >= TIMEOUT )); then
      echo -e "  ${RED}✘${NC}  $label não respondeu após ${TIMEOUT}s"
      return 1
    fi
    sleep 2
    (( elapsed += 2 )) || true
    echo -ne "  ${YELLOW}…${NC}  aguardando $label (${elapsed}s/${TIMEOUT}s)\r"
  done
  echo -ne "\033[2K"  # limpa a linha do spinner
  return 0
}

# ── Cabeçalho ────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}══════════════════════════════════════${NC}"
echo -e "${BOLD}   CoreCraft — Smoke Tests${NC}"
echo -e "${BOLD}══════════════════════════════════════${NC}"
echo ""

# ── Aguardar serviços ────────────────────────────────────────────────────────
if [[ "$WAIT" == "true" ]]; then
  echo -e "${BLUE}[INFO]${NC} Aguardando serviços ficarem prontos..."
  echo ""
  SERVICES_OK=true
  for spec in "8001:Atividade 1" "8002:Atividade 2" "8003:Atividade 3"; do
    port="${spec%%:*}"
    name="${spec#*:}"
    if ! wait_for_port "$port" "$name"; then
      SERVICES_OK=false
    fi
  done

  if [[ "$SERVICES_OK" == "false" ]]; then
    echo ""
    echo -e "${RED}[ERRO]${NC} Um ou mais serviços não iniciaram. Verifique os logs:"
    echo "  docker compose logs --tail=30"
    exit 1
  fi
  echo -e "${GREEN}[OK]${NC} Todos os serviços estão prontos."
  echo ""
fi

# ── Atividade 1 ──────────────────────────────────────────────────────────────
echo -e "${BOLD}Atividade 1 — Mempool Snapshot (porta 8001)${NC}"
check "GET /api/mempool/summary"   "http://127.0.0.1:8001/api/mempool/summary"
check "GET /api/blockchain/lag"    "http://127.0.0.1:8001/api/blockchain/lag"
echo ""

# ── Atividade 2 ──────────────────────────────────────────────────────────────
echo -e "${BOLD}Atividade 2 — Eventos ZMQ (porta 8002)${NC}"
check "GET /api/events/summary"         "http://127.0.0.1:8002/api/events/summary"
check "GET /api/events/latest"          "http://127.0.0.1:8002/api/events/latest"
check "GET /api/events/state-comparison" "http://127.0.0.1:8002/api/events/state-comparison"
echo ""

# ── Atividade 3 ──────────────────────────────────────────────────────────────
echo -e "${BOLD}Atividade 3 — Multi-Wallet PSBT (porta 8003)${NC}"
check "GET /wallets"        "http://127.0.0.1:8003/wallets"
check "GET /wallet/status"  "http://127.0.0.1:8003/wallet/status"
echo ""

# ── Resultado ────────────────────────────────────────────────────────────────
TOTAL=$(( PASS + FAIL ))
echo -e "${BOLD}══════════════════════════════════════${NC}"
if (( FAIL == 0 )); then
  echo -e "${GREEN}${BOLD}  RESULTADO: $PASS/$TOTAL endpoints OK${NC}"
else
  echo -e "${RED}${BOLD}  RESULTADO: $PASS/$TOTAL OK — $FAIL falharam${NC}"
  echo ""
  echo -e "${YELLOW}  Dica:${NC} verifique os logs com  docker compose logs --tail=50"
fi
echo -e "${BOLD}══════════════════════════════════════${NC}"
echo ""

(( FAIL == 0 ))
