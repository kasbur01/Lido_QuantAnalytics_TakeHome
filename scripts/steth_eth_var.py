#!/usr/bin/env python

import os
from pathlib import Path

from dotenv import load_dotenv
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lido_takehome.market_data import fetch_dune_query_results
from lido_takehome.risk import (
    compute_steth_eth_basis,
    compute_14d_change,
    compute_rolling_var,
)


def make_basis_var_figure(df, var_col: str) -> go.Figure:
    """
    Plot
      - stETH/ETH basis (as %, stETH/ETH - 1) on left axis
      - 14d 99% VaR of basis change (720d lookback) on right axis
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Basis (%)
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["basis"] * 100.0,
            name="stETH/ETH basis (%, stETH/ETH - 1)",
            hovertemplate="Date: %{x}<br>Basis: %{y:.3f}%<extra></extra>"
        ),
        secondary_y=True,
    )

    # VaR (% of basis *change*)
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=-df[var_col] * 100.0,  # plot magnitude of left-tail quantile
            name="14d 99% VaR of basis change (%, 720d lookback)",
            hovertemplate="Date: %{x}<br>VaR: %{y:.3f}%<extra></extra>"
        ),
        secondary_y=False,
    )

    fig.update_layout(
        title="stETH/ETH Basis and 14-Day 99% Historical VaR (720-day lookback)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        template="plotly_white",
        xaxis_title="Date",
    )

    fig.update_yaxes(title_text="Basis (%)", secondary_y=True, showgrid=False)
    fig.update_yaxes(title_text="VaR (%)", secondary_y=False)

    return fig


def main() -> None:
    # 0) Load env so we can read API key and query id
    load_dotenv()

    dune_api_key = os.getenv("DUNE_API_KEY")
    if dune_api_key is None:
        raise RuntimeError("DUNE_API_KEY must be set in your .env file.")

    dune_query_id_str = os.getenv("DUNE_QUERY_ID")
    if dune_query_id_str is None:
        raise RuntimeError("DUNE_QUERY_ID must be set in your .env file.")
    try:
        dune_query_id = int(dune_query_id_str)
    except ValueError:
        raise RuntimeError(
            f"DUNE_QUERY_ID in .env must be an integer, got: {dune_query_id_str!r}"
        )

    # 1) Load data from Dune
    df = fetch_dune_query_results(dune_query_id, dune_api_key)
    # df columns: date, steth_price_usd, eth_price_usd

    # 2) Basis: stETH/ETH - 1
    df = compute_steth_eth_basis(
        df,
        steth_col="steth_price_usd",
        eth_col="eth_price_usd",
        as_deviation_from_par=True,
    )

    # 3) 14-day absolute change of the basis
    df = compute_14d_change(
        df,
        col="basis",
        out_col="basis_change_14d",
    )

    # 4) 720-day rolling 99% VaR on 14d basis change (1% left tail)
    var_col = "basis_change_14d_var_720d_1p"
    df = compute_rolling_var(
        df,
        col="basis_change_14d",
        window=720,
        quantile=0.01,
        out_col=var_col,
    )

    # df_plot = df.dropna(subset=[var_col]).copy() -> activate this if we only want to show full data with VaR not being NaN due to lookback window
    df_plot = df.copy()

    # 5) Build figure
    fig = make_basis_var_figure(df_plot, var_col=var_col)

    # 6) Save HTML
    out_dir = Path("charts/publish")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "steth_eth_basis_var.html"
    fig.write_html(out_path)

    # 7) Small printed summary
    latest = df_plot.iloc[-1]
    basis_pct = latest["basis"] * 100.0
    var_pct = -latest[var_col] * 100.0  # magnitude

    print("=== stETH/ETH 14-Day 99% Historical VaR (720d lookback) ===")
    print(f"Latest date:             {latest['date'].date()}")
    print(f"Current basis:           {basis_pct:+.2f}% (stETH vs ETH)")
    print(f"14d 99% VaR (magnitude): {var_pct:.2f}%")
    print()
    print(f"Interactive chart saved to: {out_path.resolve()}")


if __name__ == "__main__":
    main()