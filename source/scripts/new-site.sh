#!/usr/bin/env bash
# Usage: scripts/new-site.sh <site> [app ...]   — creates a site with erpnext (+ given apps); passwords from .secrets
set -euo pipefail
cd "$(dirname "$0")/.."
site=$1; shift
apps="--install-app erpnext"; for a in "$@"; do apps="$apps --install-app $a"; done
sudo docker exec -u frappe -e ADMIN_PW="$(cat .secrets/admin_password)" -e DBPW="$(cat .secrets/db_root_password)" kodeerp-frappe-1 bash -lc \
 "cd /workspace/development/frappe-bench && bench new-site $site --db-root-username root --db-root-password \"\$DBPW\" --admin-password \"\$ADMIN_PW\" --mariadb-user-host-login-scope=% $apps"
