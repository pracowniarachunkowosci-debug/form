"""All current checkout/R01.6 regression suites, isolated from staging and Stripe.

Requires PF_PHP_BIN (PHP 8.5 with PDO SQLite/curl) and Node on PATH.
The HTTP suite runs the original restored loopback launcher/router, without edits.
No antivirus exceptions or alternate router copies are used.
"""
from pathlib import Path
import hashlib,json,os,queue,re,signal,subprocess,sys,threading,time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.artifacts/p0-regression';OUT.mkdir(parents=True,exist_ok=True)
PHP=os.environ.get('PF_PHP_BIN','php')
ENV=dict(os.environ,PF_PHP_BIN=PHP)
results=[]

def record(name,command,timeout=90):
    started=time.monotonic()
    try:
        r=subprocess.run(command,cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=timeout)
        result={'name':name,'status':'PASS' if r.returncode==0 else 'FAIL','exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
    except subprocess.TimeoutExpired:
        result={'name':name,'status':'FAIL','exitCode':None,'stdout':'','stderr':'TIMEOUT'}
    result['seconds']=round(time.monotonic()-started,3);results.append(result)
    print(name+': '+result['status'],flush=True)
    return result

version=record('PHP 8.5',[PHP,'-r','if(PHP_MAJOR_VERSION!==8||PHP_MINOR_VERSION!==5)exit(1);echo PHP_VERSION;'])
if version['status']!='PASS':raise SystemExit('PHP 8.5 required')
for name in ('checkout-reconciliation','checkout-sandbox','checkout-locker','checkout-live-gates'):
    record(name,[PHP,'-d','disable_functions=curl_exec','tests/'+name+'.php'])
for name,file in (
    ('configurator-journey','tests/configurator-journey.cjs'),
    ('composition','scripts/check_store_composition.cjs'),
    ('inpost-ui','tests/inpost-mock-ui.cjs'),
    ('variant-gallery','tests/variant-gallery-r016.mjs'),
    ('consent','scripts/check_consent.cjs')):
    record(name,['node',file])
record('pricing',['python','scripts/check_winter26_pricing.py'])
php_sources=sorted((ROOT/'api').glob('*.php'))+[ROOT/'scripts/reconcile-reservations.php']+sorted((ROOT/'tests').glob('*.php'))+sorted((ROOT/'tests/fixtures').glob('*.php'))
lint_failures=[]
for file in php_sources:
    r=subprocess.run([PHP,'-l',str(file)],cwd=ROOT,capture_output=True,text=True)
    if r.returncode:lint_failures.append({'path':file.relative_to(ROOT).as_posix(),'stderr':r.stderr})
results.append({'name':'PHP lint','status':'FAIL' if lint_failures else 'PASS','files':len(php_sources),'failures':lint_failures})
print('PHP lint: '+results[-1]['status'],flush=True)

# The launcher owns and cleans up its one child. No existing process/port is terminated.
launcher=None; lines=queue.Queue(); own_db=None
try:
    launcher=subprocess.Popen([PHP,'tests/inpost-mock-demo.php'],cwd=ROOT,env=ENV,
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name=='nt' else 0)
    def consume():
        for line in launcher.stdout:lines.put(line)
    reader=threading.Thread(target=consume,daemon=True);reader.start()
    deadline=time.monotonic()+15; launch_text=[]
    while own_db is None and time.monotonic()<deadline:
        try:line=lines.get(timeout=.1)
        except queue.Empty:
            if launcher.poll() is not None:break
            continue
        launch_text.append(line)
        match=re.search(r'SQLite \(reserved\): (.+)',line)
        if match:own_db=Path(match.group(1).strip())
    if own_db is None:
        results.append({'name':'inpost-http','status':'BLOCKED','reason':'Original loopback launcher did not become ready; inspect security history. No bypass attempted.'})
        print('inpost-http: BLOCKED',flush=True)
    else:
        assert own_db.resolve().parent==(ROOT/'.artifacts/inpost-mock-demo').resolve()
        record('inpost-http',['node','tests/inpost-mock-http.cjs',str(own_db)])
finally:
    if launcher is not None and launcher.poll() is None:
        try:
            launcher.send_signal(signal.CTRL_BREAK_EVENT if os.name=='nt' else signal.SIGINT)
            launcher.wait(timeout=5)
        except (OSError,subprocess.TimeoutExpired):
            if os.name=='nt':subprocess.run(['taskkill','/PID',str(launcher.pid),'/T','/F'],capture_output=True)
            else:launcher.terminate()
            launcher.wait(timeout=5)
    # Keep this isolated demo DB as local evidence. Never package it or use it as staging data.

head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
source_hashes={name:hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
               for name in tracked if name and (ROOT/name).is_file() and (name.startswith(('api/','tests/','ops/p0/')) or name=='scripts/reconcile-reservations.php')}
report={'scope':'local isolated fixtures and loopback only','baseOrCandidateHead':head,'stripeCalls':0,'inpostCalls':0,
        'stagingAccess':False,'results':results,'allPassed':all(r['status']=='PASS' for r in results),'sourceSha256LF':source_hashes}
(OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('ALL PASS' if report['allPassed'] else 'GATE FAILED',flush=True)
sys.exit(0 if report['allPassed'] else 1)
