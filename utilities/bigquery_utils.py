import logging
from typing import Dict

from google.cloud import bigquery
from google.oauth2 import service_account

from config import BQ_DATASET, BQ_SERVICE_ACCOUNT, BQ_TABLE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

_cached_prices: Dict[str, float] = {}


def fetch_latest_prices_bq() -> Dict[str, float]:
    """Fetch the latest prices from BigQuery.

    Returns cached results if any error occurs.
    """
    global _cached_prices

    try:
        if BQ_SERVICE_ACCOUNT:
            creds = service_account.Credentials.from_service_account_file(
                BQ_SERVICE_ACCOUNT
            )
            client = bigquery.Client(credentials=creds)
        else:
            client = bigquery.Client()

        query = f"SELECT ticker, price FROM `{BQ_DATASET}.{BQ_TABLE}`"
        results = client.query(query).result()

        prices = {row["ticker"]: float(row["price"]) for row in results}
        _cached_prices = prices
        return prices

    except Exception as exc:  # pragma: no cover - network-dependent
        logger.error(f"Error fetching prices from BigQuery: {exc}")
        return _cached_prices
