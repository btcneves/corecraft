#!/usr/bin/env bash
#
# CoreCraft Smoke Tests
# =====================
# Verifies that all three activities are responding correctly.
# Waits until services are ready (useful right after docker compose --profile all up).
#
# Usage:
#   ./scripts/smoke-test.sh              # test everything, wait up to 60s
#   ./scripts/smoke-test.sh --no-wait    # fail immediately if not ready
#   ./scripts/smoke-test.sh --timeout 120
#

set -uo pipefail

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# ── Options ──────────────────────────────────────────────────────────────────
WAIT=true
TIMEOUT=60

while [[ $# -gt 0 ]]; do
  case $1 in
    --no-wait)   WAIT=false; shift ;;
    --timeout)
      if [[ $# -lt 2 || "$2" == -* ]]; then
        echo -e "${RED}Missing value for --timeout${NC}"
        exit 1
      fi
      TIMEOUT="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--no-wait] [--timeout SECONDS]"
      exit 0 ;;
    *) echo -e "${RED}Unknown option: $1${NC}"; exit 1 ;;
  esac
done

if ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]]; then
  echo -e "${RED}Invalid timeout: $TIMEOUT${NC}"
  exit 1
fi

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
      echo -e "  ${RED}✘${NC}  $label did not respond after ${TIMEOUT}s"
      return 1
    fi
    sleep 2
    (( elapsed += 2 )) || true
    echo -ne "  ${YELLOW}…${NC}  waiting for $label (${elapsed}s/${TIMEOUT}s)\r"
  done
  echo -ne "\033[2K"  # clear spinner line
  return 0
}

# ── Header ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}══════════════════════════════════════${NC}"
echo -e "${BOLD}   CoreCraft — Smoke Tests${NC}"
echo -e "${BOLD}══════════════════════════════════════${NC}"
echo ""

# ── Wait for services ────────────────────────────────────────────────────────
if [[ "$WAIT" == "true" ]]; then
  echo -e "${BLUE}[INFO]${NC} Waiting for services to be ready..."
  echo ""
  SERVICES_OK=true
  for spec in "8001:Activity 1" "8002:Activity 2" "8003:Activity 3"; do
    port="${spec%%:*}"
    name="${spec#*:}"
    if ! wait_for_port "$port" "$name"; then
      SERVICES_OK=false
    fi
  done

  if [[ "$SERVICES_OK" == "false" ]]; then
    echo ""
    echo -e "${RED}[ERROR]${NC} One or more services did not start. Check logs:"
    echo "  docker compose logs --tail=30"
    exit 1
  fi
  echo -e "${GREEN}[OK]${NC} All services are ready."
  echo ""
fi

# ── Activity 1 ───────────────────────────────────────────────────────────────
echo -e "${BOLD}Activity 1 — Mempool Snapshot (port 8001)${NC}"
check "GET /api/mempool/summary"   "http://127.0.0.1:8001/api/mempool/summary"
check "GET /api/blockchain/lag"    "http://127.0.0.1:8001/api/blockchain/lag"
echo ""

# ── Activity 2 ───────────────────────────────────────────────────────────────
echo -e "${BOLD}Activity 2 — ZMQ Events (port 8002)${NC}"
check "GET /api/events/summary"         "http://127.0.0.1:8002/api/events/summary"
check "GET /api/events/latest"          "http://127.0.0.1:8002/api/events/latest"
check "GET /api/events/state-comparison" "http://127.0.0.1:8002/api/events/state-comparison"
echo ""

# ── Activity 3 ───────────────────────────────────────────────────────────────
echo -e "${BOLD}Activity 3 — Multi-Wallet PSBT (port 8003)${NC}"
check "GET /wallets"        "http://127.0.0.1:8003/wallets"
check "GET /wallet/status"  "http://127.0.0.1:8003/wallet/status"
echo ""

# ── Result ───────────────────────────────────────────────────────────────────
TOTAL=$(( PASS + FAIL ))
echo -e "${BOLD}══════════════════════════════════════${NC}"
if (( FAIL == 0 )); then
  echo -e "${GREEN}${BOLD}  RESULT: $PASS/$TOTAL endpoints OK${NC}"
else
  echo -e "${RED}${BOLD}  RESULT: $PASS/$TOTAL OK — $FAIL failed${NC}"
  echo ""
  echo -e "${YELLOW}  Tip:${NC} check logs with  docker compose logs --tail=50"
fi
echo -e "${BOLD}══════════════════════════════════════${NC}"
echo ""

(( FAIL == 0 ))
