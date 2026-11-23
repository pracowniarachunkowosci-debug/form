"""Verify the signed-off R01.6 static pages and their active catalog models."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "docs/r016/photo-correction"


class Catalog(HTMLParser):
    def __init__(self):
        super().__init__()
        self.models = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article" and "object-card" in attrs.get("class", "").split():
            self.models.append(attrs.get("data-variant-card"))


def check_pages():
    manifest = (REFERENCE / "manifest.json").read_bytes().replace(b"\r\n", b"\n")
    release = json.loads((REFERENCE / "release.json").read_bytes())
    if hashlib.sha256(manifest).hexdigest() != release["manifest_sha256"]:
        raise ValueError("Unexpected R01.6 page manifest")
    for row in json.loads(manifest):
        name = row["path"]
        if name == "sitemap.xml" or (name.startswith("winter-") and name.endswith(".html")):
            data = (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
            if hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise ValueError(f"Stale generated page: {name}")
    catalog = Catalog()
    catalog.feed((ROOT / "winter-26.html").read_text(encoding="utf-8"))
    pricing = json.loads((ROOT / "data/winter26-pricing-pl.json").read_bytes())
    if sorted(catalog.models) != sorted(pricing["eligibleModelIds"]):
        raise ValueError("Catalog cards differ from eligible pricing models")


if __name__ == "__main__":
    check_pages()
