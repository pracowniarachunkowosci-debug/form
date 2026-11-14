# R01.5 integration — pf26 Sandbox

Scope: the accepted R01.5 presentation integrated with the existing application at
`https://pf26.uber.space`. PR #28 remains a draft. No production deployment or merge.

## Source and packaging

Baseline application/PR commit: `ec8495f5716b001d43e81f078e7de2b97f16718d`.
The fresh, read-only staging inventory contains 124 files. The release contains
285 files: eight existing presentation files change and 161 namespaced assets are
added. No existing file is deleted. The staging-only root overlay serves the new
`winter-26.html` at `/`; the repository's portfolio `index.html` is unchanged.

Modified deployed files: `index.html`, `winter-26.html`, the three active model
pages, `winter-zestaw-4.html`, `winter-config.js`, and the HTML in `api/result.php`.
Executable PHP blocks in the return page, the checkout request handler, and the
availability handler are compared with the baseline. Other backend files, public
commercial JSON, legal pages, `.htaccess`, and `robots.txt` must match staging
byte for byte. Existing PHP-FPM/private runtime configuration is not changed.

`scripts/build_r015_staging.py` builds from current checked-out sources and the
verified staging security overlay. It produces a deterministic ZIP, SHA-256,
complete manifest and file delta under ignored `.artifacts/r015-release/`.
It excludes development fixtures, scripts, documentation, private configuration,
databases and credentials. This is a pf26-specific build, not the historical LH
builder. The old renderer's gate test retains its original HTML fixture because
its template selectors are not the new R01.5 view.

## Photography

The namespaced gallery has 20 existing arrangements and five color-confirmed
product frames. Arrangements remain the first tab and explicitly do not confirm
the selected finish. Missing confirmed material produces an empty-state message.

| Model | Confirmed product frames | Arrangements |
|---|---|---:|
| VASE | Dual 1, White 1 | 12 |
| KNITTED STAR | Marble 2 | 5 |
| KNITTED MEDALLION | Marble 1 | 3 |

Only `full-soft-czerwono-czarny-main` (VASE / Dual / main) is OWNER APPROVED.
The approval check requires the exact ID, model, color, role and source SHA-256.
VASE White uses `full-soft-bialy-nakrapiany-top`; STAR Marble uses
`knitted-star-bialy-main` and WEB015; MEDALLION Marble uses
`knitted-medallion-bialy-main`. WEB018 is excluded as REJECTED_QUALITY and WEB016
as ARCHIVED_BY_OWNER. Their original files are retained in the source archive.
Image bytes, original hashes, roles, geometry and the sales catalog photoAsset
are not changed. No other photograph is implicitly approved.

## Validation before deployment

- PHP 8.5 lint: all 12 API sources passed.
- Existing checkout-sandbox, checkout-live-gates, checkout-locker, inpost-mock
  and inpost-mock-ui suites passed using isolated local fixtures, without Stripe calls.
- Pricing, configuration registry, legacy store gate, config, composition,
  configurator journey and consent checks passed.
- Sizes 1/2/4/6/8, missing choices, model changes clearing color, repeated variants,
  unavailable color, direct edit and one in-flight request are covered by existing
  behavioral suites. The browser completed a six-item composition, edited a
  particular item, exercised both synthetic pickup points, zoom and model changes.
- A local HTTP checkout fixture recorded exactly one request for one click, with
  six selections and an idempotency ID; no payment or reservation was created.
- Composer overflow checks passed at 320/360/390/430/1280/1440 px.

## Deployment and rollback gates

The owner-local SSH session holds no saved passphrase. Existing Basic Auth/tester
credentials are decrypted from DPAPI in memory and sent only through verified SSH
to pf26 for HTTPS tests. Reports contain booleans, hashes and aggregate counts.

Before any write the remote helper verifies the pf26 UID, existing DocumentRoot,
all baseline file hashes, all SQLite table hashes and the private configuration
hash. The fresh baseline contains **three paid orders and one released order**;
all are preserved, including the additional order beyond earlier acceptance.

A full private copy of the 124-file release is hash-verified on the same account.
New assets are installed first; each existing file is replaced atomically.
The existing Basic Auth `.htaccess` stays in place throughout. Failure of any
post-deployment security/data gate triggers restoration of the original files.
Only this deployment's exact newly added hashes can be removed during rollback.

HTTP gates cover anonymous 401, both required headers independently on 401/200,
wrong password, alternate API path, unsigned webhook 400 SIGNATURE, private path
denial, served page hashes, tester login, real status/stock, both MOCK points,
real success/cancel return routes and rejection of an invalid checkout payload.
No positive new checkout or payment is required for this visual integration.
Final verification repeats complete public hashes and every SQLite table hash.

For immediate rollback while the owner-local session is open, submit a unique
command ID with action `rollback` through its ignored local command queue.
The helper uses the verified deployment backup, refuses public-file drift and
never replaces or restores the database. A new session requires the existing
SSH key to be unlocked locally; no new credentials are generated.

Actual deployment evidence and screenshots are recorded separately after the
real HTTP/browser checks. A successful local build alone is not acceptance.
