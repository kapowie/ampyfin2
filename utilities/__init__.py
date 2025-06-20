def fetch_latest_prices_bq():
    """Lazy wrapper for :func:`bigquery_utils.fetch_latest_prices_bq`."""
    from .bigquery_utils import fetch_latest_prices_bq as _fetch

    return _fetch()


__all__ = ["fetch_latest_prices_bq"]
