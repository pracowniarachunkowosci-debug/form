#!/bin/bash
# Private CLI helper. URLs are credentials; only private curl config files contain them.
set -eu
case "${1:-}" in
  success) config=/home/pf26/winter26/config/reconcile-monitor-success.curl ;;
  failure) config=/home/pf26/winter26/config/reconcile-monitor-failure.curl ;;
  *) exit 64 ;;
esac
test -f "$config" && test ! -L "$config" || exit 1
# No URL, credentials, order identifiers, body or logs in the process arguments/output.
exec /usr/bin/curl --config "$config" --proto '=https' --silent --output /dev/null --fail --connect-timeout 3 --max-time 5
