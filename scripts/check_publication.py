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
for path in ('robots.txt', 'sitemap.xml'):
    assert (ROOT/path).read_text(encoding='utf-8') == baseline(path), path
html = (ROOT/'winter-26.html').read_text(encoding='utf-8')
ga = lambda s: next(x for x in re.findall(r'<script>.*?</script>', s, re.S) if 'PF_GA_MEASUREMENT_ID' in x)
assert ga(html) == ga(baseline('winter-26.html')), 'GA initialization changed'
# Owner approved a temporary concept image; all content outside its figure stays frozen.
approved = subprocess.check_output(['git', 'show', 'e054e60:winter-26.html'], cwd=ROOT).decode().replace('\r\n', '\n')
for element in ('main', 'header'):
    block = lambda s: re.search(r'<' + element + r'\b.*?</' + element + '>', s, re.S).group()
    without_hero = lambda s: re.sub(r'<figure class="w26-hero-art">.*?</figure>', '', s, flags=re.S)
    assert without_hero(block(html)) == without_hero(block(approved)), f'Approved {element} changed outside hero figure'
assert 'Wizualizacja koncepcyjna AI na podstawie modelu Pracowni Form.' in html
script = (ROOT/'script.js').read_text(encoding='utf-8')
original_script = baseline('script.js')
assert script.split('// Cookie consent + GA4')[0] == original_script.split('// Cookie consent + GA4')[0]
assert script.split('// Interaktywne badanie')[1] == original_script.split('// Interaktywne badanie')[1]
for forbidden in ('noindex', 'nofollow', 'Content-Security-Policy', 'form-action', 'previews/', 'buy.stripe.com', 'js.stripe.com', 'checkout.stripe.com'):
    assert forbidden not in html, forbidden
assert html.count('class="product-card"') == 4
cards = re.findall(r'<article class="product-card".*?</article>', html, re.S)
assert all(card.count('class="status-pill"') == 1 for card in cards)
assert html.count('Miejsce na fotografię produktu') == 4
assert 'https://pracowniaform.com/winter-26.html' in html
assert not any(t == 'form' for t, a in pages['winter-26.html'].tags)
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
