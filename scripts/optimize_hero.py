"""Re-encode approved R04, without altering composition. Requires Pillow with AVIF.
Usage: python scripts/optimize_hero.py /path/to/winter-after-dark-r04.png
"""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, __version__

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1])
original = Image.open(source).convert('RGB')
assert original.size == (1536, 1024), 'Use the approved R04 source'
outputs = []
for width in (480, 768, 1024, 1536):
    resized = original.resize((width, round(width * 2 / 3)), Image.Resampling.LANCZOS)
    for extension, options in [('avif', {'quality': 53, 'speed': 6}), ('webp', {'quality': 80, 'method': 6})]:
        path = root / f'assets/winter-r04-{width}.{extension}'
        resized.save(path, **options)
        outputs.append({'file': path.relative_to(root).as_posix(), 'width': width,
                        'height': resized.height, 'bytes': path.stat().st_size})
share = root / 'assets/winter-r04-social.jpg'
original.resize((1200, 800), Image.Resampling.LANCZOS).save(share, quality=85, optimize=True, progressive=True)
outputs.append({'file': share.relative_to(root).as_posix(), 'width': 1200, 'height': 800, 'bytes': share.stat().st_size})
report = {'source': source.name, 'source_bytes': source.stat().st_size,
          'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'pillow': __version__, 'outputs': outputs}
(root / 'docs').mkdir(exist_ok=True)
(root / 'docs/hero-optimization.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
