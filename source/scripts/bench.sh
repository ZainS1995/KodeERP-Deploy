#!/usr/bin/env bash
# Run any bench command inside the dev container, e.g. scripts/bench.sh --site kodeerp.localhost migrate
exec sudo docker exec -i -u frappe kodeerp-frappe-1 bash -lc "cd /workspace/development/frappe-bench && bench $(printf '%q ' "$@")"
