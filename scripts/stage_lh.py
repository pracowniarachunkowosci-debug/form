"""Upload a verified webroot to a NEW release directory on PF's existing LH server."""
import argparse
from ftplib import FTP_TLS
from getpass import getpass
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path, PurePosixPath
import re
import ssl
from zipfile import ZipFile


def checked_files(directory):
    report = json.loads((directory/'release.json').read_text(encoding='utf-8'))
    archive = directory/'pracownia-form-lh.zip'
    manifest = (directory/'manifest.json').read_bytes()
    if (sha256(archive.read_bytes()).hexdigest() != report['archive_sha256'] or
            sha256(manifest).hexdigest() != report['manifest_sha256']):
        raise ValueError('Release or manifest checksum mismatch')
    reference = json.loads(manifest)
    with ZipFile(archive) as z:
        entries = [r['path'] for r in reference]
        if z.namelist() != entries or len(set(entries)) != len(entries): raise ValueError('Unexpected archive entries')
        for row in reference:
            name = row['path']
            if not re.fullmatch(r'[A-Za-z0-9_./-]+', name) or any(i in ('','.','..') for i in name.split('/')): raise ValueError('Unsafe path')
            raw = z.read(name)
            if len(raw)!=row['bytes'] or sha256(raw).hexdigest()!=row['sha256']: raise ValueError(name)
            yield name,raw,row['sha256']


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory', type=Path, help='Local directory containing ZIP, manifest.json and release.json')
    ap.add_argument('--upload',action='store_true',help='Upload only to a fresh child directory; does not change DNS or the active vhost')
    ap.add_argument('--base-dir',help='Existing absolute FTPS parent in the intended LH account')
    ap.add_argument('--name',help='A new release directory, e.g. winter26-20261111-rc1')
    ap.add_argument('--host',default='serwer533947.lh.pl',help='Verified LH hostname from the hosting panel')
    args = ap.parse_args()
    files=list(checked_files(args.directory))
    if not args.upload:
        print(f'Verified {len(files)} webroot files locally. Nothing uploaded.');return
    if (not args.base_dir or not args.base_dir.startswith('/') or '..' in args.base_dir.split('/') or
        not re.fullmatch(r'winter26-[a-zA-Z0-9_-]+',args.name or '') or not re.fullmatch(r'[a-zA-Z0-9-]+\.lh\.pl',args.host)):
        ap.error('Specify an existing absolute --base-dir, a NEW --name winter26-... and the FTPS host from LH.')
    user=os.environ.get('PF_FTPS_USER') or input('Login FTPS (LH): ')
    password=os.environ.get('PF_FTPS_PASSWORD') or getpass('Hasło FTPS (LH): ')
    with FTP_TLS(context=ssl.create_default_context(),timeout=30) as ftp:
        ftp.connect(args.host,21);ftp.auth();ftp.login(user,password);ftp.prot_p()
        ftp.cwd(args.base_dir);ftp.mkd(args.name);ftp.cwd(args.name)  # aborts if the directory exists
        made=set()
        for name,raw,expected in files:
            for sub in reversed(PurePosixPath(name).parents):
                component=sub.as_posix()
                if component!='.' and component not in made:
                    ftp.mkd(component);made.add(component)
            ftp.storbinary('STOR '+name,BytesIO(raw))
            got=sha256();ftp.retrbinary('RETR '+name,got.update)
            if got.hexdigest()!=expected: raise ValueError('Remote verification failed: '+name)
        print(f'Uploaded and verified {len(files)} files in {ftp.pwd()}. No vhost or DNS changes.')


if __name__=='__main__': main()
