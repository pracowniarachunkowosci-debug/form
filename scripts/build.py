"""Render review pages and shared navigation. Python standard library only; no deploy."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
COMPANY = ('PRACOWNIA RACHUNKOWOŚCI spółka z ograniczoną odpowiedzialnością',
           'ul. Trawowa 19/1, 54-614 Wrocław',
           'NIP 8943197084 · KRS 0000997294 · REGON 523408785',
           'Kapitał zakładowy: 5 000 zł',
           'Sąd Rejonowy dla Wrocławia-Fabrycznej we Wrocławiu, VI Wydział Gospodarczy Krajowego Rejestru Sądowego')
NAV = [('winter-26.html', 'WINTER 26'), ('index.html#kolekcje', 'Koncepty'), ('index.html#pracownia', 'Pracownia'), ('kontakt.html', 'Kontakt')]
DOCS = [('regulamin-sklepu.html', 'Regulamin sklepu'), ('zwroty-i-reklamacje.html', 'Zwroty i reklamacje'), ('formularz-odstapienia.html', 'Formularz odstąpienia'), ('dostawa-i-platnosci.html', 'Dostawa i płatności'), ('polityka-prywatnosci.html', 'Polityka prywatności'), ('zasady-premiery.html', 'Zasady listy premierowej')]

def links(items):
    return '\n'.join(f'<a href="{url}">{label}</a>' for url, label in items)

HEADER = f'''<header class="site-header" id="top">
  <a href="index.html" class="brand" aria-label="Pracownia Form — strona główna"><span class="brand-mark">PF</span><span class="brand-text"><strong>Pracownia Form</strong><small>Obiekty i światło</small></span></a>
  <button class="menu-toggle" id="menuBtn" aria-expanded="false" aria-controls="siteNav" aria-label="Otwórz menu" type="button"><span></span><span></span><span></span></button>
  <nav class="site-nav" id="siteNav" aria-label="Nawigacja główna">{links(NAV)}</nav>
</header>'''
FOOTER = f'''<footer class="footer review-footer">
  <div class="footer-intro"><a href="index.html" class="footer-wordmark">Pracownia Form<span>Forma. Światło. Codzienność.</span></a><p>WINTER 26 · kolekcja w przygotowaniu.</p><p class="review-label">Wersja robocza do akceptacji · sprzedaż nieaktywna</p></div>
  <div class="footer-cols"><div><h2>Pracownia</h2>{links(NAV)}<a href="koncepty.html">Archiwum inspiracji</a></div><div><h2>Informacje / projekty</h2>{links(DOCS)}</div></div>
  <div class="company-details"><p>Marka Pracownia Form · {'<br>'.join(COMPANY)}</p><p>E-mail marki: <a href="mailto:kontakt@pracowniaform.com">kontakt@pracowniaform.com</a> — obsługa skrzynki do potwierdzenia.<br>Adres zwrotów i telefon sklepu: do potwierdzenia.</p></div>
  <p class="copyright">© 2026 Pracownia Form · Dokumenty są projektami do weryfikacji prawnej.</p>
</footer>'''
BANNER = '<div class="review-banner">PROJEKT DO AKCEPTACJI <span>Sprzedaż i płatności nieaktywne</span></div>'
SKIP = '<a class="skip-link" href="#main">Przejdź do treści</a>'
CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'none'; frame-src 'none'; form-action 'none'; base-uri 'self'; object-src 'none'"

def head(title, description, filename, extra=''):
    canonical = 'https://pracowniaform.com/' + ('' if filename == 'index.html' else filename)
    return f'''<!doctype html>
<html lang="pl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{html.escape(title)} — Pracownia Form</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:locale" content="pl_PL"><meta property="og:site_name" content="Pracownia Form">
<meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(description, quote=True)}"><meta property="og:url" content="{canonical}">
<link rel="icon" href="favicon.svg" type="image/svg+xml"><meta name="theme-color" content="#faf8f3">
<link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="review.css">{extra}
</head>'''

def page(filename, title, description, body, css='', bodyclass='document-page'):
    output = head(title, description, filename, css) + f'\n<body class="{bodyclass}">{SKIP}{HEADER}{BANNER}<main id="main">{body}</main>{FOOTER}<script src="script.js"></script></body></html>\n'
    (ROOT / filename).write_text(output, encoding='utf-8')

def legal(filename, title, description):
    content = (ROOT / 'content' / filename).read_text(encoding='utf-8')
    toc = '\n'.join(f'<a href="#{id_}">{html.unescape(label)}</a>' for id_, label in re.findall(r'<section id="([^"]+)">\s*<h2>(.*?)</h2>', content))
    body = f'''<section class="document-hero shell"><p class="eyebrow">Pracownia Form / Informacje</p><h1>{title}</h1><p class="document-lead">{description}</p><p class="document-status">DRAFT · 1 listopada 2026 · do weryfikacji prawnej</p></section>
<div class="document-layout shell"><nav class="document-toc" aria-label="Spis treści"><p class="eyebrow">Na tej stronie</p>{toc}</nav><article class="document-content"><div class="draft-note"><strong>Projekt dokumentu — nie obowiązuje jako regulamin sprzedaży.</strong><p>Sklep nie przyjmuje zamówień ani płatności. Pola oznaczone „do potwierdzenia” wymagają decyzji przed publikacją.</p></div>{content}</article></div>'''
    page(filename, title, description, body)

def product_card(p):
    return f'''<article class="product-card" id="{p['id']}" aria-labelledby="name-{p['id']}">
<div class="product-photo"><span class="photo-index">{p['number']} / {p['family']}</span><div class="photo-placeholder"><span class="placeholder-mark" aria-hidden="true">PF</span><p>Fotografia w przygotowaniu</p><small>{p['name']}</small></div><span class="photo-caption">Miejsce na zatwierdzone zdjęcie produktu</span></div>
<div class="product-heading"><h3 id="name-{p['id']}">{p['name']}</h3><span class="status-pill">W przygotowaniu</span></div><p class="product-description">{p['description']}</p>
<dl class="product-facts"><div><dt>Kolory</dt><dd>Do zatwierdzenia</dd></div><div><dt>Materiał</dt><dd>Do zatwierdzenia</dd></div><div><dt>Cena</dt><dd>Do zatwierdzenia</dd></div><div><dt>Dostępność</dt><dd>Niedostępny</dd></div><div><dt>Przewidywana wysyłka</dt><dd>Termin do zatwierdzenia</dd></div></dl>
<details class="product-details"><summary>Identyfikacja i bezpieczeństwo</summary><p>Model: {p['name']}. SKU wariantu, wymiary i identyfikator partii: do potwierdzenia.</p><p>Producent, adres pocztowy i kontakt elektroniczny: do potwierdzenia dla tego modelu. Dane sprzedawcy znajdują się w <a href="kontakt.html">kontakcie</a>.</p><p>Informacje bezpieczeństwa i instrukcja w języku polskim: w przygotowaniu po ocenie ryzyka i testach. Przed sprzedażą zostaną umieszczone także na produkcie, opakowaniu lub w dołączonej dokumentacji, odpowiednio do wymogów. Kod QR może je jedynie uzupełniać.</p></details></article>'''

def winter():
    data = json.loads((ROOT / 'data/winter-26.json').read_text(encoding='utf-8'))
    assert data['reviewOnly'] and not data['saleEnabled'], 'This renderer only supports review builds'
    families = ''
    for family, subtitle, description in [('KNITTED', 'Rytm splotu.', 'Dwie formy inspirowane fakturą dzianiny. Detal, który zaprasza do spojrzenia z bliska.'), ('SCULPTURAL', 'Ruch w formie.', 'Dwa rzeźbiarskie kierunki. Skręt, pełna bryła i spotkanie powierzchni ze światłem.')]:
        families += f'<section class="family shell" id="{family.lower()}" aria-labelledby="title-{family.lower()}"><div class="family-heading"><div><p class="eyebrow">{family} / WINTER 26</p><h2 id="title-{family.lower()}">{subtitle}</h2></div><p>{description}</p></div><div class="product-grid">' + ''.join(product_card(p) for p in data['products'] if p['family'] == family) + '</div></section>'
    body = '''<section class="w26-hero shell" aria-labelledby="winter-title"><div class="w26-hero-copy"><p class="eyebrow">Kolekcja sezonowa / 2026</p><h1 id="winter-title">WINTER<br><em>26</em><span>Małe formy.<br>Własny rytm.</span></h1><p>Cztery obiekty. Dwa spojrzenia na fakturę i światło. Zimowy rozdział Pracowni Form.</p><a class="editorial-button" href="#knitted">Poznaj kolekcję <span aria-hidden="true">↗</span></a><p class="hero-caption">KNITTED STAR · KNITTED MEDALLION<br>HELIX · FULL SOFT</p></div><figure class="w26-hero-art"><div class="editorial-paper" role="img" aria-label="Neutralna kompozycja typograficzna na jasnym tle papieru, bez przedstawienia produktu"><span class="paper-edition" aria-hidden="true">Pracownia Form / 2026</span><span class="paper-words" aria-hidden="true">Światło.<br>Faktura.<br><em>Forma.</em></span><span class="paper-baseline" aria-hidden="true"><span>KNITTED / SCULPTURAL</span><span>26</span></span></div><figcaption>01 / Studium światła <span>Neutralna kompozycja editorial.<br>Fotografie kolekcji w przygotowaniu.</span></figcaption></figure></section>
<nav class="collection-nav shell" aria-label="Sekcje WINTER 26"><a href="#knitted">01 / KNITTED</a><a href="#sculptural">02 / SCULPTURAL</a><a href="#zestawy">03 / Zestawy</a><a href="#realizacja">04 / Realizacja</a></nav>
<section class="w26-intro shell"><p class="eyebrow">Forma na zimę</p><h2>Sezon się zmienia.<br><em>Uważność zostaje.</em></h2><p>WINTER 26 to kameralna kolekcja dekoracyjnych obiektów. Łączy rytm splotu z rzeźbiarską geometrią. Finalne materiały, fotografie, paleta i ceny są w przygotowaniu.</p></section>''' + families + '''
<section class="sets-section" id="zestawy"><div class="shell"><div class="family-heading"><div><p class="eyebrow">Kompozycje / projekt</p><h2>Razem, w Twoim rytmie.</h2></div><p>Dwie propozycje zestawów. Skład, możliwość łączenia modeli i kolory wymagają zatwierdzenia.</p></div><div class="sets-grid"><article><span class="set-number">02</span><h3>Zestaw 2 sztuk</h3><p>Konfiguracja do zatwierdzenia.<br>Cena do zatwierdzenia.</p><span class="status-pill">W przygotowaniu</span></article><article><span class="set-number">04</span><h3>Zestaw 4 sztuk</h3><p>Konfiguracja do zatwierdzenia.<br>Cena do zatwierdzenia.</p><span class="status-pill">W przygotowaniu</span></article></div></div></section>
<section class="fulfilment shell" id="realizacja"><div><p class="eyebrow">Od formy do wysyłki</p><h2>Mały stan.<br><em>Spokojny proces.</em></h2><p>Planowany model: niewielki zapas gotowych obiektów i ewentualny druk standardowych wariantów na zamówienie. Uruchomienie po zatwierdzeniu.</p></div><div class="fulfilment-list"><article><h3>01 / Na magazynie</h3><p>Gotowy wariant SKU. Ilość i czas przygotowania do wysyłki będą potwierdzone osobno.</p></article><article><h3>02 / Druk na zamówienie</h3><p>Standardowy wariant katalogowy. Czas produkcji i wysyłki do ustalenia. Sam druk po zamówieniu nie wyłącza 14-dniowego prawa odstąpienia.</p></article><article><h3>03 / Niedostępny</h3><p>Aktualny status wszystkich czterech modeli. Bez możliwości zakupu i bez obietnicy daty premiery.</p></article><a class="text-link" href="dostawa-i-platnosci.html">Projekt zasad dostawy i płatności ↗</a></div></section>
<section class="archive-link shell"><p class="eyebrow">Z archiwum pracowni</p><h2>Inne kierunki, ten sam język.</h2><p>SOLIS, VINE WAVE CAST i SOLIS DISH pozostają inspiracjami poza kolekcją WINTER 26.</p><a class="text-link" href="koncepty.html">Przejdź do konceptów ↗</a></section>'''
    page('winter-26.html', 'WINTER 26 — KNITTED & SCULPTURAL', 'KNITTED STAR, KNITTED MEDALLION, HELIX i FULL SOFT. Projekt kolekcji WINTER 26; finalne warianty w przygotowaniu, sprzedaż nieaktywna.', body, '<link rel="stylesheet" href="winter-26.css">', 'winter-page')

def supporting_pages():
    page('kontakt.html', 'Kontakt', 'Dane spółki prowadzącej markę Pracownia Form i status kanałów kontaktu.', f'''<section class="document-hero shell"><p class="eyebrow">Pracownia / Kontakt</p><h1>Porozmawiajmy<br>o formie.</h1><p class="document-lead">Kolekcja, detal, współpraca. Tutaj zaczyna się rozmowa.</p></section><div class="document-layout shell"><div><p class="eyebrow">Dane przedsiębiorcy</p></div><article class="document-content"><section><h2>Pracownia Form</h2><p>{'<br>'.join(COMPANY)}</p><p>Dane rejestrowe sprawdzono 1 listopada 2026 r. w oficjalnym API KRS; oznaczenie sądu z pełnego odpisu. REGON podmiotu: 523408785; API KRS zwraca identyfikator rozszerzony 52340878500000.</p></section><section><h2>Kontakt z marką</h2><p><a href="mailto:kontakt@pracowniaform.com">kontakt@pracowniaform.com</a></p><p>Obsługa skrzynki i telefon sklepu: do potwierdzenia. Zweryfikowano rekordy pocztowe domeny; nie potwierdza to dostarczalności do konkretnej skrzynki.</p><div class="draft-note"><strong>Adres zwrotów i reklamowanych towarów: do potwierdzenia.</strong><p>Nie przyjmujemy założenia, że siedziba spółki jest adresem do odsyłania paczek. Numer telefonu biura rachunkowego nie jest automatycznie numerem sklepu.</p></div><p><a href="zwroty-i-reklamacje.html">Projekt procedury zwrotów i reklamacji</a></p></section></article></div>''')
    cards = ''
    for id_, name, photo, description in [('solis', 'SOLIS', 'winter-26-solis-winter.webp', 'Studium skręconej formy wazonu.'), ('vine', 'VINE WAVE CAST', 'winter-26-vine-product.webp', 'Kierunek rzeźbiarskiego stojaka na wino.'), ('solis-dish', 'SOLIS DISH', 'winter-26-solis-dish.webp', 'Studium niskiej, organicznej formy.')]:
        cards += f'<article id="{id_}"><figure><img src="assets/{photo}" alt="Archiwalna wizualizacja konceptu {name}" width="1200" height="900" loading="lazy"><figcaption>Wizualizacja koncepcyjna. Nie jest fotografią gotowej oferty.</figcaption></figure><h2>{name}</h2><p>{description}</p><p>Koncept archiwalny · bez ceny i dostępności.</p></article>'
    page('koncepty.html', 'Archiwum inspiracji', 'SOLIS, VINE WAVE CAST i SOLIS DISH — archiwalne koncepcje poza kolekcją WINTER 26.', '<section class="document-hero shell"><p class="eyebrow">Archiwum / Poszukiwania</p><h1>Forma w procesie.</h1><p class="document-lead">Dawne kierunki pozostają częścią historii pracowni. Nie należą do czteromodelowej kolekcji WINTER 26 i nie są gotową ofertą.</p><a class="text-link" href="winter-26.html">Zobacz WINTER 26 ↗</a></section><div class="archive-grid shell">' + cards + '</div>')
    for filename, title in [('zapis-prawie-gotowy.html', 'Potwierdzenie zapisu — podgląd'), ('zapis-potwierdzony.html', 'Status zapisu — podgląd')]:
        page(filename, title, 'Lokalna wersja robocza nie tworzy zapisów na listę premierową.', '<section class="document-hero shell"><p class="eyebrow">Lista premierowa / Podgląd</p><h1>Zapisy są wyłączone.</h1><p class="document-lead">Ta strona nie potwierdza utworzenia ani zatwierdzenia nowego zapisu. Wersja robocza nie wysyła danych do systemu mailingowego.</p><a class="text-link" href="zasady-premiery.html">Projekt zasad listy premierowej ↗</a></section>')

def normalize_legacy():
    for filename in ['index.html', 'kolekcja-nord.html', 'kolekcja-stone.html', 'kolekcja-kintsugi.html']:
        path = ROOT / filename
        text = path.read_text(encoding='utf-8')
        # Remove production integrations from review HTML, including stale structured data.
        text = re.sub(r'\s*<script\b[^>]*>.*?</script>', '', text, flags=re.S)
        text = re.sub(r'<link[^>]+href="https://sibforms[^>]+>', '', text)
        text = re.sub(r'<link[^>]+href="(?:favicon.ico|apple-touch-icon.png)"[^>]*>', '', text)
        text = re.sub(r'<div class="cookie-banner".*?(?=</body>)', '', text, flags=re.S)
        text = text.replace('</body>', '<script src="script.js"></script>\n</body>')
        if filename == 'index.html':
            text = re.sub(r'(<meta\s+(?:name="description"|property="og:description"|name="twitter:description")\s+content=")[^"]*', r'\1Pracownia Form — obiekty, faktura i światło. WINTER 26 w przygotowaniu; Nord, Stone i Kintsugi jako przyszłe koncepty.', text)
            text = text.replace('forma, funkcja, trwałość', 'forma, światło, codzienność')
            text = text.replace('Forma.<br />Funkcja.<br />Trwałość.', 'Forma.<br />Światło.<br />Codzienność.')
            text = text.replace('Premiera pierwszych kolekcji w formule limitowanego pre-orderu.', 'WINTER 26 — cztery modele w przygotowaniu. Sprzedaż nieaktywna.')
            text = text.replace('<a href="#kolekcje" class="btn btn-primary">Poznaj kolekcje</a>', '<a href="winter-26.html" class="btn btn-primary">Poznaj WINTER 26</a>')
            text = text.replace('Nie projektujemy sezonowych dekoracji. Tworzymy formy, które mają zostać z Tobą na lata:', 'Projektujemy obiekty do codzienności i kolekcje sezonowe. Łączy je uważność na proporcje:')
            text = text.replace('Trzy kolekcje. Jedna filozofia formy.', 'Przyszłe koncepty. Wspólny język.')
            text = text.replace('Pierwsza premiera Pracowni Form obejmuje trzy kolekcje: Nord, Stone i Kintsugi.', 'Nord, Stone i Kintsugi to przyszłe kierunki projektowe, bez aktywnej oferty i potwierdzonej daty premiery.')
            text = text.replace('Wykończenia pierwszych kolekcji będą dostępne w wybranych wariantach podczas premiery.', 'Paleta inspiracyjna dla przyszłych konceptów. Nie określa zatwierdzonych kolorów WINTER 26.')
            text = re.sub(r'<section class="newsletter preorder".*?</section>', '<section class="newsletter preorder" id="preorder"><div class="shell"><p class="eyebrow">Lista premierowa / projekt</p><h2>Bądź blisko pracowni.</h2><p>Przygotowujemy informacje o kolekcji WINTER 26. W tej wersji zapisy są wyłączone. Lista nie będzie zamówieniem ani rezerwacją.</p><a class="text-link" href="zasady-premiery.html">Przeczytaj projekt zasad listy premierowej ↗</a></div></section>', text, flags=re.S)
            text = re.sub(r'<summary>Czy mogę zamówić produkty w pre-orderze\?</summary>\s*<p>.*?</p>', '<summary>Czy mogę już zamówić WINTER 26?</summary><p>Nie. Kolekcja jest w przygotowaniu. Ceny, warianty i terminy wymagają zatwierdzenia. Nord, Stone i Kintsugi pozostają przyszłymi konceptami.</p>', text, flags=re.S)
            text = re.sub(r'<summary>Czy produkty nadają się do ogrodu i na taras\?</summary>\s*<p>.*?</p>', '<summary>Jakie będzie przeznaczenie produktów?</summary><p>Przeznaczenie, warunki użytkowania i informacje bezpieczeństwa zostaną określone dla każdego modelu po testach. Nie deklarujemy odporności na wilgoć ani zastosowania na zewnątrz bez potwierdzenia.</p>', text, flags=re.S)
            if 'class="home-winter"' not in text:
                text = text.replace('<section class="collections section"', '<section class="home-winter"><div><p class="eyebrow">Kolekcja w przygotowaniu</p><h2>WINTER 26</h2></div><div><p>KNITTED STAR, KNITTED MEDALLION, HELIX i FULL SOFT. Rytm splotu spotyka rzeźbiarską geometrię. Cztery modele, dwa kierunki.</p><a class="editorial-button" href="winter-26.html">Zobacz kolekcję ↗</a></div></section><section class="collections section"', 1)
        else:
            name = filename.removeprefix('kolekcja-').removesuffix('.html').title()
            text = re.sub(r'(<meta\s+(?:name="description"|property="og:description"|name="twitter:description")\s+content=")[^"]*', rf'\1{name} — przyszły koncept Pracowni Form. Wizualizacje inspiracyjne, bez aktywnej oferty i zatwierdzonej daty premiery.', text)
            text = text.replace('Pierwsza premiera', 'Przyszły koncept')
            text = text.replace(f'{name} pojawi się w pierwszej premierze Pracowni Form.', f'{name} pozostaje kierunkiem na przyszłość.')
            text = re.sub(r'Dołącz do listy premierowej, aby otrzymać wcześniejsze informacje\s+o dostępności, wykończeniach i formule pre-orderu\.', 'Termin premiery, warianty i dostępność nie zostały zatwierdzone.', text)
            text = text.replace('Limitowana edycja pierwszej premiery Pracowni Form.', 'Wizualizacja wykończenia — do dalszych prac projektowych.')
            text = re.sub(r'Informacje o dostępności i formule pre-orderu otrzymają w pierwszej\s+kolejności osoby zapisane na listę premierową\.', 'Dostępność oraz termin premiery nie zostały ustalone.', text)
            if 'class="concept-notice"' not in text:
                text = re.sub(r'(<main[^>]*>)', r'\1<div class="concept-notice">Przyszły koncept · wizualizacje inspiracyjne. Brak aktywnej oferty, cen i daty premiery. Materiały, przeznaczenie i parametry wymagają weryfikacji.</div>', text, count=1)
        path.write_text(text, encoding='utf-8', newline='\n')

if __name__ == '__main__':
    normalize_legacy()
    winter()
    supporting_pages()
    for filename, title in DOCS:
        legal(filename, title, {'regulamin-sklepu.html': 'Projekt zasad przyszłych zakupów — od wyboru wariantu do realizacji zamówienia.', 'zwroty-i-reklamacje.html': 'Dwa różne prawa. Jasna ścieżka odstąpienia i zgłoszenia niezgodności towaru z umową.', 'formularz-odstapienia.html': 'Wzór oświadczenia oraz lokalny podgląd przyszłej funkcji elektronicznego odstąpienia.', 'dostawa-i-platnosci.html': 'Plan dostaw i płatności. Terminy, koszty oraz dostawcy wymagają zatwierdzenia.', 'polityka-prywatnosci.html': 'Dane administratora, stan tego podglądu oraz projekt zasad dla przyszłego sklepu.', 'zasady-premiery.html': 'Lista informacyjna, która nie jest zamówieniem ani rezerwacją produktu.'}[filename])
    for path in ROOT.glob('*.html'):
        text = path.read_text(encoding='utf-8')
        text = re.sub(r'<header\b.*?</header>', HEADER, text, count=1, flags=re.S)
        text = re.sub(r'<footer\b.*?</footer>', FOOTER, text, count=1, flags=re.S)
        # Consistent review-only shell on retained legacy pages as well.
        text = re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="noindex, nofollow">', text)
        if 'name="robots"' not in text:
            text = text.replace('</head>', '<meta name="robots" content="noindex, nofollow">\n</head>')
        if 'rel="canonical"' not in text:
            text = text.replace('</head>', f'<link rel="canonical" href="https://pracowniaform.com/{path.name}">\n</head>')
        if 'Content-Security-Policy' not in text:
            text = text.replace('</head>', f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n</head>')
        if 'href="review.css"' not in text:
            text = text.replace('</head>', '<link rel="stylesheet" href="review.css">\n</head>')
        if 'class="skip-link"' not in text:
            text = text.replace('<header', SKIP + '<header', 1)
        if 'class="review-banner"' not in text:
            text = text.replace('</header>', '</header>' + BANNER, 1)
        text = text.replace('<main>', '<main id="main">')
        text = '\n'.join(line.rstrip() for line in text.splitlines()) + '\n'
        text = re.sub(r'\n{3,}', '\n\n', text)
        path.write_text(text, encoding='utf-8', newline='\n')
    print('Rendered WINTER 26, six documents and shared shell. No deployment.')
    # Review pages are intentionally noindex. Publish an empty sitemap until approval;
    # a separate candidate records future canonical URLs without submitting them.
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<!-- REVIEW ONLY: all pages are noindex. Do not deploy this branch. -->\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" />\n', encoding='utf-8')
    candidates = [path.name for path in ROOT.glob('*.html') if not path.name.startswith('zapis-')]
    (ROOT / 'docs/sitemap-after-approval.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join('<url><loc>https://pracowniaform.com/' + ('' if name == 'index.html' else name) + '</loc></url>' for name in sorted(candidates)) + '\n</urlset>\n', encoding='utf-8')
