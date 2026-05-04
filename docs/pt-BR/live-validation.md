# Validacao ao Vivo — CoreCraft

[Versao em ingles](../en-US/live-validation.md)

Esta pagina resume a validacao real executada contra `bitcoind -regtest` com Bitcoin Core v31.0.

## Ambiente

| Campo | Valor |
|-------|-------|
| Data | 2026-05-02 |
| Bitcoin Core | v31.0.0 |
| Rede | `regtest` |
| RPC | `127.0.0.1:18443` |
| ZMQ rawblock | `tcp://127.0.0.1:28332` |
| ZMQ rawtx | `tcp://127.0.0.1:28333` |
| Backends | 8001, 8002, 8003 |

## Checklist

- [x] Bitcoin Core em execucao.
- [x] RPC respondendo.
- [x] ZMQ configurado.
- [x] Wallets criadas e carregadas.
- [x] Atividade 1 validada.
- [x] Atividade 2 validada.
- [x] Atividade 3 validada.
- [x] Ciclo PSBT validado: broadcast, mempool e confirmado.
- [x] Caminho de erro HTTP 503 validado com o no offline.

## Endpoints Validados

| Atividade | Endpoints |
|-----------|-----------|
| 1 | `/api/mempool/summary`, `/api/blockchain/lag` |
| 2 | `/api/events/summary`, `/api/events/latest`, `/api/events/state-comparison` |
| 3 | `/wallets`, `/wallet/select`, `/wallet/status`, `/tx/send`, `/tx/{txid}` |

## Conclusao

Todos os endpoints obrigatorios foram exercitados em uma sessao linear de validacao. A evidencia completa em ingles, incluindo respostas JSON longas capturadas da execucao real, esta em [`../en-US/live-validation.md`](../en-US/live-validation.md).

