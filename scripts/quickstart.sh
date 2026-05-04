#!/usr/bin/env bash
#
# CoreCraft — Quickstart
# ======================
# Ponto de entrada único. Deteta o sistema operativo e delega
# para o script de setup correto.
#
# Uso:
#   ./scripts/quickstart.sh
#   ./scripts/quickstart.sh --single-activity atividade-1
#   ./scripts/quickstart.sh --no-build
#

set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}║       CoreCraft — Quickstart         ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════╝${NC}"
echo ""

# Detetar OS
OS="unknown"
if [[ "$(uname)" == "Darwin" ]]; then
  OS="macos"
elif [[ "$(uname)" == "Linux" ]]; then
  OS="linux"
fi

echo -e "${BLUE}[INFO]${NC} Sistema detetado: $OS"
echo ""

if [[ "$OS" == "linux" ]]; then
  exec "$SCRIPT_DIR/setup-linux.sh" "$@"

elif [[ "$OS" == "macos" ]]; then
  exec "$SCRIPT_DIR/setup-mac.sh" "$@"

else
  echo -e "${YELLOW}[AVISO]${NC} Sistema não reconhecido ou Windows detetado."
  echo ""
  echo "  No Windows, execute num terminal (Prompt de Comando ou PowerShell):"
  echo ""
  echo -e "    ${BOLD}scripts\\setup-windows.bat${NC}"
  echo ""
  echo "  Alternativa recomendada — usar WSL 2 com Ubuntu e correr:"
  echo ""
  echo -e "    ${BOLD}./scripts/quickstart.sh${NC}"
  echo ""
  echo "  Guia completo: docs/getting-started.md"
  echo ""
  exit 1
fi
