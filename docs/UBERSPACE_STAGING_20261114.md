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

## Stage 3 result — STOP, automatic rollback verified

The owner-required security gate failed **before uploading any application**.
The harmless bootstrap control file returned HTTP **401**, but its response did
not satisfy the complete required `X-Robots-Tag: noindex, noarchive` and
`Cache-Control: no-store` header check. The evidence records this combined check;
it does not identify which individual header/directive was missing. No bypass or
retry was performed after the failed gate.

[Sanitized deployment stop](uberspace-20261114/deployment-security-stop.json).

Preflight passed: pinned SSH identity, only the default domain on the account,
verified default-domain symlink, original webroot containing only the welcome
file, no unknown files, PHP 8.5, and the expected existing Stripe Sandbox account.
The default DocumentRoot was briefly switched to a protected directory containing
only a harmless control file. Basic Auth used a password hash outside DocumentRoot,
behind the existing account WWW mode-0750 boundary. The application was not copied.

Rollback restored the original DocumentRoot and welcome file. Its SHA-256 before,
after rollback, and in an independent HTTPS GET is identical:
`6ece1bba2d491b00526758be614a75bf0ea045ead6a1246438fb15e252d114af`.
The root returns 200 with that welcome page, and the control URL returns 404.

New staging directories remain quarantined outside the active DocumentRoot, with
`Require all denied`; the copied welcome backup is retained. The private directory
skeleton is empty. The Basic Auth password hash remains outside DocumentRoot.
No application, Stripe-secret configuration, database, seed or webhook endpoint was
installed. FPM configuration was not changed during this attempt. PHP remains 8.5.
Sandbox API access in this stage was read-only account/balance/endpoint inspection.

The fresh staging package has 124 files; only `.htaccess` and `robots.txt` are
staging overlays. CLI seed and Live-maintenance sources are excluded from the
public archive. Source application files remain unchanged.
[Staging package provenance](uberspace-20261114/staging-package.json).

Additional existing loopback HTTP suite passed: tester-independent MOCK UI/status,
point selection/errors, host/origin guards, hidden internals, canonical SQLite
order data, stock idempotency, courier and mixed 2+4 cart. No provider calls.
[Local HTTP evidence](uberspace-20261114/local-mock-http.json).

The old LH-specific runtime harness was not portable to this workspace (hard-coded
historical fixture directory); its attempted invocation returned
`local_harness_failed`. This is not recorded as an Uberspace acceptance result.
No LH fixtures or resources were changed to force it to run.

Remote application checkout, card/BLIK, signed webhook/redelivery, post-payment
SQLite and viewport/physical-phone acceptance are **NOT RUN**, because publication
stopped at the earlier security gate. No store URL is ready for owner acceptance.
Further deployment requires addressing the response-header gate and a new owner
decision to resume. No Stripe Live, real shipping, merge or production changes.
