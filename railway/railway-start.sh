#!/bin/sh
# Direct Railway startup — skips s6-overlay to ensure Railway env vars
# reach the gateway without being filtered or overridden by the .env loader.
set -e

HERMES_HOME="${HERMES_HOME:-/opt/data}"

# Bootstrap data directory
mkdir -p \
    "$HERMES_HOME/cron" \
    "$HERMES_HOME/sessions" \
    "$HERMES_HOME/logs" \
    "$HERMES_HOME/memories" \
    "$HERMES_HOME/skills" \
    "$HERMES_HOME/plans" \
    "$HERMES_HOME/workspace" \
    "$HERMES_HOME/home"

printf 'docker\n' > "$HERMES_HOME/.install_method"

# Seed config and SOUL on first boot
if [ ! -f "$HERMES_HOME/config.yaml" ] && [ -f /opt/hermes/cli-config.yaml.example ]; then
    cp /opt/hermes/cli-config.yaml.example "$HERMES_HOME/config.yaml"
fi
if [ ! -f "$HERMES_HOME/SOUL.md" ] && [ -f /opt/hermes/docker/SOUL.md ]; then
    cp /opt/hermes/docker/SOUL.md "$HERMES_HOME/SOUL.md"
fi

# Sync bundled skills
if [ -d /opt/hermes/skills ]; then
    /opt/hermes/.venv/bin/python /opt/hermes/tools/skills_sync.py 2>/dev/null || true
fi

# Write a MINIMAL .env that does NOT override the Railway env vars.
# Hermes's load_hermes_dotenv uses override=True, so any key present in .env
# will stomp the Docker-injected env var. Writing only non-credential keys
# here keeps all secrets in Railway's env where they belong.
cat > "$HERMES_HOME/.env" << 'ENVEOF'
TERMINAL_TIMEOUT=60
TERMINAL_LIFETIME_SECONDS=300
BROWSERBASE_PROXIES=false
BROWSER_SESSION_TIMEOUT=300
WEB_TOOLS_DEBUG=false
VISION_TOOLS_DEBUG=false
ENVEOF
chmod 600 "$HERMES_HOME/.env"

echo "[railway-start] Starting QuickKick gateway"
echo "[railway-start] TELEGRAM token set: $(test -n "${TELEGRAM_BOT_TOKEN:-}" && echo YES || echo NO)"

# Activate venv and drop to hermes user
. /opt/hermes/.venv/bin/activate
cd /opt/data

# s6-overlay installs to /command/; fall back to su if not available
if [ -x /command/s6-setuidgid ]; then
    exec /command/s6-setuidgid hermes hermes gateway run
elif [ -x /usr/bin/s6-setuidgid ]; then
    exec /usr/bin/s6-setuidgid hermes hermes gateway run
else
    exec su -s /bin/sh hermes -c "exec hermes gateway run"
fi
