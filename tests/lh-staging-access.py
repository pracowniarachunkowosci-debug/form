"""Offline tests of the HTTP verifier, NOT tests of Apache or LH."""
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lh_access', ROOT/'scripts/check_lh_staging_access.py')
access = importlib.util.module_from_spec(spec)
spec.loader.exec_module(access)


class AccessTests(unittest.TestCase):
    def test_credentials_cannot_leave_https_stage(self):
        class RejectNetwork:
            def open(self, *args, **kwargs):
                raise AssertionError('must reject before transport')
        for url in ('http://test.pracowniaform.com/', access.TECHNICAL+'/',
                    'https://test.pracowniaform.com.evil.invalid/', 'https://pracowniaform.com/'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                access.request(RejectNetwork(), 'GET', url, 'Basic synthetic')

    def test_redirects_never_follow_or_forward_credentials(self):
        self.assertIsNone(access.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.invalid/'))

    def test_invalid_signature_requires_actual_error_code(self):
        class Response(BytesIO):
            status = 400
            headers = {'X-Robots-Tag': 'noindex', 'Cache-Control': 'no-store'}
        class Opener:
            def __init__(self, raw): self.raw = raw
            def open(self, *args, **kwargs): return Response(self.raw)
        for raw, expected in [(b'{"error":"SIGNATURE"}', True),
                              (b'{"error":"UNAVAILABLE"}', False), (b'<h1>400</h1>', False)]:
            self.assertEqual(access.request(Opener(raw), 'POST', access.STAGE+'/api/webhook.php')['signature_rejected'], expected)

    def test_public_content_is_failure_even_with_noindex(self):
        public = {'status': 200, 'noindex': True, 'no_store': True,
                  'basic_challenge': False, 'signature_rejected': False,
                  'redirect_to_stage_https': False}
        with patch.object(access, 'request', return_value=public):
            result = access.check(None, 'Basic synthetic', '/assets/fixture.webp')
        self.assertFalse(result['pass'])
        self.assertFalse(next(r for r in result['checks'] if r['check']=='anonymous_asset')['pass'])
        self.assertFalse(next(r for r in result['checks'] if r['check']=='unsigned_webhook')['pass'])

    def test_transport_errors_are_redacted_and_not_pass(self):
        with patch.object(access, 'request', side_effect=urllib.error.URLError('PRIVATE TEST PASSWORD')):
            result = access.check(None, 'Basic PRIVATE TEST PASSWORD', '/assets/fixture.webp')
        self.assertFalse(result['pass'])
        self.assertNotIn('PRIVATE TEST PASSWORD', json.dumps(result))
        self.assertEqual(len(result['checks']), 21)

    def test_broad_post_api_exception_does_not_pass(self):
        def fixture(opener, method, url, auth):
            result = {'status': 401, 'noindex': True, 'no_store': True,
                      'basic_challenge': True, 'signature_rejected': False,
                      'redirect_to_stage_https': False}
            if not url.startswith(access.STAGE+'/') or (auth and '/api/' in url):
                result['status'] = 403
            elif auth:
                result['status'] = 200
            elif method == 'POST' and url == access.STAGE+'/api/webhook.php':
                result.update(status=400, signature_rejected=True)
            return result
        with patch.object(access, 'request', side_effect=fixture):
            self.assertTrue(access.check(None, 'Basic synthetic', '/assets/fixture.webp')['pass'])
        def broken(opener, method, url, auth):
            result = fixture(opener, method, url, auth)
            if method == 'POST' and url == access.STAGE+'/api/status.php':
                # PHP rejects the wrong method, but Apache wrongly let it through.
                result.update(status=405, basic_challenge=False)
            return result
        with patch.object(access, 'request', side_effect=broken):
            result = access.check(None, 'Basic synthetic', '/assets/fixture.webp')
        self.assertFalse(result['pass'])
        self.assertFalse(next(r for r in result['checks'] if r['check']=='anonymous_api_post')['pass'])

    def test_bad_asset_path_rejected_before_network(self):
        with patch.object(access, 'request', side_effect=AssertionError('network')):
            for asset in ('https://other.invalid/a.webp', '/assets/../a.webp', '/api/status.php'):
                with self.assertRaises(ValueError):
                    access.check(None, 'Basic synthetic', asset)


if __name__ == '__main__':
    unittest.main(verbosity=2)
