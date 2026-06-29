#!/bin/bash
# QuickKick gateway auto-start hook
# Fires on every SessionStart — restarts the gateway if it's not running

# Only run in remote (cloud) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Check if gateway is already running (match python process specifically)
if pgrep -f "python3 -m gateway.run" > /dev/null 2>&1; then
  echo "[session-start] QuickKick gateway already running — skipping"
  exit 0
fi

echo "[session-start] QuickKick gateway not running — starting supervisor..."

# Ensure log directory exists
mkdir -p /root/.hermes/logs

# Start the supervisor loop (which starts the gateway)
nohup bash /root/run-quickkick.sh >> /tmp/quickkick-supervisor.log 2>&1 &

# Give it a moment to launch
sleep 5

if pgrep -f "gateway.run" > /dev/null 2>&1; then
  echo "[session-start] QuickKick gateway started successfully"
else
  echo "[session-start] WARNING: gateway may still be starting — check /tmp/quickkick-supervisor.log"
fi
