"""Read-only, offline PEM checks for the single PF staging vhost; never imports SSL."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

HOST = 'test.pracowniaform.com'
CERT = re.compile(rb'-----BEGIN CERTIFICATE-----\s+[A-Za-z0-9+/=\s]+-----END CERTIFICATE-----')
KEY = re.compile(rb'-----BEGIN ((?:RSA |EC )?PRIVATE KEY)-----\s+[A-Za-z0-9+/=\s]+-----END \1-----')


class InvalidBundle(ValueError):
    pass


def run(openssl, args, data=None):
    result = subprocess.run([openssl, *args], input=data, capture_output=True, timeout=20)
    if result.returncode:
        # OpenSSL stderr can include private filesystem paths. Do not echo it.
        raise InvalidBundle('OpenSSL rejected check: ' + args[0])
    return result.stdout


def certificates(path):
    raw = path.read_bytes()
    blocks = CERT.findall(raw)
    if not blocks or CERT.sub(b'', raw).strip():
        raise InvalidBundle('Certificate file contains missing/extra/non-certificate data')
    return blocks


def x509(openssl, cert, *args):
    return run(openssl, ['x509', *args], cert)


def der(openssl, cert):
    return x509(openssl, cert, '-outform', 'DER')


def subject_issuer(openssl, cert):
    lines = x509(openssl, cert, '-noout', '-subject', '-issuer', '-nameopt', 'RFC2253').decode().splitlines()
    return dict(line.split('=', 1) for line in lines)


def check_bundle(openssl, leaf_path, key_path, chain_path, roots_path, fullchain_path, min_days=30):
    if min_days < 1:
        raise InvalidBundle('Minimum remaining validity must be positive')
    leaves, chain, roots = (certificates(p) for p in (leaf_path, chain_path, roots_path))
    if len(leaves) != 1:
        raise InvalidBundle('Leaf field must contain exactly one certificate')
    for root in roots:
        names = subject_issuer(openssl, root)
        if names['subject'] != names['issuer'] or b'CA:TRUE' not in x509(openssl, root, '-noout', '-ext', 'basicConstraints'):
            raise InvalidBundle('Trust file must contain independently obtained self-signed CA roots, not leaf/intermediates')
    leaf = leaves[0]
    san = x509(openssl, leaf, '-noout', '-ext', 'subjectAltName').decode().splitlines()
    if ' '.join(line.strip() for line in san[1:]) != 'DNS:' + HOST:
        raise InvalidBundle('SAN must contain only the exact staging hostname')
    x509(openssl, leaf, '-noout', '-checkend', str(min_days * 86400))
    leaf_der = der(openssl, leaf)
    chain_der = [der(openssl, c) for c in chain]
    if leaf_der in chain_der or len(set(chain_der)) != len(chain_der):
        raise InvalidBundle('Chain-only must not repeat the leaf or intermediate')
    previous = subject_issuer(openssl, leaf)
    for cert in chain:
        current = subject_issuer(openssl, cert)
        if current['subject'] == current['issuer']:
            raise InvalidBundle('Chain-only must omit self-signed roots')
        if previous['issuer'] != current['subject']:
            raise InvalidBundle('Intermediate chain is not in leaf-to-root order')
        if b'CA:TRUE' not in x509(openssl, cert, '-noout', '-ext', 'basicConstraints'):
            raise InvalidBundle('Intermediate is not a CA')
        previous = current
    full_der = [der(openssl, c) for c in certificates(fullchain_path)]
    if full_der != [leaf_der, *chain_der]:
        raise InvalidBundle('Fullchain does not equal leaf followed by chain-only')
    raw_key = key_path.read_bytes()
    if not KEY.fullmatch(raw_key.strip()):
        raise InvalidBundle('Expected one unencrypted private key in a private local file')
    run(openssl, ['pkey', '-in', str(key_path), '-passin', 'pass:', '-check', '-noout'])
    key_public = run(openssl, ['pkey', '-in', str(key_path), '-passin', 'pass:', '-pubout', '-outform', 'DER'])
    leaf_public = run(openssl, ['pkey', '-pubin', '-outform', 'DER'], x509(openssl, leaf, '-noout', '-pubkey'))
    if key_public != leaf_public:
        raise InvalidBundle('Private key does not match certificate')
    # Trust ONLY the explicitly supplied anchors. Never treat exported intermediates as trust anchors.
    run(openssl, ['verify', '-purpose', 'sslserver', '-verify_hostname', HOST,
                  '-CAfile', str(roots_path), '-no-CApath', '-no-CAstore',
                  '-untrusted', str(chain_path), str(leaf_path)])
    dates = dict(line.split('=', 1) for line in x509(openssl, leaf, '-noout', '-dates').decode().splitlines())
    return {'status': 'PASS', 'scope': 'offline PEM only; not LH import or served HTTPS',
            'hostname': HOST, 'san_count': 1, 'key_matches': True,
            'chain_only_certificates': len(chain), 'explicit_trust_anchors': len(roots),
            'chain_and_server_purpose_verified': True, 'fullchain_matches': True,
            'minimum_remaining_days': min_days, **dates,
            'leaf_sha256': hashlib.sha256(leaf_der).hexdigest(),
            'issuer': subject_issuer(openssl, leaf)['issuer']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('leaf', 'key', 'chain', 'roots', 'fullchain'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--openssl', default=shutil.which('openssl'))
    parser.add_argument('--min-valid-days', type=int, default=30)
    args = parser.parse_args()
    if not args.openssl:
        parser.error('OpenSSL 3 required; pass --openssl')
    try:
        result = check_bundle(args.openssl, args.leaf.resolve(), args.key.resolve(),
                              args.chain.resolve(), args.roots.resolve(), args.fullchain.resolve(), args.min_valid_days)
    except (InvalidBundle, OSError, subprocess.TimeoutExpired) as exc:
        message = str(exc) if isinstance(exc, InvalidBundle) else 'Local file/tool access failed'
        print(json.dumps({'status': 'FAIL', 'reason': message}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
