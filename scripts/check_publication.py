"""Regression guard: publication changes must not import the isolated PR #4 runtime."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = '38e0bd9bc8296b70ac68d92753d63f447d70df3e'
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags = []; self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

baseline_files = git('ls-tree', '-r', '--name-only', BASE).decode().splitlines()
protected = [p for p in baseline_files if p not in ('winter-26.html', 'winter-26.css')]
# Git compares canonical repository content, accounting for Windows checkout CRLF.
changed = git('diff', '--name-only', BASE, '--', *protected).decode().strip()
assert not changed, f'Unexpected production changes: {changed}'
html = (ROOT/'winter-26.html').read_text(encoding='utf-8')
original = git('show', f'{BASE}:winter-26.html').decode()
ga = lambda s: next(x for x in re.findall(r'<script>.*?</script>', s, re.S) if 'PF_GA_MEASUREMENT_ID' in x)
assert ga(html).replace('\r\n','\n') == ga(original).replace('\r\n','\n')
cookie = lambda s: re.search(r'<div class="cookie-banner".*?(?=\s*<script src="script.js")', s, re.S).group().strip()
assert cookie(html).replace('\r\n','\n') == cookie(original).replace('\r\n','\n')
for forbidden in ('noindex','nofollow','Content-Security-Policy','form-action','review.css','review-banner','PROJEKT DO AKCEPTACJI','winter-after-dark-r04.png'):
    assert forbidden not in html, forbidden
page = Page(html)
ids = [a['id'] for _,a in page.tags if 'id' in a]
assert len(ids) == len(set(ids)), 'Duplicate IDs'
assert len([1 for t,a in page.tags if t=='article' and a.get('class')=='product-card']) == 4
assert any(a.get('name')=='robots' and a['content']=='index, follow' for _,a in page.tags)
assert any(a.get('rel')=='canonical' and a['href']=='https://pracowniaform.com/winter-26.html' for _,a in page.tags)
assert html.count('href="index.html#preorder"') >= 3
assert not any(t=='form' for t,a in page.tags), 'Newsletter stays on existing homepage'
references = []
for tag, attrs in page.tags:
    references += [attrs[k] for k in ('src','href') if k in attrs]
    references += [part.strip().split()[0] for part in attrs.get('srcset','').split(',') if part.strip()]
for reference in references:
    url = urlsplit(reference)
    if url.scheme or url.netloc: continue
    target = ROOT / (unquote(url.path) or 'winter-26.html')
    assert target.is_file(), f'Missing asset/page: {reference}'
    if url.fragment:
        target_page = Page(target.read_text(encoding='utf-8'))
        assert any(a.get('id')==url.fragment for _,a in target_page.tags), f'Missing anchor: {reference}'
for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
    schema=json.loads(raw)
    assert 'Product' not in raw and 'Offer' not in raw
    assert schema['@graph'][0]['@type']=='CollectionPage'
image = next(a for t,a in page.tags if t=='img')
assert image.get('fetchpriority')=='high' and image.get('loading')!='lazy'
assert image.get('width') and image.get('height') and image.get('sizes') and image.get('srcset')
manifest = json.loads((ROOT/'docs/hero-optimization.json').read_text())
for entry in manifest['outputs']:
    assert (ROOT/entry['file']).stat().st_size==entry['bytes']
    assert entry['bytes'] < 150000
print(f'PASS: {len(protected)} baseline files unchanged in Git; GA and cookies retained; {len(references)} local/remote references checked; indexable SEO; 4 previews; image budget.')
