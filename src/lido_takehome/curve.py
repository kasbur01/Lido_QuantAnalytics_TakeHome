"""
Helpers for interacting with the Curve USDC/crvUSD pool on an Anvil mainnet fork.

Includes:
- ABI loading
- Pool and token helpers
- LP whale impersonation
- Single-sided USDC withdrawal via remove_liquidity_one_coin
"""


import json
from pathlib import Path
from typing import List, Tuple

from web3 import Web3
from web3.types import TxParams

from .config import (
    CURVE_USDC_CRVUSD_POOL,
    USDC_ADDRESS,
    CRVUSD_ADDRESS,
    CURVE_USDC_INDEX,
    CURVE_LP_WHALE,
)


# Base directory of the project (two levels up from this file)
ROOT_DIR = Path(__file__).resolve().parents[2]
ABI_DIR = ROOT_DIR / "abi"


def load_abi(filename: str) -> list:
    """Load a JSON ABI from the abi/ folder."""
    path = ABI_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"ABI file not found: {path}")
    with open(path, "r") as f:
        return json.load(f)


def get_pool_contract(w3: Web3):
    """Return a web3 contract instance for the Curve USDC/crvUSD pool."""
    abi = load_abi("curve_usdc_crvusd_pool.json")
    addr = Web3.to_checksum_address(CURVE_USDC_CRVUSD_POOL)
    return w3.eth.contract(address=addr, abi=abi)


def get_erc20_contract(w3: Web3, token_address: str):
    """Return a generic ERC20 contract instance."""
    abi = load_abi("erc20.json")
    addr = Web3.to_checksum_address(token_address)
    return w3.eth.contract(address=addr, abi=abi)


def get_pool_coins(w3: Web3) -> List[str]:
    """
    Return the two underlying token addresses of the pool.
    For a plain 2-coin Curve pool, indices are 0 and 1.
    """
    pool = get_pool_contract(w3)
    c0 = pool.functions.coins(0).call()
    c1 = pool.functions.coins(1).call()
    return [c0, c1]


def get_pool_balances(w3: Web3) -> Tuple[float, float]:
    """
    Return (USDC_balance, crvUSD_balance) in human-readable units.
    We detect which index is which by looking at coins().
    """
    pool = get_pool_contract(w3)

    # Get decimals from ERC20 contracts
    usdc = get_erc20_contract(w3, USDC_ADDRESS)
    crvusd = get_erc20_contract(w3, CRVUSD_ADDRESS)
    usdc_dec = usdc.functions.decimals().call()
    crvusd_dec = crvusd.functions.decimals().call()

    # Raw balances in smallest units
    b0 = pool.functions.balances(0).call()
    b1 = pool.functions.balances(1).call()

    # Figure out which index is USDC vs crvUSD
    coins = get_pool_coins(w3)
    if coins[0].lower() == USDC_ADDRESS.lower():
        usdc_raw, crvusd_raw = b0, b1
    else:
        usdc_raw, crvusd_raw = b1, b0

    usdc_bal = usdc_raw / (10 ** usdc_dec)
    crvusd_bal = crvusd_raw / (10 ** crvusd_dec)
    return usdc_bal, crvusd_bal




def get_lp_token_contract(w3: Web3):
    pool = get_pool_contract(w3)
    try:
        lp_addr = pool.functions.token().call()
    except Exception:
        # Fallback: pool address itself (for pools where LP == pool)
        lp_addr = CURVE_USDC_CRVUSD_POOL
    return get_erc20_contract(w3, lp_addr)


def get_lp_balance(w3: Web3, holder: str) -> int:
    """Return raw LP token balance (smallest units) for a given holder."""
    lp = get_lp_token_contract(w3)
    holder_cs = Web3.to_checksum_address(holder)
    return lp.functions.balanceOf(holder_cs).call()


def impersonate(w3: Web3, addr: str) -> None:
    """Ask Anvil to impersonate `addr` so we can send txs from it."""
    w3.provider.make_request("anvil_impersonateAccount",
                             [Web3.to_checksum_address(addr)])


def stop_impersonate(w3: Web3, addr: str) -> None:
    w3.provider.make_request("anvil_stopImpersonatingAccount",
                             [Web3.to_checksum_address(addr)])

def fund_for_gas(w3: Web3, addr: str, eth_amount: float = 5.0) -> None:
    """
    On an Anvil fork, give `addr` some ETH so it can pay gas.
    This does NOT touch mainnet; it only mutates the local fork.
    """
    checksummed = Web3.to_checksum_address(addr)
    wei_amount = w3.to_wei(eth_amount, "ether")
    w3.provider.make_request(
        "anvil_setBalance",
        [checksummed, hex(wei_amount)],
    )


def withdraw_usdc_single_sided(
    w3: Web3,
    lp_holder: str,
    fraction_of_balance: float = 0.1,
    slippage_bps: int = 50,
) -> tuple[float, float, float]:
    """
    Withdraw single-sided USDC from the Curve USDC/crvUSD pool on a local fork.

    - Impersonates `lp_holder`
    - Burns `fraction_of_balance` of their LP tokens
    - Calls `remove_liquidity_one_coin` targeting USDC
    - Returns (lp_amount_used, usdc_before, usdc_after) in human-readable units
    """
    pool = get_pool_contract(w3)
    usdc = get_erc20_contract(w3, USDC_ADDRESS)
    lp = get_lp_token_contract(w3)

    holder = Web3.to_checksum_address(lp_holder)

    # Decimals
    usdc_dec = usdc.functions.decimals().call()
    lp_dec = lp.functions.decimals().call()

    # LP balance and amount to burn
    lp_balance = lp.functions.balanceOf(holder).call()
    if lp_balance == 0:
        raise RuntimeError(f"Holder {holder} has zero LP balance")

    lp_amount = int(lp_balance * fraction_of_balance)

    # Expected USDC out (for min_amount)
    expected_usdc_raw = pool.functions.calc_withdraw_one_coin(
        lp_amount,
        CURVE_USDC_INDEX,
    ).call()

    min_usdc_raw = int(expected_usdc_raw * (1 - slippage_bps / 10_000))

    # USDC balance before
    usdc_before_raw = usdc.functions.balanceOf(holder).call()

    # Impersonate holder on local fork
    impersonate(w3, holder)

    try:
        # Make sure the holder has enough ETH to pay gas on the fork
        fund_for_gas(w3, holder, eth_amount=5.0)

        tx: TxParams = {
            "from": holder,
            "gas": 1_000_000,
        }

        tx_hash = pool.functions.remove_liquidity_one_coin(
            lp_amount,
            CURVE_USDC_INDEX,
            min_usdc_raw,
        ).transact(tx)

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status != 1:
            raise RuntimeError("remove_liquidity_one_coin tx failed")
    finally:
        stop_impersonate(w3, holder)

    # USDC balance after
    usdc_after_raw = usdc.functions.balanceOf(holder).call()

    # Convert to human-readable
    lp_used = lp_amount / (10 ** lp_dec)
    usdc_before = usdc_before_raw / (10 ** usdc_dec)
    usdc_after = usdc_after_raw / (10 ** usdc_dec)

    return lp_used, usdc_before, usdc_after