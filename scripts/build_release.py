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
for check in (['scripts/render_store.py', '--check'], ['scripts/check_store_gate.py']):
    subprocess.run([sys.executable, *check], check=True, cwd=ROOT)
subprocess.run([sys.executable, str(ROOT/'scripts/check_publication.py')], check=True, cwd=ROOT)
files = sorted([*ROOT.glob('*.html'), *ROOT.glob('*.css'), ROOT/'script.js', ROOT/'store-gallery.js', ROOT/'favicon.svg', ROOT/'robots.txt', ROOT/'sitemap.xml', *[p for p in (ROOT/'assets').rglob('*') if p.is_file()]])
allowed_assets = {'.avif', '.webp', '.jpg', '.jpeg', '.png', '.svg', '.woff', '.woff2'}
assert all(p.suffix.lower() in allowed_assets for p in files if 'assets' in p.relative_to(ROOT).parts)
manifest = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
with zipfile.ZipFile(OUT/'pracownia-form-lh.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for p in files:
        info = zipfile.ZipInfo(p.relative_to(ROOT).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, p.read_bytes(), compresslevel=9)
(OUT/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
with zipfile.ZipFile(OUT/'pracownia-form-lh.zip') as archive:
    assert archive.testzip() is None
    assert archive.namelist() == [item['path'] for item in manifest]
    for item in manifest:
        assert hashlib.sha256(archive.read(item['path'])).hexdigest() == item['sha256']
release = {
    'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'source_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT)),
    'archive': 'pracownia-form-lh.zip',
    'archive_sha256': hashlib.sha256((OUT/'pracownia-form-lh.zip').read_bytes()).hexdigest(),
    'archive_bytes': (OUT/'pracownia-form-lh.zip').stat().st_size,
    'manifest_sha256': hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest(),
    'files': len(files), 'deployment_authorized': False
}
(OUT/'release.json').write_text(json.dumps(release, indent=2)+'\n', encoding='utf-8')
print(f'Local archive only: {len(files)} files, {sum(item["bytes"] for item in manifest):,} bytes uncompressed.')
print(json.dumps(release))
