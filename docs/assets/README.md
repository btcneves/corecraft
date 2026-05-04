# Dashboard Assets / Assets dos Dashboards

This directory stores shared visual evidence used by both documentation tracks.

Esta pasta armazena evidencias visuais compartilhadas pelas documentacoes em PT-BR e EN-US.

## Stable File Names / Nomes Estaveis

- `activity-1-dashboard.png`
- `activity-2-events.png`
- `activity-3-wallet.png`

Update these files from a real `docker compose up --build` run, preferably after validating RPC, ZMQ, and PSBT with smoke tests.

Atualize estes arquivos a partir de uma execucao real de `docker compose up --build`, de preferencia depois de validar RPC, ZMQ e PSBT com smoke tests.

## Refresh / Atualizacao

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m playwright install chromium
make mine-10
python scripts/capture-dashboard-screenshots.py
```

The capture script uses Playwright with a `1440x900` viewport, waits for `networkidle`, and saves full-page PNG screenshots.

O script de captura usa Playwright com viewport `1440x900`, aguarda `networkidle` e salva screenshots PNG de pagina inteira.
