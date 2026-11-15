#!/bin/bash
# Private CLI helper; invoked only by the pf26 user service, never from HTTP.
set -eu
umask 077
app=/var/www/virtual/pf26/winter26/app
runtime=/home/pf26/winter26/runtime
config=/home/pf26/winter26/config/test.json
test "$(id -un)" = pf26 || exit 1
test -d "$runtime/cache" && test -d "$runtime/logs" || exit 1
exec 9>"$runtime/cache/reconcile.lock"
/usr/bin/flock -n 9 || exit 75
php="$(command -v php)"
test "$("$php" -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')" = 8.5 || exit 1
tmp="$(mktemp "$runtime/logs/reconcile.XXXXXXXX")"
trap 'rm -f -- "$tmp"' EXIT
set +e
"$php" "$app/scripts/reconcile-reservations.php" --config "$config" --once --limit 1 >"$tmp" 2>&1
code=$?
set -e
mv -f -- "$tmp" "$runtime/logs/reconcile-latest.ndjson"
if test "$code" -ne 0; then
  # Nonzero exit triggers OnFailure; no false healthy heartbeat after an escalation.
  exit "$code"
fi
/bin/bash "$app/scripts/reconcile-notify.sh" success
