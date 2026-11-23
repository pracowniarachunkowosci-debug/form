"""Exercise the packaged status endpoint over loopback HTTP with disposable TEST sessions."""
import argparse
from hashlib import sha256
import http.client
import json
import os
from pathlib import Path
import shutil
import socket
import sqlite3
import subprocess
import tempfile
import time
import uuid
from zipfile import ZipFile


def exercise(root, port):
    dbfile = root / "fixture.sqlite"
    owner = uuid.uuid4().hex + "aaaa"
    states = ["paid", "pending", "released", "review", "reserved", "reconcile"]
    ids = {state: str(uuid.uuid4()) for state in [*states, "legacy"]}
    with sqlite3.connect(dbfile) as db:
        db.executescript("""
            CREATE TABLE store_meta(name TEXT, value TEXT);
            INSERT INTO store_meta VALUES('mode','test');
            CREATE TABLE orders(req TEXT PRIMARY KEY,state TEXT,owner TEXT);
            CREATE TABLE stock(available INTEGER);
            INSERT INTO stock VALUES(16);
        """)
        db.executemany("INSERT INTO orders VALUES(?,?,?)",
                       [(rid, state if state != "legacy" else "paid",
                         owner if state != "legacy" else None) for state, rid in ids.items()])
    db.close()
    initial = dbfile.read_bytes()
    sessions = {}
    for name, visitor in [("own", owner), ("other", "b"*36), ("empty", None), ("expired", owner)]:
        sid = uuid.uuid4().hex
        sessions[name] = sid
        expires = int(time.time()) + (-100 if name == "expired" else 1000)
        record = f"tester_until|i:{expires};"
        if visitor:
            record += f'visitor|s:36:"{visitor}";'
        (root / ("sess_" + sid)).write_text(record, encoding="ascii")

    def check(label, expected, identity="own", request=None, method="POST",
              media="application/json", origin="https://pf.test", state=None):
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        headers = {"Host": "pf.test", "Origin": origin, "Content-Type": media}
        if identity:
            headers["Cookie"] = "pf_winter_sandbox=" + sessions[identity]
        conn.request(method, "/api/order-status.php",
                     json.dumps({"requestId": ids["paid"]} if request is None else request), headers)
        response = conn.getresponse()
        data = json.loads(response.read())
        conn.close()
        assert response.status == expected, (label, response.status, data.get("error"))
        assert response.getheader("Cache-Control") == "no-store"
        assert set(data) == ({"state", "message"} if state else {"error", "message"})
        if state:
            assert data["state"] == state
        print("PASS", label, response.status)
        return data

    for state in states:
        check(state, 200, request={"requestId": ids[state]}, state=state)
    check("repeat paid", 200, state="paid")
    check("anonymous", 403, identity=None)
    check("expired tester", 403, identity="expired")
    check("missing owner", 401, identity="empty")
    hidden = check("foreign owner", 404, identity="other")
    assert check("missing UUID", 404, request={"requestId": str(uuid.uuid4())}) == hidden
    assert check("owner NULL", 404, request={"requestId": ids["legacy"]}) == hidden
    check("malformed UUID", 422, request={"requestId": "invalid"})
    check("extra parameter", 422, request={"requestId": ids["paid"], "state": "paid"})
    check("wrong method", 405, method="GET")
    check("wrong origin", 403, origin="https://other.test")
    check("wrong content type", 415, media="text/plain")
    assert dbfile.read_bytes() == initial
    dbfile.rename(root / "offline.sqlite")
    check("database unavailable", 503)
    assert not dbfile.exists()
    print("PASS fixture bytes unchanged and absent database not created")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("php", "reference", "package"):
        parser.add_argument("--"+name, required=True, type=Path)
    args = parser.parse_args()
    php = args.php.resolve()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        web = root / "www"
        shutil.copytree(args.reference / "api", web / "api")
        with ZipFile(args.package) as z:
            for row in json.loads(z.read("manifest.json")):
                name = row["path"]
                target = (web / name).resolve()
                assert web in target.parents
                if name.startswith("api/"):
                    data = z.read("after/" + name)
                    assert sha256(data).hexdigest() == row["after"]
                    target.write_bytes(data)
        db_path = (root / "fixture.sqlite").as_posix()
        if os.name == "nt":
            db_path = db_path[2:]
        config = root / "fixture.json"
        config.write_text(json.dumps(dict(origin="https://pf.test", db_file=db_path,
            stripe_key="rk_test_fixture", webhook_secret="whsec_fixture", login_sha256="0"*64)))
        prepend = root / "transport.php"
        prepend.write_text("<?php $_SERVER['HTTPS']='on';", encoding="ascii")
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        proc = subprocess.Popen([php, "-d", f"session.save_path={root}", "-d",
            f"auto_prepend_file={prepend}", "-S", f"127.0.0.1:{port}", "-t", web],
            cwd=root, env={**os.environ, "PF_TEST_CONFIG": str(config)}, stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                if proc.poll() is not None:
                    raise RuntimeError("PHP server failed to start")
                try:
                    with socket.create_connection(("127.0.0.1", port), .1):
                        break
                except OSError:
                    time.sleep(.05)
            exercise(root, port)
        finally:
            proc.terminate()
            proc.wait(timeout=5)


if __name__ == "__main__":
    main()
