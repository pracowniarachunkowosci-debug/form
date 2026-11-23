"""Build only the tested checkout delta for the approved FINAL store."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
for field in ("reference", "manifest", "output"):
    parser.add_argument("--"+field, required=True, type=Path)
args = parser.parse_args()
output = args.output.resolve()
php = os.environ.get("PF_PHP_BIN", "php")

def run(cwd, *command):
    subprocess.run(command, cwd=cwd, check=True)

def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}

if subprocess.check_output(["git","status","--porcelain"], cwd=ROOT).strip():
    sys.exit("Build requires a clean committed worktree")
if output.exists():
    sys.exit("Use a new output directory")
with tempfile.TemporaryDirectory() as temp:
    tmp = Path(temp)
    scratch = tmp / "store"
    delta = tmp / "delta"
    run(ROOT, sys.executable, "scripts/check_publication.py", "--final-reference",
        args.reference.resolve(), "--manifest", args.manifest.resolve())
    run(ROOT, sys.executable, "scripts/prepare_final_checkout_review.py", "--reference",
        args.reference.resolve(), "--manifest", args.manifest.resolve(), "--output", delta)
    shutil.copytree(args.reference, scratch)
    original = inventory(scratch)
    shutil.copytree(delta/"after", scratch, dirs_exist_ok=True)
    rows = json.loads((delta/"manifest.json").read_bytes())
    expected = original | {r["path"]:r["after"] for r in rows}
    if inventory(scratch) != expected:
        raise ValueError("Unexpected changes to FINAL")
    for folder in ("scripts", "tests", "ops"):
        shutil.copytree(ROOT/folder, scratch/folder, ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("check_winter26_pricing", "render_store", "check_render_eol",
                 "check_config_registry", "check_store_gate"):
        run(ROOT, sys.executable, f"scripts/{name}.py", *(["--check"] if name=="render_store" else []))
    run(scratch, "node", "scripts/check_consent.cjs", "--final")
    for name in ("store-gallery.js", "winter-config.js", "winter-payment-result.js"):
        run(scratch, "node", "--check", name)
    for name in ("scripts/check_config.cjs", "scripts/check_store_composition.cjs",
                 "tests/configurator-journey.cjs", "tests/inpost-mock-ui.cjs",
                 "tests/checkout-retry-ui.cjs", "tests/checkout-status-ui.cjs",
                 "tests/checkout-basket-lock-ui.cjs"):
        run(scratch, "node", name)
    for path in sorted((scratch/"api").glob("*.php")):
        run(scratch, php, "-l", path)
    for suite in ("checkout-sandbox", "checkout-live-gates", "checkout-locker", "checkout-retry",
                  "checkout-pending", "checkout-reconciliation", "checkout-status",
                  "checkout-status-security", "staging-runtime-routing"):
        run(scratch, php, f"tests/{suite}.php")
    # Verify rollback only on this disposable local tree.
    for row in rows:
        path = scratch/row["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["after"]:
            raise ValueError(f"Candidate changed during tests: {path}")
        if row["before"] is None:
            path.unlink()
        else:
            shutil.copyfile(delta/"before"/row["path"], path)
    for folder in ("scripts", "tests", "ops"):
        shutil.rmtree(scratch/folder)
    if inventory(scratch) != original:
        raise ValueError("Rollback did not restore the verified reference")
    archive = tmp/"checkout-review.zip"
    with ZipFile(archive,"w") as z:
        for path in sorted(delta.rglob("*")):
            if path.is_file():
                z.writestr(ZipInfo(path.relative_to(delta).as_posix()),path.read_bytes(),compress_type=ZIP_DEFLATED)
    with ZipFile(archive) as z:
        assert z.testzip() is None
        for name in z.namelist():
            assert z.read(name)==(delta/name).read_bytes()
    output.mkdir(parents=True)
    shutil.copyfile(archive,output/archive.name)
    shutil.copyfile(delta/"manifest.json",output/"manifest.json")
    print("PASS offline FINAL build and rollback", inventory(output))
