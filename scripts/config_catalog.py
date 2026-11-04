"""Project only approved physical variants into the static catalog presented to browsers."""
import json
import re
from html import escape

def catalog_data(store, media):
    models = []
    variant_keys, skus = set(), set()
    colors = {}
    for c in store['configuration']['colors']:
        assert re.fullmatch(r'[a-z0-9-]+', c['id']) and c['id'] not in colors
        assert type(c['approved']) is bool
        if c['approved']: assert c['label'].strip() and re.fullmatch(r'#[0-9a-fA-F]{6}', c['hex'])
        colors[c['id']] = c
    def photo(key):
        m = media[key]
        return dict(thumb=f'assets/store/{key}-{m["widths"][0]}.webp',
                    image=f'assets/store/{key}-{m["widths"][-1]}.webp')
    for p in store['products']:
        if p['type'] != 'pojedynczy': continue
        shots = p['photos']
        model = dict(id=p['id'], name=p['name'], family=p['family'], variants=[],
                     thumb=photo(shots[0]['asset'])['thumb'] if shots else None)
        for v in p.get('variants',[]):
            c=colors[v['colorId']]
            pair=(p['id'], c['id'])
            assert pair not in variant_keys
            variant_keys.add(pair)
            if v['sku'] is not None:
                assert isinstance(v['sku'],str) and v['sku'].strip() and v['sku'] not in skus
                skus.add(v['sku'])
            assert v['status'] in ('draft','approved')
            if v['status'] != 'approved' or c['approved'] is not True: continue
            stock, price = v['stock'], v['grossGrosz']
            assert stock is None or type(stock) is int and stock >= 0
            assert price is None or type(price) is int and price > 0
            assert type(v['available']) is bool
            assert not v['available'] or (v['sku'] and stock and price)
            variant=dict(colorId=c['id'], label=c['label'], hex=c['hex'], sku=v['sku'],
                         stock=stock, grossGrosz=price, available=v['available'], photo=None)
            if v['photoAsset'] is not None:
                shot=next((s for s in shots if s['asset']==v['photoAsset'] and s['kind']=='fotografia' and s.get('colorId')==c['id']),None)
                assert shot,'Variant requires an actual photograph associated with its model'
                variant['photo']={**photo(shot['asset']), 'alt':shot['alt']}
            model['variants'].append(variant)
        models.append(model)
    sizes=store['configuration']['sizes']
    assert [s['size'] for s in sizes]==[4,6,8]
    for s in sizes:
        assert type(s['priceApproved']) is bool
        assert not s['priceApproved'] or (type(s['grossGrosz']) is int and s['grossGrosz']>0)
        assert type(s['shippingApproved']) is bool
        if s['shippingApproved']: assert type(s['shippingGrosz']) is int and s['shippingGrosz']>=0
    return dict(models=models,sizes=[dict(size=s['size'],grossGrosz=s['grossGrosz'] if s['priceApproved'] else None,
        shippingGrosz=s['shippingGrosz'] if s['shippingApproved'] is True else None) for s in sizes])

def controls(p, data):
    variants=next(m['variants'] for m in data['models'] if m['id']==p['id'])
    message='Wybierz próbkę, aby obejrzeć wariant.' if variants else 'Paletę pokażemy po zatwierdzeniu próbek.'
    fallback='<noscript>Paleta: '+', '.join(escape(v['label']) for v in variants)+'. Do zmiany zdjęcia włącz JavaScript.</noscript>' if variants else ''
    return (f'<section class="variant-choice" data-color-model="{escape(p["id"])}" aria-label="Kolory modelu">'
            '<h4>Wybierz kolor</h4><div data-swatches></div>'
            f'<p data-variant-status aria-live="polite">{message}</p>{fallback}</section>')

def config_scripts(data):
    safe=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<',r'\u003c')
    return f'<script type="application/json" id="winter-options">{safe}</script><script defer src="winter-config.js"></script>'

BUILDER = '''<section id="kompozycja" class="atelier" aria-labelledby="atelier-title">
<header class="atelier-intro"><p class="eyebrow">WINTER 26 &nbsp; / &nbsp; Kompozycje</p>
<h1 id="atelier-title">Skomponuj swój zestaw</h1>
<p>Wybierz liczbę ozdób, a potem ułóż własny rytm form. Ten sam model może powrócić w kilku miejscach.</p></header>
<div data-builder hidden>
<fieldset class="size-picker"><legend>Wielkość zestawu</legend><div data-sizes></div></fieldset>
<div class="compose-layout"><div class="workspace">
<p class="eyebrow">01 &nbsp; / &nbsp; Układ zestawu</p><h2>Twoje bombki</h2>
<p class="help">Wybierz miejsce, które chcesz uzupełnić lub zmienić. <a href="#sklad">Podsumowanie ↓</a></p>
<div data-slots class="slots" role="group" aria-label="Miejsca w zestawie"></div>
<div class="edit-position"><p class="eyebrow" data-edit-title></p>
<fieldset><legend>Wybierz model</legend><div data-models class="model-grid"></div></fieldset>
<p class="help">Wizualizacje modeli są poglądowe.</p>
<fieldset><legend>Wybierz kolor</legend><div data-colors></div></fieldset>
<button class="ink-button" data-next type="button">Następna bombka →</button></div></div>
<aside class="composition" id="sklad" aria-label="Podsumowanie zestawu"><p class="eyebrow">02 &nbsp; / &nbsp; Kompozycja</p><h2>Twój zestaw</h2>
<p class="count" data-count aria-live="polite" aria-atomic="true"></p>
<div class="progress-line" aria-hidden="true"><span></span></div><p data-summary-note></p>
<ul data-summary></ul><p data-totals></p>
<button type="button" class="reset-set" data-reset>Wyczyść wybór</button>
<a href="index.html#preorder" class="ink-button">Powiadom mnie ↗</a>
<small>Kompozycja jest podglądem. Nie rezerwuje produktów.</small></aside></div>
<dialog class="atelier-confirm" aria-labelledby="change-question"><h2 id="change-question"></h2>
<form method="dialog"><button class="ink-button" value="cancel" autofocus>Zachowaj wybór</button><button class="reset-set" value="ok" data-confirm-ok></button></form></dialog>
</div><noscript>Do komponowania zestawu włącz JavaScript. Możesz też przejść do listy premierowej.</noscript></section>'''
