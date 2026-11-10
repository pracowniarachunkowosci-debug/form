"""Exercise the generated-page check in isolation on LF, CRLF and a content regression."""
import subprocess
import sys
import tempfile
from pathlib import Path
from shutil import copytree

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as directory:
    tmp = Path(directory)
    for folder in ('data', 'scripts'):
        copytree(root / folder, tmp / folder, ignore=lambda *_: ['__pycache__'])
    for eol in (b'\n', b'\r\n'):
        for source in [*root.glob('*.html'), root / 'sitemap.xml']:
            (tmp / source.name).write_bytes(source.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', eol))
        command = [sys.executable, str(tmp / 'scripts/render_store.py'), '--check']
        subprocess.run(command, cwd=tmp, check=True)
    card = tmp / 'winter-helix.html'
    original = card.read_bytes()
    cta = 'Powiadom mnie o przedsprzedaży'.encode('utf-8')
    assert cta in original
    card.write_bytes(original.replace(cta, b'Nieaktualny opis', 1))
    result = subprocess.run(command, cwd=tmp, capture_output=True)
    assert result.returncode and b'Stale generated page: winter-helix.html' in result.stderr
print('PASS: LF and CRLF render identically; actual card edit is rejected.')
