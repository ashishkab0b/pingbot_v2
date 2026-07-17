#!/usr/bin/env bash

set -Eeuo pipefail

readonly PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly CERTIFICATE_NAME="emapingbot.com"
readonly MINIMUM_VALIDITY_SECONDS=2592000

cd "$PROJECT_DIR"

if ! docker compose ps --status running --services | grep -qx nginx; then
  echo "nginx must be running before certificate renewal" >&2
  exit 1
fi

certbot_command=(
  renew
  --webroot
  --webroot-path=/var/www/certbot
  --non-interactive
  --no-random-sleep-on-renew
)
certbot_command+=("$@")

docker compose --profile maintenance run --rm --no-deps certbot "${certbot_command[@]}"
docker compose exec -T nginx nginx -s reload

if ! timeout 15 openssl s_client \
  -connect 127.0.0.1:443 \
  -servername "$CERTIFICATE_NAME" </dev/null 2>/dev/null \
  | openssl x509 -checkend "$MINIMUM_VALIDITY_SECONDS" -noout; then
  echo "served certificate expires in fewer than 30 days" >&2
  exit 1
fi

echo "certificate renewal check completed successfully"
