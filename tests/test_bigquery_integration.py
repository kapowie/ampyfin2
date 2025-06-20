import importlib
import os
import sys

import pytest


def load_real_bigquery_utils(monkeypatch):
    # ensure required variables for config
    defaults = {
        "API_KEY": "x",
        "API_SECRET": "y",
        "BASE_URL": "http://example.com",
        "WANDB_API_KEY": "z",
        "MONGO_URL": "mongodb://example",
    }
    for k, v in defaults.items():
        monkeypatch.setenv(k, v)
    sys.modules.pop("config", None)
    sys.modules.pop("utilities.bigquery_utils", None)
    import utilities.bigquery_utils as bq

    importlib.reload(bq)
    return bq


@pytest.mark.integration
def test_fetch_latest_prices_real(monkeypatch):
    if not (
        os.getenv("BQ_DATASET")
        and os.getenv("BQ_TABLE")
        and os.getenv("BQ_SERVICE_ACCOUNT")
    ):
        pytest.skip("BigQuery environment not configured")

    bq = load_real_bigquery_utils(monkeypatch)

    prices = bq.fetch_latest_prices_bq()
    assert isinstance(prices, dict)
    assert prices  # should contain at least one ticker price
