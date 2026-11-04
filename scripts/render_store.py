"""Render the LH static catalog and detail pages. No network or customer input."""
import json,re,sys
from html import escape
from pathlib import Path
from store_gate import checkout_link
from store_panel import purchase_panel, facts, price
ROOT=Path(__file__).resolve().parents[1]
def read(p): return p.read_bytes().decode('utf8').replace('\r\n', '\n')
def write(p,s):
    if '--check' in sys.argv:
        assert p.exists() and read(p)==s, f'Stale generated page: {p.name}'
    else: p.write_bytes(s.encode('utf8'))
def e(s): return escape(str(s),quote=True)
store=json.loads(read(ROOT/'data/winter26-products.json')); products=store['products']; policy=store['release']
media=json.loads(read(ROOT/'data/store-media.json'))
URL='https://pracowniaform.com/'
def page(p): return 'winter-'+p['slug']+'.html'
def image(shot,sizes,loading='lazy'):
    m=media[shot['asset']]
    def src(ext,w): return f'assets/store/{shot["asset"]}-{w}.{ext}'
    def srcset(ext): return ', '.join(f'{src(ext,w)} {w}w' for w in m['widths'])
    return (f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<img src="{src("webp",m["widths"][-1])}" srcset="{srcset("webp")}" sizes="{sizes}" '
            f'width="{m["width"]}" height="{m["height"]}" loading="{loading}" decoding="async" alt="{e(shot["alt"])}"></picture>')
def state(p): return 'Dostępny' if checkout_link(p,store) else 'W przygotowaniu'
def card(p,n):
    shot=next(iter(p['photos']),None); slug=e(p['slug']); dest=page(p)
    visual=image(shot,'(max-width: 720px) 90vw, 46vw') if shot else '<span class="set-monogram">Fotografia w przygotowaniu</span>'
    caption=('Wizualizacja poglądowa' if shot['kind']=='wizualizacja' else 'Fotografia produktu') if shot else 'Fotografia w przygotowaniu'
    return f'''<article class="product-card" id="{slug}" aria-labelledby="name-{slug}">
<a class="store-cover" href="{dest}" aria-label="Zobacz {e(p['name'])}">{visual}<span class="cover-number">0{n} / {p['family']}</span></a>
<div class="product-heading"><h3 id="name-{slug}"><a href="{dest}">{e(p['name'])}</a></h3><span class="status-pill">{state(p)}</span></div>
<p class="product-description">{e(p['description'])}</p>
<div class="premiere-action"><p class="purchase-note">{caption} · druk 3D</p><a class="editorial-button" href="{dest}">Poznaj obiekt <span aria-hidden="true">↗</span></a></div>
</article>'''
def sets():
    cards=[]
    for p in products[4:]:
        cards.append(f'<article><span class="set-number">0{p["slug"][-1]}</span><h3>{e(p["name"])}</h3><p>{e(p["description"])}</p><a class="set-link" href="{page(p)}">Zobacz zapowiedź ↗</a></article>')
    shot=next(iter(products[-1]['photos']),None)
    scene=('<figure class="set-scene">'+image(shot,'90vw')+'<figcaption>Studium kolekcji · '+('wizualizacja poglądowa' if shot['kind']=='wizualizacja' else 'fotografia')+'</figcaption></figure>') if shot else ''
    return scene+'<div class="sets-grid">' + ''.join(cards)+'</div>'
catalog_path=ROOT/'winter-26.html'
catalog=read(catalog_path)
for n,p in enumerate(products[:4],1):
    catalog,c=re.subn(r'<article class="product-card" id="'+p['slug']+r'".*?</article>',lambda _:card(p,n),catalog,count=1,flags=re.S);assert c==1
catalog,c=re.subn(r'(?:<figure class="set-scene">.*?</figure>)?<div class="sets-grid">.*?</article></div>(?=</div></section>)',lambda _:sets(),catalog,count=1,flags=re.S);assert c==1
if 'href="store.css"' not in catalog: catalog=catalog.replace('href="winter-26.css">','href="winter-26.css"><link rel="stylesheet" href="store.css">',1)
write(catalog_path,catalog)
def gallery(p):
    if not p['photos']: return '<div class="set-monogram"><span>PF</span><p>Fotografia w przygotowaniu</p></div>'
    figures=[];buttons=[]
    for i,shot in enumerate(p['photos']):
        m=media[shot['asset']]; full=f'assets/store/{shot["asset"]}-{m["widths"][-1]}.webp'
        label=e(shot['label']);kind='Wizualizacja poglądowa' if shot['kind']=='wizualizacja' else 'Fotografia produktu'
        figures.append(f'<figure data-frame><a href="{full}" data-zoom aria-label="Powiększ: {label}">'+image(shot,'(max-width: 760px) 90vw, 48vw','eager' if not i else 'lazy')+f'<span class="magnify" aria-hidden="true">＋</span></a><figcaption>{i+1:02} / {len(p["photos"]):02} · {label}<small>{kind}</small></figcaption></figure>')
        buttons.append(f'<button type="button" data-slide="{i}" aria-label="Pokaż ujęcie {i+1}: {label}">{image(dict(shot,alt=""),"64px")}<span>{i+1:02}</span></button>')
    return '<section class="store-gallery" aria-label="Galeria produktu">'+''.join(figures)+'<div class="thumbs" hidden aria-label="Wybór ujęcia">'+''.join(buttons)+'</div><p class="sr-only" aria-live="polite" data-gallery-status></p></section>'
def detail(p,n):
    title=e(p['name']);slug=e(p['slug']); dest=page(p); photos=p['photos']
    head,tail=catalog.split('<main id="main">',1)
    tail=tail.split('</main>',1)[1]
    head=re.sub(r'<script type="application/ld\+json">.*?</script>','',head,flags=re.S)
    head=re.sub(r'<title>.*?</title>',f'<title>{title} — WINTER 26 | Pracownia Form</title>',head)
    head=head.replace('WINTER 26 — KNITTED &amp; SCULPTURAL — Pracownia Form',title+' — WINTER 26 | Pracownia Form')
    head=re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*',lambda m:m[1]+e(p['description']),head)
    head=head.replace(URL+'winter-26.html',URL+dest)
    head=head.replace('winter-page winter-hybrid','winter-page winter-hybrid store-detail')
    for anchor in ('kierunek','obiekty','proces'):
        head=head.replace(f'href="#{anchor}"',f'href="winter-26.html#{anchor}"')
        tail=tail.replace(f'href="#{anchor}"',f'href="winter-26.html#{anchor}"')
    if photos:
        shot=photos[0];m=media[shot['asset']];w=m['widths'][-1]
        head=head.replace('assets/winter-r04-social.jpg',f'assets/store/{shot["asset"]}-{w}.webp').replace('Zimowy editorial bez produktów: igliwie, wstążka i ciepłe światło',e(shot['alt']))
        for attr,v in [('width',w),('height',round(m['height']*w/m['width']))]:
            head=re.sub(rf'(og:image:{attr}" content=")\d+',lambda a:a[1]+str(v),head)
    link=checkout_link(p,store); target=p['slug'] if p['type']=='pojedynczy' else 'zestawy'
    if link:
        head=head.replace('Kolekcja w przygotowaniu · sprzedaż nieaktywna','Kolekcja WINTER 26')
    specs=facts([('Technika','Druk 3D'),('Materiał',p['material']),('Kolor',p['color']),('Wymiary',p['dimensions']),
                 ('SKU',p['sku']),('Stan fizyczny',p['stock']),('Ilość','1 zestaw' if p['type']=='zestaw' else '1 sztuka')])
    safety_rows=facts([(label,p['gpsr'][key]) for label,key in [('Producent','producer'),('Adres','address'),('E-mail','email'),
                       ('Identyfikator','identifier'),('Instrukcja i ostrzeżenia','warnings')]])
    safety=('<dl>'+safety_rows+'</dl>') if safety_rows else '<p>Informacje o produkcie udostępnimy przed sprzedażą.</p>'
    shipping=''.join(f'<p>{label}: {value}</p>' for label,value in [
        ('Koszt', price(policy['shippingPLN']) if policy['shippingPLN'] is not None else None),
        ('Termin nadania', e(p['dispatch']) if p['dispatch'] else None)] if value is not None)
    note='Forma ma znaczenie.' if p['type']!='zestaw' else ('Skład: '+e(p['setContents']) if p['setContents'] else '')
    commercial=''.join(f'<a class="text-link" href="{e(policy[k])}">{label}</a> ' for k,label in [('termsPage','Regulamin sprzedaży'),('returnsPage','Zwroty i reklamacje')] if policy[k])
    main=f'''<main id="main" class="shell store-page"><nav class="crumb" aria-label="Ścieżka"><a href="winter-26.html#{target}">WINTER 26</a><span>/</span>{title}</nav>
<div class="store-layout">{gallery(p)}<section class="store-story"><p class="eyebrow">0{n} / {e(p['family'])} · WINTER 26</p><h1>{title}</h1><p class="store-lead">{e(p['description'])}</p><span class="status-pill">{state(p)}</span>
{purchase_panel(p,store)}<dl class="facts">{specs}</dl>
{f'<p class="edition-note">{note}</p>' if note else ''}</section></div>
<section class="store-info"><div><p class="eyebrow">01 / Realizacja</p><h2>Dostawa</h2><p>{e(policy['delivery'])}. Ręczna realizacja.</p>{shipping}</div>
<div><p class="eyebrow">02 / Po zakupie</p><h2>Zwroty i reklamacje</h2><p>{e(policy['returnsSummary'] or 'Zasady i adres zwrotów wymagają zatwierdzenia przed sprzedażą.')}</p>{('<p>'+e(policy['complaintsSummary'])+'</p>') if policy['complaintsSummary'] else ''}{commercial}<a class="text-link" href="kontakt.html">Kontakt z pracownią</a></div>
<div><p class="eyebrow">03 / Identyfikacja</p><h2>Bezpieczeństwo</h2>{safety}</div>
<div><p class="eyebrow">04 / Pracownia</p><h2>Sprzedawca</h2><p>PRACOWNIA RACHUNKOWOŚCI sp. z o.o.<br>ul. Trawowa 19/1, 54-614 Wrocław<br>NIP 8943197084 · KRS 0000997294</p><a class="text-link" href="mailto:kontakt@pracowniaform.com">kontakt@pracowniaform.com</a></div></section>
<div class="store-order"><p>{'1 sztuka · płatność na stronie Stripe' if link else 'Sprzedaż nieaktywna. Zapis na listę nie jest zamówieniem.'}</p><a class="editorial-button" href="{e(link or 'index.html#preorder')}">{'Kup' if link else 'Powiadom mnie'} ↗</a><a class="text-link" href="winter-26.html#{target}">Wróć do kolekcji</a></div></main>'''
    dialog='<dialog class="zoom-dialog" aria-label="Powiększenie obrazu"><form method="dialog"><button autofocus>Zamknij ×</button></form><img alt=""><p></p></dialog>'
    return head+main+tail.replace('<script src="script.js">',dialog+'<script src="store-gallery.js" defer></script><script src="script.js">')
for n,p in enumerate(products,1): write(ROOT/page(p),detail(p,n))
sitemap=ROOT/'sitemap.xml'
xml=read(sitemap)
for p in products:
    loc=URL+page(p)
    if loc not in xml: xml=xml.replace('</urlset>',f'  <url><loc>{loc}</loc></url>\n</urlset>')
write(sitemap,xml)
print('Rendered catalog +',len(products),'static detail pages')
