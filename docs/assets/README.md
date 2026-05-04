# Dashboard Assets

This directory reserves stable names for screenshots/GIFs of React dashboards:

- `atividade-1-dashboard.png`
- `atividade-2-events.png`
- `atividade-3-wallet.png`

Visual files must be updated from a real run of `docker compose up --build`, preferably after validating RPC, ZMQ and PSBT with smoke tests.

To refresh the screenshots:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m playwright install chromium
make mine-10
python scripts/capture-dashboard-screenshots.py
```

The capture script uses Playwright with a `1440x900` viewport, waits for `networkidle`, and saves full-page PNG screenshots.
