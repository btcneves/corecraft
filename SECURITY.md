# Security Policy

## Scope

CoreCraft is a **local development and learning tool** designed to run against a Bitcoin Core node in `regtest` mode. It is not hardened for production use.

## Important warnings

**Do not expose the backends to the internet without precautions.** The APIs have no authentication. Anyone with network access could read mempool data or trigger wallet operations on the connected node.

**Never use these applications against `mainnet` or `testnet` nodes.** The target environment is `regtest` only. Coins in regtest have no real-world value.

**Keep `.env` files out of version control.** RPC credentials are stored in `.env` files, which are excluded via `.gitignore`. Never commit `.env` files.

## External access

If you need to expose a backend externally (e.g., for a demo), use a tunnel with access controls:

- [Cloudflare Tunnel](docs/deploy-cloudflare-tunnel.md) — restrict access by IP or authentication policy
- [VPS deploy](docs/deploy-vps.md) — configure `ufw` to allow only trusted IPs

## Reporting a vulnerability

Open a GitHub issue with the label `security`. For sensitive disclosures, contact the maintainer directly via the email listed in the repository profile.
