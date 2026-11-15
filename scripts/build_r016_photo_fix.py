"""Fresh 382-file release; only the owner-confirmed photograph map may differ."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.artifacts/r016-photo-fix';OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT)
previous=json.loads((ROOT/'docs/r016/release.json').read_text())
baseline=(ROOT/'docs/r016/manifest.json').read_bytes().replace(b'\r\n',b'\n')
assert sha(baseline)==previous['manifest_sha256']=='b0b872737ea303d693e7340f6b7b0544e7441485070caba17f36402b9e2f640a'
rows=json.loads(baseline);assert len(rows)==382
archive=ROOT/'.artifacts/r016-release/winter26-r016-staging.zip'
assert sha(archive.read_bytes())==previous['archive_sha256']
(OUT/'previous-r016.zip').write_bytes(archive.read_bytes())
changed='assets/winter26-r016/variant-media.js';blobs={}
with zipfile.ZipFile(archive) as z:
 for r in rows:
  n=r['path'];old=z.read(n);assert sha(old)==r['sha256']
  if n in ('.htaccess','robots.txt'):b=old
  else:
   b=(ROOT/('winter-26.html' if n=='index.html' else n)).read_bytes()
   if n.endswith(('.html','.js','.css','.svg','.php','.json','.txt','.xml')):b=b.replace(b'\r\n',b'\n')
  if n!=changed:assert sha(b)==r['sha256'],('Protected file changed',n)
  blobs[n]=b
old={r['path']:r['sha256'] for r in rows}
assert [n for n,b in blobs.items() if sha(b)!=old[n]]==[changed]
media=json.loads(blobs[changed].decode().split('=',1)[1].strip().rstrip(';'))
assert len(media)==42 and sum(m['ownerStatus']=='OWNER APPROVED' for m in media)==1 and sum(m['colorConfirmed'] for m in media)==11
for m in media:assert sha(blobs[m['zoom'].lstrip('/')])==m['sourceSha256']
manifest=[{'path':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(blobs.items())]
package=OUT/'winter26-r016-photo-fix.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in sorted(blobs.items()):
  i=zipfile.ZipInfo(n,(1980,1,1,0,0,0));i.create_system=3;i.external_attr=0o100644<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,b)
with zipfile.ZipFile(package) as z:
 assert z.testzip() is None and z.namelist()==[r['path'] for r in manifest]
 assert all(sha(z.read(r['path']))==r['sha256'] for r in manifest)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
release={'edition':'R01.6','revision':'owner-photo-correction-20261115','target':'https://pf26.uber.space','source_commit':git('rev-parse','HEAD').decode().strip(),'source_dirty':bool(git('status','--porcelain')),'archive_sha256':sha(package.read_bytes()),'manifest_sha256':sha((OUT/'manifest.json').read_bytes()),'files':len(manifest),'changed':[{'path':changed,'change':'modified','sha256':sha(blobs[changed])}],'deleted':[],'baseline_manifest':rows,'baseline_manifest_sha256':previous['manifest_sha256'],'protectedFilesUnchanged':True}
(OUT/'release.json').write_text(json.dumps(release,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in release.items() if k!='baseline_manifest'},indent=2))
