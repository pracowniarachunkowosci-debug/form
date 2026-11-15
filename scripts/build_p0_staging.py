"""Fresh complete pf26 release from a clean Git checkout; no network/credentials/database.

Only two public PHP files may differ from the accepted 382-file R01.6 manifest,
plus the new reservation helper. Private scheduler files are packaged separately.
"""
from pathlib import Path
import hashlib, json, re, subprocess, zipfile, os

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.artifacts/p0-build'
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda *args:subprocess.check_output(['git','-c','core.autocrlf=false',*args],cwd=ROOT)
assert not git('status','--porcelain').strip(), 'A clean committed worktree is required'
head=git('rev-parse','HEAD').decode().strip()
baseline_file=ROOT/'docs/r016/photo-correction/manifest.json'
baseline_bytes=baseline_file.read_bytes().replace(b'\r\n',b'\n')
release=json.loads((ROOT/'docs/r016/photo-correction/release.json').read_text())
assert sha(baseline_bytes)==release['manifest_sha256']
baseline=json.loads(baseline_bytes);assert len(baseline)==382
modified={'api/_common.php','api/checkout.php'}
public={}
for row in baseline:
    name=row['path']
    source=ROOT/('ops/p0/public/'+name if name in ('.htaccess','robots.txt') else 'winter-26.html' if name=='index.html' else name)
    data=source.read_bytes()
    if source.suffix in ('.html','.css','.js','.cjs','.php','.json','.svg','.xml','.txt') or name=='.htaccess':
        data=data.replace(b'\r\n',b'\n')
    if name not in modified:assert sha(data)==row['sha256'], 'Protected source differs: '+name
    public[name]=data
public['api/_reservations.php']=(ROOT/'api/_reservations.php').read_bytes().replace(b'\r\n',b'\n')
assert len(public)==383
private={'scripts/reconcile-reservations.php':(ROOT/'scripts/reconcile-reservations.php').read_bytes().replace(b'\r\n',b'\n')}
for name in ('reconcile-tick.sh','reconcile-notify.sh'):
    private['scripts/'+name]=(ROOT/'ops/p0'/name).read_bytes().replace(b'\r\n',b'\n')
for name in ('pf26-reconcile.service','pf26-reconcile.timer','pf26-reconcile-alert.service'):
    private['systemd/'+name]=(ROOT/'ops/p0'/name).read_bytes().replace(b'\r\n',b'\n')

secret=re.compile(rb'(?:sk_(?:live|test)_[A-Za-z0-9]{16,}|whsec_[A-Za-z0-9]{16,}|-----BEGIN [A-Z ]*PRIVATE KEY|https://hc-ping[.]com/[0-9a-f]{8}-|[A-Z]:\\Users\\)')
for name,data in public.items():
    assert not re.search(r'(?i)(?:^|/)(?:[.]git|[.]env|config|runtime|tests?|docs|scripts)(?:/|$)|[.](?:sqlite|db|dpapi|pem|key|zip)$',name),name
for group in (public,private):
    for name,data in group.items():
        if name.endswith(('.php','.html','.css','.js','.json','.txt','.sh','.service','.timer')) or name=='.htaccess':
            assert not secret.search(data),'Secret marker: '+name

OUT.mkdir(parents=True,exist_ok=True)
php=os.environ.get('PF_PHP_BIN','php');lint={}
for name,data in {**public,**{'private/'+n:b for n,b in private.items()}}.items():
    if name.endswith('.php'):
        p=OUT/'lint'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        result=subprocess.run([php,'-l',str(p)],capture_output=True,text=True)
        lint[name]=result.returncode==0
assert all(lint.values()),'Packaged PHP failed lint'

def package(label,blobs):
    rows=[{'path':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(blobs.items())]
    archive=OUT/('winter26-p0-'+label+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(blobs.items()):
            i=zipfile.ZipInfo(n,(1980,1,1,0,0,0));i.create_system=3
            i.external_attr=(0o100600 if label=='private' else 0o100644)<<16
            i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,b)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and z.namelist()==[r['path'] for r in rows]
        assert all(sha(z.read(r['path']))==r['sha256'] for r in rows)
    manifest=OUT/(label+'-manifest.json');manifest.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n')
    return {'archive':archive.name,'sha256':sha(archive.read_bytes()),'files':len(rows),'manifest':manifest.name,'manifestSha256':sha(manifest.read_bytes())}

old={r['path']:r['sha256'] for r in baseline}
delta=[{'path':n,'change':'modified' if n in old else 'added','sha256':sha(b)} for n,b in sorted(public.items()) if old.get(n)!=sha(b)]
assert {r['path'] for r in delta}==modified|{'api/_reservations.php'}
report={'sourceCommit':head,'cleanWorktree':True,'baselineManifestSha256':sha(baseline_bytes),
    'public':package('public',public),'private':package('private',private),'publicDelta':delta,'publicDeleted':[],
    'protectedPublicFilesUnchanged':380,'phpLint':lint,'secretScan':'PASS','freshSourceBuild':True,
    'historicalArchiveUsedByBuilder':False,'uploaded':False,'databaseOpened':False}
assert not git('status','--porcelain').strip(),'Build changed tracked files'
(OUT/'build-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(report,indent=2))
