#!/usr/bin/env bash
#
# CoreCraft Setup Script for Linux
# ==================================
# This script sets up the CoreCraft Docker environment on Linux.
#
# Usage: ./scripts/setup-linux.sh [--no-build] [--single-activity <name>]
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
      echo "CoreCraft Setup Script for Linux"
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
  error "This script should not be run as root"
  exit 1
fi

echo ""
echo "=========================================="
echo "  CoreCraft Setup - Linux"
echo "=========================================="
echo ""

# Step 1: Check Docker installation
info "Checking Docker installation..."

if ! command -v docker &> /dev/null; then
  error "Docker is not installed. Please install Docker Engine or Docker Desktop first."
  echo ""
  echo "For Ubuntu/Debian:"
  echo "  sudo apt-get update"
  echo "  sudo apt-get install docker.io docker-compose-plugin"
  echo ""
  echo "Or visit: https://docs.docker.com/engine/install/"
  exit 1
fi

if ! docker compose version &> /dev/null; then
  error "Docker Compose v2 is not installed. Please install Docker Compose Plugin."
  echo ""
  echo "For Ubuntu/Debian:"
  echo "  sudo apt-get update"
  echo "  sudo apt-get install docker-compose-plugin"
  echo ""
  exit 1
fi

DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "unknown")
success "Docker $DOCKER_VERSION with Compose $COMPOSE_VERSION detected"

# Step 2: Check Docker daemon is running
info "Checking Docker daemon..."
if ! docker info &> /dev/null; then
  error "Docker daemon is not running. Please start Docker first."
  echo ""
  echo "Try: sudo systemctl start docker"
  exit 1
fi
success "Docker daemon is running"

# Step 3: Check for port conflicts
info "Checking for port conflicts..."
PORT_CONFLICTS=false

for PORT in 80 8001 8002 8003 18443 28332 28333; do
  if ss -tuln | grep -q ":$PORT "; then
    warn "Port $PORT is already in use"
    PORT_CONFLICTS=true
  fi
done

if [[ "$PORT_CONFLICTS" == "true" ]]; then
  warn "Some ports are already in use. You may need to stop other services or change ports."
fi

# Step 4: Setup .env file
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

# Step 5: Validate .env file
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

# Step 6: Build Docker images
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

# Step 7: Show next steps
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
info "Documentation: docs/README.md"
echo ""