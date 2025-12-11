# Lido Take-Home Assignment

This repository contains implementations for on-chain Curve interactions (Part 2) and a historical VaR analysis of the stETH/ETH basis (Part 3). All components are fully reproducible and designed to run without touching mainnet.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Part 2 - Curve USDC/crvUSD Interaction](#part-2---curve-usdccrvusd-interaction)
- [Part 3 - stETH/ETH Basis VaR Analysis](#part-3---stethheth-basis-var-analysis)
- [Project Structure](#project-structure)

## Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- Alchemy API key for mainnet RPC access
- Dune Analytics API key

## Environment Setup

Create your .env file:

cp .env.example .env

Fill in at minimum:

ALCHEMY_MAINNET_URL=YOUR_MAINNET_RPC_URL  
LOCAL_FORK_URL=http://127.0.0.1:8545  

DUNE_API_KEY=your_dune_api_key  
DUNE_QUERY_ID=6324708  

Dune query used for price data:  
https://dune.com/queries/6324708

---

# Part 2 — Curve USDC/crvUSD Interaction

This part implements on-chain interactions with the Curve USDC/crvUSD pool using a local Anvil mainnet fork. This enables:

- account impersonation  
- simulated withdrawals  
- reproducible state-changing calls  
- safe experimentation without touching mainnet

### Implementation Locations
- `src/lido_takehome/curve.py`
- `notebooks/Part2_curve.ipynb`
- CLI scripts in `scripts/`

---

## Running the Local Fork (Anvil)

### Terminal 1 — start the fork

source .env  
anvil --fork-url "$ALCHEMY_MAINNET_URL"  

Keep this terminal open.

### Terminal 2 — run scripts

source .venv/bin/activate  
python -m scripts.curve_withdraw_usdc  

Or use the Jupyter notebook.

---

## ABI Requirements

All ABI files are stored in `abi/`:

abi/
curve_usdc_crvusd_pool.json
erc20.json

### Curve pool ABI (implementation ABI required)
Proxy: https://etherscan.io/address/0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E  
Implementation (copy ABI from here):  
https://etherscan.io/address/0x67fe41a94e779ccfa22cff02cc2957dc9c0e4286

Save to:

abi/curve_usdc_crvusd_pool.json

### ERC20 ABI (USDC, crvUSD, LP token)
Use ABI from USDC implementation:  
https://etherscan.io/address/0x43506849d7c04f9138d1a2050bbf3a0c054402dd

Save to:

abi/erc20.json

---

## Included CLI Scripts

### scripts/curve_inspect_pool.py
Connects to the fork, loads the Curve pool, prints balances.

Run:

python -m scripts.curve_inspect_pool

### scripts/curve_withdraw_usdc.py
Main simulation script:

- impersonates LP whale  
- burns LP tokens  
- withdraws USDC via remove_liquidity_one_coin  
- prints amount withdrawn  

Run:

python -m scripts.curve_withdraw_usdc

Underlying logic is in `src/lido_takehome/curve.py`.

---

# Part 3 — stETH/ETH Basis 14-Day 99% VaR (720-Day Lookback)

This part computes and visualizes the 14-day historical 99% Value-at-Risk (VaR) of the stETH/ETH basis using a 720-day rolling window.

### Implementation Files
- `src/lido_takehome/market_data.py`
- `src/lido_takehome/risk.py`
- `scripts/steth_eth_var.py`
- `notebooks/part3_var_steth_eth.ipynb`

---

## Data Source (Dune)

Daily median USD prices for ETH and stETH are loaded from:

https://dune.com/queries/6324708

Your `.env` must include:

DUNE_API_KEY=your_api_key  
DUNE_QUERY_ID=6324708

---

# Running Part 3

## Option A — Run the CLI Script (recommended)

### 1. Activate the virtual environment

source .venv/bin/activate

### 2. Run the VaR generator

python -m scripts.steth_eth_var

This will:

1. Load ETH & stETH prices from Dune  
2. Compute basis = stETH/ETH − 1  
3. Compute 14-day absolute basis changes  
4. Compute 720-day rolling 99% VaR  
5. Save interactive Plotly chart to:

charts/steth_eth_basis_var.html

Example console output:

=== stETH/ETH 14-Day 99% Historical VaR (720d lookback) ===  
Latest date:             YYYY-MM-DD  
Current basis:           +X.XX%  
14d 99% VaR (magnitude): Y.YY%  
Interactive chart saved to: charts/steth_eth_basis_var.html  

---

## Option B — Explore in Jupyter Notebook

Open:

notebooks/part3_var_steth_eth.ipynb

The notebook includes:

- ETH/stETH price diagnostics  
- comparison of pct_change vs diff  
- reasoning for using absolute 14-day changes  
- full VaR computation  
- final interactive visualization  
- brief interpretation  

---

## Notes on the Visualization

- VaR is shown on the primary axis (main output).  
- Basis is shown on a secondary axis for context.  
- Full basis history is plotted even when VaR is initially undefined.  
- This explains why VaR collapses when crisis-era data roll out of the lookback window.  
- Tooltips are rounded for readability.  

---

## Project Structure

Lido_QuantAnalytics_TakeHome/
│
├── abi/
│   ├── curve_usdc_crvusd_pool.json
│   └── erc20.json
│
├── notebooks/
│   ├── Part2_curve.ipynb
│   └── part3_var_steth_eth.ipynb
│
├── scripts/
│   ├── curve_inspect_pool.py
│   ├── curve_withdraw_usdc.py
│   └── steth_eth_var.py
│
├── src/
│   └── lido_takehome/
│       ├── curve.py
│       ├── market_data.py
│       ├── risk.py
│       └── init.py
│
├── charts/               # generated output
├── .env.example
├── README.md
└── requirements.txt
