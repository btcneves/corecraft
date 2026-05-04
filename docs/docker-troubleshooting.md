# Docker Troubleshooting

This guide helps you diagnose and resolve common issues with the CoreCraft Docker stack.

## Quick Diagnostics

Run these commands to get an overview of the system state:

```bash
# Check service status
docker compose ps

# View recent logs for errors
docker compose logs --tail=20 bitcoind
docker compose logs --tail=20 atividade-1
docker compose logs --tail=20 atividade-2
docker compose logs --tail=20 atividade-3

# Test health endpoints
curl -s http://localhost:8001/health | jq .
curl -s http://localhost:8002/health | jq .
curl -s http://localhost:8003/health | jq .

# Check port conflicts
netstat -tuln | grep -E ':(80|8001|8002|8003|18443|28332|28333)'

# Check disk space
docker system df
df -h
```

## Common Issues

### 1. RPC Authentication Failing

**Symptoms:**
```text
ThreadRPCServer incorrect password attempt from 127.0.0.1
```
or
```text
error: incorrect rpcuser or rpcpassword
```

**Causes:**
- `BTC_RPC_USER`/`BTC_RPC_PASSWORD` in `.env` do not match the `rpcauth` in `infra/bitcoin/bitcoin.conf`
- `.env` file was modified after `bitcoin-init` ran

**Solution:**

1. Check your `.env` matches the default:
   ```bash
   cat .env
   ```
Should show:
   ```bash
   BTC_RPC_USER=user
   BTC_RPC_PASSWORD=password
   ```

2. If you need to change credentials:
   - Generate new `rpcauth` using Bitcoin Core's script:
     ```bash
     docker run --rm bitcoin/bitcoin:26 python3 /usr/bin/rpcauth.py newuser
     ```
   - Update `infra/bitcoin/bitcoin.conf` with the new `rpcauth` value
   - Update `.env` with matching credentials
   - Reset everything:
     ```bash
     docker compose down -v
     docker compose up --build
     ```

3. Test connectivity:
   ```bash
   docker compose exec bitcoind bitcoin-cli -regtest -rpcuser=user -rpcpassword=password getblockchaininfo
   ```

### 2. bitcoind Unhealthy

**Symptoms:**
- `docker compose ps` shows `bitcoind` as `unhealthy`
- Other services cannot connect to Bitcoin

**Causes:**
- First-time blockchain sync takes time
- Insufficient resources
- Port conflicts

**Solution:**

1. Wait longer (first startup can take 2-5 minutes):
   ```bash
   docker compose logs -f bitcoind
   ```

2. Check if bitcoind is actually running:
   ```bash
   docker compose exec bitcoind ps aux | grep bitcoin
   ```

3. Check bitcoind logs:
   ```bash
   docker compose logs bitcoind
   ```

4. Verify ports aren't conflicting:
   ```bash
   # Linux
   ss -tuln | grep -E ':(18443|28332|28333)'
   
   # macOS
   lsof -i :18443
   
   # Windows
   netstat -ano | findstr ":18443"
   ```

5. Increase resources in Docker Desktop (macOS/Windows):
   - Settings → Resources → Memory: 4GB+
   - Settings → Resources → CPUs: 2+

### 3. Unhealthy Backend Services

**Symptoms:**
- `docker compose ps` shows `atividade-*` as `unhealthy`
- `/health` endpoint returns 500 or times out

**Causes:**
- Application crash
- Can't connect to bitcoind
- Missing dependencies

**Solution:**

1. Check if the service is running:
   ```bash
   docker compose logs atividade-1
   ```

2. Test health endpoint directly:
   ```bash
   curl -v http://localhost:8001/health
   ```

3. If `/health` works but Bitcoin routes fail:
   ```bash
   # Test from inside the container
   docker compose exec atividade-1 python -c "
   import urllib.request
   try:
       r = urllib.request.urlopen('http://bitcoind:18443', timeout=3)
       print('Connected to bitcoind')
   except Exception as e:
       print(f'Cannot connect: {e}')
   "
   ```

4. Restart the service:
   ```bash
   docker compose restart atividade-1
   ```

5. Rebuild if needed:
   ```bash
   docker compose build --no-cache atividade-1
   docker compose up -d atividade-1
   ```

### 4. ZMQ Not Receiving Events

**Symptoms:**
- Activity 2 shows `{"status":"waiting_for_zmq_block"}`
- No events received after mining blocks

**Causes:**
- ZMQ ports not properly exposed
- Network connectivity issues
- bitcoind ZMQ not configured

**Solution:**

1. Verify ZMQ is enabled in bitcoind:
   ```bash
   docker compose exec bitcoind bitcoin-cli -regtest getzmqnotifications
   ```
Should show:
   ```json
   [
     {"type": "pubrawblock", "address": "tcp://0.0.0.0:28332"},
     {"type": "pubrawtx", "address": "tcp://0.0.0.0:28333"}
   ]
   ```

2. Test ZMQ connectivity from activity-2:
   ```bash
   docker compose exec atividade-2 python -c "
   import zmq
   ctx = zmq.Context()
   sock = ctx.socket(zmq.SUB)
   sock.connect('tcp://bitcoind:28332')
   sock.setsockopt(zmq.SUBSCRIBE, b'')
   sock.setsockopt(zmq.RCVTIMEO, 5000)
   try:
       msg = sock.recv()
       print(f'Received: {len(msg)} bytes')
   except zmq.Again:
       print('Timeout - no messages')
   ```

3. Check firewall (Linux):
   ```bash
   sudo ufw status
   # If active, allow Docker network
   sudo ufw allow from 172.16.0.0/12
   ```

4. Mine a block to trigger ZMQ:
   ```bash
   make mine
   ```

### 5. Caddy Proxy Not Working

**Symptoms:**
- `http://localhost/atividade-1/` returns error
- Direct ports (8001, 8002, 8003) work fine

**Causes:**
- Caddy cannot reach backend services
- Port 80 already in use
- Caddy configuration error

**Solution:**

1. Check if port 80 is available:
   ```bash
   # Linux
   sudo ss -tuln | grep ':80 '
   
   # macOS
   lsof -i :80
   
   # Windows (admin)
   netstat -ano | findstr ":80 "
   ```

2. Common port 80 conflicts:
   - Apache/Nginx
   - IIS (Windows)
   - Another Docker container

3. Stop conflicting service or change Caddy port in `docker-compose.yml`:
   ```yaml
   caddy:
     ports:
       - "8080:80"  # Use 8080 instead
   ```

4. Check Caddy logs:
   ```bash
   docker compose logs caddy
   ```

5. Verify Caddyfile is valid:
   ```bash
   docker compose exec caddy caddy validate --config /etc/caddy/Caddyfile
   ```

### 6. Port Already in Use

**Symptoms:**
```text
Error starting userland proxy: listen tcp 0.0.0.0:8001: bind: address already in use
```

**Solution:**

1. Find what's using the port:
   ```bash
   # Linux
   ss -tuln | grep ':8001'
   sudo lsof -i :8001
   
   # macOS
   lsof -i :8001
   
   # Windows
   netstat -ano | findstr ":8001"
   tasklist | findstr "<PID>"
   ```

2. Stop the conflicting service or change ports in `docker-compose.yml`:
   ```yaml
   atividade-1:
     ports:
       - "8011:8001"  # Use 8011 instead
   ```

3. Or use Docker Compose profiles to run only what you need:
   ```bash
   docker compose --profile atividade-1 up
   ```

### 7. Out of Disk Space

**Symptoms:**
```text
no space left on device
```

**Solution:**

1. Clean up Docker:
   ```bash
   # Remove unused data
   docker system prune -a --volumes
   
   # Remove specific volumes
   docker compose down -v
   ```

2. Check what's using space:
   ```bash
   docker system df
   docker compose ps -q | xargs docker inspect --format='{{.Name}}: {{.SizeRootFs}}'
   ```

3. For Bitcoin data specifically:
   ```bash
   # This will reset the blockchain
   docker volume rm corecraft-bitcoin-data
   docker compose up -d bitcoind
   ```

### 8. bitcoin-init Fails

**Symptoms:**
- `bitcoin-init` exits with error
- Wallets not created

**Solution:**

1. Check logs:
   ```bash
   docker compose logs bitcoin-init
   ```

2. Manually verify wallets:
   ```bash
   docker compose exec bitcoind bitcoin-cli -regtest listwalletdir
   docker compose exec bitcoind bitcoin-cli -regtest listwallets
   ```

3. Manually create wallets if needed:
   ```bash
   docker compose exec bitcoind bitcoin-cli -regtest createwallet wallet1
   docker compose exec bitcoind bitcoin-cli -regtest createwallet wallet2
   docker compose exec bitcoind bitcoin-cli -regtest -rpcwallet=wallet1 getnewaddress
   docker compose exec bitcoind bitcoin-cli -regtest -rpcwallet=wallet1 generatetoaddress 101 <address>
   ```

### 9. Build Failures

**Symptoms:**
```text
ERROR: failed to solve: failed to compute cache key
```

**Solution:**

1. Clean Docker build cache:
   ```bash
   docker builder prune -a
   ```

2. Rebuild without cache:
   ```bash
   docker compose build --no-cache
   ```

3. If using BuildKit, try:
   ```bash
   DOCKER_BUILDKIT=0 docker compose build
   ```

4. Check disk space:
   ```bash
   df -h
   docker system df
   ```

### 10. Network Connectivity Issues

**Symptoms:**
- Services cannot communicate
- Timeouts connecting to bitcoind

**Solution:**

1. Inspect the network:
   ```bash
   docker network inspect corecraft-network
   ```

2. Test connectivity:
   ```bash
   docker compose exec atividade-1 ping -c 3 bitcoind
   ```

3. Recreate networks:
   ```bash
   docker compose down
   docker network rm corecraft-network
   docker compose up -d
   ```

## Complete Reset

If nothing else works, do a complete reset:

```bash
# Stop everything
docker compose down -v

# Clean Docker
docker system prune -a --volumes

# Remove any orphaned containers
docker rm -f $(docker ps -aq) 2>/dev/null || true

# Remove orphaned networks
docker network prune -f

# Rebuild from scratch
docker compose up --build

# Verify
docker compose ps
curl http://localhost:8001/health
```

## Getting Help

If you're still stuck:

1. **Check logs thoroughly:**
   ```bash
   docker compose logs --tail=100 > all-logs.txt
   ```

2. **Gather system info:**
   ```bash
   docker --version
   docker compose version
   docker info
   uname -a  # Linux/macOS
   ```

3. **Create a GitHub issue** with:
   - Output of `docker compose ps`
   - Relevant logs
   - Your OS and Docker version
   - Steps to reproduce

## macOS — Apple Silicon (M1/M2/M3)

### Symptom: very slow start-up (>5 min) or timeout in health checks

**Cause:** Bitcoin Core Docker images are x86_64. On Apple Silicon, Docker Desktop runs them via Rosetta 2, which adds start-up latency (~30–60 s extra on first run) and higher RAM consumption.

**Solution:**

1. Open Docker Desktop → **Settings** → **Resources** → **Memory**: set to at least **4 GB** (6 GB recommended).
2. Check if Rosetta is enabled: Docker Desktop → **Features in development** → activate **"Use Rosetta for x86/amd64 emulation on Apple Silicon"**.
3. Increase health check timeouts if necessary:
   ```bash
   # In docker-compose.yml, adjust start_period for Bitcoin services:
   # start_period: 120s   (instead of 60s)
   ```

### Symptom: `exec format error` or `no matching manifest`

**Cause:** The image does not have an arm64 variant.

**Solution:** Force the platform in Compose:
```bash
DOCKER_DEFAULT_PLATFORM=linux/amd64 docker compose up
```

Or add to `.env`:
```bash
DOCKER_DEFAULT_PLATFORM=linux/amd64
```

### Symptom: `brew` not found after installing Homebrew

On Apple Silicon, Homebrew installs to `/opt/homebrew/bin`, not `/usr/local/bin`. Add to PATH:
```bash
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## Windows — WSL 2

### Symptom: `docker: command not found` on WSL terminal

**Cause:** Docker Desktop is not exposing the socket within WSL 2.

**Solution:**
1. Open Docker Desktop → **Settings** → **Resources** → **WSL Integration**.
2. Enable integration for your Ubuntu (or other) distribution.
3. Restart the WSL terminal.

To check:
```bash
docker --version    # should show the Docker Desktop version
docker compose version
```

### Symptom: `./scripts/quickstart.sh: Permission denied`

**Cause:** The file was cloned into a Windows file system (ex: `/mnt/c/...`) and POSIX permissions do not apply.

**Workaround:** Clone the repository within the WSL file system (not in `/mnt/c/`):
```bash
cd ~
git clone https://github.com/btcneves/CoreCraft.git
cd corecraft
./scripts/quickstart.sh
```

### Symptom: Ports already in use — conflict with native Windows

Windows can have services listening on the same ports. To check:
```powershell
# PowerShell (outside WSL)
netstat -ano | findstr ":8001 "
netstat -ano | findstr ":18443 "
```

If any port is occupied, end the process or change the port on `docker-compose.yml`.

### Symptom: `Activate.ps1 cannot be loaded` when enabling venv in PowerShell

**Cause:** PowerShell execution policy blocks scripts.

**Solution** (run once, only affects current user):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### bitcoin-cli not recognized in Command Prompt

After installing Bitcoin Core on native Windows, add to PATH:
1. Control Panel → System → Environment Variables → PATH → Edit.
2. Add: `C:\Program Files\Bitcoin\daemon\`
3. Open new terminal and check: `bitcoin-cli --version`

---

## Prevention

To avoid issues:

1. **Keep Docker updated** - Use latest Docker Desktop
2. **Allocate sufficient resources** - 4GB+ RAM (6GB+ on Apple Silicon), 2+ CPUs
3. **Regular cleanup** - `docker system prune` weekly
4. **Do not modify .env** unless you understand the implications
5. **Use profiles** - Only run what you need
6. **Monitor disk space** - Bitcoin data grows over time
7. **Apple Silicon** - Always allocate ≥4GB RAM and use Rosetta emulation
