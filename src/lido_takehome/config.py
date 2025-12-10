# src/lido_takehome/config.py
import os
from dotenv import load_dotenv
from web3 import Web3

# Load .env once at import time
load_dotenv()

ALCHEMY_MAINNET_URL = os.getenv("ALCHEMY_MAINNET_URL")
LOCAL_FORK_URL = os.getenv("LOCAL_FORK_URL", "http://127.0.0.1:8545")


def get_web3_mainnet() -> Web3:
    """Return a Web3 instance connected to the mainnet RPC."""
    if not ALCHEMY_MAINNET_URL:
        raise RuntimeError(
            "ALCHEMY_MAINNET_URL is not set. "
            "Add it to your .env file."
        )
    w3 = Web3(Web3.HTTPProvider(ALCHEMY_MAINNET_URL))
    if not w3.is_connected():
        raise RuntimeError("Could not connect to mainnet RPC.")
    return w3


def get_web3_local() -> Web3:
    """Return a Web3 instance connected to the local Anvil fork."""
    w3_local = Web3(Web3.HTTPProvider(LOCAL_FORK_URL))
    if not w3_local.is_connected():
        raise RuntimeError(
            f"Could not connect to local fork at {LOCAL_FORK_URL}. "
            "Is anvil running?"
        )
    return w3_local




# Curve USDC/crvUSD pool + tokens (Ethereum mainnet)
CURVE_USDC_CRVUSD_POOL = "0x4dece678ceceb27446b35c672dc7d61f30bad69e"
USDC_ADDRESS           = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
CRVUSD_ADDRESS         = "0xf939e0a03fb07f59a73314e73794be0e57ac1b4e"



# Index of USDC in the USDC/crvUSD pool (coins(0) = USDC, coins(1) = crvUSD)
CURVE_USDC_INDEX = 0

# Address of a wallet that holds USDC/crvUSD LP tokens (to impersonate on the fork)
CURVE_LP_WHALE = "0x9201da0D97CaAAff53f01B2fB56767C7072dE340"