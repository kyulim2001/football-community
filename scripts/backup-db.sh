#!/bin/sh
set -e

cd "$(dirname "$0")/.."
mkdir -p backups

FILE="backups/db-$(date +%Y%m%d-%H%M%S).sql.gz"

docker compose exec -T db sh -c 'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --single-transaction --routines "$MYSQL_DATABASE"' | gzip > "$FILE"

find backups -name 'db-*.sql.gz' -mtime +7 -delete

echo "$(date '+%F %T') backup saved: $FILE ($(du -h "$FILE" | cut -f1))"
