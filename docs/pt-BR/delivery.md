# Entrega — CoreCraft

[Versao em ingles](../en-US/delivery.md)

## Escopo

Tres microservicos independentes integrados ao Bitcoin Core em `regtest`:

- Atividade 1: snapshot da mempool via RPC.
- Atividade 2: eventos em tempo real via ZMQ.
- Atividade 3: multi-wallet, PSBT e estado interpretado.

## Checklist

- [x] Backends funcionais nas tres atividades.
- [x] Frontends servidas pelo FastAPI.
- [x] Documentacao PT-BR e EN-US.
- [x] Validacao local com Bitcoin Core v31.0.
- [x] Demo publica via Cloudflare Tunnel registrada.

## Evidencias

- Validacao local: [`live-validation.md`](live-validation.md)
- Demo publica: [`public-demo.md`](public-demo.md)
- Guia de smoke tests: [`smoke-tests.md`](smoke-tests.md)

## URLs da Demo

| Atividade | URL |
|-----------|-----|
| 1 | `https://administrators-humanitarian-define-author.trycloudflare.com` |
| 2 | `https://dice-garcia-hub-particular.trycloudflare.com` |
| 3 | `https://move-after-salaries-kde.trycloudflare.com` |

As URLs `trycloudflare.com` sao temporarias e dependem dos processos locais ativos.

