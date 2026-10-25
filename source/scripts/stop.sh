#!/usr/bin/env bash
# Stop bench processes; pass --all to also stop the containers (data volumes are kept).
set -uo pipefail
cd "$(dirname "$0")/.."
sudo docker exec kodeerp-frappe-1 bash -c 'pkill -f "honcho start"; pkill -f "frappe.utils.bench_helper"; pkill -f "socketio.js"; true' 2>/dev/null
for i in $(seq 1 20); do sudo docker exec kodeerp-frappe-1 pgrep -f "honcho start|bench_helper|socketio.js" >/dev/null 2>&1 || break; sleep 1; done
[ "${1:-}" = "--all" ] && sudo docker compose -p kodeerp -f compose.dev.yml --env-file .secrets/compose.env stop
echo stopped
