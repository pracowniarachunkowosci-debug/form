"""Encode selected owner materials without retouching. Pass the input folder as argv[1].
Requires Pillow with AVIF. Source PNGs stay outside the web root.
"""
import hashlib, json, sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
folder = Path(sys.argv[1])
board = '294daed2-49d0-4179-a336-a5f96c2f108e.png'
def portrait(suffix): return 'Obraz ChatGPT 4 lis 2026, 16_22_'+suffix+'.png'
shots = [
 ('star',portrait('38-4'),None), ('star-loop',board,(873,0,1199,411)),
 ('medallion-loop',board,(609,0,873,411)), ('medallion-detail',portrait('37-3'),None),
 ('helix',portrait('35-2'),None), ('helix-detail',board,(681,770,1199,1312)),
 ('full-soft',portrait('39-5'),None), ('full-soft-side',board,(306,419,598,762)),
 ('four',board,(0,0,1199,411)), ('box',portrait('40-6'),None)]
out=ROOT/'assets/store'; out.mkdir(parents=True,exist_ok=True)
manifest={}
for key,filename,box in shots:
 src=folder/filename
 with Image.open(src) as raw:
    image=raw.convert('RGB')
 if box: image=image.crop(box)
 widths=sorted({min(n,image.width) for n in (360,680,1120)})
 for w in widths:
    small=image.resize((w,round(image.height*w/image.width)),Image.Resampling.LANCZOS)
    for ext,opt in [('avif',dict(quality=52,speed=7)),('webp',dict(quality=80,method=5))]:
       small.save(out/f'{key}-{w}.{ext}',**opt)
 manifest[key]=dict(source=filename,sha256=hashlib.sha256(src.read_bytes()).hexdigest(),crop=box,
                     width=image.width,height=image.height,widths=widths)
(ROOT/'data').mkdir(exist_ok=True)
(ROOT/'data/store-media.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Encoded',len(shots),'reviewed views; originals untouched.')
