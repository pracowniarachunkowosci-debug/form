"""Prepare the reversible checkout delta for offline review against verified FINAL bytes."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from check_final_reference import verify_final

ROOT = Path(__file__).resolve().parents[1]
PATHS = ("api/_common.php", "api/_reservations.php", "winter-config.js", "api/checkout.php",
         "api/result.php", "api/_order_status.php", "api/order-status.php", "winter-payment-result.js",
         "api/_checkout_identity.php", "api/dispatch-quote.php")
def digest(data):
    return hashlib.sha256(data).hexdigest()

def apache_rules(data):
    old = b"(?:checkout|dispatch-quote)"
    anchor = b"RewriteRule ^llms"
    if data.count(old) != 2 or data.count(anchor) != 1:
        raise ValueError("Unexpected FINAL route table")
    eol = b"\r\n" if b"\r\n" in data else b"\n"
    return data.replace(old, b"(?:checkout|dispatch-quote|order-status)").replace(
        anchor, br"RewriteRule ^winter-payment-result\.js$ - [END]" + eol + anchor)

def main():
    parser = argparse.ArgumentParser()
    for arg in ("reference", "manifest", "output"):
        parser.add_argument("--" + arg, required=True, type=Path)
    args = parser.parse_args()
    verify_final(args.reference, args.manifest, ROOT / "winter-26.html")
    args.output.mkdir(parents=True, exist_ok=False)
    rows = []
    for name in (*PATHS, ".htaccess"):
        original = args.reference / name
        before = original.read_bytes() if original.is_file() else None
        if name == ".htaccess":
            after = apache_rules(before)
        else:
            if before is not None:
                base = subprocess.check_output(["git", "show", f"ce3d214:{name}"], cwd=ROOT)
                if before.replace(b"\r\n", b"\n") != base.replace(b"\r\n", b"\n"):
                    raise ValueError(f"Checkout base changed: {name}")
            after = subprocess.check_output(["git", "show", f"HEAD:{name}"], cwd=ROOT)
        for folder, data in (("before", before), ("after", after)):
            if data is not None:
                target = args.output / folder / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        rows.append({"path":name, "before":digest(before) if before is not None else None,
                     "after":digest(after)})
    (args.output / "manifest.json").write_text(json.dumps(rows, indent=2)+"\n", encoding="utf8")

if __name__ == "__main__":
    main()
