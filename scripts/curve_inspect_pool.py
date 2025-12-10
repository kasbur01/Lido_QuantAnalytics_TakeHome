#!/usr/bin/env python

"""
Quick inspection tool for the Curve USDC/crvUSD pool.

This script connects to the local Anvil mainnet fork and prints:
  - The pool's USDC balance
  - The pool's crvUSD balance

It is intentionally simple and mirrors the functions in `lido_takehome.curve`.
"""

from lido_takehome.config import get_web3_local
from lido_takehome.curve import get_pool_balances


def main() -> None:
    # Connect to local fork (Anvil)
    w3 = get_web3_local()
    print("Connected to local fork:", w3.is_connected())

    # Fetch balances from the pool
    usdc_bal, crvusd_bal = get_pool_balances(w3)

    print("\nCurve USDC/crvUSD Pool Balances:")
    print(f"  USDC:   {usdc_bal:,.2f}")
    print(f"  crvUSD: {crvusd_bal:,.2f}")


if __name__ == "__main__":
    main()