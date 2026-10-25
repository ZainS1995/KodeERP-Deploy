#!/usr/bin/env bash
# Runs INSIDE the kodeerp-frappe-1 container (as user frappe).
set -euo pipefail
cd /workspace/development
bench init --skip-redis-config-generation --frappe-branch version-16 --python python3.14 frappe-bench
cd frappe-bench
bench set-config -g db_host 127.0.0.1
bench set-config -gp db_port 3307
bench set-config -g redis_cache redis://127.0.0.1:13100
bench set-config -g redis_queue redis://127.0.0.1:13101
bench set-config -g redis_socketio redis://127.0.0.1:13101
bench set-config -gp webserver_port 8080
bench set-config -gp socketio_port 9010
bench get-app --branch version-16 erpnext
echo ERPNEXT_DONE
bench get-app --branch version-16 hrms
echo ALL_DONE
