"""Extract the owner-supplied screenshot's scene without generative changes.

Requires Pillow with AVIF. Usage: python scripts/prepare_concept_hero.py screenshot.png
The crop is specific to the reviewed 1505x1045 screenshot, not arbitrary uploads.
"""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, __version__

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1])
original = Image.open(source).convert('RGB')
assert original.size == (1505, 1045), 'Unexpected screenshot dimensions; review crop before proceeding'
box = (722, 187, 1415, 880)
scene = original.crop(box)
source_dir = root / 'docs/sources'
source_dir.mkdir(exist_ok=True)
scene.save(source_dir / 'open-bauble-concept.png')
outputs = []
for width in (360, 480, 693):
    resized = scene.resize((width, width), Image.Resampling.LANCZOS)
    for extension, options in [('avif', {'quality': 55, 'speed': 6}), ('webp', {'quality': 82, 'method': 6})]:
        path = root / f'assets/winter-open-concept-{width}.{extension}'
        resized.save(path, **options)
        outputs.append({'file': path.relative_to(root).as_posix(), 'width': width,
                        'height': width, 'bytes': path.stat().st_size,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
report = {'status': 'AI concept preview, not a product photograph',
          'source': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'source_dimensions': list(original.size), 'crop_xyxy': list(box),
          'crop_dimensions': list(scene.size), 'upscaled': False, 'pillow': __version__,
          'outputs': outputs}
(root/'docs/hero-concept-optimization.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(report, indent=2))
