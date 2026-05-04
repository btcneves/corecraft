#!/usr/bin/env bash
#
# CoreCraft — Quickstart
# ======================
# Ponto de entrada unico. Detecta o sistema operacional e delega
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

# Detect OS
OS="unknown"
if [[ "$(uname)" == "Darwin" ]]; then
  OS="macos"
elif [[ "$(uname)" == "Linux" ]]; then
  OS="linux"
fi

echo -e "${BLUE}[INFO]${NC} Sistema detectado: $OS"
echo ""

if [[ "$OS" == "linux" ]]; then
  exec "$SCRIPT_DIR/setup-linux.sh" "$@"

elif [[ "$OS" == "macos" ]]; then
  exec "$SCRIPT_DIR/setup-mac.sh" "$@"

else
  echo -e "${YELLOW}[WARN]${NC} Sistema nao reconhecido ou Windows detectado."
  echo ""
  echo "  No Windows, execute em PowerShell:"
  echo ""
  echo -e "    ${BOLD}.\\scripts\\setup-windows.ps1${NC}"
  echo ""
  echo "  Compatibilidade com Prompt de Comando:"
  echo ""
  echo -e "    ${BOLD}scripts\\setup-windows.bat${NC}"
  echo ""
  echo "  Alternativa recomendada: WSL 2 com Ubuntu:"
  echo ""
  echo -e "    ${BOLD}./scripts/quickstart.sh${NC}"
  echo ""
  echo "  Guia completo: docs/README.md"
  echo ""
  exit 1
fi
