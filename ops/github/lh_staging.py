"""Local staging packaging / locked FTPS proposal. Never imports candidate Python."""
import argparse
from ftplib import FTP_TLS
from hashlib import sha256
from http.client import HTTPConnection, HTTPSConnection
from io import BytesIO
import json
import os
from pathlib import Path, PurePosixPath
import re
import ssl
import stat
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


REPOSITORY = 'pracowniarachunkowosci-debug/form'
FTPS_HOST = 'serwer533947.lh.pl'
FTPS_USER = 'serwer533947_pfstage14'
# FTP '/' MUST be confirmed to map only to /public_html/pf-stage-20261114.
# PWD cannot prove the server-side jail; this is a prerequisite for acceptance.
FTPS_ROOT = '/'
TECHNICAL_PREFIX = '/pf-stage-20261114/'
ARCHIVE = 'pf-staging-denied.zip'
PROTECTION = Path(__file__).with_name('staging-deny.htaccess')
INFRASTRUCTURE_ACCEPTED = False  # Code-review lock, deliberately not an env var.
MAX_ARCHIVE = 256 * 1024 * 1024
MAX_FILE = 32 * 1024 * 1024
MAX_TOTAL = 512 * 1024 * 1024
MAX_ENTRIES = 5000
CANARY = 'pf-access-check.txt'
CANARY_BYTES = b'PF staging access probe; not application data.\n'
CLI_ONLY = frozenset({'api/prepare-live.php', 'api/seed-test.php'})


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_sha(value):
    require(re.fullmatch(r'[0-9a-f]{40}', value or '') is not None, 'Full lowercase commit SHA required')
    return value


def digest(raw):
    return sha256(raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def protection_bytes():
    # Stable LF content even when the checkout uses Windows CRLF.
    return PROTECTION.read_bytes().replace(b'\r\n', b'\n')


def allowed_path(name, protected=False):
    if protected and name in CLI_ONLY:
        return False
    if protected and name == '.htaccess':
        return True
    if not re.fullmatch(r'[A-Za-z0-9_./-]+', name):
        return False
    parts = name.split('/')
    if any(part in ('', '.', '..') or part.startswith('.') for part in parts):
        return False
    suffix = PurePosixPath(name).suffix.lower()
    if len(parts) == 1:
        return suffix in {'.html', '.css'} or name in {
            'script.js', 'store-gallery.js', 'winter-config.js', 'favicon.svg', 'robots.txt', 'sitemap.xml'}
    if len(parts) == 2 and parts[0] == 'api':
        return suffix == '.php'
    if parts[0] == 'assets':
        return suffix in {'.avif', '.webp', '.jpg', '.jpeg', '.png', '.svg', '.woff', '.woff2'}
    return name in {'data/winter26-pricing-pl.json', 'data/winter26-products.json'}


def read_limited(path, maximum):
    require(path.is_file() and not path.is_symlink(), 'Expected a regular local file')
    require(path.stat().st_size <= maximum, 'File exceeds safety limit')
    return path.read_bytes()


def read_bundle(directory, expected_sha, protected=False, expected_hashes=None):
    checked_sha(expected_sha)
    archive_name = ARCHIVE if protected else 'pracownia-form-lh.zip'
    raw_zip = read_limited(directory / archive_name, MAX_ARCHIVE)
    raw_manifest = read_limited(directory / 'manifest.json', 2 * 1024 * 1024)
    raw_release = read_limited(directory / 'release.json', 64 * 1024)
    actual = dict(bundle_sha256=digest(raw_zip), manifest_sha256=digest(raw_manifest),
                  release_sha256=digest(raw_release))
    if expected_hashes is not None:
        require(actual == expected_hashes, 'Bundle hashes differ from the dependent build outputs')
    report = json.loads(raw_release)
    rows = json.loads(raw_manifest)
    require(report['source_commit'] == expected_sha and report['source_dirty'] is False,
            'Wrong or dirty source revision')
    require(report['archive'] == archive_name and report['archive_sha256'] == digest(raw_zip)
            and report['archive_bytes'] == len(raw_zip)
            and report['manifest_sha256'] == digest(raw_manifest), 'Release metadata mismatch')
    require(report['uploaded_by_this_build'] is False, 'Unexpected upload provenance')
    require(isinstance(rows, list) and 0 < len(rows) <= MAX_ENTRIES
            and report['files'] == len(rows), 'Invalid manifest size')
    if protected:
        require(report['deployment_target'] == 'LH PF staging quarantine'
                and report['protection'] == 'deny-all-v1', 'Not a protected staging bundle')
    blobs = {}
    with ZipFile(BytesIO(raw_zip)) as archive:
        infos = archive.infolist()
        names = [row['path'] for row in rows]
        require(len(set(names)) == len(names) and archive.namelist() == names, 'Duplicate or unexpected ZIP entries')
        require(sum(info.file_size for info in infos) <= MAX_TOTAL, 'Expanded archive too large')
        for info, row in zip(infos, rows):
            name = info.filename
            mode = info.external_attr >> 16
            require(allowed_path(name, protected) and not info.is_dir(), 'Forbidden public payload path')
            require(stat.S_IFMT(mode) in (0, stat.S_IFREG), 'Links and special files forbidden')
            require(not info.flag_bits & 1 and info.file_size <= MAX_FILE, 'Unsupported ZIP member')
            require(type(row['bytes']) is int and info.file_size == row['bytes'], 'Member size mismatch')
            raw = archive.read(info)
            require(len(raw) == row['bytes'] and digest(raw) == row['sha256'], 'Member hash mismatch')
            blobs[name] = raw
    require('index.html' in blobs, 'No webroot entry point')
    if protected:
        require(next(iter(blobs)) == '.htaccess' and blobs['.htaccess'] == protection_bytes(),
                'Exact deny-all policy must be the first member')
        require(blobs['robots.txt'] == b'User-agent: *\nDisallow: /\n', 'Missing staging robots policy')
    return blobs, report, actual


def package(source, output, expected_sha):
    blobs, original, _ = read_bundle(source, expected_sha)
    # Nested .htaccess / .user.ini / secrets / DB / scripts are excluded by allowed_path.
    blobs = {'.htaccess': protection_bytes(), **{name: raw for name, raw in blobs.items() if name not in CLI_ONLY}}
    blobs['robots.txt'] = b'User-agent: *\nDisallow: /\n'
    output.mkdir(parents=True, exist_ok=False)
    rows = [dict(path=name, bytes=len(raw), sha256=digest(raw)) for name, raw in blobs.items()]
    with ZipFile(output / ARCHIVE, 'x', compression=ZIP_DEFLATED) as archive:
        for name, raw in blobs.items():
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, raw, compresslevel=9)
    manifest = json_bytes(rows)
    (output / 'manifest.json').write_bytes(manifest)
    raw_zip = (output / ARCHIVE).read_bytes()
    report = dict(source_commit=expected_sha, source_dirty=False, archive=ARCHIVE,
                  archive_sha256=digest(raw_zip), archive_bytes=len(raw_zip),
                  manifest_sha256=digest(manifest), files=len(rows),
                  deployment_target='LH PF staging quarantine', protection='deny-all-v1',
                  source_archive_sha256=original['archive_sha256'], uploaded_by_this_build=False)
    (output / 'release.json').write_bytes(json_bytes(report))
    _, _, hashes = read_bundle(output, expected_sha, protected=True)
    return hashes


def release_name(sha, run_id, attempt):
    checked_sha(sha)
    require(all(re.fullmatch(r'[1-9][0-9]{0,19}', value or '') for value in (run_id, attempt)),
            'Invalid Actions run identity')
    return f'winter26-{sha}-{run_id}-{attempt}'


def check_denial(name):
    # Only fixed technical-host URLs. No proxy, redirects, credentials or user URLs.
    # All aliases and the dedicated HTTPS/private config must ALSO pass the prior gate.
    for connection in (HTTPConnection(FTPS_HOST, timeout=20),
                       HTTPSConnection(FTPS_HOST, timeout=20, context=ssl.create_default_context())):
        try:
            connection.request('GET', TECHNICAL_PREFIX + name + '/' + CANARY)
            response = connection.getresponse()
            require(response.status == 403, 'Technical route is not denied (redirects also fail)')
            require('noindex' in response.getheader('X-Robots-Tag', '').lower(), 'No noindex response header')
            require('no-store' in response.getheader('Cache-Control', '').lower(), 'No no-store response header')
            require(response.read(4096).strip() == b'PF staging quarantine', 'Wrong denial policy response')
        finally:
            connection.close()


def send_new_directory(ftp, name, blobs, probe):
    # Called only after upload() has checked its hard lock, identity and all hashes.
    # No delete, rename, chmod, SITE, resume, overwriting old releases or vhost changes.
    require(re.fullmatch(r'winter26-[0-9a-f]{40}-[1-9][0-9]{0,19}-[1-9][0-9]{0,19}', name)
            is not None, 'Invalid generated release name')
    require(blobs.get('.htaccess') == protection_bytes(), 'Missing protection')
    ftp.cwd(FTPS_ROOT)
    require(ftp.pwd() == FTPS_ROOT, 'Unexpected FTPS namespace')
    ftp.mkd(name)  # collision/failure aborts; never catch and reuse existing directory
    ftp.cwd(name)
    require(ftp.pwd() == '/' + name, 'Unexpected new directory')

    def store_verified(path, raw):
        ftp.storbinary('STOR ' + path, BytesIO(raw))
        received = sha256()
        ftp.retrbinary('RETR ' + path, received.update)
        require(received.hexdigest() == digest(raw), 'Remote readback mismatch')

    store_verified('.htaccess', blobs['.htaccess'])
    store_verified(CANARY, CANARY_BYTES)
    probe(name)  # no application bytes until HTTP and HTTPS denial are proven
    made = set()
    for path, raw in blobs.items():
        if path == '.htaccess':
            continue
        require(allowed_path(path, protected=True), 'Forbidden payload path')
        for parent in reversed(PurePosixPath(path).parents):
            directory = parent.as_posix()
            if directory != '.' and directory not in made:
                ftp.mkd(directory)
                made.add(directory)
        store_verified(path, raw)
    probe(name)
    # Leave guard and harmless canary in place, including on partial failure.


def upload(source, expected_sha):
    # FIRST operation: no file reads, credentials or network before this reviewed lock.
    require(INFRASTRUCTURE_ACCEPTED,
            'BLOCKED: HTTPS, private PHP-FPM config, public exposure and FTPS jail acceptance outstanding')
    checked_sha(expected_sha)
    require(os.environ.get('GITHUB_REPOSITORY') == REPOSITORY
            and os.environ.get('GITHUB_EVENT_NAME') == 'workflow_dispatch'
            and os.environ.get('GITHUB_REF') == 'refs/heads/main'
            and os.environ.get('GITHUB_WORKFLOW_REF') == REPOSITORY + '/.github/workflows/lh-staging.yml@refs/heads/main'
            and os.environ.get('GITHUB_SHA') == expected_sha
            and os.environ.get('GITHUB_WORKFLOW_SHA') == expected_sha, 'Untrusted execution context')
    hashes = {key: os.environ.get('EXPECTED_' + key.upper(), '')
              for key in ('bundle_sha256', 'manifest_sha256', 'release_sha256')}
    require(all(re.fullmatch(r'[0-9a-f]{64}', value) for value in hashes.values()), 'Missing build hash binding')
    blobs, _, _ = read_bundle(source, expected_sha, protected=True, expected_hashes=hashes)
    name = release_name(expected_sha, os.environ.get('GITHUB_RUN_ID'), os.environ.get('GITHUB_RUN_ATTEMPT'))
    password = os.environ.get('PF_FTPS_PASSWORD', '')
    require(bool(password) and '\r' not in password and '\n' not in password, 'Missing or invalid staging password')
    with FTP_TLS(context=ssl.create_default_context(), timeout=30) as ftp:
        ftp.connect(FTPS_HOST, 21)
        ftp.auth()
        ftp.login(FTPS_USER, password)
        ftp.prot_p()
        ftp.set_pasv(True)
        send_new_directory(ftp, name, blobs, check_denial)
    print('Verified staging quarantine upload; no activation. Directory: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('package', 'verify', 'upload'):
        sub = commands.add_parser(command)
        sub.add_argument('--source', required=True, type=Path)
        sub.add_argument('--sha', required=True)
        if command == 'package':
            sub.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.command == 'package':
        hashes = package(args.source, args.output, args.sha)
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as handle:
                handle.writelines(f'{key}={value}\n' for key, value in hashes.items())
        print(json.dumps(hashes))
    elif args.command == 'verify':
        read_bundle(args.source, args.sha, protected=True)
        print('Local integrity only; not an LH infrastructure or provenance acceptance.')
    else:
        upload(args.source, args.sha)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        # Never print provider replies, request arguments or credential-bearing exceptions.
        raise SystemExit('PF staging operation refused/failed. Deployment remains unaccepted; inspect locally without secrets.') from None
