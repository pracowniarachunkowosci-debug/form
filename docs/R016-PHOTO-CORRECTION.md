# R01.6 — owner correction of STAR and MEDALLION photographs

15 November 2026. Owner confirmed that all photographs previously assigned to
White for KNITTED STAR and KNITTED MEDALLION are Marble. The supplied screenshot
identified the blurred third STAR lifestyle photograph with the red ribbon and
orange as the exact quality rejection.

## Exact decisions

Seven source-hash-bound color decisions are recorded as OWNER COLOR CONFIRMED,
not new OWNER APPROVED approvals. The exact rejected photo additionally receives
REJECTED_QUALITY and is excluded from the customer gallery and approval board.
All existing roles, originals, exports and hashes remain unchanged.

- STAR `WEB014`: gallery → Marble, same role.
- STAR `knitted-star-white-scene-1` and `knitted-star-white-scene-2`: lifestyle → Marble.
- STAR `knitted-star-white-scene-3`: color Marble, **REJECTED_QUALITY**; excluded.
- MEDALLION `knitted-medallion-white-scene-1`, `-2`, `-3`: lifestyle → Marble.

Rejected source:
`PF_W26_galeria_KNITTED-STAR_03_4x5_1600x2000.webp`.
SHA-256: `92b7427e7c37f4c62ddfeaf8ce96865270c50ac9e9c0c4f53249fe0345315e33`.

[Durable decisions, filenames and hashes](r016/owner-decisions.json),
[current matrix](r016/matrix.json), [preserved exclusions](r016/excluded.json).
The generator validates each decision against the existing exact model, role,
filename and SHA-256 before applying it, so regeneration cannot silently undo it.

## Result

STAR/Marble contains three product frames (main, gallery, detail) and two
arrangements. MEDALLION/Marble contains one main photograph and three
arrangements. White for both models honestly has no material in the current
selection. No photograph is promoted to main and the sole OWNER APPROVED
VASE/Dual main photograph is unchanged. There are 42 included records:
11 color-confirmed frames (including that one approved main) and 31 proposals.

## Verification and staging scope

The 12-pair selector suite checks the new exact counts, absence of White frames,
exclusion of the screenshot-identified frame, unchanged main roles and existing
rejections. Only `assets/winter26-r016/variant-media.js` may differ in the public
release. All other 381 public files must retain their hashes, including image
bytes, backend, checkout, security, commercial data and legal documents.

The fresh package and existing SSH transport enforce that one-file allowlist,
the hash-verified current R01.6 baseline and unchanged SQLite/private configuration.
Deployment takes a complete rollback copy before atomic replacement.

Browser automation was unavailable during this correction. The exact rejected
original was visually compared with the owner's screenshot; no new live-browser
acceptance is claimed. Automated selector and real HTTP/manifest checks are
recorded in the evidence below.

## Deployment completed

The correction is deployed at [pf26.uber.space](https://pf26.uber.space).
Deployed source: `57bff0d4844c940bdbe7b7900ea254bef3a216c8`.
The fresh archive contains 382 files and exactly one modified photograph-map
file; all other 381 are byte-identical. ZIP SHA-256:
`d771b74001782595a914f19db5306a85e95f5c0a08714e4c4ffd135aeeeec457`.
Manifest SHA-256:
`bc7fbd291716a0e5c1ff7e521ba5d42288109fda6677818a03dc420f5461702b`.

The pre-deployment inventory matched all existing R01.6 hashes. A new local
public-release copy was made, and the complete server rollback copy is:
`/var/www/virtual/pf26/winter26/backup/r016-photo-20261115-023247`.
Rollback restores public files, never the SQLite database.

Deployment and repeated read-only verification both passed. All 382 deployed
hashes match. The actual map retrieved over authenticated HTTPS confirms:

- rejected STAR scene 03 is absent;
- White galleries for STAR and MEDALLION are empty;
- STAR Marble has 3 product frames and 2 lifestyle frames, all color-confirmed;
- MEDALLION Marble has 1 product frame and 3 lifestyle frames, all color-confirmed.

Basic Auth, independent noindex/noarchive/no-store checks, private-path denial
and the exact webhook signature exception remain unchanged and pass. Every
SQLite table and private configuration hash matches the pre-deployment snapshot.
The existing **3 paid Sandbox orders and 1 released order** are preserved. No
new payment, order, reservation, stock change or shipment was created.

[Deployment](r016/photo-correction/deploy.json),
[final HTTP/data verification](r016/photo-correction/verify-final.json),
[local exact-record comparison](r016/photo-correction/local-verification.json),
[manifest](r016/photo-correction/manifest.json),
[release](r016/photo-correction/release.json).

PR #28 remains draft. Owner visual acceptance remains a browser refresh away;
there is no new screenshot or claimed manual-browser pass while browser control
is unavailable.
