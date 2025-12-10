
from __future__ import annotations

import pandas as pd

def compute_steth_eth_basis(
    df: pd.DataFrame,
    steth_col: str = "steth_price_usd",
    eth_col: str = "eth_price_usd",
    as_deviation_from_par: bool = True,
) -> pd.DataFrame:
    """
    Compute the stETH/ETH basis.

    Two common definitions:
      - ratio:               basis = steth / eth
      - deviation from par:  basis = steth / eth - 1

    This function adds:
        basis
    to the DataFrame and returns a copy.
    """
    df = df.copy()

    ratio = df[steth_col] / df[eth_col]
    if as_deviation_from_par:
        df["basis"] = ratio - 1.0  # e.g. +0.01 => +1% vs ETH
    else:
        df["basis"] = ratio

    return df


# src/lido_takehome/risk.py


def compute_14d_change(
    df: pd.DataFrame,
    col: str,
    out_col: str = "change_14d",
) -> pd.DataFrame:
    """
    Add a 14-day absolute change column based on `col`.

    This is appropriate for quantities that are already relative
    (e.g. a basis defined as stETH/ETH - 1), where a further
    pct_change would be misleading.

    Returns a copy of `df` with the new column `out_col`.
    """
    df = df.copy()

    if "date" in df.columns:
        df = df.sort_values("date")

    df[out_col] = df[col].diff(14)
    return df


def compute_rolling_var(
    df: pd.DataFrame,
    col: str,
    window: int = 60,
    quantile: float = 0.01,
    out_col: str | None = None,
) -> pd.DataFrame:
    """
    Add a rolling historical VaR column based on `col`.

    Parameters
    ----------
    df : DataFrame with a time index or 'date' column, sorted ascending.
    col : column to compute VaR on (e.g. a return or basis series).
    window : rolling window length in days.
    quantile : VaR quantile (0.01 -> 1% left tail).
    out_col : optional name of the output column; if None, auto-generates.

    Returns
    -------
    DataFrame (copy) with an additional VaR column.
    """
    df = df.copy()

    if "date" in df.columns:
        df = df.sort_values("date")

    if out_col is None:
        # e.g. var_60d_1p
        q_pct = int(quantile * 100)
        out_col = f"var_{window}d_{q_pct}p"

    df[out_col] = df[col].rolling(window=window, min_periods=window).quantile(quantile)
    return df