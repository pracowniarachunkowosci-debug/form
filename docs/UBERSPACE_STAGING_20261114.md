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
overlays were applied to a separately manifested deployment package without
editing the source application's public files.

## Stage 3 — deployed, Sandbox purchases verified

The owner authorized resumption after the earlier bootstrap STOP. Individual
response checks established that **both headers were absent on 401**. Replacing
the Header directives alone did not fix that response. A local
`ErrorDocument 401 "Authentication required"` did. Observed 401 and authenticated
200 responses now independently contain `noindex`, `noarchive` and `no-store`.
The overlay unsets the onsuccess header table and sets the always table; it has
no conflicting `Header set` directives. This is a staging overlay, not a change
to the application source.

[Header diagnosis](uberspace-20261114/response-headers.json) and
[deployment security checks](uberspace-20261114/deployment-success.json).
The previous [rollback evidence](uberspace-20261114/deployment-security-stop.json)
is retained only as historical evidence and is superseded by the successful run.

### Isolation and configuration

Only the default pf26 host was configured. Inventory found one known welcome
file and no unknown files; its backup remains intact. `html` points to
`winter26/app/public` inside the account WWW tree, never to `/home`.
Private config and database/session/cache/log/upload runtime stay outside WWW.
Directory modes are 0700, config 0400, database 0600; PHP-FPM has UMask 0077.
`PF_TEST_CONFIG` is set explicitly in the accepted FPM mechanism; no Live override.
The existing Sandbox key and the signing secret returned on creation of the
exact pf26 endpoint are held only in private config. Tester token is hashed.
The seed was run using the existing CLI source, then removed from WWW.
All 12 variants started with synthetic quantity 20, without catalog changes.

Anonymous page/asset/checkout/webhook-GET requests return 401; wrong Basic
password and alternate API paths are rejected. Only the exact POST webhook path
is exempt from Basic Auth and an unsigned request returns 400 SIGNATURE.
Technical-host and private/internal-file access tests passed. Robots blocks all
crawling and contains no production sitemap. No DNS/domain/mail/LH changes.

### Package identity

The finalized 124-file package reproduces the deployed ErrorDocument overlay:

- Archive SHA-256: `2a3701a8409c8e4818626ac7afe42053e8f912e0e93658d08b4b97201126e211`.
- Manifest SHA-256: `77a2cd1b97e771fab942d618fb30f9178e1b17777b0c33ba85415f594fe998ce`.
- The originally transported package SHA remains in the deployment evidence;
  it predates the verified, on-server ErrorDocument addition. It is not claimed
  to be the finalized archive. Application bytes are unchanged in both packages.
- Staging-only `.htaccess` and `robots.txt` overlays; excluded CLI seed and
  Live-maintenance source. No keys, private config, database or test fixtures.

[Finalized package](uberspace-20261114/staging-package.json).

### Actual remote checkout acceptance

Browser purchases on pf26 completed with **card Sandbox 70.49 PLN** (courier)
and **BLIK Sandbox 68.49 PLN** (TEST01M MOCK pickup). Stripe API independently
reports both `succeeded`, paid Checkout sessions and `livemode=false`.
No actual funds or shipments were involved. The result page correctly states
that redirect alone is not payment confirmation.

The initial SQLite observer confirmed reservation and payment via signed
webhooks. The card SKU went from 20 to 19 at reservation and was not decremented
again on payment. The second paid SKU is also 19. Stripe CLI resent both actual
completion events to the exact pf26 endpoint; stock stayed unchanged.
A separate synthetic checkout verified request idempotency and 409 for changed
contents with the same request ID. The cancel return page rendered correctly.
Explicit expiry of that own unpaid Stripe session delivered a signed expiry
event and restored its reserved item to 20. A browser cancel redirect itself
does not immediately release stock; Stripe expiry is the release trigger tested.

MOCK provider failure disabled checkout; selecting valid TEST01M restored it.
Cart, variant choice, courier/locker costs and return navigation passed in the
browser. Mobile widths 320/360/390/430 had no horizontal overflow; variant cards
and controls were inspected visually. Physical-phone acceptance is left to owner.

[Stripe payment proof](uberspace-20261114/stripe-payments.json),
[remote retries, conflict and release tests](uberspace-20261114/remote-checkout.json),
[mobile measurements](uberspace-20261114/mobile-viewports.json).

### Owner phone acceptance

Open https://pf26.uber.space/api/test-access.php. Use Basic username `pf26-tester`
and the existing password from the local DPAPI display/owner password manager;
then enter the saved tester token. Do not put credentials into URLs or messages.
Choose variants and courier or a TEST01M/TEST02M MOCK point, then test payment.
Use Stripe test card 4242 4242 4242 4242, future expiry and any three-digit CVC,
or BLIK Sandbox code 123456. Enter only synthetic customer details.
Never use real payment details or a bank-generated BLIK code.

References: [Stripe test cards](https://docs.stripe.com/testing),
[BLIK Sandbox](https://docs.stripe.com/payments/blik/accept-a-payment?payment-ui=checkout),
[official event redelivery](https://docs.stripe.com/webhooks#manual-retries).

PR #28 remains draft. No merge, Stripe Live, real shipping or production publish.
The old LH-specific harness was not portable to this checkout; its earlier
failure is not recorded as an Uberspace pass. Existing local checkout suites,
InPost MOCK suites and loopback HTTP checks passed as documented above.

[Final read-only SQLite verification](uberspace-20261114/final-sqlite.json) confirms
two paid orders, one released reservation, four unique events, private modes,
integrity `ok` and exactly 124 public files. BLIK also emitted an asynchronous
success event; duplicate resend did not add another inventory deduction.

The initial comparison detected a local manifest whitespace mismatch in
`.htaccess` (one blank line). After correcting the local overlay, the owner
unlocked a second read-only SSH check. **All 124 deployed hashes now match the
finalized manifest**, including `.htaccess`. No server application changes were
needed. The final JSON is the result of that repeated remote check.
