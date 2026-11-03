"""Build a local static release archive. Does not upload or change hosting."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.artifacts'
OUT.mkdir(exist_ok=True)
subprocess.run([sys.executable, str(ROOT/'scripts/check_publication.py')], check=True, cwd=ROOT)
files = sorted([*ROOT.glob('*.html'), *ROOT.glob('*.css'), ROOT/'script.js', ROOT/'favicon.svg', ROOT/'robots.txt', ROOT/'sitemap.xml', *[p for p in (ROOT/'assets').rglob('*') if p.is_file()]])
allowed_assets = {'.avif', '.webp', '.jpg', '.jpeg', '.png', '.svg', '.woff', '.woff2'}
assert all(p.suffix.lower() in allowed_assets for p in files if 'assets' in p.relative_to(ROOT).parts)
manifest = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
with zipfile.ZipFile(OUT/'pracownia-form-lh.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for p in files:
        archive.write(p, p.relative_to(ROOT).as_posix())
(OUT/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'Local archive only: {len(files)} files, {sum(item["bytes"] for item in manifest):,} bytes uncompressed.')
print(f'Archive SHA-256: {hashlib.sha256((OUT/"pracownia-form-lh.zip").read_bytes()).hexdigest()}')
