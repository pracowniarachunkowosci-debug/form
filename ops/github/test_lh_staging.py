"""Offline security regression tests. All temporary writes stay under ops/github/."""
from contextlib import ExitStack
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import lh_staging as staging


HERE = Path(__file__).resolve().parent
SHA = 'a0a6cd5ce2c82edcab4c132baea878b4aabbcafe'


def fixture(directory, entries=None, mode=0o100644):
    directory.mkdir()
    entries = entries or [('index.html', b'<h1>synthetic fixture</h1>'),
                          ('robots.txt', b'User-agent: *\nAllow: /\n'),
                          ('api/status.php', b'<?php // synthetic fixture'),
                          ('api/prepare-live.php', b'<?php // synthetic CLI fixture'),
                          ('api/seed-test.php', b'<?php // synthetic CLI fixture'),
                          ('assets/test.svg', b'<svg/>')]
    rows = []
    with ZipFile(directory / 'pracownia-form-lh.zip', 'w', compression=ZIP_DEFLATED) as archive:
        for name, raw in entries:
            info = ZipInfo(name)
            info.create_system = 3
            info.external_attr = mode << 16
            archive.writestr(info, raw)
            rows.append(dict(path=name, bytes=len(raw), sha256=staging.digest(raw)))
    raw_zip = (directory / 'pracownia-form-lh.zip').read_bytes()
    manifest = staging.json_bytes(rows)
    (directory / 'manifest.json').write_bytes(manifest)
    report = dict(source_commit=SHA, source_dirty=False, archive='pracownia-form-lh.zip',
                  archive_sha256=staging.digest(raw_zip), archive_bytes=len(raw_zip),
                  manifest_sha256=staging.digest(manifest), files=len(rows),
                  uploaded_by_this_build=False, deployment_target='LH Orange')
    (directory / 'release.json').write_bytes(staging.json_bytes(report))


class FakeFTP:
    def __init__(self, collision=False, corrupt=False):
        self.events = []
        self.files = {}
        self.current = '/'
        self.collision = collision
        self.corrupt = corrupt

    def cwd(self, name):
        self.current = name if name == '/' else '/' + name
        self.events.append(('cwd', name))

    def pwd(self):
        return self.current

    def mkd(self, name):
        self.events.append(('mkd', name))
        if self.collision:
            raise RuntimeError('directory already exists')

    def storbinary(self, command, stream):
        self.events.append(('store', command))
        self.files[command.removeprefix('STOR ')] = stream.read()

    def retrbinary(self, command, callback):
        self.events.append(('read', command))
        callback(b'corrupt' if self.corrupt else self.files[command.removeprefix('RETR ')])


class StagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pf-proposal-test-', dir=HERE)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Every test fails on an accidental real network connection.
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch('socket.socket.connect', side_effect=AssertionError('Network forbidden')))
        self.source = self.root / 'source'
        fixture(self.source)

    def packaged(self):
        output = self.root / 'protected'
        hashes = staging.package(self.source, output, SHA)
        return output, hashes

    def test_full_sha_and_run_identity_reject_injection(self):
        for value in ('main', 'a0a6cd5', SHA.upper(), SHA + '\n', '../x', '$(whoami)', 'a' * 39 + ';'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                staging.checked_sha(value)
        for run in ('', '0', '-1', '../x', '1\nDELE x', '$(id)'):
            with self.subTest(run=run), self.assertRaises(ValueError):
                staging.release_name(SHA, run, '1')

    def test_guard_first_and_derived_hashes_without_changing_source(self):
        before = {p.name: p.read_bytes() for p in self.source.iterdir()}
        output, hashes = self.packaged()
        blobs, report, actual = staging.read_bundle(output, SHA, True, hashes)
        self.assertEqual(next(iter(blobs)), '.htaccess')
        self.assertEqual(blobs['.htaccess'], staging.protection_bytes())
        self.assertEqual(blobs['robots.txt'], b'User-agent: *\nDisallow: /\n')
        self.assertTrue(staging.CLI_ONLY.isdisjoint(blobs))
        self.assertEqual(actual, hashes)
        self.assertEqual(report['source_archive_sha256'], staging.digest(before['pracownia-form-lh.zip']))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.source.iterdir()})
        again = self.root / 'again'
        self.assertEqual(staging.package(self.source, again, SHA), hashes)

    def test_dirty_or_wrong_commit_rejected(self):
        with self.assertRaises(ValueError):
            staging.read_bundle(self.source, 'b' * 40)
        report = json.loads((self.source / 'release.json').read_bytes())
        report['source_dirty'] = True
        (self.source / 'release.json').write_bytes(staging.json_bytes(report))
        with self.assertRaises(ValueError):
            staging.read_bundle(self.source, SHA)

    def test_zip_and_independent_build_hash_tampering_rejected(self):
        output, hashes = self.packaged()
        wrong = {**hashes, 'release_sha256': '0' * 64}
        with self.assertRaises(ValueError):
            staging.read_bundle(output, SHA, True, wrong)
        with (output / staging.ARCHIVE).open('ab') as handle:
            handle.write(b'tamper')
        with self.assertRaises(ValueError):
            staging.read_bundle(output, SHA, True)

    def test_unsafe_archive_paths_rejected(self):
        for index, name in enumerate(('../index.html', '/index.html', 'api/../x.php', 'api//x.php',
                                      'api/x.php\r\nDELE x', 'assets/a/.htaccess', '.env',
                                      'config.json', 'data/private.json', 'data/db.sqlite',
                                      '.user.ini', 'scripts/stage_lh.py', 'x\\index.html',
                                      'assets/link.php', '.htaccess')):
            with self.subTest(name=name):
                directory = self.root / f'bad-{index}'
                fixture(directory, [('index.html', b'ok'), (name, b'bad')])
                with self.assertRaises(ValueError):
                    staging.read_bundle(directory, SHA)

    def test_links_and_zip_bomb_limits_rejected(self):
        directory = self.root / 'link'
        fixture(directory, [('index.html', b'target')], stat.S_IFLNK | 0o777)
        with self.assertRaises(ValueError):
            staging.read_bundle(directory, SHA)
        with patch.object(staging, 'MAX_FILE', 1), self.assertRaises(ValueError):
            staging.read_bundle(self.source, SHA)

    def test_existing_output_not_reused(self):
        output, _ = self.packaged()
        with self.assertRaises(FileExistsError):
            staging.package(self.source, output, SHA)

    def test_upload_is_blocked_before_secrets_files_or_transport(self):
        self.assertFalse(staging.INFRASTRUCTURE_ACCEPTED)
        with patch.object(staging, 'read_bundle', side_effect=AssertionError('No file access')), \
             patch.object(staging, 'FTP_TLS', side_effect=AssertionError('No transport')), \
             patch.dict(os.environ, {'PF_FTPS_HOST': 'other.invalid', 'PF_FTPS_USER': 'production',
                                     'INFRASTRUCTURE_ACCEPTED': 'true'}):
            with self.assertRaisesRegex(ValueError, 'BLOCKED'):
                staging.upload(self.root / 'absent', SHA)

    def test_future_transport_guard_probe_then_payload_and_readback(self):
        output, _ = self.packaged()
        blobs, _, _ = staging.read_bundle(output, SHA, True)
        ftp = FakeFTP()
        name = staging.release_name(SHA, '123', '1')
        staging.send_new_directory(ftp, name, blobs, lambda _: ftp.events.append(('probe', 'deny')))
        stores = [event[1] for event in ftp.events if event[0] == 'store']
        self.assertEqual(stores[:2], ['STOR .htaccess', 'STOR ' + staging.CANARY])
        self.assertLess(ftp.events.index(('probe', 'deny')), ftp.events.index(('store', 'STOR index.html')))
        self.assertEqual(sum(e[0] == 'read' for e in ftp.events), len(stores))
        self.assertEqual(sum(e[0] == 'probe' for e in ftp.events), 2)

    def test_failed_protection_probe_never_sends_application(self):
        output, _ = self.packaged()
        blobs, _, _ = staging.read_bundle(output, SHA, True)
        ftp = FakeFTP()
        def deny(_):
            raise ValueError('HTTP unexpectedly public')
        with self.assertRaises(ValueError):
            staging.send_new_directory(ftp, staging.release_name(SHA, '123', '1'), blobs, deny)
        self.assertEqual(set(ftp.files), {'.htaccess', staging.CANARY})

    def test_collision_or_readback_error_stops_upload(self):
        output, _ = self.packaged()
        blobs, _, _ = staging.read_bundle(output, SHA, True)
        for ftp in (FakeFTP(collision=True), FakeFTP(corrupt=True)):
            with self.subTest(ftp=ftp), self.assertRaises((ValueError, RuntimeError)):
                staging.send_new_directory(ftp, staging.release_name(SHA, '123', '1'), blobs, lambda _: None)
            self.assertNotIn('index.html', ftp.files)

    def test_http_probe_rejects_public_redirect_missing_header_and_wrong_body(self):
        for status, headers, body, accepted in (
            (200, {}, b'public', False), (302, {}, b'', False), (500, {}, b'', False),
            (403, {}, b'PF staging quarantine', False),
            (403, {'X-Robots-Tag': 'noindex', 'Cache-Control': 'no-store'}, b'other policy', False),
            (403, {'X-Robots-Tag': 'noindex', 'Cache-Control': 'private, no-store'}, b'PF staging quarantine', True),
        ):
            class Response:
                def getheader(self, key, default): return headers.get(key, default)
                def read(self, _): return body
            response = Response()
            response.status = status
            with patch.object(staging, 'HTTPConnection') as http, \
                 patch.object(staging, 'HTTPSConnection') as https, \
                 patch.object(staging.ssl, 'create_default_context'):
                http.return_value.getresponse.return_value = response
                https.return_value.getresponse.return_value = response
                if accepted:
                    staging.check_denial(staging.release_name(SHA, '123', '1'))
                else:
                    with self.assertRaises(ValueError):
                        staging.check_denial(staging.release_name(SHA, '123', '1'))

    def test_workflow_hard_locks_and_no_dynamic_shell_expressions(self):
        text = (HERE / 'lh-staging.workflow.yml.example').read_text(encoding='utf-8')
        self.assertEqual(text.count('if: ${{ false && inputs.request_ftps }}'), 2)
        self.assertNotIn('pull_request_target:', text)
        self.assertNotIn('workflow_run:', text)
        self.assertNotIn('contents: write', text)
        self.assertNotIn('scripts/stage_lh.py', text)
        self.assertEqual(text.count('${{ secrets.'), 1)
        in_script = False
        for line in text.splitlines():
            if line.strip() == 'run: |':
                in_script = True
            elif line.strip() and len(line) - len(line.lstrip()) < 10:
                in_script = False
            if in_script:
                self.assertNotIn('${{', line)

    def test_actual_workflow_preflight_accepts_only_exact_pf_snapshot(self):
        text = (HERE / 'lh-staging.workflow.yml.example').read_text(encoding='utf-8')
        script = text.split("python3 - <<'PY'\n", 1)[1].split('\n          PY', 1)[0]
        script = '\n'.join(line[10:] for line in script.splitlines())
        context = dict(GITHUB_REPOSITORY=staging.REPOSITORY, GITHUB_EVENT_NAME='workflow_dispatch',
                       GITHUB_REF='refs/heads/main', GITHUB_SHA=SHA, GITHUB_WORKFLOW_SHA=SHA,
                       GITHUB_WORKFLOW_REF=staging.REPOSITORY + '/.github/workflows/lh-staging.yml@refs/heads/main',
                       REQUESTED_SHA=SHA, GITHUB_OUTPUT=str(self.root / 'job-output'))
        cases = [{}, {'REQUESTED_SHA': 'main'}, {'REQUESTED_SHA': SHA + '\n'},
                 {'REQUESTED_SHA': '$(whoami)'}, {'REQUESTED_SHA': 'b' * 40},
                 {'GITHUB_REPOSITORY': 'other/form'}, {'GITHUB_REF': 'refs/heads/other'},
                 {'GITHUB_EVENT_NAME': 'pull_request_target'}, {'GITHUB_WORKFLOW_SHA': 'b' * 40},
                 {'GITHUB_WORKFLOW_REF': staging.REPOSITORY + '/.github/workflows/other.yml@refs/heads/main'}]
        for changes in cases:
            with self.subTest(changes=changes):
                result = subprocess.run([sys.executable, '-B', '-c', script],
                                        env={**os.environ, **context, **changes}, capture_output=True)
                self.assertEqual(result.returncode == 0, not changes, result.stderr.decode())
        self.assertEqual((self.root / 'job-output').read_text(), 'sha=' + SHA + '\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
