"""Offline regression checks for the LH publication candidate; never submits forms."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = '38e0bd9bc8296b70ac68d92753d63f447d70df3e'

def baseline(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT).decode('utf-8').replace('\r\n', '\n')

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

pages = {p.name: Page(p.read_text(encoding='utf-8')) for p in ROOT.glob('*.html')}
home = (ROOT/'index.html').read_text(encoding='utf-8')
form = lambda s: re.search(r'<form\b.*?</form>', s, re.S).group()
assert form(home) == form(baseline('index.html')), 'Brevo form changed'
for path in ('robots.txt',):
    assert (ROOT/path).read_text(encoding='utf-8') == baseline(path), path
html = (ROOT/'winter-26.html').read_text(encoding='utf-8')
ga = lambda s: next(x for x in re.findall(r'<script>.*?</script>', s, re.S) if 'PF_GA_MEASUREMENT_ID' in x)
assert ga(html) == ga(baseline('winter-26.html')), 'GA initialization changed'
# The hero, header and all content outside the catalog cards / sets are frozen at PR11.
approved = subprocess.check_output(['git','show','6d8e07b:winter-26.html'],cwd=ROOT).decode().replace('\r\n','\n')
def stable_main(text):
    main=re.search(r'<main\b.*?</main>',text,re.S).group()
    main=re.sub(r'<article class="product-card".*?</article>', '<card>',main,flags=re.S)
    return re.sub(r'(?:<figure class="set-scene">.*?</figure>)?<div class="sets-grid">.*?</article></div>', '<sets>',main,flags=re.S)
assert stable_main(html)==stable_main(approved)
assert re.search(r'<header.*?</header>',html,re.S).group()==re.search(r'<header.*?</header>',approved,re.S).group()
registry=json.loads((ROOT/'data/winter26-products.json').read_text(encoding='utf8'))
from xml.etree import ElementTree as ET
def urls(s): return {x.text for x in ET.fromstring(s).findall('.//{*}loc')}
expected={f'https://pracowniaform.com/winter-{p["slug"]}.html' for p in registry['products']}
assert urls((ROOT/'sitemap.xml').read_text()) == urls(baseline('sitemap.xml')) | expected
script = (ROOT/'script.js').read_text(encoding='utf-8')
original_script = baseline('script.js')
assert script.split('// Cookie consent + GA4')[0] == original_script.split('// Cookie consent + GA4')[0]
assert script.split('// Interaktywne badanie')[1] == original_script.split('// Interaktywne badanie')[1]
for forbidden in ('noindex', 'nofollow', 'Content-Security-Policy', 'form-action', 'previews/', 'buy.stripe.com', 'js.stripe.com', 'checkout.stripe.com'):
    assert forbidden not in html, forbidden
assert html.count('class="product-card"') == 4
cards = re.findall(r'<article class="product-card".*?</article>', html, re.S)
assert all(card.count('class="status-pill"') == 1 for card in cards)
for card, product in zip(cards, (p for p in registry['products'] if p['type']=='pojedynczy'), strict=True):
    assert 'class="store-cover"' in card and f'href="winter-{product["slug"]}.html"' in card
    assert ('<picture>' in card) == bool(product['photos']), product['slug']
for product in registry['products']:
    name=f'winter-{product["slug"]}.html'
    detail=(ROOT/name).read_text(encoding='utf8')
    assert ga(detail)==ga(html) and f'href="https://pracowniaform.com/{name}"' in detail
    assert detail.count('<figure data-frame>')==len(product['photos'])
    if not registry['release']['salesApproved']:
        assert 'buy.stripe.com' not in detail and 'href="index.html#preorder"' in detail
assert 'https://pracowniaform.com/winter-26.html' in html
assert not any(t == 'form' for t, a in pages['winter-26.html'].tags)
assert len(pages) == 16
for name,page in pages.items():
    assert not any(a.get('href','').startswith(('https://buy.stripe.com','https://checkout.stripe.com')) for _,a in page.tags), name
    assert any(t == 'title' for t,a in page.tags), name
    canon=[a['href'] for t,a in page.tags if t=='link' and a.get('rel')=='canonical']
    robots = [a['content'] for t,a in page.tags if t=='meta' and a.get('name')=='robots']
    if name in {'zapis-potwierdzony.html','zapis-prawie-gotowy.html'}:
        assert any('noindex' in value for value in robots), name
    else:
        assert canon == ['https://pracowniaform.com/' + ('' if name=='index.html' else name)], (name,canon)
        assert not any('noindex' in value for value in robots), name
refs = 0
for name, page in pages.items():
    assert any('data-cookie-settings' in a for _, a in page.tags), f'No settings entry: {name}'
    assert len([1 for _, a in page.tags if 'data-cookie-banner' in a]) == 1, name
    for control in ('accept', 'reject', 'close'):
        assert any(t == 'button' and 'data-cookie-' + control in a for t, a in page.tags), name
    ids = [a['id'] for _, a in page.tags if 'id' in a]
    assert len(ids) == len(set(ids)), f'Duplicate ID: {name}'
    assert len([1 for t, a in page.tags if t == 'h1']) == 1, name
    for tag, attrs in page.tags:
        if tag == 'img':
            assert 'alt' in attrs, f'Missing alt: {name}'
        if tag == 'button' and attrs.get('class') == 'menu-toggle':
            assert attrs.get('id') == 'menuBtn' and attrs.get('aria-controls') == 'siteNav', name
        references = [attrs[k] for k in ('src', 'href') if k in attrs]
        references += [part.strip().split()[0] for part in attrs.get('srcset', '').split(',') if part.strip()]
        for reference in references:
            url = urlsplit(reference)
            if url.scheme or url.netloc:
                continue
            target = ROOT / (unquote(url.path) or name)
            assert target.is_file(), f'Missing file: {name} → {reference}'
            if url.fragment:
                assert any(a.get('id') == url.fragment for _, a in pages[target.name].tags), f'Missing anchor: {name} → {reference}'
            refs += 1
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', (ROOT/name).read_text(encoding='utf-8'), re.S):
        json.loads(raw)
        if name == 'winter-26.html':
            assert '"Product"' not in raw and '"Offer"' not in raw
for p in ROOT.glob('*.css'):
    for ref in re.findall(r'url\([\s\"\x27]*([^\)\"\x27]+)', p.read_text(encoding='utf-8')):
        if not urlsplit(ref).scheme:
            assert (ROOT/ref).is_file(), f'Missing CSS asset: {p.name} → {ref}'
hero = next(a for t, a in pages['winter-26.html'].tags if t == 'img')
assert all(hero.get(k) for k in ('width', 'height', 'sizes', 'srcset', 'alt'))
assert hero.get('fetchpriority') == 'high' and hero.get('loading') != 'lazy'
for image in [*ROOT.glob('assets/winter-r04-*'), *ROOT.glob('assets/winter-open-concept-*')]:
    assert image.stat().st_size < 150000, image.name
for name in ('polityka-prywatnosci.html', 'zasady-premiery.html'):
    legal = (ROOT/name).read_text(encoding='utf-8')
    assert '[uzupełnij datę]' not in legal and '2026-11-03' in legal
    assert 'Data zatwierdzenia' in legal
print(f'PASS: {len(pages)} pages, {refs} local references; unchanged Brevo form and WINTER layout; cookie settings on every page; draft dates; responsive hero <150 KB per asset.')
