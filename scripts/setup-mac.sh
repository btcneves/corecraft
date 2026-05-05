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
VALID_ACTIVITIES="atividade-1 atividade-2 atividade-3"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-build)
      DO_BUILD=false
      shift
      ;;
    --single-activity)
      if [[ $# -lt 2 || "$2" == -* ]]; then
        echo -e "${RED}Missing value for --single-activity${NC}"
        exit 1
      fi
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

if [[ -n "$SINGLE_ACTIVITY" && ! " $VALID_ACTIVITIES " =~ " $SINGLE_ACTIVITY " ]]; then
  echo -e "${RED}Invalid activity: $SINGLE_ACTIVITY${NC}"
  echo "Valid values: $VALID_ACTIVITIES"
  exit 1
fi

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

# ── Detectar arquitetura ──────────────────────────────────────────────────────
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
  info "Apple Silicon (arm64) detected."
  warn "Bitcoin Core Docker images are x86_64 and may run through Rosetta 2."
  warn "This can increase startup time and RAM usage."
  warn "Recommendation: allocate at least 4 GB of RAM in Docker Desktop."
  RECOMMENDED_MEM=4000000000
else
  info "Intel (x86_64) detected."
  RECOMMENDED_MEM=2000000000
fi
echo ""

# ── Check Homebrew ────────────────────────────────────────────────────────────
if ! command -v brew &> /dev/null; then
  warn "Homebrew not found. It is not required for Docker, but it is recommended."
  warn "Install from: https://brew.sh"
else
  if [[ "$ARCH" == "arm64" ]] && [[ "$(brew --prefix 2>/dev/null)" != "/opt/homebrew" ]]; then
    warn "Homebrew was found outside the native Apple Silicon path (/opt/homebrew)."
    warn "Consider installing the native version: https://brew.sh"
  else
    success "Homebrew detected ($(brew --prefix))"
  fi
fi
echo ""

# Step 1: Check Docker installation
info "Checking Docker installation..."

if ! command -v docker &> /dev/null; then
  error "Docker is not installed. Please install Docker Desktop for Mac first."
  echo ""
  if [[ "$ARCH" == "arm64" ]]; then
    echo "  Download the Apple Chip version: https://www.docker.com/products/docker-desktop/"
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
  warn "Docker has less than ${MEM_GB} GB of RAM allocated."
  warn "Adjust it in: Docker Desktop → Settings → Resources → Memory → ${MEM_GB} GB"
  if [[ "$ARCH" == "arm64" ]]; then
    warn "(Apple Silicon: Rosetta 2 overhead requires more memory than usual)"
  fi
else
  success "Docker memory allocation is adequate"
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

if ! grep -q "^COMPOSE_PROFILES=" .env; then
  warn "COMPOSE_PROFILES is not set in .env. Adding COMPOSE_PROFILES=all for full-stack defaults."
  printf "\nCOMPOSE_PROFILES=all\n" >> .env
fi

info "Validating Docker Compose configuration..."
if [[ -n "$SINGLE_ACTIVITY" ]]; then
  docker compose --profile "$SINGLE_ACTIVITY" config >/dev/null
else
  docker compose --profile all config >/dev/null
fi
success "Docker Compose configuration is valid"

# Step 7: Build Docker images
if [[ "$DO_BUILD" == "true" ]]; then
  info "Building Docker images..."
  echo ""
  
  if [[ -n "$SINGLE_ACTIVITY" ]]; then
    success "Building images for $SINGLE_ACTIVITY..."
    docker compose build "$SINGLE_ACTIVITY"
  else
    success "Building all images (this may take a few minutes)..."
    docker compose --profile all build
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
  echo "  docker compose --profile all up"
  echo ""
  echo "Or in detached mode:"
  echo ""
  echo "  docker compose --profile all up -d"
  echo ""
  echo "To start a specific activity:"
  echo "  docker compose --profile atividade-1 up   # Activity 1 only"
  echo "  docker compose --profile atividade-2 up   # Activity 2 only"
  echo "  docker compose --profile atividade-3 up   # Activity 3 only"
fi

echo ""
info "Useful commands:"
echo "  make logs       # View logs"
echo "  make ps         # Check service status"
echo "  make down       # Stop all services"
echo "  make clean      # Stop and remove volumes"
echo ""
info "Documentation: docs/README.md"
echo ""
