"""Verify the deployed staging boundary. Never uploads or follows redirects.

Run only after private runtime acceptance, with dedicated tester credentials in
PF_STAGING_HTTP_USER / PF_STAGING_HTTP_PASSWORD (never CLI arguments or report).
The anonymous webhook test sends invalid data and must be rejected by PHP.
This is not a Stripe payment test or proof of private filesystem isolation.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import ssl
import urllib.error
import urllib.request

STAGE = 'https://test.pracowniaform.com'
TECHNICAL = 'https://serwer533947.lh.pl/pf-stage-20261114/www'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(opener, method, url, authorization=None):
    # This checker is intentionally unusable against production or another vhost.
    if not (url.startswith(STAGE + '/') or url.startswith(TECHNICAL + '/') or
            url == 'http://test.pracowniaform.com/'):
        raise ValueError('Out-of-scope target')
    if authorization and not url.startswith(STAGE + '/'):
        raise ValueError('Credentials only over HTTPS to the staging hostname')
    headers = {'User-Agent': 'PF-staging-access-check', 'Cache-Control': 'no-cache'}
    if authorization:
        headers['Authorization'] = authorization
    body = b'{}' if method == 'POST' else None
    if body is not None:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        response = opener.open(req, timeout=20)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        raw = response.read(65536)
        robots = response.headers.get('X-Robots-Tag', '').lower()
        cache = response.headers.get('Cache-Control', '').lower()
        try:
            signature_rejected = json.loads(raw).get('error') == 'SIGNATURE'
        except (ValueError, AttributeError, UnicodeError):
            signature_rejected = False
        return {
            'status': response.status,
            'noindex': 'noindex' in robots,
            'no_store': 'no-store' in cache,
            'basic_challenge': response.headers.get('WWW-Authenticate', '').lower().startswith('basic '),
            'signature_rejected': signature_rejected,
            'redirect_to_stage_https': response.headers.get('Location', '') == STAGE+'/',
        }


def check(opener, authorization, asset):
    if not re.fullmatch(r'/assets/[A-Za-z0-9_./-]+\.(?:avif|webp|jpg|png|woff2)', asset) or '..' in asset:
        raise ValueError('Select an existing public asset from the release manifest')
    cases = [
        ('anonymous_root', 'GET', STAGE+'/', None, 'basic'),
        ('anonymous_head', 'HEAD', STAGE+'/', None, 'basic'),
        ('anonymous_asset', 'GET', STAGE+asset, None, 'basic'),
        ('anonymous_catalog', 'GET', STAGE+'/data/store-media.json', None, 'basic'),
        ('anonymous_api', 'GET', STAGE+'/api/status.php', None, 'basic'),
        ('anonymous_api_post', 'POST', STAGE+'/api/status.php', None, 'basic'),
        ('anonymous_root_post', 'POST', STAGE+'/', None, 'basic'),
        ('tester_root', 'GET', STAGE+'/', authorization, 'ok'),
        ('tester_asset', 'GET', STAGE+asset, authorization, 'ok'),
        ('unsigned_webhook', 'POST', STAGE+'/api/webhook.php', None, 'signature'),
        ('webhook_get', 'GET', STAGE+'/api/webhook.php', None, 'basic'),
        ('webhook_query', 'POST', STAGE+'/api/webhook.php?probe=1', None, 'basic'),
        ('webhook_path_info', 'POST', STAGE+'/api/webhook.php/probe', None, 'denied'),
        ('webhook_encoded_path', 'POST', STAGE+'/api/%77ebhook.php', None, 'denied'),
        ('internal_include', 'GET', STAGE+'/api/_common.php', authorization, 'forbidden'),
        ('cli_seed', 'POST', STAGE+'/api/seed-test.php', authorization, 'forbidden'),
        ('cli_live', 'POST', STAGE+'/api/prepare-live.php', authorization, 'forbidden'),
        ('technical_root', 'GET', TECHNICAL+'/', None, 'forbidden'),
        ('technical_asset', 'GET', TECHNICAL+asset, None, 'forbidden'),
        ('technical_webhook', 'POST', TECHNICAL+'/api/webhook.php', None, 'forbidden'),
        ('plain_http', 'GET', 'http://test.pracowniaform.com/', None, 'tls'),
    ]
    results = []
    for name, method, url, auth, expected in cases:
        try:
            result = request(opener, method, url, auth)
            code = result['status']
            passed = {
                'basic': code == 401 and result['basic_challenge'],
                'ok': code == 200,
                'signature': code == 400 and result['signature_rejected'],
                'denied': code in (401, 403, 404),
                'forbidden': code == 403,
                'tls': code == 403 or (code in (301, 302, 307, 308) and result['redirect_to_stage_https']),
            }[expected]
            # All accepted content, including PHP errors, must be noindex/no-store.
            if expected in ('ok', 'signature'):
                passed = passed and result['noindex'] and result['no_store']
            results.append({'check': name, **result, 'pass': passed})
        except (OSError, ValueError, urllib.error.URLError):
            # Do not expose response bodies, exception URLs or credentials in logs.
            results.append({'check': name, 'pass': False, 'error': 'transport_or_response_failed'})
    return {'target': STAGE, 'scope': 'real HTTP access boundary only',
            'pass': all(row['pass'] for row in results), 'checks': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--asset', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    user = os.environ.get('PF_STAGING_HTTP_USER', '')
    password = os.environ.get('PF_STAGING_HTTP_PASSWORD', '')
    if not user or ':' in user or not password or any(c in user+password for c in '\r\n'):
        parser.error('Dedicated staging HTTP credentials required in environment')
    auth = 'Basic ' + base64.b64encode((user+':'+password).encode()).decode()
    opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    report = check(opener, auth, args.asset)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(('PASS' if report['pass'] else 'FAIL') + ': staging HTTP access boundary; no payment test')
    raise SystemExit(0 if report['pass'] else 1)


if __name__ == '__main__':
    main()
