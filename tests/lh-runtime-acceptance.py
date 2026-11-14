"""LOCAL SYNTHETIC fixtures only. Never deploy, contact LH, or read real configuration."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import tempfile
import time

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / 'scripts/lh_runtime_acceptance.php.in'
EXPECTED_PARENT = Path('C:/Users/lsolt/.codex/visualizations/2026/09/04/'
                       '01a06d6a-faec-75d1-a6c5-9a6946b9c460/pf-staging-private/runtime-probe-tests')
FIXTURE = b'PF-RUNTIME-PROBE-NONSECRET-v1\n'
ERRORS = {'not_found', 'scope_rejected', 'config_rejected', 'data_failed', 'sqlite_failed',
          'cleanup_failed', 'operation_failed', 'operator_verification_required'}


def check(ok, label):
    if not ok:
        raise AssertionError(label)  # Static labels only; never dump PHP stderr/paths/fixtures.


def php_quote(value):
    return "'" + str(value).replace('\\', '\\\\').replace("'", "\\'") + "'"


def write_new(path, content):
    with path.open('xb') as handle:
        handle.write(content.encode('utf-8') if isinstance(content, str) else content)


def reparse(path):
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def verify_parent(parent):
    check(parent == EXPECTED_PARENT and parent.resolve(strict=True) == parent, 'exact_fixture_parent')
    check(parent != REPO and REPO not in parent.parents, 'fixtures_outside_repo')
    for part in [parent, *parent.parents]:
        check(not reparse(part), 'fixture_parent_no_links')


def remove_fixture_tree(root, parent):
    """Only this freshly mkdtemp-created session; never follow reparse points."""
    verify_parent(parent)
    check(root.parent == parent and root.name.startswith('pf-runtime-synthetic-')
          and not reparse(root) and root.resolve(strict=True) == root, 'cleanup_exact_owned_session')
    for current, directories, files in os.walk(root, topdown=False, followlinks=False):
        current = Path(current)
        check(root == current or root in current.parents, 'cleanup_stays_owned')
        # os.walk does not descend into symlinks; junctions are removed before this call.
        check(not reparse(current) and current.resolve(strict=True) == current, 'cleanup_no_alias')
        for name in files:
            path = current / name
            if reparse(path):
                path.unlink()
            else:
                check(path.resolve(strict=True) == path, 'cleanup_exact_file')
                path.chmod(stat.S_IREAD | stat.S_IWRITE)
                path.unlink()
        for name in directories:
            path = current / name
            check(not reparse(path), 'unexpected_reparse_during_cleanup')
            path.rmdir()
    root.rmdir()
    check(not root.exists(), 'fixture_cleanup_complete')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--php', type=Path, default=REPO / '.artifacts/tools/php/php.exe')
    ap.add_argument('--private-temp-parent', type=Path, default=EXPECTED_PARENT)
    args = ap.parse_args()
    parent = args.private_temp_parent
    verify_parent(parent)
    php = args.php.resolve(strict=True)
    source = TEMPLATE.read_text(encoding='utf-8')
    lint = subprocess.run([str(php), '-l', str(TEMPLATE)], capture_output=True, timeout=20)
    check(lint.returncode == 0 and not lint.stderr, 'template_lint')
    # This path contains synthetic data only, never PEM/ACME/private runtime files.
    session = Path(tempfile.mkdtemp(prefix='pf-runtime-synthetic-', dir=parent))
    check(session.parent == parent and session.resolve(strict=True) == session, 'exclusive_session')
    results = []
    links = []

    def run_case(name, *, server=None, substitutions=None, permission_model=True,
                 fpm_model=True, inject=None, error=None, setup=None, remaining=False):
        base = session / name
        base.mkdir()
        web = base / 'www'
        private = base / 'runtime'
        config = private / 'config'
        data = private / 'data'
        web.mkdir()
        private.mkdir()
        config.mkdir()
        data.mkdir()
        fixture = config / 'lh-runtime-probe-fixture.txt'
        write_new(fixture, FIXTURE)
        sentinel = data / 'unrelated-existing.txt'
        write_new(sentinel, b'UNRELATED_KEEP\n')
        raw_token = secrets.token_hex(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        public = web / 'runtime-probe.php'
        now = int(time.time())
        values = {'ISSUED_UNIX': str(now - 2), 'EXPIRES_UNIX': str(now + 120),
                  'TOKEN_SHA256': token_hash, 'PRIVATE_ROOT': str(private), 'WEBROOT': str(web)}
        if substitutions:
            values.update(substitutions(base, values))
        rendered = source
        for key, value in values.items():
            # All placeholders are PHP single-quoted literals; no executable interpolation.
            rendered = rendered.replace("'@" + key + "@'", php_quote(value))
        check(not re.search(r'@[A-Z_]+@', rendered), 'all_placeholders_bound')
        if fpm_model:
            old = '$probeSapi = PHP_SAPI;'
            check(rendered.count(old) == 1, 'single_sapi_test_seam')
            rendered = rendered.replace(old, "$probeSapi = 'fpm-fcgi'; // SYNTHETIC CLI MODEL")
        if permission_model:
            # Windows CLI cannot establish LH/POSIX FPM ACLs. Model ONLY the two
            # expected readonly-policy results. File IO, realpaths, cleanup and SQLite
            # remain real. Separate tests below execute the original writable path.
            old = '$out[\'config_not_writable\'] = !is_writable($fixture) && !is_writable($config) && !is_writable($private);'
            check(rendered.count(old) == 1, 'single_permission_test_seam')
            rendered = rendered.replace(old, "$out['config_not_writable'] = true; // SYNTHETIC ACL MODEL")
            old = "$configAttempt = @fopen($configCanary, 'x+b');"
            check(rendered.count(old) == 1, 'single_config_create_test_seam')
            rendered = rendered.replace(old, '$configAttempt = false; // SYNTHETIC DENIED CREATE')
        if inject:
            rendered = inject(rendered)
        if setup:
            setup(base, private, fixture)
        check(raw_token not in rendered, 'raw_token_not_in_webroot')
        write_new(public, rendered)
        request = {'HTTPS': 'on', 'SERVER_PORT': '443', 'HTTP_HOST': 'test.pracowniaform.com',
                   'REQUEST_METHOD': 'POST', 'HTTP_X_PF_PROBE_TOKEN': raw_token,
                   'DOCUMENT_ROOT': str(web), 'SCRIPT_FILENAME': str(public)}
        request.update(server or {})
        wrapper = '<?php\n// SYNTHETIC REQUEST, outside fixture WWW.\n$_SERVER = [\n'
        wrapper += ',\n'.join(php_quote(k) + ' => ' + php_quote(v) for k, v in request.items())
        wrapper += '\n];\nrequire ' + php_quote(public) + ';\n'
        runner = base / 'synthetic-request.php'
        write_new(runner, wrapper)
        result = subprocess.run([str(php), str(runner)], cwd=base, capture_output=True, timeout=30)
        check(not result.stderr, name + ':empty_stderr')
        check(result.returncode == 0, name + ':clean_exit')
        try:
            out = json.loads(result.stdout)
        except (ValueError, UnicodeError):
            raise AssertionError(name + ':safe_json_only') from None
        check(isinstance(out, dict) and out.get('error') in ERRORS, name + ':safe_error')
        check(all(isinstance(v, bool) for k, v in out.items() if k != 'error'), name + ':booleans_only')
        check(out['operator_verified'] is False and out['accepted'] is False, name + ':operator_gate')
        check(str(private).encode() not in result.stdout and raw_token.encode() not in result.stdout,
              name + ':no_disclosure')
        check(sentinel.read_bytes() == b'UNRELATED_KEEP\n', name + ':existing_data_untouched')
        if error:
            check(out['error'] == error and not out['runtime_ok'], name + ':expected_refusal')
        else:
            if not out['runtime_ok']:
                print(json.dumps({'case': name, 'safe_probe_result': out}))
            check(out['runtime_ok'] and out['error'] == 'operator_verification_required', name + ':runtime_pass')
            check(all(v for k, v in out.items() if k not in {'error', 'operator_verified', 'accepted'}),
                  name + ':all_real_operations_pass')
        if not remaining:
            check(sorted(p.name for p in data.iterdir()) == ['unrelated-existing.txt'], name + ':data_clean')
            check(out.get('cleanup_ok', True), name + ':cleanup_ok')
        else:
            check(not out['cleanup_ok'], name + ':unsafe_cleanup_refused')
        if not reparse(config):
            check(sorted(p.name for p in config.iterdir()) == ['lh-runtime-probe-fixture.txt'], name + ':config_clean')
        results.append({'case': name, 'pass': True})
        return base, out

    try:
        # Actual, unmodified CLI guard: no synthetic SAPI bypass.
        run_case('actual_cli_denied', fpm_model=False, permission_model=False, error='not_found')
        run_case('synthetic_fpm_filesystem_sqlite_pass')
        for name, changes in (
            ('http_denied', {'HTTPS': ''}), ('proxy_header_not_trusted', {'HTTPS': '', 'HTTP_X_FORWARDED_PROTO': 'https'}),
            ('port_denied', {'SERVER_PORT': '80'}), ('technical_host_denied', {'HTTP_HOST': 'serwer533947.lh.pl'}),
            ('host_suffix_denied', {'HTTP_HOST': 'test.pracowniaform.com.attacker.invalid'}),
            ('host_port_denied', {'HTTP_HOST': 'test.pracowniaform.com:443'}),
            ('get_denied', {'REQUEST_METHOD': 'GET'}), ('missing_token', {'HTTP_X_PF_PROBE_TOKEN': ''}),
            ('wrong_token', {'HTTP_X_PF_PROBE_TOKEN': '0' * 64}),
            ('document_root_mismatch', {'DOCUMENT_ROOT': 'invalid'}),
            ('script_filename_mismatch', {'SCRIPT_FILENAME': 'invalid'}),
        ):
            run_case(name, server=changes, error='scope_rejected' if name.endswith('mismatch') else 'not_found')
        now = int(time.time())
        run_case('expired', substitutions=lambda b, v: {'ISSUED_UNIX': str(now - 120), 'EXPIRES_UNIX': str(now - 1)}, error='not_found')
        run_case('not_yet_valid', substitutions=lambda b, v: {'ISSUED_UNIX': str(now + 30)}, error='not_found')
        run_case('too_long_lifetime', substitutions=lambda b, v: {'EXPIRES_UNIX': str(now + 3600)}, error='not_found')
        run_case('traversal_root', substitutions=lambda b, v: {'PRIVATE_ROOT': v['PRIVATE_ROOT'] + os.sep + '..' + os.sep + 'runtime'}, error='scope_rejected')
        run_case('nested_webroot', substitutions=lambda b, v: {'PRIVATE_ROOT': v['WEBROOT']}, error='scope_rejected')
        run_case('wrong_fixture', setup=lambda b, p, f: f.write_bytes(b'SYNTHETIC_WRONG_FIXTURE\n'), error='config_rejected')
        run_case('actual_writable_config_rejected', permission_model=False, error='config_rejected')
        run_case('unexpected_config_create_rejected', inject=lambda s: s.replace(
            '$configAttempt = false; // SYNTHETIC DENIED CREATE', "$configAttempt = @fopen($configCanary, 'x+b');"),
            error='config_rejected')

        def junction_setup(base, private, fixture):
            fixture.unlink()  # This test's own known synthetic file, not a runtime file.
            fixture.parent.rmdir()
            target = base / 'synthetic-link-target'
            target.mkdir()
            write_new(target / fixture.name, FIXTURE)
            alias = private / 'config'
            if os.name == 'nt':
                proc = subprocess.run(['cmd.exe', '/c', 'mklink', '/J', str(alias), str(target)], capture_output=True, timeout=10)
                check(proc.returncode == 0, 'synthetic_junction_created')
            else:
                alias.symlink_to(target, target_is_directory=True)
            links.append((alias, target))

        run_case('symlink_ancestor_denied', setup=junction_setup, error='scope_rejected')
        run_case('exclusive_collision_preserves_existing', inject=lambda s: s.replace(
            "$handle = createOwn($file);", "$file = $data . $sep . 'unrelated-existing.txt';\n    $handle = createOwn($file);"), error='data_failed')
        run_case('exception_does_not_leak', inject=lambda s: s.replace(
            "$out['data_read_write'] = true;", "$out['data_read_write'] = true; throw new RuntimeException('SYNTHETIC_LEAK ' . $private);"), error='data_failed')
        run_case('delete_journal_failure_cleanup', inject=lambda s: s.replace(
            "$out['sqlite_delete_journal_seen'] = true;", "$out['sqlite_delete_journal_seen'] = true; throw new RuntimeException('SYNTHETIC_LEAK ' . $private);"), error='sqlite_failed')
        run_case('wal_failure_cleanup', inject=lambda s: s.replace(
            "$out['sqlite_shm_seen'] = true;", "$out['sqlite_shm_seen'] = true; throw new RuntimeException('SYNTHETIC_LEAK ' . $private);"), error='sqlite_failed')
        run_case('wal_file_required', inject=lambda s: s.replace(
            "demand(sidecarSeen($sqlite . '-wal'));", "demand(sidecarSeen($sqlite . '-missing-wal'));"), error='sqlite_failed')
        run_case('shm_file_required', inject=lambda s: s.replace(
            "demand(sidecarSeen($sqlite . '-shm'));", "demand(sidecarSeen($sqlite . '-missing-shm'));"), error='sqlite_failed')
        base, out = run_case('root_identity_mismatch_no_delete', inject=lambda s: s.replace(
            "$out['data_read_write'] = true;", "$out['data_read_write'] = true; $roots[$run] = [0, -1, 0040000];"),
            error='cleanup_failed', remaining=True)
        check(any((base / 'runtime/data').glob('pf-runtime-probe-*/*.tmp')), 'unsafe_root_file_preserved')
        base, out = run_case('foreign_file_not_deleted', inject=lambda s: s.replace(
            "$out['data_delete'] = true;", "$out['data_delete'] = true; file_put_contents($run . $sep . 'foreign.txt', 'SYNTHETIC_FOREIGN');"),
            error='cleanup_failed', remaining=True)
        check(any(p.read_bytes() == b'SYNTHETIC_FOREIGN' for p in (base / 'runtime/data').glob('pf-runtime-probe-*/foreign.txt')),
              'foreign_file_preserved')
    finally:
        # Remove only generated junctions themselves, never their targets through an alias.
        for alias, target in links:
            check(session in alias.parents and session in target.parents and reparse(alias)
                  and alias.resolve(strict=True) == target, 'cleanup_known_junction')
            if os.name == 'nt':
                os.rmdir(alias)
            else:
                alias.unlink()
        remove_fixture_tree(session, parent)
    print(json.dumps({'scope': 'LOCAL SYNTHETIC ONLY; no LH/FPM/ACL/HTTPS acceptance',
                      'sapi_and_readonly_acl_modeled': True, 'real_filesystem_and_sqlite': True,
                      'lint': True, 'cases': results, 'cleanup': True}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # Assertion labels are static; OS/PHP error text may contain full paths.
        label = str(exc) if isinstance(exc, AssertionError) else 'local_harness_failed'
        print(json.dumps({'pass': False, 'error': label}))
        raise SystemExit(1) from None
