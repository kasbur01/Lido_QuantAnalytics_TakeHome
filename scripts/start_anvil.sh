#!/usr/bin/env bash
set -e

echo "--------------------------------------------"
echo "        Starting Local Anvil Fork"
echo "--------------------------------------------"

#
# 1) Load .env variables if present
#
if [ -f ".env" ]; then
  echo "Loading environment variables from .env ..."
  set -a
  source .env
  set +a
else
  echo "Warning: .env file not found in current directory."
fi

#
# 2) Check that Anvil is installed
#
if ! command -v anvil &> /dev/null; then
  echo "Error: 'anvil' not found."
  echo "Install Foundry: https://book.getfoundry.sh/getting-started/installation"
  exit 1
fi

#
# 3) Check RPC URL
#
if [ -z "$ALCHEMY_MAINNET_URL" ]; then
  echo "Error: ALCHEMY_MAINNET_URL is not set."
  echo "Please add it to your .env file:"
  echo "  ALCHEMY_MAINNET_URL=https://eth-mainnet.g.alchemy.com/v2/XXXX"
  exit 1
fi

#
# 4) Start Anvil fork
#
echo "Starting anvil fork against:"
echo "  $ALCHEMY_MAINNET_URL"
echo ""
echo "Press Ctrl+C to stop the fork."
echo ""

anvil --fork-url "$ALCHEMY_MAINNET_URL"