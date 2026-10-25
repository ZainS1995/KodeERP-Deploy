#!/usr/bin/env bash
# Nightly backup of every KodeERP site (database + public + private files), copied out of Docker and kept 14 days.
# Install (as the user that runs docker):  crontab -e  ->
#   30 2 * * * cd /opt/kodeerp/deploy-kit && ./backup-nightly.sh >> /var/log/kodeerp-backup.log 2>&1
# Copy /opt/kodeerp-backups off the server regularly (another disk, S3, Google Drive...). A backup on the same disk is not a backup.
set -euo pipefail
DEST="${BACKUP_DEST:-/opt/kodeerp-backups}"; KEEP_DAYS="${KEEP_DAYS:-14}"
COMPOSE="${COMPOSE:-docker compose}"
STAMP="$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEST/$STAMP"
$COMPOSE exec -T backend bench --site all backup --with-files
CID="$($COMPOSE ps -q backend)"
DOCKER="${DOCKER:-docker}"
# The backend's working directory is /home/frappe/frappe-bench; sites live in ./sites/<site name>/
for SITE in $($COMPOSE exec -T backend bash -c 'cd sites && for d in */; do [ -f "$d/site_config.json" ] && echo "${d%/}"; done'); do
  if $COMPOSE exec -T backend test -d "sites/$SITE/private/backups"; then
    mkdir -p "$DEST/$STAMP/$SITE"
    LATEST="$($COMPOSE exec -T backend bash -c "ls -t sites/$SITE/private/backups/*-database.sql.gz | head -1 | sed 's/-database.sql.gz//'")"
    for SUF in database.sql.gz files.tar private-files.tar site_config_backup.json; do
      $DOCKER cp "$CID:/home/frappe/frappe-bench/$LATEST-$SUF" "$DEST/$STAMP/$SITE/" 2>/dev/null || true
    done
    gzip -t "$DEST/$STAMP/$SITE/"*-database.sql.gz
  fi
done
chmod -R go-rwx "$DEST/$STAMP" || echo "warning: could not tighten permissions on $DEST/$STAMP"
find "$DEST" -mindepth 1 -maxdepth 1 -type d -mtime +"$KEEP_DAYS" -exec rm -rf {} +
echo "$(date -Is) backup OK -> $DEST/$STAMP"
