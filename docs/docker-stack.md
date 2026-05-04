# Docker Stack

CoreCraft uses Docker Compose to orchestrate all services needed for the Bitcoin development environment. This guide covers everything you need to know to work with the Docker stack.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/btcneves/corecraft.git
cd corecraft

# Setup environment
cp .env.example .env

# Build and start all services
docker compose up --build

# Or use the setup script for your platform
./scripts/setup-linux.sh      # Linux
./scripts/setup-mac.sh        # macOS
scripts\setup-windows.bat     # Windows
```

## Services Overview

| Service | Description | Ports | Health Check |
|---------|-------------|-------|--------------|
| `bitcoind` | Bitcoin Core regtest node with RPC and ZMQ | 18443, 28332, 28333 | `bitcoin-cli getblockchaininfo` |
| `bitcoin-init` | Initializes wallets and mines initial blocks | - | One-time init |
| `atividade-1` | Mempool monitoring (FastAPI + React) | 8001 | `GET /health` |
| `atividade-2` | ZMQ event listener (FastAPI + React + WebSocket) | 8002 | `GET /health` |
| `atividade-3` | Transaction interpreter (FastAPI + React) | 8003 | `GET /health` |
| `caddy` | Reverse proxy for all activities | 80 | N/A |

## Running Services

### Start All Services

```bash
# Build and start (foreground)
docker compose up --build

# Start in detached mode (background)
docker compose up -d --build

# Start without rebuilding
docker compose up
```

### Run Individual Activities

Use Docker Compose profiles to run specific activities:

```bash
# Activity 1 only (Mempool)
docker compose --profile atividade-1 up

# Activity 2 only (ZMQ Events)
docker compose --profile atividade-2 up

# Activity 3 only (Transaction Interpreter)
docker compose --profile atividade-3 up
```

### Using Setup Scripts

The setup scripts handle everything automatically:

```bash
# Linux/macOS
./scripts/setup-linux.sh --single-activity atividade-1
./scripts/setup-mac.sh --single-activity atividade-2

# Windows
scripts\setup-windows.bat --single-activity atividade-3

# Skip build (use existing images)
./scripts/setup-linux.sh --no-build
```

## Access Services

### Via Caddy Proxy (Recommended)

```
http://localhost/atividade-1/
http://localhost/atividade-2/
http://localhost/atividade-3/
```

### Direct Access

```
http://localhost:8001  # Activity 1
http://localhost:8002  # Activity 2
http://localhost:8003  # Activity 3
```

### Bitcoin RPC

```bash
# From host
bitcoin-cli -regtest -rpcuser=user -rpcpassword=password getblockchaininfo

# From container
docker compose exec bitcoind bitcoin-cli -regtest getblockchaininfo
```

## Useful Commands

### Makefile Targets

```bash
make up          # Start all services (build first)
make down        # Stop all services
make logs        # View all logs
make ps          # Check service status
make build       # Build images only
make restart     # Restart all services
make clean       # Stop and remove volumes (fresh start)
make bitcoin-cli # Interactive bitcoin-cli shell
make mine        # Mine one block to wallet1
make smoke       # Run smoke tests
make config      # Validate docker-compose.yml
```

### Docker Compose Commands

```bash
# View logs
docker compose logs -f                    # All services
docker compose logs -f atividade-1        # Specific service

# Check status
docker compose ps
docker compose top

# Execute commands
docker compose exec bitcoind bitcoin-cli -regtest getblockchaininfo
docker compose exec atividade-1 python -c "print('Hello')"

# Resource usage
docker stats

# Restart services
docker compose restart atividade-1
```

## Environment Variables

### Root `.env` File

```bash
# Bitcoin RPC credentials (must match rpcauth in bitcoin.conf)
BTC_RPC_USER=user
BTC_RPC_PASSWORD=password
BTC_RPC_AUTH=user:corecraft$55eef9f3661634839386ead63a2e72d60d0ef27470547ec7b4b12d0e9dce8db2

# Application logging
LOG_LEVEL=INFO
```

### Internal Service Environment

These are set automatically by docker-compose.yml:

```bash
# All activities
PYTHONUNBUFFERED=1
BTC_RPC_HOST=bitcoind
BTC_RPC_PORT=18443
BTC_RPC_USER=${BTC_RPC_USER}
BTC_RPC_PASSWORD=${BTC_RPC_PASSWORD}

# Activity 2 only (ZMQ)
ZMQ_RAWBLOCK_ENDPOINT=tcp://bitcoind:28332
ZMQ_RAWTX_ENDPOINT=tcp://bitcoind:28333
```

## Volumes

| Volume | Purpose | Persistence |
|--------|---------|-------------|
| `bitcoin-data` | Bitcoin blockchain and wallet data | Persistent |
| `caddy-data` | Caddy TLS certificates | Persistent |
| `caddy-config` | Caddy configuration | Persistent |

### Volume Management

```bash
# List volumes
docker volume ls | grep corecraft

# Inspect volume
docker volume inspect corecraft-bitcoin-data

# Remove all volumes (reset everything)
docker compose down -v
# or
make clean

# Backup Bitcoin data
docker run --rm -v corecraft-bitcoin-data:/data -v $(pwd):/backup alpine tar czf /backup/bitcoin-data.tar.gz /data
```

## Network

All services connect via the `corecraft-network` bridge network:

```bash
# List networks
docker network ls | grep corecraft

# Inspect network
docker network inspect corecraft-network

# Test connectivity
docker compose exec atividade-1 ping -c 3 bitcoind
```

## Health Checks

Services are monitored with health checks:

```bash
# Check health status
docker compose ps

# Test health endpoints manually
curl -s http://localhost:8001/health
curl -s http://localhost:8002/health
curl -s http://localhost:8003/health
```

## Logging

Logs are configured with rotation to prevent disk space issues:

- Max size per file: 10MB
- Max number of files: 3
- Total max per service: 30MB

```bash
# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f --tail=100 atividade-1

# View logs with timestamps
docker compose logs -f -t atividade-2
```

## Troubleshooting

See [docker-troubleshooting.md](docker-troubleshooting.md) for common issues.

### Quick Diagnostics

```bash
# Check if all services are healthy
docker compose ps

# View recent logs for errors
docker compose logs --tail=50 bitcoind
docker compose logs --tail=50 atividade-1

# Test Bitcoin connectivity
docker compose exec bitcoind bitcoin-cli -regtest getblockchaininfo

# Check port conflicts
docker compose ps
netstat -tuln | grep -E ':(80|8001|8002|8003|18443|28332|28333)'
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Port already in use | Stop conflicting service or change ports in docker-compose.yml |
| bitcoind unhealthy | Wait longer (first sync takes time) or check `docker compose logs bitcoind` |
| RPC auth failed | Verify BTC_RPC_USER/PASSWORD match bitcoin.conf rpcauth |
| ZMQ not connecting | Ensure ZMQ ports (28332, 28333) are exposed and accessible |
| Out of disk space | Run `docker system prune -a` and `make clean` |

## Performance Tuning

### Resource Limits

Edit `docker-compose.yml` to add resource limits:

```yaml
services:
  bitcoind:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### Docker Desktop Settings

For macOS/Windows:

1. Open Docker Desktop Settings
2. Go to Resources
3. Allocate:
   - CPUs: 2-4
   - Memory: 4-8GB
   - Swap: 1GB
   - Disk: 50GB+

### WSL 2 Settings (Windows)

Create `.wslconfig` in your user home directory:

```ini
[wsl2]
memory=8GB
processors=4
swap=1GB
```

## Development Mode

For development with hot-reload, use:

```bash
# Run without Docker (local development)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r atividade-1/backend/requirements.txt
uvicorn atividade-1.backend.app.main:app --reload
```

## Security Notes

- Containers run as non-root user (`corecraft`)
- Bitcoin RPC is only accessible within the Docker network
- Ports exposed to host are minimal (80, 8001-8003, 18443, 28332-28333)
- No sensitive data is baked into images

## Update

To update to the latest version:

```bash
# Pull latest changes
git pull

# Rebuild images
docker compose build --no-cache

# Restart services
docker compose down
docker compose up -d
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Network                          │
│                    (corecraft-network)                       │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   bitcoind   │◄──►│ bitcoin-init │    │    caddy     │  │
│  │  (regtest)   │    │   (one-time) │    │  (proxy:80)  │  │
│  │              │    │              │    │              │  │
│  │ RPC: 18443   │    └──────────────┘    └──────▲───────┘  │
│  │ ZMQ: 28332   │                                │          │
│  │      28333   │    ┌──────────────┐            │          │
│  └──────▲───────┘    │  atividade-1 │◄───────────┘          │
│         │             │   (:8001)    │                       │
│         │             └──────────────┘                       │
│         │                                                    │
│         │             ┌──────────────┐                       │
│         └────────────►│  atividade-2 │◄─── External Access   │
│         ZMQ           │   (:8002)    │     (ports 80,       │
│                       └──────────────┘      8001-8003)      │
│                                                              │
│                       ┌──────────────┐                       │
│                       │  atividade-3 │                       │
│                       │   (:8003)    │                       │
│                       └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
