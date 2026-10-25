#!/usr/bin/env bash
# Stop the public preview: tunnel, nginx, gunicorn. Dev stack (scripts/start.sh) is untouched.
# Note: stopping the tunnel means the next preview-start gets a NEW trycloudflare URL.
cd "$(dirname "$0")/.."
TUN_PAT='cloudflared tunnel .*--url http://127\.0\.0\.1:8088'
GUNI_PAT='gunicorn -b 127\.0\.0\.1:8001'
pkill -f "$TUN_PAT" && echo "tunnel stopped"; rm -f /tmp/kodeerp-preview-tunnel.pid
[ -f /tmp/kodeerp-preview-nginx.pid ] && kill "$(cat /tmp/kodeerp-preview-nginx.pid)" 2>/dev/null && echo "nginx stopped"
if sudo docker exec kodeerp-frappe-1 pkill -TERM -f "$GUNI_PAT"; then
  for i in $(seq 1 30); do sudo docker exec kodeerp-frappe-1 pgrep -f "$GUNI_PAT" >/dev/null 2>&1 || break; sleep 1; done
  sudo docker exec kodeerp-frappe-1 pkill -KILL -f "$GUNI_PAT" 2>/dev/null
  echo "gunicorn stopped"
fi
rm -f preview/current-url.txt; true
