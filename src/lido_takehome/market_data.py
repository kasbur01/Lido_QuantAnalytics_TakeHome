# src/lido_takehome/market_data.py
# Ideally we would implement a fallback (csv or other data source like coingecko)

from __future__ import annotations
import pandas as pd
import requests


def fetch_dune_query_results(query_id: int, dune_api_key: str) -> pd.DataFrame:
    """
    Fetch ETH & stETH daily prices from a saved Dune query.

    The query must return columns:
        - date
        - steth_price_usd
        - eth_price_usd
    """
    url = f"https://api.dune.com/api/v1/query/{query_id}/results"
    headers = {"X-Dune-API-Key": dune_api_key}

    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    rows = data["result"]["rows"]

    df = pd.DataFrame(rows)

    required_cols = {"date", "steth_price_usd", "eth_price_usd"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Dune query missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.sort_values("date").reset_index(drop=True)

    return df[["date", "steth_price_usd", "eth_price_usd"]]