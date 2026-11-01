"""Dependency-free review checks: links/assets, document semantics and no-sale boundaries."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote, quote
from urllib.request import urlopen
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
errors = []

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.refs, self.tags = path, [], [], []
        self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        self.tags.append((tag, a))
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'img' and not a.get('alt'): errors.append(f'{self.path.name}: missing image alt')
        if tag == 'form': errors.append(f'{self.path.name}: live form is forbidden in review')
        if tag == 'script' and a.get('src') != 'script.js': errors.append(f'{self.path.name}: unexpected executable script')
        for attr in ['href', 'src', 'action']:
            if attr in a: self.refs.append((tag, attr, a[attr], a))
        if 'style' in a:
            self.refs.extend(('style', 'url', url, {}) for url in re.findall(r"url\(['\"]?([^)'\"]+)", a['style']))

pages = {p.name: Page(p) for p in ROOT.glob('*.html')}
refs = 0
http_paths = set(pages)
for name, page in pages.items():
    if len(page.ids) != len(set(page.ids)): errors.append(f'{name}: duplicate IDs')
    if sum(t == 'h1' for t, _ in page.tags) != 1: errors.append(f'{name}: must have one H1')
    for required in ['main', 'siteNav', 'menuBtn']:
        if required not in page.ids: errors.append(f'{name}: missing {required}')
    for attr, expected in [('name', 'description'), ('name', 'robots'), ('property', 'og:title'), ('property', 'og:description')]:
        if not any(t == 'meta' and a.get(attr) == expected for t, a in page.tags): errors.append(f'{name}: missing {expected}')
    if not any(t == 'meta' and a.get('content') == 'noindex, nofollow' for t, a in page.tags): errors.append(f'{name}: not noindex')
    if not any(t == 'link' and a.get('rel') == 'canonical' for t, a in page.tags): errors.append(f'{name}: missing canonical')
    if not any(t == 'meta' and "form-action 'none'" in a.get('content', '') and "connect-src 'none'" in a.get('content', '') for t, a in page.tags): errors.append(f'{name}: review CSP absent')
    for tag, attr, raw, attrs in page.refs:
        refs += 1
        url = urlsplit(raw)
        if raw == '#': errors.append(f'{name}: empty anchor')
        if url.scheme in ['mailto', 'tel', 'data']: continue
        if url.netloc:
            if tag in ['script', 'iframe', 'img'] or (tag == 'link' and attrs.get('rel') == 'stylesheet'): errors.append(f'{name}: external runtime asset {raw}')
            continue
        target = unquote(url.path) or name
        http_paths.add(target)
        if not (ROOT / target).is_file(): errors.append(f'{name}: missing file {target}')
        if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids: errors.append(f'{name}: missing anchor {target}#{url.fragment}')
for path in ROOT.glob('*.css'):
    for raw in re.findall(r"url\(['\"]?([^)'\"]+)", path.read_text(encoding='utf-8')):
        if not raw.startswith('data:'): http_paths.add(raw)
        if not raw.startswith('data:') and not (ROOT / raw).is_file(): errors.append(f'{path.name}: missing CSS asset {raw}')
data = json.loads((ROOT / 'data/winter-26.json').read_text(encoding='utf-8'))
assert data['reviewOnly'] and data['saleEnabled'] is False
assert {p['name'] for p in data['products']} == {'KNITTED STAR', 'KNITTED MEDALLION', 'HELIX', 'FULL SOFT'}
assert set(data['availabilityLabels']) == {'in_stock', 'made_to_order', 'unavailable'}
for product in data['products']:
    assert product['photo'] is None and product['material'] is None
    for variant in product['variants']:
        assert variant['availability'] == 'unavailable'
        assert all(variant[k] is None for k in ['sku', 'color', 'pricePLN', 'stock', 'dispatchDaysInStock', 'dispatchDaysMadeToOrder'])
        assert f'id="{product["id"]}"' in (ROOT / 'winter-26.html').read_text(encoding='utf-8')
assert [s['quantity'] for s in data['sets']] == [2, 4]
for path in [ROOT / 'sitemap.xml', ROOT / 'docs/sitemap-after-approval.xml']: ET.parse(path)
for path in ROOT.glob('*.html'):
    text = path.read_text(encoding='utf-8')
    for stale in ['pracowniaform.pl', '[uzupełnij', 'ec.europa.eu/consumers/odr', 'PF_GA_MEASUREMENT_ID']:
        if stale in text: errors.append(f'{path.name}: stale marker {stale}')
print(f'Checked {len(pages)} pages, {refs} HTML references, CSS assets, metadata, CSP and product data.')
if '--http' in sys.argv:
    for path in sorted(http_paths):
        try:
            with urlopen('http://127.0.0.1:8763/' + quote(path), timeout=10) as response:
                if response.status != 200: errors.append(f'HTTP {response.status}: {path}')
        except Exception as exc:
            errors.append(f'HTTP failure {path}: {exc}')
    print(f'HTTP GET checked {len(http_paths)} unique local pages/assets on 127.0.0.1:8763.')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('PASS: no broken internal references or assets; no live forms/external runtime assets; draft boundaries present.')
