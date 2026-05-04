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

## Alternativa

```bash
ngrok http 8001
ngrok http 8002
ngrok http 8003
```

