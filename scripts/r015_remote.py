"""pf26-only deploy/verify/rollback, invoked through an already verified SSH session.
Credentials arrive only on stdin and are never written or included in results.
"""
import os,sys,json,base64,hashlib,zipfile,io,sqlite3,stat,ssl,urllib.request,urllib.error,http.cookiejar,urllib.parse,shutil,time,re,subprocess
from pathlib import Path,PurePosixPath
D=json.load(sys.stdin);report={'deployed':False};changed=[];backup=None
pub=Path('/var/www/virtual/pf26/winter26/app/public')
db=Path('/home/pf26/winter26/runtime/database/sandbox.sqlite')
config=Path('/home/pf26/winter26/config/test.json')
backup_root=pub.parent.parent/'backup'
allowed={'index.html','winter-26.html','winter-full-soft.html','winter-knitted-star.html','winter-knitted-medallion.html','winter-zestaw-4.html','winter-config.js','api/result.php'}
sha=lambda b:hashlib.sha256(b).hexdigest()
old={r['path']:r['sha256'] for r in D['baseline']['files']}
def need(ok,name):
 report[name]=bool(ok)
 if not ok:raise RuntimeError(name)
def snapshot():
 out={'tables':{},'mode':None,'orderStates':{},'databaseMode':oct(stat.S_IMODE(db.stat().st_mode))}
 with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) as c:
  c.execute('PRAGMA query_only=ON');c.execute('BEGIN')
  out['integrity']=c.execute('PRAGMA integrity_check').fetchone()[0]
  for name, in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall():
   assert re.fullmatch('[a-zA-Z_][a-zA-Z_0-9]*',name)
   rows=sorted(json.dumps(list(r),sort_keys=True,ensure_ascii=True,default=str) for r in c.execute('SELECT * FROM "'+name+'"'))
   out['tables'][name]={'rows':len(rows),'sha256':sha(json.dumps(rows).encode())}
  out['orderStates']=dict(c.execute('SELECT state,COUNT(*) FROM orders GROUP BY state'))
  out['mode']=c.execute("SELECT value FROM store_meta WHERE name='mode'").fetchone()[0]
 out['configSha256']=sha(config.read_bytes())
 return out
def inventory(root):
 result={}
 for p in root.rglob('*'):
  assert not p.is_symlink()
  if p.is_file():result[p.relative_to(root).as_posix()]=sha(p.read_bytes())
 return result
def safe_name(n):
 return isinstance(n,str) and '\\' not in n and not n.startswith('/') and all(x not in ('','..','.') for x in n.split('/'))
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k):return None
op=urllib.request.build_opener(NoRedirect(),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
def req(path,auth=False,data=None,wrong=False,ctype='application/x-www-form-urlencoded'):
 assert path.startswith('/') and not path.startswith('//')
 h={'Origin':'https://pf26.uber.space','Content-Type':ctype}
 if auth:
  c=D['credentials'];h['Authorization']='Basic '+base64.b64encode((c['basic_username']+':'+(c['basic_password']+'-wrong' if wrong else c['basic_password'])).encode()).decode()
 r=urllib.request.Request('https://pf26.uber.space'+path,headers=h,data=data)
 try:
  with op.open(r,timeout=30) as res:return res.status,res.read(),res.headers
 except urllib.error.HTTPError as e:return e.code,e.read(),e.headers
def headers(h,label):
 robots=','.join(h.get_all('X-Robots-Tag',[])).lower();cache=','.join(h.get_all('Cache-Control',[])).lower()
 need('noindex' in robots,label+'_noindex');need('noarchive' in robots,label+'_noarchive');need('no-store' in cache,label+'_no_store')
def http_checks(manifest):
 for label,path,data in [('root','/',None),('asset','/assets/winter26-r015/ui.js',None),('checkout','/api/checkout.php',b'{}'),('webhook_get','/api/webhook.php',None),('alt_api','/api//checkout.php',b'{}')]:
  code,body,h=req(path,data=data);need(code==401,'anonymous_'+label+'_401');headers(h,'anonymous_'+label)
 code,_,_=req('/',True,wrong=True);need(code==401,'wrong_password_401')
 code,body,_=req('/api/webhook.php',data=b'{}',ctype='application/json');need(code==400 and json.loads(body).get('code')=='SIGNATURE','unsigned_webhook_400_SIGNATURE')
 for i,path in enumerate(['/config/test.json','/runtime/database/sandbox.sqlite','/winter26/config/test.json','/.htpasswd','/api/_common.php']):
  code,_,_=req(path,True);need(code in (403,404),'private_probe_'+str(i)+'_denied')
 for path in ['index.html','winter-26.html','winter-zestaw-4.html','winter-config.js','winter-full-soft.html','winter-knitted-star.html','winter-knitted-medallion.html','assets/winter26-r015/ui.js']:
  code,body,h=req('/'+path,True);need(code==200 and sha(body)==manifest[path],'authenticated_'+path.replace('/','_')+'_hash');headers(h,'authenticated_'+path.replace('/','_'))
 code,_,_=req('/api/test-access.php',True,urllib.parse.urlencode({'token':D['credentials']['tester_token']}).encode());need(code==303,'tester_login')
 code,body,_=req('/api/status.php',True);status=json.loads(body)
 with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) as c:stock=dict(c.execute('SELECT sku,n FROM stock'))
 need(code==200 and status['mode']=='test' and status['points_provider']=='mock' and status['stock']==stock,'sandbox_status_and_stock')
 for point in ['TEST01M','TEST02M']:
  code,body,_=req('/api/pickup-point.php?id='+point,True);need(code==200 and json.loads(body)['id']==point,'point_'+point)
 for label,path in [('return','/api/result.php'),('cancel','/api/result.php?cancel=1')]:
  code,body,h=req(path,True);need(code==200 and b'/assets/winter26-r015/r01.css' in body,'real_'+label+'_200');headers(h,'real_'+label)
 code,body,_=req('/api/checkout.php',True,b'{}',ctype='application/json');need(code==422,'invalid_checkout_rejected')
 report['httpChecksComplete']=True
def restore(names):
 for name in reversed(names):
  target=pub/name
  if name in old:
   source=backup/name;assert sha(source.read_bytes())==old[name]
   tmp=backup/(name+'.restore');tmp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,tmp);os.replace(tmp,target)
  else:
   # Only this release's exact file can be removed. Never delete a directory recursively.
   assert sha(target.read_bytes())==new[name];target.unlink()
 return inventory(pub)==old
try:
 need(os.getuid()==__import__('pwd').getpwnam('pf26').pw_uid,'account_pf26')
 need(Path('/var/www/virtual/pf26/html').resolve()==pub and pub.resolve()==pub and pub.is_dir(),'existing_documentroot')
 before=snapshot();need(before==D['baseline']['database'],'all_database_tables_and_config_match_baseline')
 need(before['mode']=='test' and before['integrity']=='ok' and before['databaseMode']=='0o600','private_sqlite_test_mode')
 action=D['action'];assert action in ('deploy','verify','rollback')
 if action=='rollback':
  deployment=D['deployment'];backup=Path(deployment['rollback_directory']);need(backup.parent==backup_root and backup.name.startswith('r015-') and backup.resolve()==backup,'rollback_directory_scoped')
  new={r['path']:r['sha256'] for r in json.loads((backup/'release-manifest.json').read_text())}
  need(inventory(pub)==new,'no_drift_before_rollback');names=[n for n in new if new[n]!=old.get(n)]
  need(restore(names),'rollback_all_original_hashes');need(snapshot()==before,'rollback_database_unchanged');report['rolled_back']=True
 elif action=='deploy':
  need(inventory(pub)==old,'no_drift_before_deploy')
  release=D['release'];need(release['target']=='https://pf26.uber.space' and not release['source_dirty'],'target_and_clean_source')
  raw=base64.b64decode(D['archive'],validate=True);need(sha(raw)==release['archive_sha256'],'archive_transport_sha256')
  z=zipfile.ZipFile(io.BytesIO(raw));rows=D['manifest'];new={r['path']:r['sha256'] for r in rows}
  need(sha((json.dumps(rows,indent=2)+'\n').encode())==release['manifest_sha256'],'manifest_transport_sha256')
  need(len(new)==len(rows)==285 and set(z.namelist())==set(new) and len(z.namelist())==len(new),'manifest_inventory')
  need(all(safe_name(n) for n in new) and set(old)<=set(new),'safe_paths_no_deletions')
  need(all((i.external_attr>>16)&0o170000==0o100000 and i.file_size<40*1024**2 for i in z.infolist()),'regular_bounded_files')
  need(all(sha(z.read(r['path']))==r['sha256'] and len(z.read(r['path']))==r['bytes'] for r in rows),'all_archive_hashes')
  delta=[n for n in new if new[n]!=old.get(n)]
  need({n for n in delta if n in old}==allowed and all(n in allowed or n.startswith('assets/winter26-r015/') for n in delta),'visual_only_allowlist')
  need(all(new[n]==h for n,h in old.items() if n not in allowed),'protected_backend_security_legal_data_unchanged')
  # Compare every executable block, including short echo tags. Only CRLF/LF
  # differs between the verified Windows-era baseline and canonical release.
  php_blocks=lambda b:re.findall(rb'<\?(?:php|=).*?\?>',b.replace(b'\r\n',b'\n'),re.S)
  need(php_blocks((pub/'api/result.php').read_bytes())==php_blocks(z.read('api/result.php')),'result_php_logic_unchanged')
  backup_root.mkdir(exist_ok=True,mode=0o700);need(backup_root.resolve()==backup_root,'backup_root_scoped')
  backup=backup_root/('r015-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
  for n in old:
   dest=backup/n;dest.parent.mkdir(parents=True,exist_ok=True,mode=0o700);shutil.copy2(pub/n,dest)
  need(all(sha((backup/n).read_bytes())==h for n,h in old.items()),'full_rollback_copy_verified')
  (backup/'release-manifest.json').write_text(json.dumps(rows));(backup/'old-manifest.json').write_text(json.dumps(D['baseline']['files']))
  check=backup/'result-lint.php';check.write_bytes(z.read('api/result.php'))
  lint=subprocess.run(['php','-l',str(check)],capture_output=True);need(lint.returncode==0,'remote_php_lint')
  version=subprocess.run(['php','-r','echo PHP_MAJOR_VERSION,".",PHP_MINOR_VERSION;'],capture_output=True);need(version.stdout==b'8.5','php_85_preserved')
  # Assets first, then atomic replacements. Existing .htaccess remains in place throughout.
  order=sorted(delta,key=lambda n:(n in old,n=='winter-config.js',n))
  for n in order:
   target=pub/n;target.parent.mkdir(parents=True,exist_ok=True,mode=0o755)
   tmp=backup/('incoming-'+sha(n.encode())[:20]);tmp.write_bytes(z.read(n));tmp.chmod(0o644);os.replace(tmp,target);changed.append(n)
  need(inventory(pub)==new,'all_285_deployed_hashes')
  http_checks(new)
  need(snapshot()==before,'all_tables_orders_stock_events_config_unchanged_after_deploy')
  report.update(deployed=True,rollback_directory=str(backup),archive_sha256=release['archive_sha256'],orderStates=before['orderStates'],files=len(new),source_commit=release['source_commit'])
 else:
  rows=D['manifest'];new={r['path']:r['sha256'] for r in rows}
  need(inventory(pub)==new,'all_285_deployed_hashes');http_checks(new)
  need(snapshot()==before,'all_tables_orders_stock_events_config_unchanged_after_verify')
  report.update(verified=True,orderStates=before['orderStates'],files=len(new))
except Exception as e:
 report['error']=str(e) if isinstance(e,RuntimeError) else type(e).__name__
 if changed:
  try:report['rolled_back']=restore(changed)
  except Exception:report['rollback_requires_attention']=True
print(json.dumps(report))
