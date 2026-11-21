"""Build a review-only package from committed blobs and a read-only Uberspace baseline."""
from pathlib import Path
import argparse,hashlib,json,subprocess,zipfile
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=root)
if git('status','--porcelain'):raise SystemExit('Commit changes before packaging.')
e=json.loads(args.baseline.read_text(encoding='utf-8'))
assert e['salesPaused'] is True and e['database']['vaseDual']==16
assert e['domains']['pf26.uber.space']['canonical']=='/var/www/virtual/pf26/winter26/app/public'
files=['api/_common.php','api/_reservations.php','api/_production.php','winter-config.js','api/checkout.php','api/result.php','api/_order_status.php','api/order-status.php','winter-payment-result.js','api/_checkout_identity.php','api/dispatch-quote.php']
def sha(blob):return hashlib.sha256(blob).hexdigest()
blobs={f:git('show','HEAD:'+f) for f in files}
manifest={'purpose':'REVIEW ONLY — no deployment authorization','deploymentReady':False,'target':'pf26.uber.space only','sourceCommit':git('rev-parse','HEAD').decode().strip(),'parentFix':git('rev-parse','6869924').decode().strip(),
 'blockers':['staging gateway/routing and actual FPM proof not installed or accepted','legacy NULL-owner orders require separate ownership decision','legacy full build fails','final diagnostic hooks require separate assembly and final hashes'],
 'runtime':[{'path':f,'beforeSha256':e['runtimeBaseline'][f],'afterSha256':sha(blobs[f])} for f in files]}
extras=['OPCACHE_STATUS_AUDIT_20261121.txt','PAID_STATUS_REVIEW_20261121.txt','ops/staging-runtime/gateway.php','ops/staging-runtime/entry-hook.txt','tests/checkout-status-security.php','tests/staging-runtime-routing.php','tests/checkout-status.php','tests/checkout-status-ui.cjs','scripts/build_status_security_review.py','scripts/build_release.py']
extra={f:git('show','HEAD:'+f) for f in extras};manifest['reviewFiles']={f:sha(b) for f,b in extra.items()}
args.output.mkdir(parents=True,exist_ok=True);package=args.output/'status-security-review.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for f,b in blobs.items():z.writestr('runtime/'+f,b)
 for f,b in extra.items():z.writestr('review/'+f,b)
 z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(package) as z:
 assert z.testzip() is None
 for f,b in blobs.items():assert z.read('runtime/'+f)==b
 for f,b in extra.items():assert z.read('review/'+f)==b
(args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
(args.output/'package.sha256').write_text(sha(package.read_bytes())+'  '+package.name+'\n')
print('PASS: 11 runtime proposals, exact committed bytes, verified zip; not deployed.')
