"""Validate the WINTER 26 photo handoff without assigning photos to SKUs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED_SOURCE_IDS = {
    "004", "008", "014", "232", "238", "243", "244", "245", "248", "250",
    "255", "257", "258", "259", "260", "261", "262", "263", "045", "171",
    "213", "083", "146",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("handoff", type=Path)
    args = parser.parse_args()
    manifest_path = args.handoff / "PRODUCT_PHOTO_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assets = manifest.get("assets", [])
    failures: list[str] = []

    if manifest.get("collection") != "WINTER 26":
        failures.append("manifest collection is not WINTER 26")
    if manifest.get("asset_count") != 26 or len(assets) != 26:
        failures.append("expected exactly 26 assets")
    if manifest.get("automatic_assignment_allowed") is not False:
        failures.append("automatic assignment must remain disabled")

    source_ids = {str(asset.get("source_image_id")) for asset in assets}
    if source_ids != EXPECTED_SOURCE_IDS:
        failures.append(f"unexpected source id set: {sorted(source_ids ^ EXPECTED_SOURCE_IDS)}")

    for asset in assets:
        asset_id = asset.get("asset_id", "unknown")
        if asset.get("product_name") != "DO POTWIERDZENIA":
            failures.append(f"{asset_id}: product identity is already exposed")
        if asset.get("SKU") != "DO POTWIERDZENIA":
            failures.append(f"{asset_id}: SKU is already exposed")
        if asset.get("product_slug") is not None:
            failures.append(f"{asset_id}: product_slug must remain null")
        if asset.get("ready_for_auto_assignment") is not False:
            failures.append(f"{asset_id}: ready_for_auto_assignment must be false")
        if asset.get("same_product_assignment_confirmed") is not False:
            failures.append(f"{asset_id}: same_product_assignment_confirmed must be false")
        relative_path = asset.get("relative_path")
        if not isinstance(relative_path, str) or not (args.handoff / relative_path).is_file():
            failures.append(f"{asset_id}: missing handoff file")

    if failures:
        print("PHOTO_HANDOFF FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    roles = {role: sum(asset.get("image_role") == role for asset in assets) for role in ("main", "gallery", "detail")}
    editors = {editor: sum(asset.get("editing_source") == editor for asset in assets) for editor in ("Codex", "Claude")}
    print("PHOTO_HANDOFF PASS")
    print(f"assets={len(assets)} source_ids={len(source_ids)} roles={roles} editors={editors}")
    print("assignment=blocked_until_owner_confirmation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
