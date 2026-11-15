"""Build a local LH webroot archive from a clean checkout; no upload or provider calls."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GIT_DIR = os.environ.get('PF_GIT_DIR')
GIT = ['git', '-c', 'safe.directory=*']
if GIT_DIR:
    GIT += ['--git-dir', GIT_DIR, '--work-tree', str(ROOT)]

def git(*args: str) -> bytes:
    return subprocess.check_output([*GIT, *args], cwd=ROOT)

commit = git('rev-parse', 'HEAD').decode().strip()
if git('status', '--porcelain'):
    sys.exit('Release requires a clean checkout; commit or isolate your changes first.')
OUT = ROOT / '.artifacts' / ('lh-' + commit[:12])
OUT.mkdir(parents=True, exist_ok=True)
def payload(p):
    data = p.read_bytes()
    return data.replace(b'\r\n', b'\n') if p.suffix in {'.html','.js','.css','.svg','.txt','.xml'} else data

for check in (['scripts/check_winter26_pricing.py'], ['scripts/render_store.py', '--check'], ['scripts/check_render_eol.py'], ['scripts/check_config_registry.py'], ['scripts/check_store_gate.py']):
    subprocess.run([sys.executable, *check], check=True, cwd=ROOT)
subprocess.run([sys.executable, str(ROOT/'scripts/check_publication.py')], check=True, cwd=ROOT)
subprocess.run(['node','scripts/check_consent.cjs'], cwd=ROOT, check=True)
subprocess.run(['node','--check','store-gallery.js'], cwd=ROOT, check=True)
subprocess.run(['node','scripts/check_config.cjs'], cwd=ROOT, check=True)
subprocess.run(['node','scripts/check_store_composition.cjs'],cwd=ROOT,check=True)
subprocess.run(['node','tests/configurator-journey.cjs'],cwd=ROOT,check=True)
php = os.environ.get('PF_PHP_BIN') or shutil.which('php')
if not php:
    sys.exit('PHP CLI with curl and PDO SQLite is required to verify this release (set PF_PHP_BIN).')
for source in sorted((ROOT/'api').glob('*.php')):
    subprocess.run([php,'-l',str(source)],check=True,cwd=ROOT,stdout=subprocess.DEVNULL)
for suite in ('tests/checkout-sandbox.php','tests/checkout-live-gates.php','tests/checkout-locker.php'):
    subprocess.run([php,suite],check=True,cwd=ROOT)
subprocess.run(['node','tests/inpost-mock-ui.cjs'],check=True,cwd=ROOT,env={**os.environ,'PF_PHP_BIN':php})
# Only program sources and public catalogs: no private configuration, databases or test drivers.
backend = sorted((ROOT/'api').glob('*.php'))
catalogs = [ROOT/'data/winter26-pricing-pl.json', ROOT/'data/winter26-products.json']
files = sorted([*backend, *catalogs, *ROOT.glob('*.html'), *ROOT.glob('*.css'), ROOT/'script.js', ROOT/'store-gallery.js', ROOT/'winter-config.js', ROOT/'favicon.svg', ROOT/'robots.txt', ROOT/'sitemap.xml', *[p for p in (ROOT/'assets').rglob('*') if p.is_file()]], key=lambda p: p.relative_to(ROOT).as_posix())
allowed_assets = {'.avif', '.webp', '.jpg', '.jpeg', '.png', '.svg', '.woff', '.woff2'}
assert all(p.suffix.lower() in allowed_assets for p in files if 'assets' in p.relative_to(ROOT).parts)
blobs = {p.relative_to(ROOT).as_posix(): payload(p) for p in files}
manifest = [{'path': name, 'bytes': len(blob), 'sha256': hashlib.sha256(blob).hexdigest()} for name, blob in blobs.items()]
with zipfile.ZipFile(OUT/'pracownia-form-lh.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for p in files:
        info = zipfile.ZipInfo(p.relative_to(ROOT).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, blobs[info.filename], compresslevel=9)
(OUT/'manifest.json').write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode())
with zipfile.ZipFile(OUT/'pracownia-form-lh.zip') as archive:
    assert archive.testzip() is None
    assert archive.namelist() == [item['path'] for item in manifest]
    for item in manifest:
        assert hashlib.sha256(archive.read(item['path'])).hexdigest() == item['sha256']
release = {
    'source_commit': commit,
    'source_dirty': bool(git('status', '--porcelain')),
    'archive': 'pracownia-form-lh.zip',
    'archive_sha256': hashlib.sha256((OUT/'pracownia-form-lh.zip').read_bytes()).hexdigest(),
    'archive_bytes': (OUT/'pracownia-form-lh.zip').stat().st_size,
    'manifest_sha256': hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest(),
    'files': len(files), 'deployment_target': 'LH Orange', 'uploaded_by_this_build': False
}
(OUT/'release.json').write_text(json.dumps(release, indent=2)+'\n', encoding='utf-8')
print(f'Output: {OUT}')
print(f'Local archive only: {len(files)} files, {sum(item["bytes"] for item in manifest):,} bytes uncompressed.')
print(json.dumps(release))
