#!/usr/bin/env bash
# Restore a KodeERP backup into the running stack as a new site.
# usage: ./restore-site.sh <new-site-name e.g. erp.example.com> <database.sql.gz> [files.tar] [private-files.tar]
set -euo pipefail
SITE="$1"; DB="$2"; PUB="${3:-}"; PRIV="${4:-}"
DB_ROOT_PASSWORD="$(grep -E "^DB_ROOT_PASSWORD=" .env | cut -d= -f2-)"
C="docker compose exec -T backend"
docker compose cp "$DB" backend:/tmp/db.sql.gz
ARGS=(--force --db-root-username root --db-root-password "$DB_ROOT_PASSWORD")
if [ -n "$PUB" ];  then docker compose cp "$PUB"  backend:/tmp/files.tar;   ARGS+=(--with-public-files /tmp/files.tar); fi
if [ -n "$PRIV" ]; then docker compose cp "$PRIV" backend:/tmp/private.tar; ARGS+=(--with-private-files /tmp/private.tar); fi
if [ -z "${ADMIN_PW:-}" ]; then read -rsp "New Administrator password for $SITE: " ADMIN_PW; echo; fi
# 1) empty site with a DB user reachable from the app containers ('%' host), 2) restore the backup into it
$C bench new-site "$SITE" --db-root-username root --db-root-password "$DB_ROOT_PASSWORD" --admin-password "$ADMIN_PW" --mariadb-user-host-login-scope=%
$C bench --site "$SITE" restore /tmp/db.sql.gz "${ARGS[@]}"
$C bench --site "$SITE" migrate
$C bench --site "$SITE" set-admin-password "$ADMIN_PW"
$C bench --site "$SITE" clear-cache
$C bench --site "$SITE" clear-website-cache
$C bench --site "$SITE" enable-scheduler
$C bench --site "$SITE" set-config host_name "https://$SITE"
echo "Restored $SITE. If the old site had an encryption_key, set it now:  $C bench --site $SITE set-config encryption_key '<key>'"
