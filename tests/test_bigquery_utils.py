import importlib
import json
import sys
import types


def load_bigquery_utils(monkeypatch, service_account=""):
    env = {
        "API_KEY": "x",
        "API_SECRET": "y",
        "BASE_URL": "http://example.com",
        "WANDB_API_KEY": "z",
        "MONGO_URL": "mongodb://example",
        "BQ_DATASET": "ds",
        "BQ_TABLE": "tbl",
        "BQ_SERVICE_ACCOUNT": service_account,
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)

    bigquery_mod = types.ModuleType("google.cloud.bigquery")
    service_account_mod = types.ModuleType("google.oauth2.service_account")

    class DummyCreds:
        @classmethod
        def from_service_account_file(cls, path, **kwargs):
            return cls()

        @classmethod
        def from_service_account_info(
            cls, info, **kwargs
        ):  # pragma: no cover - used indirectly
            return cls()

    service_account_mod.Credentials = DummyCreds

    google_mod = types.ModuleType("google")
    cloud_mod = types.ModuleType("cloud")
    oauth_mod = types.ModuleType("oauth2")

    google_mod.cloud = cloud_mod
    google_mod.oauth2 = oauth_mod
    cloud_mod.bigquery = bigquery_mod
    oauth_mod.service_account = service_account_mod

    # stub dotenv.load_dotenv used by config
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
    import utilities.bigquery_utils as bqu

    importlib.reload(bqu)
    return bqu


def make_client(rows=None, error=False):
    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def query(self, query):
            if error:
                raise RuntimeError("boom")

            class Job:
                def result(self_inner):
                    return rows or []

            return Job()

    return FakeClient


def test_fetch_latest_prices_success(monkeypatch):
    bq = load_bigquery_utils(monkeypatch)
    rows = [{"ticker": "AAPL", "price": 123.45}, {"ticker": "MSFT", "price": 54.32}]
    monkeypatch.setattr(bq.bigquery, "Client", make_client(rows), raising=False)

    prices = bq.fetch_latest_prices_bq()

    assert prices == {"AAPL": 123.45, "MSFT": 54.32}


def test_fetch_latest_prices_ignores_empty_rows(monkeypatch):
    bq = load_bigquery_utils(monkeypatch)
    rows = [
        {"ticker": "AAPL", "price": 123.45},
        {"ticker": None, "price": None},
    ]
    monkeypatch.setattr(bq.bigquery, "Client", make_client(rows), raising=False)

    prices = bq.fetch_latest_prices_bq()

    assert prices == {"AAPL": 123.45}


def test_fetch_latest_prices_failure_uses_cache(monkeypatch):
    bq = load_bigquery_utils(monkeypatch)
    rows = [{"ticker": "GOOG", "price": 99.9}]
    monkeypatch.setattr(bq.bigquery, "Client", make_client(rows), raising=False)

    first = bq.fetch_latest_prices_bq()
    assert first == {"GOOG": 99.9}

    monkeypatch.setattr(bq.bigquery, "Client", make_client(error=True), raising=False)
    second = bq.fetch_latest_prices_bq()

    assert second == first


def test_fetch_latest_prices_cache_ttl(monkeypatch):
    bq = load_bigquery_utils(monkeypatch)
    rows = [{"ticker": "IBM", "price": 10.0}]
    call_count = {"count": 0}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def query(self, query):
            call_count["count"] += 1

            class Job:
                def result(self_inner):
                    return rows

            return Job()

    monkeypatch.setattr(bq.bigquery, "Client", FakeClient, raising=False)
    current_time = [1000.0]
    monkeypatch.setattr(bq.time, "time", lambda: current_time[0], raising=False)

    first = bq.fetch_latest_prices_bq()
    assert call_count["count"] == 1

    second = bq.fetch_latest_prices_bq()
    assert call_count["count"] == 1
    assert second == first

    current_time[0] += 61
    third = bq.fetch_latest_prices_bq()
    assert call_count["count"] == 2
    assert third == first


def test_json_service_account(monkeypatch):
    data = {"key": "value"}
    bq = load_bigquery_utils(monkeypatch, json.dumps(data))

    captured = {}

    def fake_from_info(info, scopes=None):
        captured["info"] = info
        captured["scopes"] = scopes
        return bq.service_account.Credentials()

    monkeypatch.setattr(
        bq.service_account.Credentials,
        "from_service_account_info",
        fake_from_info,
    )
    monkeypatch.setattr(bq.bigquery, "Client", make_client([]), raising=False)

    bq.fetch_latest_prices_bq()

    assert captured["info"] == data
    assert captured["scopes"] == bq._SCOPES
