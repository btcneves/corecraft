#!/usr/bin/env bash
#
# CoreCraft Setup Script for macOS
# =================================
# This script sets up the CoreCraft Docker environment on macOS.
#
# Usage: ./scripts/setup-mac.sh [--no-build] [--single-activity <name>]
#
# Options:
#   --no-build           Skip building images (use existing images)
#   --single-activity    Start only one activity (atividade-1, atividade-2, or atividade-3)
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory (root of project)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$SCRIPT_DIR"

# Default options
DO_BUILD=true
SINGLE_ACTIVITY=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-build)
      DO_BUILD=false
      shift
      ;;
    --single-activity)
      SINGLE_ACTIVITY="$2"
      shift 2
      ;;
    -h|--help)
      echo "CoreCraft Setup Script for macOS"
      echo ""
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --no-build           Skip building images (use existing images)"
      echo "  --single-activity    Start only one activity (atividade-1, atividade-2, or atividade-3)"
      echo "  -h, --help           Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Logging functions
info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
  echo -e "${GREEN}[OK]${NC} $1"
}

warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
echo "=========================================="
echo "  CoreCraft Setup - macOS"
echo "=========================================="
echo ""

# ── Detetar arquitetura ───────────────────────────────────────────────────────
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
  info "Apple Silicon (arm64) detetado."
  warn "As imagens Docker do Bitcoin Core são x86_64 — correrão via Rosetta 2."
  warn "Isto pode aumentar o tempo de arranque (~30 s extra) e o consumo de RAM."
  warn "Recomendação: alocar pelo menos 4 GB de RAM no Docker Desktop."
  RECOMMENDED_MEM=4000000000
else
  info "Intel (x86_64) detetado."
  RECOMMENDED_MEM=2000000000
fi
echo ""

# ── Verificar Homebrew ────────────────────────────────────────────────────────
if ! command -v brew &> /dev/null; then
  warn "Homebrew não encontrado. Não é obrigatório para Docker, mas é recomendado."
  warn "Para instalar: https://brew.sh"
else
  if [[ "$ARCH" == "arm64" ]] && [[ "$(brew --prefix 2>/dev/null)" != "/opt/homebrew" ]]; then
    warn "Homebrew encontrado mas não no caminho Apple Silicon (/opt/homebrew)."
    warn "Considere reinstalar a versão nativa: https://brew.sh"
  else
    success "Homebrew detetado ($(brew --prefix))"
  fi
fi
echo ""

# Step 1: Check Docker installation
info "Checking Docker installation..."

if ! command -v docker &> /dev/null; then
  error "Docker is not installed. Please install Docker Desktop for Mac first."
  echo ""
  if [[ "$ARCH" == "arm64" ]]; then
    echo "  Descarregar a versão 'Apple Chip': https://www.docker.com/products/docker-desktop/"
  else
    echo "  Download: https://www.docker.com/products/docker-desktop/"
  fi
  echo ""
  echo "  Ou via Homebrew:"
  echo "    brew install --cask docker"
  exit 1
fi

if ! docker compose version &> /dev/null; then
  error "Docker Compose v2 is not installed. Docker Desktop should include this."
  echo ""
  echo "Please reinstall Docker Desktop."
  exit 1
fi

DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "unknown")
success "Docker $DOCKER_VERSION with Compose $COMPOSE_VERSION detected"

# Step 2: Check Docker daemon is running
info "Checking Docker daemon..."
if ! docker info &> /dev/null; then
  error "Docker daemon is not running. Please start Docker Desktop first."
  echo ""
  echo "Open Docker from your Applications folder and wait for it to start."
  exit 1
fi
success "Docker daemon is running"

# Step 3: Check Docker Desktop resources
info "Checking Docker resources..."
DOCKER_MEM=$(docker info --format '{{.MemTotal}}' 2>/dev/null || echo "0")
if [[ "$DOCKER_MEM" -lt "$RECOMMENDED_MEM" ]]; then
  MEM_GB=$(( RECOMMENDED_MEM / 1000000000 ))
  warn "Docker tem menos de ${MEM_GB} GB de RAM alocados."
  warn "Ajuste em: Docker Desktop → Settings → Resources → Memory → ${MEM_GB} GB"
  if [[ "$ARCH" == "arm64" ]]; then
    warn "(Apple Silicon: o overhead do Rosetta 2 exige mais memória que o normal)"
  fi
else
  success "Memória Docker adequada"
fi

# Step 4: Check for port conflicts
info "Checking for port conflicts..."
PORT_CONFLICTS=false

for PORT in 80 8001 8002 8003 18443 28332 28333; do
  if lsof -i :$PORT &> /dev/null; then
    warn "Port $PORT is already in use"
    PORT_CONFLICTS=true
  fi
done

if [[ "$PORT_CONFLICTS" == "true" ]]; then
  warn "Some ports are already in use. You may need to stop other services or change ports."
fi

# Step 5: Setup .env file
info "Setting up environment file..."

if [[ -f .env ]]; then
  warn ".env file already exists. Skipping creation."
  echo "  To reset, delete .env and run again."
else
  if [[ -f .env.example ]]; then
    cp .env.example .env
    success "Created .env from .env.example"
  else
    error ".env.example not found. Cannot create .env file."
    exit 1
  fi
fi

# Step 6: Validate .env file
info "Validating environment file..."
REQUIRED_VARS=("BTC_RPC_USER" "BTC_RPC_PASSWORD" "LOG_LEVEL")
MISSING_VARS=()

for VAR in "${REQUIRED_VARS[@]}"; do
  if ! grep -q "^$VAR=" .env; then
    MISSING_VARS+=("$VAR")
  fi
done

if [[ ${#MISSING_VARS[@]} -gt 0 ]]; then
  warn "Missing environment variables: ${MISSING_VARS[*]}"
  warn "Please add them to .env file"
else
  success "Environment file is valid"
fi

# Step 7: Build Docker images
if [[ "$DO_BUILD" == "true" ]]; then
  info "Building Docker images..."
  echo ""
  
  if [[ -n "$SINGLE_ACTIVITY" ]]; then
    success "Building images for $SINGLE_ACTIVITY..."
    docker compose build $SINGLE_ACTIVITY
  else
    success "Building all images (this may take a few minutes)..."
    docker compose build
  fi
  
  success "Docker images built successfully"
else
  info "Skipping Docker build (--no-build flag set)"
fi

# Step 8: Show next steps
echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""

if [[ -n "$SINGLE_ACTIVITY" ]]; then
  success "To start $SINGLE_ACTIVITY, run:"
  echo ""
  echo "  docker compose --profile $SINGLE_ACTIVITY up"
  echo ""
  echo "Or in detached mode:"
  echo ""
  echo "  docker compose --profile $SINGLE_ACTIVITY up -d"
else
  success "To start all services, run:"
  echo ""
  echo "  docker compose up"
  echo ""
  echo "Or in detached mode:"
  echo ""
  echo "  docker compose up -d"
  echo ""
  echo "To start a specific activity:"
  echo "  docker compose --profile atividade-1 up   # Only Atividade 1"
  echo "  docker compose --profile atividade-2 up   # Only Atividade 2"
  echo "  docker compose --profile atividade-3 up   # Only Atividade 3"
fi

echo ""
info "Useful commands:"
echo "  make logs       # View logs"
echo "  make ps         # Check service status"
echo "  make down       # Stop all services"
echo "  make clean      # Stop and remove volumes"
echo ""
info "Documentation: docs/docker-stack.md"
echo ""