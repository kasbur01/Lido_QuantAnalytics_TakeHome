Lido Take-Home Assignment — README

This repository contains implementations for on-chain Curve interactions (Part 2) and a historical VaR analysis of the stETH/ETH basis (Part 3).
All components are fully reproducible and designed to run without touching mainnet.

⸻

🛠️ Environment Setup

Create your .env file:

cp .env.example .env

Fill in at minimum:

ALCHEMY_MAINNET_URL=YOUR_MAINNET_RPC_URL
LOCAL_FORK_URL=http://127.0.0.1:8545

DUNE_API_KEY=your_dune_api_key
DUNE_QUERY_ID=6324708

The Dune query used in this project:
🔗 https://dune.com/queries/6324708

⸻

Part 2 — Curve USDC/crvUSD Interaction

This part implements on-chain interactions with the Curve USDC/crvUSD pool using a local Anvil mainnet fork, enabling:
	•	account impersonation
	•	simulated withdrawals
	•	reproducible state-changing calls
	•	safe experimentation without touching mainnet

Location of implementation
	•	src/lido_takehome/curve.py — core logic
	•	notebooks/Part2_curve.ipynb — exploratory walkthrough
	•	Scripts in scripts/ provide CLI tooling (see below)

⸻

▶️ Running the Local Fork (Anvil)

Terminal 1 — start fork

source .env
anvil --fork-url "$ALCHEMY_MAINNET_URL"

Keep this terminal open.

Terminal 2 — run scripts

source .venv/bin/activate
python -m scripts.curve_withdraw_usdc

Or use the notebook for interactive inspection.

⸻

📁 ABI Requirements

All ABIs are stored locally for reproducibility.

abi/
  curve_usdc_crvusd_pool.json
  erc20.json

1. Curve USDC/crvUSD Pool ABI

Proxy (user-facing):
https://etherscan.io/address/0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E

Implementation (copy ABI from here):
https://etherscan.io/address/0x67fe41a94e779ccfa22cff02cc2957dc9c0e4286

Save to:

abi/curve_usdc_crvusd_pool.json

2. ERC-20 ABI (USDC, crvUSD, LP token)

USDC implementation (use this ABI):
https://etherscan.io/address/0x43506849d7c04f9138d1a2050bbf3a0c054402dd

Save to:

abi/erc20.json

This single ERC-20 ABI works for:
	•	USDC
	•	crvUSD
	•	LP token

⸻

🗂️ Included CLI Scripts

▶️ scripts/curve_inspect_pool.py

Sanity-check tool:
	•	connects to local fork
	•	loads Curve pool
	•	prints USDC + crvUSD balances

Run:

python -m scripts.curve_inspect_pool

Confirms:
	•	fork is running
	•	ABIs load correctly
	•	contracts respond as expected

⸻

▶️ scripts/curve_withdraw_usdc.py

Main simulation script:
	•	impersonates a real LP whale
	•	burns a fraction of LP tokens
	•	calls remove_liquidity_one_coin to withdraw USDC
	•	prints the withdrawal results

Run:

python -m scripts.curve_withdraw_usdc

What the script demonstrates
	1.	Connects to Anvil mainnet fork
	2.	Loads Curve pool
	3.	Reads balances
	4.	Impersonates LP whale
	5.	Performs single-sided USDC withdrawal
	6.	Prints:

LP tokens burned
USDC before
USDC after
USDC received

Underlying logic resides in:

src/lido_takehome/curve.py


⸻
⸻

📉 Part 3 — stETH/ETH Basis 14-Day 99% VaR (720-Day Lookback)

This part computes and visualizes the historical 99% Value-at-Risk (VaR) of the
14-day change in the stETH/ETH basis, using a 720-day rolling window.

The implementation lives in:
	•	src/lido_takehome/market_data.py — Dune API loader for ETH & stETH prices
	•	src/lido_takehome/risk.py — basis calculation, 14-day changes, rolling VaR
	•	scripts/steth_eth_var.py — CLI script generating the final HTML chart
	•	notebooks/part3_var_steth_eth.ipynb — detailed, documented notebook walkthrough

⸻

🔗 Data Source (Dune)

We fetch daily median USD prices for ETH and stETH using the query:

https://dune.com/queries/6324708

Your .env file must contain:

DUNE_API_KEY=your_api_key
DUNE_QUERY_ID=6324708

The project includes a lightweight Dune wrapper that handles:
	•	authenticated API access
	•	result pagination
	•	conversion into a tidy, date-indexed DataFrame

⸻

▶️ Running Part 3

Option A — Run the reproducible script (recommended)

This produces the final interactive Plotly chart submitted for the assignment.

1. Activate the virtual environment

source .venv/bin/activate

2. Run the VaR computation + chart generator

python -m scripts.steth_eth_var

This will:
	1.	Load ETH & stETH prices from Dune
	2.	Compute the basis: basis = stETH/ETH − 1
	3.	Compute 14-day absolute basis changes
	4.	Compute the 720-day rolling 99% historical VaR
	5.	Write the interactive chart to:

charts/steth_eth_basis_var.html

At the end a summary is printed:

=== stETH/ETH 14-Day 99% Historical VaR (720d lookback) ===
Latest date:             YYYY-MM-DD
Current basis:           +X.XX%
14d 99% VaR (magnitude): Y.YY%
Interactive chart saved to: charts/steth_eth_basis_var.html


⸻

Option B — Explore interactively in Jupyter Notebook

Open:

notebooks/part3_var_steth_eth.ipynb

The notebook includes:
	•	raw ETH/stETH price diagnostics
	•	comparison of percentage vs absolute basis changes
	•	argumentation for using absolute changes
	•	step-by-step calculation of basis, returns, and VaR
	•	the final interactive Plotly visualization
	•	a short commentary interpreting the VaR behavior

⸻

📝 Notes on the Visualization
	•	VaR is plotted on the primary axis (it is the main output of Part 3).
	•	The basis is plotted on a secondary axis for context.
	•	The chart shows the full basis history, even where VaR is initially undefined,
which clarifies why VaR drops sharply once crisis-period observations fall out of the 720-day window.
	•	Tooltips are rounded for readability, and the chart is fully interactive and shareable.

⸻