# Contributing

## Prerequisites

- Python 3.11+
- Bitcoin Core 26.0+ running in `regtest` mode
- `pip` and `venv`

## Local setup

Each activity is independent. The setup steps are the same for all three:

```bash
cd atividade-1/backend          # or atividade-2 / atividade-3
cp ../.env.example .env         # fill in your RPC credentials
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8001 --reload
```

See [`docs/setup-bitcoin-core.md`](docs/setup-bitcoin-core.md) for Bitcoin Core configuration.

## Project conventions

- **No Bitcoin libraries.** Use the `rpc_client.py` pattern from the existing activities — `requests` + `HTTPBasicAuth` + JSON-RPC 2.0.
- **No shared modules across activities.** Each activity must be fully self-contained.
- **No database.** In-memory state only (`deque` or `dict`).
- **Structured 503.** Routes that depend on the node return `{"detail": {"error": "node_unavailable", "detail": "..."}}` with HTTP 503 when the node is offline — never HTTP 500.

## Testing

Test against a live `bitcoind -regtest` node. The smoke tests in [`docs/smoke-tests.md`](docs/smoke-tests.md) cover the full flow for each activity.

## Submitting changes

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-change`.
3. Make your changes and validate against a live regtest node.
4. Open a pull request with a clear description of what changed and why.

## Reporting issues

Open a GitHub issue describing the expected behaviour, the actual behaviour, and the Bitcoin Core version you are using.
