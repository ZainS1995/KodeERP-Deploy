#!/usr/bin/env bash
# Start KodeERP dev stack: containers + bench processes (web :8080, socketio :9010, worker, scheduler)
set -euo pipefail
cd "$(dirname "$0")/.."
pgrep -x dockerd >/dev/null || { export PATH=$PATH:/usr/sbin; sudo bash -c 'nohup dockerd > /var/log/dockerd.log 2>&1 &'; sleep 6; }
sudo docker compose -p kodeerp -f compose.dev.yml --env-file .secrets/compose.env up -d
# loopback-only guard for dev ports (bench serve binds 0.0.0.0 with the Werkzeug debugger)
for p in 8080 9010; do sudo iptables -C INPUT -p tcp --dport $p ! -i lo -j DROP 2>/dev/null || sudo iptables -I INPUT -p tcp --dport $p ! -i lo -j DROP; done
if sudo docker exec kodeerp-frappe-1 pgrep -f "honcho start" >/dev/null; then echo "bench already running"; else
  sudo docker exec -u frappe -d kodeerp-frappe-1 bash -lc 'cd /workspace/development/frappe-bench && nohup bench start > logs/bench-start.log 2>&1'
fi
for i in $(seq 1 30); do code=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: kodeerp.localhost" http://127.0.0.1:8080/api/method/ping || true); [ "$code" = 200 ] && { echo "KodeERP up: http://127.0.0.1:8080 (Host: kodeerp.localhost)"; exit 0; }; sleep 2; done
echo "web did not come up; see development/frappe-bench/logs/bench-start.log"; exit 1
