# WINTER 26 — Uberspace 8 Sandbox

## Accepted infrastructure

Owner accepted the real PHP-FPM and private SQLite acceptance on 2026-11-14.
Deployment is authorized only to `pf26.uber.space`, PHP 8.5, Stripe Sandbox,
synthetic inventory and InPost MOCK. This supersedes the LH staging target for
the present work; no LH, DNS, mail, production or other-project changes are authorized.
PR #28 remains draft; no merge or production publication.

[Sanitized acceptance evidence](uberspace-20261114/fpm-acceptance.json):

- SSH host key matched the panel and pinned known_hosts before authentication.
- CLI and actual HTTPS PHP-FPM both reported PHP 8.5.12; HTTP 200, `fpm-fcgi`.
- PDO SQLite, cURL 8.23.0 and OpenSSL 3.6.5 available; SQLite 3.54.1.
- An explicit FPM pool `env[PF_TEST_CONFIG]` supplied the private synthetic config.
  The current application's `config_path()` logic selected this path through
  `getenv()`. It did not rely on the SSH environment.
- Config read passed; ordinary write was denied with mode 0400. Runtime
  create/read/rename/delete passed. Same-UID chmod remains possible; modes are
  not isolation against a compromised account owner.
- Real SQLite commit/rollback, DELETE journal, WAL, SHM, snapshot isolation and
  integrity check passed. Private config/token/database/WAL/SHM HTTP access denied.
- HTTPS/exact-host/token/replay gates passed. Probe and synthetic private files
  removed; original FPM configuration restored byte-for-byte and reloaded;
  probe returns 404 and pre-existing WWW files are unchanged.
- PHP 8.5 remains selected. No application or real order ledger was installed
  during infrastructure acceptance.

## Fresh build and source identity

Application baseline: `9cb6100e6368c125e9fc6cbde6958496838c490d`.
Checked PR head: `d8198ded71980c9aa702241a227b24157fd1e969`.
Their diff adds only nine infrastructure documentation/tool/test files; no
application, pricing, SKU, inventory, asset or photo change.

A fresh clean-checkout build of that head passed PHP lint and all three existing
checkout suites (`checkout-sandbox`, `checkout-live-gates`, `checkout-locker`),
plus the build's Python/JS gates and InPost MOCK UI assertions. Additional InPost
MOCK PHP assertions passed. These are local tests, not remote purchase acceptance.

[Fresh build provenance](uberspace-20261114/fresh-build.json). The existing builder
uses a historical `lh-` archive name; this is a newly built local artifact, not an
LH upload and not a reused historical ZIP. Staging-only protection and robots
overlays will be applied to a separately manifested deployment package without
editing the source application's public files.

## Stage 3 status

Preparation in progress. No stage-3 server deployment or remote purchase result
is claimed yet. Sandbox secrets are supplied locally, outside Git and logs.
Publication requires inventory/backup, private configuration, Basic Auth covering
all content with only the exact signed POST webhook exception, and real HTTP
security checks. Any failed deployment security gate stops publication.

Pending: server deployment, remote signed Stripe webhooks, card/BLIK Sandbox,
inventory/idempotency checks, mobile viewport checks and owner physical-phone
acceptance. No Stripe Live or real shipping.
