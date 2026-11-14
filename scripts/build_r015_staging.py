"""Fresh pf26-only visual release; preserves the verified security overlay.

Requires the owner-local read-only baseline made by r015_session.py.
Does not connect, deploy, read credentials or open a database.
"""
from pathlib import Path
import hashlib,json,re,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1]
BASE='ec8495f5716b001d43e81f078e7de2b97f16718d'
OUT=ROOT/'.artifacts/r015-release';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda x:hashlib.sha256(x).hexdigest()
git=lambda *a:subprocess.check_output(['git',*a],cwd=ROOT)
baseline=json.loads((ROOT/'.artifacts/r015-session/baseline.json').read_text())
backup=ROOT/'.artifacts/r015-backups'/baseline['backupId']/'public.zip'
assert sha(backup.read_bytes())==baseline['archiveSha256']
changed={'index.html','winter-26.html','winter-full-soft.html','winter-knitted-star.html','winter-knitted-medallion.html','winter-zestaw-4.html','winter-config.js','api/result.php'}
blobs={}
with zipfile.ZipFile(backup) as z:
 for row in baseline['files']:
  name=row['path'];old=z.read(name);assert sha(old)==row['sha256']
  if name in ('.htaccess','robots.txt'):blob=old
  else:
   source=ROOT/('winter-26.html' if name=='index.html' else name)
   blob=source.read_bytes()
   if source.suffix in ('.html','.js','.css','.svg','.txt','.xml') or name=='api/result.php':blob=blob.replace(b'\r\n',b'\n')
  if name not in changed:assert blob==old,('Protected file changed',name)
  blobs[name]=blob
for p in sorted((ROOT/'assets/winter26-r015').rglob('*')):
 if p.is_file():
  assert p.suffix in ('.js','.css','.jpg','.webp','.avif','.png','.svg')
  blob=p.read_bytes()
  if p.suffix in ('.js','.css','.svg'):blob=blob.replace(b'\r\n',b'\n')
  blobs[p.relative_to(ROOT).as_posix()]=blob
assert len(blobs)>124 and len(baseline['files'])==124
# Keep all executable result-page PHP and the checkout request/availability code exact.
old=git('show',BASE+':api/result.php').decode()
assert re.findall(r'<\?php(.*?)\?>',old,re.S)==re.findall(r'<\?php(.*?)\?>',blobs['api/result.php'].decode(),re.S)
old=git('show',BASE+':winter-config.js').decode();new=blobs['winter-config.js'].decode()
for marker,end in [("get('[data-checkout]').onclick=async",'\n    async function availability'),('    async function availability',None)]:
 assert marker in old and marker in new,marker
 a=old[old.index(marker):];b=new[new.index(marker):]
 if end and end in a:a=a[:a.index(end)];b=b[:b.index(end)]
 # Availability's tail includes final initialize/draw calls, preserved too.
 assert a==b,('Checkout behavior changed',marker)
# Embedded commercial data is the exact existing source, never prototype values.
for name in ('winter-zestaw-4.html',):
 before=git('show',BASE+':'+name).decode();after=blobs[name].decode()
 assert re.search(r'id="winter-options">(.*?)</script>',before,re.S).group(1)==re.search(r'id="winter-options">(.*?)</script>',after,re.S).group(1)
media=json.loads(blobs['assets/winter26-r015/variant-media.js'].decode().split('=',1)[1].strip().rstrip(';'))
assert len(media)==25 and sum(x['role']!='lifestyle' for x in media)==5
assert sum(x['ownerStatus']=='OWNER APPROVED' for x in media)==1
for m in media:
 assert m['role']=='lifestyle' or m['colorConfirmed']
 assert m['ownerStatus'] not in ('REJECTED_QUALITY','ARCHIVED_BY_OWNER')
 assert sha(blobs[m['zoom'].lstrip('/')])==m['sourceSha256']
for name,blob in blobs.items():
 assert not re.search(r'(?i)(?:^|/)(?:\.git|\.env|config|runtime|tests?|docs|scripts)(?:/|$)|\.(?:sqlite|db|dpapi|pem|key|zip)$',name),name
 if name.endswith(('.html','.js','.css','.php','.json','.txt')):
  assert not re.search(rb'(?:sk_(?:live|test)_[A-Za-z0-9]{16,}|whsec_[A-Za-z0-9]{16,}|-----BEGIN .*PRIVATE KEY|[A-Z]:\\Users\\)',blob),name
manifest=[{'path':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(blobs.items())]
with zipfile.ZipFile(OUT/'winter26-r015-staging.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in sorted(blobs.items()):
  i=zipfile.ZipInfo(n,(1980,1,1,0,0,0));i.create_system=3;i.external_attr=0o100644<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,b)
with zipfile.ZipFile(OUT/'winter26-r015-staging.zip') as z:
 assert z.testzip() is None and z.namelist()==[r['path'] for r in manifest]
 assert all(sha(z.read(r['path']))==r['sha256'] for r in manifest)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
old={r['path']:r['sha256'] for r in baseline['files']}
delta=[{'path':r['path'],'change':'modified' if r['path'] in old else 'added','sha256':r['sha256']} for r in manifest if old.get(r['path'])!=r['sha256']]
release={'target':'https://pf26.uber.space','base':BASE,'source_commit':git('rev-parse','HEAD').decode().strip(),'source_dirty':bool(git('status','--porcelain')),'archive_sha256':sha((OUT/'winter26-r015-staging.zip').read_bytes()),'manifest_sha256':sha((OUT/'manifest.json').read_bytes()),'files':len(manifest),'changed':delta,'deleted':[],'protectedFilesUnchanged':True,'rootOverlay':'index.html <- winter-26.html','photoCounts':{'lifestyle':20,'confirmedProduct':5,'ownerApproved':1}}
(OUT/'release.json').write_text(json.dumps(release,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in release.items() if k!='changed'},indent=2))
print('Changes:',len(delta),'modified:',sum(x['change']=='modified' for x in delta))
