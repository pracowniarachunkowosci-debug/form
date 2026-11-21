"""Offline review package only. Never deploys, accesses Stripe, or touches a database."""
from pathlib import Path
import hashlib,json,os,subprocess,zipfile
root=Path(__file__).resolve().parents[1]
before={
 'api/_common.php':'85276bf045ac21b775f338e166bed2767f42493938fc1762449d7cafcdc27860',
 'api/_reservations.php':'e82122b57ade52f434e05d4aa9b28e139990513064d5cc927138a7feed05f77c',
 'winter-config.js':'8ad0bd3dcdf50cec40c6c4faa92958b36087b4b3775d9715646839eb634204ec',
}
php=os.environ.get('PF_PHP_BIN','php')
for p in before:
 subprocess.run([php,'-l',p] if p.endswith('.php') else ['node','--check',p],cwd=root,check=True)
out=root/'.artifacts'/'checkout-retry';out.mkdir(parents=True,exist_ok=True)
manifest={'baseRelease':'PF-W26-FINAL-20261119-145544-CET','purpose':'REVIEW ONLY; full legacy build has unresolved failures; no deployment approval',
 'files':[{'path':p,'beforeSha256':h,'afterSha256':hashlib.sha256((root/p).read_bytes()).hexdigest()} for p,h in before.items()]}
with zipfile.ZipFile(out/'checkout-review.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in before:z.write(root/p,p)
 z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(out/'checkout-review.zip') as z:
 assert z.testzip() is None
 for f in manifest['files']:assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['afterSha256']
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PASS review-only patch archive: exact three runtime files, verified hashes. Not deployed.')
