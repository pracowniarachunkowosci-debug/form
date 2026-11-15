"""Reuse the existing R01.5/R01.4 audit and exports, never reclassify originals.

Only the already selected 46 records are considered. No session-wide photo audit.
"""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'winter26-design-r01-5/design-r01'
DEST=ROOT/'assets/winter26-r016';DEST.mkdir(parents=True,exist_ok=True)
EVIDENCE=ROOT/'docs/r016';EVIDENCE.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=json.loads((SOURCE/'variant-media.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
media=[];excluded=[]
for a in raw:
    if not a['activeVariant'] or a['ownerStatus']=='REJECTED_QUALITY' or a['galleryDisposition'] in ('ARCHIVED_BY_OWNER','EXCLUDED'):
        excluded.append({k:a[k] for k in ('id','modelId','colorId','role','sourceFile','sourceSha256','ownerStatus','galleryDisposition')});continue
    fields=('id','modelId','colorId','role','label','width','height','sourceFile','sourcePath','sourceSha256','evidence','note')
    m={k:a[k] for k in fields}
    m.update(ownerStatus=a['ownerStatus'] if a['colorConfirmed'] else 'PROPOSAL',colorConfirmed=a['colorConfirmed'],activeVariant=True,galleryIncluded=True)
    # These two existing audit records explicitly require model/geometry confirmation.
    # Keep them in the owner's board, not as selected customer variants.
    m['reviewOnly']=a['id'] in ('WEB006','WEB022')
    m['alt']=a['alt'] if a['colorConfirmed'] else 'Propozycja przypisania: '+a['alt']
    urls={}
    originals=[{'file':a['zoom'],'sha256':a['sourceSha256']}]+a['derivatives']
    for source in originals:
        p=SOURCE/source['file'];assert sha(p)==source['sha256'],p.name
        existing=ROOT/'assets/winter26-r015/variants'/p.name
        if existing.exists():assert sha(existing)==source['sha256'];target=existing
        else:
            target=DEST/'variants'/p.name;target.parent.mkdir(exist_ok=True)
            if not target.exists():shutil.copyfile(p,target)
            assert sha(target)==source['sha256']
        urls[source['file']]='/'+target.relative_to(ROOT).as_posix()
    for key in ('src','thumb','zoom'):m[key]=urls[a[key]]
    m['srcset']=', '.join(urls[x['file']]+' '+str(x['width'])+'w' for x in a['derivatives'] if x['width']>=480)
    media.append(m)
assert len(media)==43 and sum(m['ownerStatus']=='OWNER APPROVED' for m in media)==1
(DEST/'variant-media.js').write_text('// Existing audited candidates; proposals are not production approvals.\nexport const variantMedia = '+json.dumps(media,ensure_ascii=False,indent=2)+';\n',encoding='utf-8',newline='\n')
models={'full-soft':'VASE','knitted-star':'KNITTED STAR','knitted-medallion':'KNITTED MEDALLION'}
colors={'dual':'Dual','red-matte':'Czerwony matowy','white':'Biały','marble':'Marble'}
matrix=[]
for model,name in models.items():
 for color,label in colors.items():
    group=[m for m in media if (m['modelId'],m['colorId'])==(model,color)]
    matrix.append({'modelId':model,'model':name,'colorId':color,'color':label,'confirmed':[m['id'] for m in group if m['colorConfirmed']],'proposals':[m['id'] for m in group if not m['colorConfirmed']],'reviewOnly':[m['id'] for m in group if m['reviewOnly']],'roles':{r:sum(m['role']==r for m in group) for r in ('main','gallery','detail','lifestyle')},'missingAll':not group})
for name,value in [('matrix.json',matrix),('media-provenance.json',media),('excluded.json',excluded)]:
 (EVIDENCE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'records':len(media),'confirmed':sum(m['colorConfirmed'] for m in media),'proposals':sum(not m['colorConfirmed'] for m in media),'reviewOnly':sum(m['reviewOnly'] for m in media),'missing':[(m['model'],m['color']) for m in matrix if m['missingAll']]}))
