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
reported separately once the owner-unlocked SSH session completes.
