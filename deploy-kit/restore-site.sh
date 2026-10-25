#!/usr/bin/env bash
# Restore a KodeERP backup into the running stack as a site named after its public domain.
# Run from this deploy-kit folder, after `docker compose ... up -d` is healthy.
# usage: ./restore-site.sh <domain> <database.sql.gz> <files.tar> <private-files.tar> [old site_config.json]
#   e.g. ./restore-site.sh fnb.kodenova.com ../backups/fnb.localhost/20261021_195544-fnb_localhost-database.sql.gz \
#        ../backups/fnb.localhost/20261021_195544-fnb_localhost-files.tar \
#        ../backups/fnb.localhost/20261021_195544-fnb_localhost-private-files.tar \
#        ../../KodeERP-Secrets-2026-10-21/fnb.localhost/site_config.json
# The Administrator password is read from $ADMIN_PW or asked for (never put it on the command line history).
set -euo pipefail
SITE="$1"; DB="$2"; PUB="$3"; PRIV="$4"; OLDCONF="${5:-}"
DB_ROOT_PASSWORD="$(grep -E '^DB_ROOT_PASSWORD=' .env | cut -d= -f2-)"
COMPOSE="${COMPOSE:-docker compose}"
C="$COMPOSE exec -T backend"
if [ -z "${ADMIN_PW:-}" ]; then read -rsp "New Administrator password for $SITE: " ADMIN_PW; echo; fi

$COMPOSE cp "$DB"   backend:/tmp/restore-db.sql.gz
$COMPOSE cp "$PUB"  backend:/tmp/restore-files.tar
$COMPOSE cp "$PRIV" backend:/tmp/restore-private.tar

# 1) empty site whose DB user may log in from the app containers ('%'), 2) restore the backup into it
$C bench new-site "$SITE" --db-root-username root --db-root-password "$DB_ROOT_PASSWORD" \
   --admin-password "$ADMIN_PW" --mariadb-user-host-login-scope=%
$C bench --site "$SITE" restore /tmp/restore-db.sql.gz \
   --with-public-files /tmp/restore-files.tar --with-private-files /tmp/restore-private.tar \
   --db-root-username root --db-root-password "$DB_ROOT_PASSWORD" --force

# 3) carry over non-database settings from the old site_config.json (encryption key, branch -> cost-centre map)
if [ -n "$OLDCONF" ]; then
  for KEY in encryption_key kodeerp_branch_cost_centers kodeerp_sync_line_dimensions kodeerp_branch_cost_center_sync; do
    VAL="$(python3 -c 'import json,sys; c=json.load(open(sys.argv[1])); k=sys.argv[2]; print(json.dumps(c[k]) if k in c else "")' "$OLDCONF" "$KEY")"
    [ -z "$VAL" ] && continue
    if [ "$KEY" = encryption_key ]; then VAL="$(python3 -c 'import json,sys;print(json.loads(sys.argv[1]))' "$VAL")"; $C bench --site "$SITE" set-config "$KEY" "$VAL" >/dev/null
    else $C bench --site "$SITE" set-config -p "$KEY" "$VAL" >/dev/null; fi
    echo "copied $KEY from old site_config"
  done
fi

$C bench --site "$SITE" migrate
$C bench --site "$SITE" set-admin-password "$ADMIN_PW"
$C bench --site "$SITE" set-config host_name "https://$SITE"
$C bench --site "$SITE" enable-scheduler
$C bench --site "$SITE" clear-cache
$C bench --site "$SITE" clear-website-cache
$C rm -f /tmp/restore-db.sql.gz /tmp/restore-files.tar /tmp/restore-private.tar
echo "Restored $SITE. Next: verify (see DEPLOY.md step 9) and change every demo user's password."
