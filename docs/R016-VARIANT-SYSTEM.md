# R01.6 — real color variant selection

This is a functional update to the accepted R01.5 design on pf26 Sandbox.
The existing PHP/backend, checkout controller, SQLite, pricing, SKU, inventory,
shipping, Stripe, InPost and legal documents are unchanged. No payments are needed.

## Selection rules

Both gallery tabs filter by the exact model and selected color. A missing selected
variant has an empty state, never a fallback photograph of another color. With no
color selected, arrangements are explicitly model inspiration. Each unconfirmed
staging candidate is labelled **PROPOSAL · kolor do oceny**, including in zoom.
The proposal path is enabled only on the protected pf26 hostname and loopback.
The reusable selector excludes proposals by default.

Cards use native radio controls outside the navigation link. Selecting a color
updates the visible frame/empty state, variant name, status and destination URL.
Only an existing `main` role can occupy the card image. A gallery, detail or
lifestyle frame is never automatically promoted. A candidate main frame remains
a labelled proposal; it is not a new production photoAsset assignment.
Product pages read the selected color from the URL, retain it between model
links and reset the selected gallery frame when model/color changes.

## Existing photographic material

The preparation uses the 46 previously audited R01.4/R01.5 records and existing
exports. It does not repeat the full-session audit or generate/retouch photographs.
43 records remain: 5 confirmed frames and 38 proposals. The source originals and
all reused derivatives are SHA-256 checked; roles are retained exactly.

Two candidates (WEB006 and WEB022, VASE White) remain **review-only** because the
earlier audit requires geometry/model confirmation. They appear in the owner's
board, not in selected customer card/gallery imagery. This prevents a proposed
smoother geometry from silently replacing the approved VASE shape.

| Model | Finish | Confirmed | Proposals | Roles present |
|---|---|---:|---:|---|
| VASE | Dual | 1 | 9 | main, gallery, lifestyle |
| VASE | Red matte | 0 | 7 | main, gallery, lifestyle |
| VASE | White | 1 | 2 review-only | confirmed gallery; review-only main/lifestyle |
| VASE | Marble | 0 | 9 | main, gallery, detail, lifestyle |
| KNITTED STAR | Dual | 0 | 0 | missing |
| KNITTED STAR | Red matte | 0 | 4 | main, gallery, lifestyle |
| KNITTED STAR | White | 0 | 4 | gallery, lifestyle; no main promotion |
| KNITTED STAR | Marble | 2 | 0 | main, detail |
| KNITTED MEDALLION | Dual | 0 | 0 | missing |
| KNITTED MEDALLION | Red matte | 0 | 0 | missing |
| KNITTED MEDALLION | White | 0 | 3 | lifestyle only |
| KNITTED MEDALLION | Marble | 1 | 0 | main |

Counts are existing export records, not a claim of independent photographic shots:
some details were already separately exported crops. Only the exact VASE Dual
main photo retains OWNER APPROVED. The other four confirmed frames retain
OWNER COLOR CONFIRMED. STAR WEB018 remains REJECTED_QUALITY; MEDALLION WEB016
remains ARCHIVED_BY_OWNER. Cappuccino remains inactive. Originals are preserved.

[Complete matrix](r016/matrix.json), [provenance and hashes](r016/media-provenance.json),
[preserved exclusions](r016/excluded.json).

## Owner approval board

`/winter-foto-r016.html` displays all 12 combinations in one responsive matrix.
Each cell includes actual candidate imagery, thumbnails, source filename,
unchanged role, status and approve/reject controls. Existing decisions cannot be
silently revoked. New decisions are local to the browser and must be exported and
imported into the durable register before publication; they do not modify the
shop/backend or automatically approve other images. `?test=1` uses in-memory
test decisions only, so browser validation cannot fabricate owner approvals.

## Build, verification and rollback

`build_r016_staging.py` starts from the hash-verified 285-file R01.5 release. Six
existing HTML views change (including the staging root overlay); new assets and
the approval board are added. All previous assets and backend files remain exact.
The previous archive is copied to a local rollback location. The existing
owner-unlocked SSH transport validates the fixed R01.5 baseline manifest and all
database/configuration hashes, then creates a verified server rollback copy.
Post-deployment failure restores the public release without replacing SQLite.

Local checks cover all 12 pairs in strict and proposal modes, exact model/color
matching, role preservation, exclusions and exact owner approval matching.
Existing composition/checkout behavior tests pass. Real local browser interaction
checks cover both tabs for 12 variants at desktop and mobile sizes, changing card
images/links, missing frames, board controls in test mode and responsive layout.
[Deployment evidence and real pf26 browser acceptance](R016-STAGING-ACCEPTANCE.md) include the full matrix, actual screenshots, immutable manifests and preserved database checks.
