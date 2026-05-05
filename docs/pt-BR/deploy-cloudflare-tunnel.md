# Deploy com Cloudflare Tunnel

[Versao em ingles](../en-US/deploy-cloudflare-tunnel.md)

Cloudflare Tunnel permite expor um backend local na internet sem abrir portas no roteador.

## Instalacao

Linux:

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

macOS:

```bash
brew install cloudflare/cloudflare/cloudflared
```

## Expor Atividades

```bash
cloudflared tunnel --url http://localhost:8001
cloudflared tunnel --url http://localhost:8002
cloudflared tunnel --url http://localhost:8003
```

O comando exibira uma URL `https://...trycloudflare.com`.

As frontends usam URLs relativas por padrao, entao funcionam quando servidas pelo proprio backend.

## Tunnel nomeado para VPS

Para deploy repetivel em VPS, crie um Cloudflare Tunnel nomeado no dashboard da Cloudflare e configure hostnames publicos apontando para o Caddy:

| Hostname publico | Service |
|------------------|---------|
| `corecraft.example.com` | `http://caddy:80` |

Depois salve o token do tunnel no secret `CLOUDFLARE_TUNNEL_TOKEN` do GitHub e execute o workflow **Deploy** com target `vps-cloudflare`.

O workflow usa [`docker-compose.cloudflare.yml`](../../docker-compose.cloudflare.yml), que sobe um sidecar `cloudflared` na mesma rede Docker do Caddy:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.cloudflare.yml \
  --profile all \
  --profile cloudflare \
  up -d --build
```

Assim, nao e necessario expor as portas da aplicacao diretamente no firewall da VPS.

## Alternativa

```bash
ngrok http 8001
ngrok http 8002
ngrok http 8003
```
