"""Verify a local copy of PF-W26-FINAL. No network or deployment operations."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree

FINAL_MANIFEST = "b5047c5fdd51a24908726428b046a073ddd5ee6ab1ae62dee5d3e9b12ba7da00"


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.robots = set()
        self.canonical = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name", "").lower() == "robots":
            self.robots.update(v.strip().lower() for v in attrs["content"].split(","))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical.append(attrs["href"])


def verify_final(root, manifest, staging):
    raw = manifest.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FINAL_MANIFEST:
        raise ValueError("Unrecognized production manifest")
    files = {row["path"]: row for row in json.loads(raw)}
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    if actual != set(files):
        raise ValueError("Missing or extra files in the production reference")
    for name, row in files.items():
        data = (root / name).read_bytes()
        if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError(f"Production reference mismatch: {name}")
    for loc in ElementTree.parse(root / "sitemap.xml").findall(".//{*}loc"):
        url = urlsplit(loc.text)
        if (url.scheme, url.netloc) != ("https", "pracowniaform.com"):
            raise ValueError(f"Unexpected sitemap origin: {loc.text}")
        name = url.path.lstrip("/")
        if not name or name.endswith("/"):
            name += "index.html"
        meta = Metadata()
        meta.feed((root / name).read_text(encoding="utf8"))
        if meta.canonical != [loc.text] or meta.robots & {"noindex", "nofollow", "none"}:
            raise ValueError(f"Unindexable sitemap page or wrong canonical: {name}")
    meta = Metadata()
    meta.feed(staging.read_text(encoding="utf8"))
    if not {"noindex", "nofollow", "noarchive"} <= meta.robots:
        raise ValueError("Staging indexing protection missing")
    print(f"Verified {len(files)} approved production files, sitemap and staging robots")
