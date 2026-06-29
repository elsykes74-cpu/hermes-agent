#!/bin/sh
# Railway-specific entrypoint: write Railway env vars into HERMES_HOME/.env
# BEFORE s6-overlay starts. stage2-hook.sh skips seeding if .env already exists,
# so the correct values are in place when load_hermes_dotenv runs.
set -e

HERMES_HOME="${HERMES_HOME:-/opt/data}"
mkdir -p "$HERMES_HOME"

cat > "$HERMES_HOME/.env" << ENVEOF
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
GATEWAY_ALLOW_ALL_USERS=${GATEWAY_ALLOW_ALL_USERS:-true}
TELEGRAM_HOME_CHANNEL=${TELEGRAM_HOME_CHANNEL:-}
PLAYWRIGHT_BROWSERS_PATH=${PLAYWRIGHT_BROWSERS_PATH:-/opt/hermes/.playwright}
TERMINAL_TIMEOUT=60
TERMINAL_LIFETIME_SECONDS=300
BROWSERBASE_PROXIES=false
BROWSERBASE_ADVANCED_STEALTH=false
BROWSER_SESSION_TIMEOUT=300
BROWSER_INACTIVITY_TIMEOUT=120
WEB_TOOLS_DEBUG=false
VISION_TOOLS_DEBUG=false
ENVEOF

chown hermes:hermes "$HERMES_HOME/.env" 2>/dev/null || true
chmod 600 "$HERMES_HOME/.env"

echo "[railway-entrypoint] Wrote $HERMES_HOME/.env"
echo "[railway-entrypoint] GATEWAY_ALLOW_ALL_USERS=${GATEWAY_ALLOW_ALL_USERS:-NOT_SET}"
echo "[railway-entrypoint] TELEGRAM_BOT_TOKEN set: $(test -n "${TELEGRAM_BOT_TOKEN:-}" && echo YES || echo NO)"
echo "[railway-entrypoint] .env contents (keys only):"
grep -o '^[A-Z_]*' "$HERMES_HOME/.env" || true

exec /init /opt/hermes/docker/main-wrapper.sh "$@"
