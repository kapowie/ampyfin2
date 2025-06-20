import importlib
import sys
import types

import pandas as pd


def load_utils(monkeypatch, use_bq):
    env = {
        "API_KEY": "x",
        "API_SECRET": "y",
        "BASE_URL": "http://example.com",
        "WANDB_API_KEY": "z",
        "MONGO_URL": "mongodb://example",
        "BQ_DATASET": "ds",
        "BQ_TABLE": "tbl",
        "BQ_SERVICE_ACCOUNT": "",
        "USE_BIGQUERY_PRICES": "true" if use_bq else "false",
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)

    bigquery_mod = types.ModuleType("google.cloud.bigquery")
    service_account_mod = types.ModuleType("google.oauth2.service_account")

    class DummyCreds:
        @classmethod
        def from_service_account_file(cls, path):
            return cls()

    service_account_mod.Credentials = DummyCreds

    google_mod = types.ModuleType("google")
    cloud_mod = types.ModuleType("cloud")
    oauth_mod = types.ModuleType("oauth2")

    google_mod.cloud = cloud_mod
    google_mod.oauth2 = oauth_mod
    cloud_mod.bigquery = bigquery_mod
    oauth_mod.service_account = service_account_mod

    dotenv_mod = types.ModuleType("dotenv")
    dotenv_mod.load_dotenv = lambda override=True: None
    sys.modules["dotenv"] = dotenv_mod

    sys.modules["google"] = google_mod
    sys.modules["google.cloud"] = cloud_mod
    sys.modules["google.cloud.bigquery"] = bigquery_mod
    sys.modules["google.oauth2"] = oauth_mod
    sys.modules["google.oauth2.service_account"] = service_account_mod

    sys.modules.pop("config", None)
    sys.modules.pop("utilities.bigquery_utils", None)
    sys.modules.pop("utilities.ranking_trading_utils", None)
    import utilities.ranking_trading_utils as rtu

    importlib.reload(rtu)
    return rtu


def test_get_latest_price_uses_yfinance(monkeypatch):
    rtu = load_utils(monkeypatch, use_bq=False)

    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol

        def history(self):
            return pd.DataFrame({"Close": [12.34]})

    monkeypatch.setattr(rtu.yf, "Ticker", FakeTicker)
    monkeypatch.setattr(
        rtu, "fetch_latest_prices_bq", lambda: (_ for _ in ()).throw(AssertionError())
    )

    assert rtu.get_latest_price("AAPL") == 12.34


def test_get_latest_price_uses_bigquery(monkeypatch):
    rtu = load_utils(monkeypatch, use_bq=True)

    monkeypatch.setattr(rtu, "fetch_latest_prices_bq", lambda: {"AAPL": 55.0})
    monkeypatch.setattr(
        rtu.yf, "Ticker", lambda *a, **k: (_ for _ in ()).throw(AssertionError())
    )

    assert rtu.get_latest_price("AAPL") == 55.0
