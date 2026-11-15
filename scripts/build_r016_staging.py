"""Fresh visual-only R01.6 package against the verified deployed R01.5 manifest."""
from pathlib import Path
import hashlib,json,re,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'.artifacts/r016-release';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT)
e=ROOT/'docs/r015-20261115';previous=json.loads((e/'release.json').read_text());rows=json.loads((e/'manifest.json').read_text())
assert sha((e/'manifest.json').read_bytes().replace(b'\r\n',b'\n'))==previous['manifest_sha256']
saved=ROOT/'.artifacts/r016-backup/r015-public.zip'
archive=saved if saved.exists() else ROOT/'.artifacts/r015-release/winter26-r015-staging.zip'
assert sha(archive.read_bytes())==previous['archive_sha256']
verification=json.loads((ROOT/'.artifacts/r015-session/verify-before-r016.json').read_text())
assert verification['verified'] and verification['all_285_deployed_hashes'] and verification['all_tables_orders_stock_events_config_unchanged_after_verify']
modified={'index.html','winter-26.html','winter-full-soft.html','winter-knitted-star.html','winter-knitted-medallion.html','winter-zestaw-4.html'}
blobs={}
with zipfile.ZipFile(archive) as z:
 for r in rows:
  n=r['path'];old=z.read(n);assert sha(old)==r['sha256']
  if n in modified:
   p=ROOT/('winter-26.html' if n=='index.html' else n);blobs[n]=p.read_bytes().replace(b'\r\n',b'\n')
  elif n in ('.htaccess','robots.txt'):blobs[n]=old
  else:
   current=(ROOT/n).read_bytes()
   if sha(current)!=r['sha256']:current=current.replace(b'\r\n',b'\n')
   assert sha(current)==r['sha256'],('Protected source differs',n)
   blobs[n]=current
 # Keep a verified local R01.5 rollback package before transport metadata changes.
 backup=ROOT/'.artifacts/r016-backup';backup.mkdir(exist_ok=True)
 (backup/'r015-public.zip').write_bytes(archive.read_bytes())
 (backup/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n')
for p in [ROOT/'winter-foto-r016.html',*sorted((ROOT/'assets/winter26-r016').rglob('*'))]:
 if p.is_file():
  assert p.suffix in ('.html','.js','.css','.jpg','.webp','.avif','.png','.svg')
  b=p.read_bytes();blobs[p.relative_to(ROOT).as_posix()]=b.replace(b'\r\n',b'\n') if p.suffix in ('.html','.js','.css','.svg') else b
# No checkout/controller, PHP, prices, availability, shipping, catalog or legal change.
base='958f4b3dff3307e25c2b57ee72a7330a99289f01'
for r in rows:
 n=r['path']
 if n not in modified:assert sha(blobs[n])==r['sha256']
 if n in ('winter-config.js','api/result.php') or n.endswith('.json') or n.startswith('api/'):
  assert (ROOT/n).read_bytes().replace(b'\r\n',b'\n')==git('show',base+':'+n).replace(b'\r\n',b'\n'),n
old=git('show',base+':winter-zestaw-4.html').decode();new=blobs['winter-zestaw-4.html'].decode()
assert re.search(r'id="winter-options">(.*?)</script>',old,re.S).group(1)==re.search(r'id="winter-options">(.*?)</script>',new,re.S).group(1)
media=json.loads(blobs['assets/winter26-r016/variant-media.js'].decode().split('=',1)[1].strip().rstrip(';'))
assert len(media)==42 and sum(m['ownerStatus']=='OWNER APPROVED' for m in media)==1
assert sum(m['colorConfirmed'] for m in media)==11
for m in media:
 assert m['ownerStatus'] in ('OWNER APPROVED','OWNER COLOR CONFIRMED','PROPOSAL')
 assert m['id'] not in ('WEB018','WEB016','knitted-star-white-scene-3') and m['colorId']!='cappuccino'
 assert sha(blobs[m['zoom'].lstrip('/')])==m['sourceSha256']
for n,b in blobs.items():
 assert not re.search(r'(?i)(?:^|/)(?:\.git|\.env|config|runtime|tests?|docs|scripts)(?:/|$)|\.(?:sqlite|db|dpapi|pem|key|zip)$',n)
 if n.endswith(('.html','.js','.css','.php','.json','.txt')):
  assert not re.search(rb'(?:sk_(?:live|test)_[A-Za-z0-9]{16,}|whsec_[A-Za-z0-9]{16,}|-----BEGIN .*PRIVATE KEY|[A-Z]:\\Users\\)',b),n
manifest=[{'path':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(blobs.items())]
with zipfile.ZipFile(OUT/'winter26-r016-staging.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in sorted(blobs.items()):
  i=zipfile.ZipInfo(n,(1980,1,1,0,0,0));i.create_system=3;i.external_attr=0o100644<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,b)
with zipfile.ZipFile(OUT/'winter26-r016-staging.zip') as z:
 assert z.testzip() is None and z.namelist()==[r['path'] for r in manifest]
 assert all(sha(z.read(r['path']))==r['sha256'] for r in manifest)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
old={r['path']:r['sha256'] for r in rows}
delta=[{'path':r['path'],'change':'modified' if r['path'] in old else 'added','sha256':r['sha256']} for r in manifest if old.get(r['path'])!=r['sha256']]
assert {d['path'] for d in delta if d['change']=='modified'}==modified
release={'edition':'R01.6','target':'https://pf26.uber.space','base':base,'source_commit':git('rev-parse','HEAD').decode().strip(),'source_dirty':bool(git('status','--porcelain')),'archive_sha256':sha((OUT/'winter26-r016-staging.zip').read_bytes()),'manifest_sha256':sha((OUT/'manifest.json').read_bytes()),'files':len(manifest),'changed':delta,'deleted':[],'protectedFilesUnchanged':True,'baseline_manifest':rows,'baseline_manifest_sha256':previous['manifest_sha256'],'photoCounts':{'records':len(media),'ownerApproved':1,'colorConfirmedAdditional':sum(m['colorConfirmed'] for m in media)-1,'proposals':sum(m['ownerStatus']=='PROPOSAL' for m in media),'reviewOnly':sum(m['reviewOnly'] for m in media)}}
(OUT/'release.json').write_text(json.dumps(release,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in release.items() if k not in ('changed','baseline_manifest')},indent=2))
