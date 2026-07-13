#!/usr/bin/env bash
# Launch the QuickKick Telegram bot via Hermes gateway.
# Run this script from the hermes-agent directory.
set -euo pipefail
cd "$(dirname "$0")"

# Load .env so the bot token and API key are available
export $(grep -v '^#' .env | grep -v '^\s*$' | xargs)

# Verify an LLM API key is set before starting
if [[ -z "${ANTHROPIC_API_KEY:-}" && -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "ERROR: No LLM API key found in .env"
  echo "  Add ANTHROPIC_API_KEY=sk-ant-api03-... (from console.anthropic.com)"
  echo "  or OPENROUTER_API_KEY=sk-or-... (from openrouter.ai/keys)"
  exit 1
fi

echo "Starting QuickKick bot (@Quickkickbot)..."
python3 -m gateway.run
