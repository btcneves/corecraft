# Deploy — Cloudflare Tunnel

Cloudflare Tunnel permite expor um servidor local na internet sem abrir portas no roteador.

## Instalação

```bash
# Linux (x64)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# macOS
brew install cloudflare/cloudflare/cloudflared
```

## Expor cada atividade

```bash
# Atividade 1 (backend deve estar rodando em 8001)
cloudflared tunnel --url http://localhost:8001

# Atividade 2 (backend deve estar rodando em 8002)
cloudflared tunnel --url http://localhost:8002

# Atividade 3 (backend deve estar rodando em 8003)
cloudflared tunnel --url http://localhost:8003
```

O cloudflared exibirá uma URL pública no formato `https://xxxx-xxxx.trycloudflare.com`.

## Configurar o frontend para URL pública (se necessário)

Se o frontend precisar chamar a API por URL absoluta (ex.: mobile ou externo), configure a variável `API_BASE` em cada `app.js`:

```js
const API_BASE = 'https://xxxx-xxxx.trycloudflare.com';
```

Por padrão, os frontends usam URLs relativas (`/api/...`), portanto funcionam sem alteração quando o backend serve o frontend.

## Dica: rodar múltiplos túneis

```bash
cloudflared tunnel --url http://localhost:8001 &
cloudflared tunnel --url http://localhost:8002 &
cloudflared tunnel --url http://localhost:8003 &
```

## Alternativa: ngrok

```bash
ngrok http 8001
ngrok http 8002
ngrok http 8003
```
