import json
import logging
import os
import time
from typing import Dict, Optional

from google.cloud import bigquery
from google.oauth2 import service_account

from config import BQ_DATASET, BQ_SERVICE_ACCOUNT, BQ_TABLE

__all__ = ["fetch_latest_prices_bq", "get_latest_price_bq"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

_cached_prices: Dict[str, float] = {}
_cache_timestamp: float = 0.0
_CACHE_TTL_SECONDS = 60

# scopes required for BigQuery and Drive access
_SCOPES = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/drive",
]


def _load_credentials() -> Optional[service_account.Credentials]:
    """Return Credentials from BQ_SERVICE_ACCOUNT if provided."""
    if not BQ_SERVICE_ACCOUNT:
        return None

    if os.path.isfile(BQ_SERVICE_ACCOUNT):
        return service_account.Credentials.from_service_account_file(
            BQ_SERVICE_ACCOUNT,
            scopes=_SCOPES,
        )

    try:
        info = json.loads(BQ_SERVICE_ACCOUNT)
    except Exception as exc:  # pragma: no cover - invalid json
        logger.error(f"Invalid BQ_SERVICE_ACCOUNT: {exc}")
        return None

    return service_account.Credentials.from_service_account_info(info, scopes=_SCOPES)


def fetch_latest_prices_bq() -> Dict[str, float]:
    """Fetch the latest prices from BigQuery.

    Returns cached results if any error occurs. Results are cached for
    ``_CACHE_TTL_SECONDS`` to limit BigQuery requests.
    """
    global _cached_prices, _cache_timestamp

    if _cached_prices and time.time() - _cache_timestamp < _CACHE_TTL_SECONDS:
        return _cached_prices

    try:
        creds = _load_credentials()
        if creds:
            client = bigquery.Client(credentials=creds)
        else:
            client = bigquery.Client()

        query = f"SELECT ticker, price FROM `{BQ_DATASET}.{BQ_TABLE}` limit 120"
        results = client.query(query).result()

        prices: Dict[str, float] = {}
        for row in results:
            ticker = row.get("ticker")
            price = row.get("price")
            if ticker is None or price is None:
                continue
            prices[ticker] = float(price)
        _cached_prices = prices
        _cache_timestamp = time.time()
        return prices

    except Exception as exc:  # pragma: no cover - network-dependent
        logger.error(f"Error fetching prices from BigQuery: {exc}")
        return _cached_prices


def get_latest_price_bq(ticker: str) -> Optional[float]:
    """Return the latest price for ``ticker`` using BigQuery cache."""
    prices = fetch_latest_prices_bq()
    return prices.get(ticker)
