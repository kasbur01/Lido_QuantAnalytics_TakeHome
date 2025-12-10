#!/usr/bin/env python
"""
Script: curve_withdraw_usdc.py

Purpose:
    Demonstrates a single-sided USDC withdrawal from the Curve USDC/crvUSD
    pool on a local Anvil mainnet fork.

    This script:
        • Connects to the local fork (Anvil)
        • Reads pool balances (USDC & crvUSD)
        • Checks the LP balance of a known LP whale
        • Impersonates the whale on the fork
        • Burns a fraction of their LP tokens
        • Calls remove_liquidity_one_coin() to withdraw USDC
        • Prints before/after balances and the USDC received

Usage:
    # Start Anvil fork in another terminal:
    anvil --fork-url "$ALCHEMY_MAINNET_URL"

    # Then run this script:
    python -m scripts.curve_withdraw_usdc

Notes:
    - This script is intended for demonstration and testing only.
    - All real transaction logic lives in `lido_takehome.curve`.
"""

from lido_takehome.config import get_web3_local, CURVE_LP_WHALE
from lido_takehome.curve import (
    get_pool_balances,
    get_lp_balance,
    withdraw_usdc_single_sided,
)


def main() -> None:
    """Run a USDC single-sided withdrawal simulation on the local fork."""
    # Connect to local Anvil fork
    w3 = get_web3_local()
    print("Connected to local fork:", w3.is_connected())

    # Show current pool balances
    usdc_bal, crvusd_bal = get_pool_balances(w3)
    print(f"Pool balances  →  USDC: {usdc_bal:,.2f}   crvUSD: {crvusd_bal:,.2f}")

    # Check LP whale
    print("\nLP whale:", CURVE_LP_WHALE)
    lp_balance_raw = get_lp_balance(w3, CURVE_LP_WHALE)
    print("LP balance (raw smallest units):", lp_balance_raw)

    # Perform withdrawal
    lp_used, usdc_before, usdc_after = withdraw_usdc_single_sided(
        w3,
        CURVE_LP_WHALE,
        fraction_of_balance=0.05,   # burn 5% of LP
        slippage_bps=50,            # allow 0.50% slippage
    )

    # Summarize results
    print("\nWithdrew single-sided USDC from Curve pool:")
    print(f"  LP burned:        {lp_used:,.6f}")
    print(f"  USDC before:      {usdc_before:,.2f}")
    print(f"  USDC after:       {usdc_after:,.2f}")
    print(f"  USDC received:    {usdc_after - usdc_before:,.2f}")


if __name__ == "__main__":
    main()