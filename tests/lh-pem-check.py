"""Offline regression checks with throwaway synthetic certificates, never real ACME keys."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pemcheck', ROOT/'scripts/check_lh_pem.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--openssl', required=True)
    ap.add_argument('--private-temp-parent', type=Path, required=True)
    args = ap.parse_args()
    parent = args.private_temp_parent.resolve(strict=True)
    if parent == ROOT or ROOT in parent.parents:
        raise ValueError('Fixtures must be outside repository')
    with tempfile.TemporaryDirectory(prefix='pf-synthetic-pem-', dir=parent) as directory:
        temp = Path(directory).resolve(strict=True)
        assert temp.parent == parent  # exact owned cleanup boundary
        def command(*items):
            result = subprocess.run([args.openssl, *items], cwd=temp, capture_output=True, timeout=30)
            if result.returncode:
                raise RuntimeError('Synthetic fixture command failed: ' + items[0])
        command('req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-keyout', 'root.key', '-out', 'root.pem',
                '-subj', '/CN=PF SYNTHETIC TEST ROOT', '-days', '3', '-addext', 'basicConstraints=critical,CA:TRUE',
                '-addext', 'keyUsage=critical,keyCertSign,cRLSign')
        command('req', '-new', '-newkey', 'rsa:2048', '-nodes', '-keyout', 'int.key', '-out', 'int.csr', '-subj', '/CN=PF SYNTHETIC INTERMEDIATE')
        (temp/'int.ext').write_text('basicConstraints=critical,CA:TRUE,pathlen:0\nkeyUsage=critical,keyCertSign,cRLSign\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\n')
        command('x509', '-req', '-in', 'int.csr', '-CA', 'root.pem', '-CAkey', 'root.key', '-set_serial', '2', '-days', '2', '-extfile', 'int.ext', '-out', 'chain.pem')
        for label, san in [('leaf', 'DNS:test.pracowniaform.com'), ('extra', 'DNS:test.pracowniaform.com,DNS:www.test.pracowniaform.com'), ('wrong', 'DNS:example.invalid')]:
            command('req', '-new', '-newkey', 'rsa:2048', '-nodes', '-keyout', label+'.key', '-out', label+'.csr', '-subj', '/CN=PF SYNTHETIC LEAF')
            (temp/(label+'.ext')).write_text('basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\nsubjectAltName='+san+'\n')
            command('x509', '-req', '-in', label+'.csr', '-CA', 'chain.pem', '-CAkey', 'int.key', '-set_serial', str(10+len(label)), '-days', '2', '-extfile', label+'.ext', '-out', label+'.pem')
            (temp/(label+'-full.pem')).write_bytes((temp/(label+'.pem')).read_bytes()+(temp/'chain.pem').read_bytes())
        (temp/'duplicate-chain.pem').write_bytes((temp/'chain.pem').read_bytes()*2)
        (temp/'mixed-key.pem').write_bytes((temp/'leaf.key').read_bytes()+(temp/'leaf.pem').read_bytes())
        command('req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-keyout', 'other-root.key', '-out', 'other-root.pem', '-subj', '/CN=UNTRUSTED SYNTHETIC ROOT', '-days', '3')
        cases = [
            ('valid_synthetic', {}, True),
            ('mismatched_key', {'key_path':temp/'wrong.key'}, False),
            ('extra_certificate_in_key', {'key_path':temp/'mixed-key.pem'}, False),
            ('extra_www_SAN', {'leaf_path':temp/'extra.pem','key_path':temp/'extra.key','fullchain_path':temp/'extra-full.pem'}, False),
            ('wrong_hostname', {'leaf_path':temp/'wrong.pem','key_path':temp/'wrong.key','fullchain_path':temp/'wrong-full.pem'}, False),
            ('fullchain_in_leaf', {'leaf_path':temp/'leaf-full.pem'}, False),
            ('leaf_in_chain', {'chain_path':temp/'leaf-full.pem'}, False),
            ('duplicate_intermediate', {'chain_path':temp/'duplicate-chain.pem'}, False),
            ('wrong_fullchain', {'fullchain_path':temp/'wrong-full.pem'}, False),
            ('untrusted_root', {'roots_path':temp/'other-root.pem'}, False),
            ('leaf_used_as_trust_anchor', {'roots_path':temp/'leaf.pem'}, False),
            ('intermediate_used_as_trust_anchor', {'roots_path':temp/'chain.pem'}, False),
            ('insufficient_remaining_validity', {'min_days':30}, False),
        ]
        results=[]
        for name, changes, expected in cases:
            values={'leaf_path':temp/'leaf.pem','key_path':temp/'leaf.key','chain_path':temp/'chain.pem','roots_path':temp/'root.pem','fullchain_path':temp/'leaf-full.pem','min_days':1}
            values.update(changes)
            try: module.check_bundle(args.openssl,**values); actual=True
            except module.InvalidBundle: actual=False
            assert actual == expected, name
            results.append({'case':name,'pass':True})
    assert not temp.exists()
    print(json.dumps({'scope':'synthetic local fixtures, not a real LE certificate','cases':results,'cleanup':True},indent=2))


if __name__=='__main__': main()
