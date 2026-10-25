#!/usr/bin/env bash
# Temporary public preview: gunicorn (prod WSGI, no debugger) + nginx on 127.0.0.1:8088, exposed via a Cloudflare quick tunnel.
# The dev server (bench serve :8080, Werkzeug debugger) is NEVER exposed.
# Idempotent: each piece is (re)started only if it is not actually serving. A running tunnel is reused, so the URL is kept.
set -euo pipefail
cd "$(dirname "$0")/.."
C=kodeerp-frappe-1
TUN_PID=/tmp/kodeerp-preview-tunnel.pid
TUN_LOG=/tmp/kodeerp-preview-tunnel.log
# Matches the real cloudflared command line (flags sit between "tunnel" and "--url").
TUN_PAT='cloudflared tunnel .*--url http://127\.0\.0\.1:8088'
GUNI_PAT='gunicorn -b 127\.0\.0\.1:8001'

ping8001() { sudo docker exec "$C" curl -s -o /dev/null -m 3 -w '%{http_code}' -H "X-Frappe-Site-Name: kodeerp.localhost" http://127.0.0.1:8001/api/method/ping 2>/dev/null | grep -q '^200$'; }

sudo ln -sfn /workspace/kodeerp/development /workspace/development   # asset symlinks use the container path

# --- gunicorn: decide by health, not by process name (old workers can linger after preview-stop) ---
if ping8001; then
  echo "gunicorn already serving on 127.0.0.1:8001"
else
  # clear any half-dead leftovers (e.g. workers still draining after pkill), then start fresh
  if sudo docker exec "$C" pgrep -f "$GUNI_PAT" >/dev/null 2>&1; then
    sudo docker exec "$C" pkill -TERM -f "$GUNI_PAT" || true
    for i in $(seq 1 20); do sudo docker exec "$C" pgrep -f "$GUNI_PAT" >/dev/null 2>&1 || break; sleep 1; done
    sudo docker exec "$C" pkill -KILL -f "$GUNI_PAT" 2>/dev/null || true
  fi
  sudo docker exec -u frappe -d "$C" bash -lc 'cd /workspace/development/frappe-bench/sites && exec ../env/bin/gunicorn -b 127.0.0.1:8001 -w 2 --threads 4 -t 120 --max-requests 2000 --access-logfile ../logs/preview-gunicorn.log --error-logfile ../logs/preview-gunicorn.err frappe.app:application'
  for i in $(seq 1 60); do ping8001 && break; sleep 1; done
  ping8001 && echo "gunicorn started on 127.0.0.1:8001" || { echo "ERROR: gunicorn did not come up; see logs/preview-gunicorn.err" >&2; exit 1; }
fi

# --- nginx ---
[ -f /tmp/kodeerp-preview-nginx.pid ] && kill -0 "$(cat /tmp/kodeerp-preview-nginx.pid)" 2>/dev/null || /usr/sbin/nginx -c "$PWD/preview/nginx.conf"
curl -sf -o /dev/null http://127.0.0.1:8088/api/method/ping && echo "local prod-style server OK on 127.0.0.1:8088"

# --- tunnel: reuse the running one (keeps the URL); start one only if none is running ---
pid=""
[ -f "$TUN_PID" ] && kill -0 "$(cat "$TUN_PID")" 2>/dev/null && pid=$(cat "$TUN_PID")
[ -z "$pid" ] && pid=$(pgrep -f "$TUN_PAT" | head -1 || true)
if [ -n "$pid" ]; then
  echo "$pid" > "$TUN_PID"; echo "tunnel already running (pid $pid)"
  u=$(cat preview/current-url.txt 2>/dev/null || true)
else
  # sandbox DNS maps argotunnel.com to a fake IP and blocks it, so pin published Cloudflare edge IPs
  : > "$TUN_LOG"
  nohup tools/bin/cloudflared tunnel --no-autoupdate --protocol http2 --edge 198.41.192.7:7844 --edge 198.41.200.13:7844 --url http://127.0.0.1:8088 > "$TUN_LOG" 2>&1 &
  echo $! > "$TUN_PID"
  u=""
fi
if [ -z "${u:-}" ] || ! grep -q trycloudflare <<<"$u"; then
  for i in $(seq 1 40); do u=$(grep -aoE 'https://[a-z0-9-]+\.trycloudflare\.com' "$TUN_LOG" | tail -1 || true); [ -n "$u" ] && break; sleep 1; done
fi
echo "${u:-tunnel URL not found; see $TUN_LOG}" | tee preview/current-url.txt
