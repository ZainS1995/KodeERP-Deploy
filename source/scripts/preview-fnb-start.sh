#!/usr/bin/env bash
# Second temporary preview for the F&B demo tenant (fnb.localhost): its own nginx on 127.0.0.1:8093 + its own Cloudflare
# quick tunnel. Shares the gunicorn on 127.0.0.1:8001 started by preview-start.sh. Never touches the main demo nginx/tunnel.
#
# Why links die (diagnosed 2026-10-21): the box is paused/hibernated while idle. During a pause cloudflared cannot answer
# edge heartbeats; Cloudflare then sometimes deletes the account-less quick tunnel. On resume the process is still ALIVE
# but loops on "Unauthorized: Tunnel not found" forever, so "process running" != "link working".
# This script therefore:
#   * reuses a running tunnel only if its log does not end in "Tunnel not found" (otherwise kills it and starts fresh),
#   * starts cloudflared fully detached (setsid + nohup + </dev/null) so no parent shell exit/SIGHUP can kill it,
#   * uses http2 over TCP (QUIC is unnecessary through the box egress), IPv4 edges, a fixed metrics port,
#   * keeps old logs (rotated with a timestamp) for later debugging.
# A quick tunnel URL ALWAYS changes on restart; only a named tunnel / own domain gives a stable URL.
set -euo pipefail
cd "$(dirname "$0")/.."
PID=/tmp/kodeerp-fnb-tunnel.pid; LOG=/tmp/kodeerp-fnb-tunnel.log; LOGDIR=/tmp/kodeerp-fnb-tunnel-logs
METRICS=127.0.0.1:20293
PAT='cloudflared tunnel .*--url http://127\.0\.0\.1:8093'
sudo docker exec kodeerp-frappe-1 curl -sf -o /dev/null -H "X-Frappe-Site-Name: fnb.localhost" http://127.0.0.1:8001/api/method/ping \
  || { echo "gunicorn :8001 not serving; run scripts/preview-start.sh first" >&2; exit 1; }
[ -f /tmp/kodeerp-fnb-nginx.pid ] && kill -0 "$(cat /tmp/kodeerp-fnb-nginx.pid)" 2>/dev/null || /usr/sbin/nginx -c "$PWD/preview/nginx-fnb.conf"
curl -sf -o /dev/null http://127.0.0.1:8093/api/method/ping && echo "F&B nginx OK on 127.0.0.1:8093"

# Is the existing tunnel actually registered? Last registration outcome in the log decides.
tunnel_dead() { local last; last=$(grep -aE 'Registered tunnel connection|Tunnel not found' "$LOG" 2>/dev/null | tail -1 || true)
  [[ "$last" == *"Tunnel not found"* ]]; }

pid=""; [ -f "$PID" ] && kill -0 "$(cat "$PID")" 2>/dev/null && pid=$(cat "$PID")
[ -z "$pid" ] && pid=$(pgrep -f "$PAT" | head -1 || true)
if [ -n "$pid" ] && tunnel_dead; then
  echo "F&B tunnel pid $pid is alive but Cloudflare deleted it (Tunnel not found); restarting" >&2
  pkill -f "$PAT" || true; sleep 2; pkill -9 -f "$PAT" || true; pid=""; : > preview/fnb-url.txt
fi
if [ -n "$pid" ]; then echo "$pid" > "$PID"; echo "F&B tunnel already running and registered (pid $pid)"; u=$(cat preview/fnb-url.txt 2>/dev/null || true)
else
  mkdir -p "$LOGDIR"; [ -s "$LOG" ] && mv "$LOG" "$LOGDIR/tunnel-$(date +%Y%m%d-%H%M%S).log"
  ls -1t "$LOGDIR"/tunnel-*.log 2>/dev/null | tail -n +21 | xargs -r rm -f   # keep last 20
  setsid nohup tools/bin/cloudflared tunnel --no-autoupdate --protocol http2 --edge-ip-version 4 \
    --edge 198.41.192.7:7844 --edge 198.41.200.13:7844 --metrics "$METRICS" \
    --url http://127.0.0.1:8093 </dev/null > "$LOG" 2>&1 &
  echo $! > "$PID"; u=""
fi
if [ -z "${u:-}" ] || ! grep -q trycloudflare <<<"$u"; then
  for i in $(seq 1 40); do u=$(grep -aoE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | tail -1 || true); [ -n "$u" ] && break; sleep 1; done
fi
echo "${u:-tunnel URL not found; see $LOG}" | tee preview/fnb-url.txt
