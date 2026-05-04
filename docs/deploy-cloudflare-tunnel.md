# Deploy — Cloudflare Tunnel

Cloudflare Tunnel allows you to expose a local server to the internet without opening ports on the router.

## Installation

```bash
# Linux (x64)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# macOS
brew install cloudflare/cloudflare/cloudflared
```

## Expose each activity

```bash
# Activity 1 (backend must be running on 8001)
cloudflared tunnel --url http://localhost:8001

# Activity 2 (backend must be running on 8002)
cloudflared tunnel --url http://localhost:8002

# Activity 3 (backend must be running on 8003)
cloudflared tunnel --url http://localhost:8003
```

cloudflared will display a public URL in the format `https://xxxx-xxxx.trycloudflare.com`.

## Configure the frontend for public URL (if necessary)

If the frontend needs to call the API via absolute URL (e.g. mobile or external), configure the variable `API_BASE` in each `app.js`:

```js
const API_BASE = 'https://xxxx-xxxx.trycloudflare.com';
```

By default, frontends use relative URLs (`/api/...`), so they work unchanged when the backend serves the frontend.

## Tip: run multiple tunnels

```bash
cloudflared tunnel --url http://localhost:8001 &
cloudflared tunnel --url http://localhost:8002 &
cloudflared tunnel --url http://localhost:8003 &
```

## Alternative: ngrok

```bash
ngrok http 8001
ngrok http 8002
ngrok http 8003
```
