"""Owner-local SSH session for the explicitly approved pf26 R01.5 integration.
Passphrase stays in memory; commands and reports never contain credentials.
"""
import sys,json,hashlib,stat,threading,zipfile,time,shlex,base64,ctypes
from pathlib import Path
from datetime import datetime,timezone
import tkinter as tk
sys.path.insert(0,str(Path.home()/'AppData/Local/Temp/pf26-ssh-dialog-libs'))
import paramiko
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'.artifacts/r015-session';STATE.mkdir(parents=True,exist_ok=True)
PUBLIC='/var/www/virtual/pf26/winter26/app/public'
HASH=lambda b:hashlib.sha256(b).hexdigest()

READ_DB='''import json,sqlite3,hashlib,os,stat
from pathlib import Path
assert os.getuid()==__import__('pwd').getpwnam('pf26').pw_uid
db=Path('/home/pf26/winter26/runtime/database/sandbox.sqlite')
pub=Path('/var/www/virtual/pf26/winter26/app/public')
assert Path('/var/www/virtual/pf26/html').resolve()==pub
out={'tables':{},'mode':None,'orderStates':{},'databaseMode':oct(stat.S_IMODE(db.stat().st_mode))}
with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) as c:
 c.execute('PRAGMA query_only=ON');c.execute('BEGIN')
 out['integrity']=c.execute('PRAGMA integrity_check').fetchone()[0]
 names=[r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
 for name in names:
  assert __import__('re').fullmatch('[a-zA-Z_][a-zA-Z_0-9]*',name)
  rows=sorted(json.dumps(list(r),sort_keys=True,ensure_ascii=True,default=str) for r in c.execute('SELECT * FROM "'+name+'"'))
  out['tables'][name]={'rows':len(rows),'sha256':hashlib.sha256(json.dumps(rows).encode()).hexdigest()}
 out['orderStates']=dict(c.execute('SELECT state,COUNT(*) FROM orders GROUP BY state'))
 out['mode']=c.execute("SELECT value FROM store_meta WHERE name='mode'").fetchone()[0]
out['configSha256']=hashlib.sha256(Path('/home/pf26/winter26/config/test.json').read_bytes()).hexdigest()
assert out['integrity']=='ok' and out['mode']=='test' and out['orderStates'].get('paid',0)>=2 and out['orderStates'].get('released',0)>=1
print(json.dumps(out))
'''

def save(name,value):
    p=STATE/(name+'.json');temp=p.with_suffix('.new');temp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');temp.replace(p)
def remote(ssh,code,payload=None,timeout=300):
    ch=ssh.get_transport().open_session(timeout=20);ch.settimeout(timeout)
    ch.exec_command('python3 -c '+shlex.quote(code))
    if payload is not None:ch.sendall(json.dumps(payload).encode())
    ch.shutdown_write();raw=ch.makefile('rb').read()
    if ch.recv_exit_status()!=0:raise RuntimeError('REMOTE_OPERATION_FAILED')
    return json.loads(raw)
def credentials():
    class Blob(ctypes.Structure):_fields_=[('cbData',ctypes.c_ulong),('pbData',ctypes.POINTER(ctypes.c_ubyte))]
    raw=(Path.home()/'.ssh/pf26_stage3_secrets.dpapi').read_bytes();b=ctypes.create_string_buffer(raw)
    src=Blob(len(raw),ctypes.cast(b,ctypes.POINTER(ctypes.c_ubyte)));dst=Blob()
    if not ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(src),None,None,None,None,1,ctypes.byref(dst)):raise RuntimeError('DPAPI_UNLOCK_FAILED')
    try:d=json.loads(ctypes.string_at(dst.pbData,dst.cbData))
    finally:ctypes.windll.kernel32.LocalFree(dst.pbData)
    assert d['purpose']=='pf26-uberspace-stage3-sandbox' and d['origin']=='https://pf26.uber.space'
    return {k:d[k] for k in ('basic_username','basic_password','tester_token')}
def snapshot(ssh):
    before_db=remote(ssh,READ_DB);sftp=ssh.open_sftp()
    assert sftp.normalize(PUBLIC)==PUBLIC
    def inventory(path=''):
        rows=[]
        for a in sorted(sftp.listdir_attr(PUBLIC+('/'+path if path else '')),key=lambda a:a.filename):
            assert '/' not in a.filename and '\\' not in a.filename and a.filename not in ('.','..')
            rel=(path+'/' if path else '')+a.filename
            if stat.S_ISDIR(a.st_mode):rows.extend(inventory(rel))
            elif stat.S_ISREG(a.st_mode):rows.append({'path':rel,'size':a.st_size,'mtime':a.st_mtime,'mode':stat.S_IMODE(a.st_mode)})
            else:raise RuntimeError('PUBLIC_LINK_OR_SPECIAL_FILE')
        return rows
    rows=inventory();assert 0<len(rows)<2000 and sum(r['size'] for r in rows)<512*1024**2
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dest=ROOT/'.artifacts/r015-backups'/stamp;dest.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(dest/'public.zip','x',zipfile.ZIP_DEFLATED) as z:
        for i,row in enumerate(rows):
            ui.after(0,lambda i=i:label.config(text=f'Kopia aktualnego wydania: {i+1} / {len(rows)}'))
            data=sftp.open(PUBLIC+'/'+row['path'],'rb').read();assert len(data)==row['size']
            row['sha256']=HASH(data);z.writestr(row['path'],data)
    assert [{k:r[k] for k in ('path','size','mtime','mode')} for r in rows]==inventory()
    with zipfile.ZipFile(dest/'public.zip') as z:
        assert z.testzip() is None
        for row in rows:assert HASH(z.read(row['path']))==row['sha256']
    assert remote(ssh,READ_DB)==before_db
    (dest/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    save('baseline',{'backupId':stamp,'archiveSha256':HASH((dest/'public.zip').read_bytes()),'files':rows,'database':before_db,'remoteWrites':0})
    sftp.close()

def run(password):
    ssh=None
    try:
        ssh=paramiko.SSHClient();ssh.load_host_keys(str(Path.home()/'.ssh/pf26_uberspace_known_hosts'));ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        ssh.connect('kari.uberspace.de',username='pf26',key_filename=str(Path.home()/'.ssh/pf26_uberspace'),passphrase=password,look_for_keys=False,allow_agent=False,timeout=15,auth_timeout=20,disabled_algorithms={'keys':['ssh-rsa','ecdsa-sha2-nistp256','ecdsa-sha2-nistp384','ecdsa-sha2-nistp521']})
        password=None;ssh.get_transport().set_keepalive(30)
        snapshot(ssh);save('connection',{'connected':True,'snapshotComplete':True,'host':'pf26','time':datetime.now(timezone.utc).isoformat()})
        ui.after(0,lambda:label.config(text='Kopia i baza sprawdzone. Pozostaw okno otwarte podczas integracji.'))
        done=set()
        while not stop.is_set():
            command=STATE/'command.json'
            if command.is_file():
                task=json.loads(command.read_text(encoding='utf-8'))
                ident=task['id'];assert ident.replace('-','').isalnum()
                if ident not in done:
                    action=task['action'];assert action in ('verify','deploy','rollback','finish')
                    if action=='finish':break
                    code=(ROOT/'scripts/r015_remote.py').read_text(encoding='utf-8')
                    payload={'action':action,'baseline':json.loads((STATE/'baseline.json').read_text()),'credentials':credentials()}
                    package=ROOT/'.artifacts/r015-release'
                    if action in ('deploy','verify') and (package/'release.json').is_file():
                        payload['release']=json.loads((package/'release.json').read_text());payload['manifest']=json.loads((package/'manifest.json').read_text())
                    if action=='deploy':payload['archive']=base64.b64encode((package/'winter26-r015-staging.zip').read_bytes()).decode()
                    if action in ('verify','rollback') and (STATE/'deployed.json').is_file():payload['deployment']=json.loads((STATE/'deployed.json').read_text())
                    result=remote(ssh,code,payload,timeout=600);payload=None
                    save(ident,result)
                    if action=='deploy' and result.get('deployed'):save('deployed',result)
                    done.add(ident)
                    ui.after(0,lambda:label.config(text='Operacja wykonana. Wyniki sprawdzane w czacie; pozostaw okno otwarte.'))
            stop.wait(1)
    except Exception as e:
        save('session-error',{'errorType':type(e).__name__,'code':str(e) if isinstance(e,RuntimeError) else 'SSH_SESSION_FAILED'})
        ui.after(0,lambda:label.config(text='Sesja wymaga sprawdzenia w czacie. Nie podawaj hasla.'))
        ui.after(0,lambda:button.config(state='normal'))
    finally:
        password=None
        if ssh:ssh.close()
        save('connection',{'connected':False})

stop=threading.Event();ui=tk.Tk();ui.title('Pracownia Form - integracja R01.5 pf26');ui.geometry('720x260')
tk.Label(ui,text='Zatwierdzona integracja R01.5 — tylko pf26',font=('Segoe UI',12)).pack(pady=16)
tk.Label(ui,text='Najpierw kopia i kontrola bazy. Wdrozenie po testach, z rollbackiem.').pack()
tk.Label(ui,text='Wpisz passphrase istniejacego klucza SSH; nie zostanie zapisana.').pack(pady=8)
entry=tk.Entry(ui,show='*',width=48);entry.pack()
label=tk.Label(ui,text='Sekrety sklepu zostana uzyte z istniejacego magazynu DPAPI.');label.pack(pady=12)
def start():
    password=entry.get();entry.delete(0,tk.END);button.config(state='disabled');threading.Thread(target=run,args=(password,),daemon=True).start()
button=tk.Button(ui,text='Odblokuj sesje integracji',command=start);button.pack()
def close():stop.set();ui.destroy()
ui.protocol('WM_DELETE_WINDOW',close);entry.focus_set();ui.mainloop()
