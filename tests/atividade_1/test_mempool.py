import pytest

from tests.conftest import FakeRPC, import_activity_module


def test_mempool_summary_classifies_fee_rates(monkeypatch: pytest.MonkeyPatch) -> None:
    mempool = import_activity_module("atividade-1", "app.mempool", monkeypatch)
    rpc = FakeRPC(
        {
            "getmempoolinfo": {"size": 3, "bytes": 400},
            "getrawmempool": {
                "low": {"fees": {"base": 0.000001}, "vsize": 20},
                "medium": {"fees": {"base": 0.00001}, "vsize": 50},
                "high": {"fees": {"base": 0.0001}, "vsize": 100},
            },
        }
    )

    result = mempool.summary(rpc)

    assert result["tx_count"] == 3
    assert result["total_vsize"] == 400
    assert result["fee_distribution"] == {"low": 1, "medium": 1, "high": 1}
    assert result["min_fee_rate"] == 5.0
    assert result["max_fee_rate"] == 100.0


def test_blockchain_lag(monkeypatch: pytest.MonkeyPatch) -> None:
    mempool = import_activity_module("atividade-1", "app.mempool", monkeypatch)
    rpc = FakeRPC({"getblockchaininfo": {"blocks": 10, "headers": 12}})

    assert mempool.lag(rpc) == {"blocks": 10, "headers": 12, "lag": 2}
