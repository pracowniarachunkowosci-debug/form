"""Project only approved physical variants into the static catalog presented to browsers."""
import json
import re
from html import escape

def catalog_data(store, media, pricing):
    models = []
    variant_keys, skus = set(), set()
    colors = {}
    for c in store['configuration']['colors']:
        assert re.fullmatch(r'[a-z0-9-]+', c['id']) and c['id'] not in colors
        assert type(c['approved']) is bool
        if c['approved']: assert c['label'].strip() and (c.get('hex') is None or re.fullmatch(r'#[0-9a-fA-F]{6}', c['hex']))
        colors[c['id']] = c
    def photo(key):
        m = media[key]
        return dict(thumb=f'assets/store/{key}-{m["widths"][0]}.webp',
                    image=f'assets/store/{key}-{m["widths"][-1]}.webp')
    for p in store['products']:
        if p['type'] != 'pojedynczy' or p['id'] not in pricing['eligibleModelIds']: continue
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
            variant=dict(colorId=c['id'], label=c['label'], hex=c.get('hex'), sku=v['sku'],
                         stock=stock, grossGrosz=price, available=v['available'], photo=None)
            if v['photoAsset'] is not None:
                shot=next((s for s in shots if s['asset']==v['photoAsset'] and s['kind']=='fotografia' and s.get('colorId')==c['id']),None)
                assert shot,'Variant requires an actual photograph associated with its model'
                variant['photo']={**photo(shot['asset']), 'alt':shot['alt']}
            model['variants'].append(variant)
        models.append(model)
    sizes = {1:pricing['singleGrossGrosz'], **{int(k):v for k,v in pricing['setGrossGrosz'].items()}}
    assert sorted(sizes) == [1,2,4,6,8] and all(type(v) is int and v > 0 for v in sizes.values())
    threshold = pricing['freeCourierFromOrnaments']
    return dict(models=models, featured=pricing['featuredSetSize'], freeFrom=threshold, smallOrderLockerGrosz=pricing['smallOrderLockerGrosz'],
                sizes=[dict(size=n, grossGrosz=sizes[n], shippingGrosz=0 if n>=threshold else pricing['smallOrderCourierGrosz']) for n in sorted(sizes)])

def controls(p, data):
    variants=next(m['variants'] for m in data['models'] if m['id']==p['id'])
    message='Wybierz wykończenie.' if variants else 'Paletę pokażemy po zatwierdzeniu próbek.'
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
<p>Wybierz wzory i wykończenia. Możesz powtarzać swoje ulubione ozdoby. Od sześciu sztuk dostawa w Polsce jest w cenie.</p></header>
<div data-builder hidden>
<fieldset class="size-picker"><legend>Wielkość zestawu</legend><div data-sizes></div></fieldset>
<div class="compose-layout"><div class="workspace">
<p class="eyebrow">01 &nbsp; / &nbsp; Układ zestawu</p><h2>Twoje bombki</h2>
<p class="help">Wybierz miejsce, które chcesz uzupełnić lub zmienić. <a href="#sklad">Podsumowanie ↓</a></p>
<div data-slots class="slots" role="group" aria-label="Miejsca w zestawie"></div>
<div class="edit-position"><p class="eyebrow" data-edit-title></p>
<fieldset><legend>Wybierz model</legend><div data-models class="model-grid"></div></fieldset>
<p class="help">Kadry przedstawiają formę. Nie pokazują wszystkich wykończeń.</p>
<fieldset><legend>Wybierz kolor</legend><div data-colors></div></fieldset>
<button class="ink-button" data-next type="button">Następna bombka →</button></div></div>
<aside class="composition" id="sklad" aria-label="Podsumowanie zestawu"><p class="eyebrow">02 &nbsp; / &nbsp; Kompozycja</p><h2>Twój zestaw</h2>
<p class="count" data-count aria-live="polite" aria-atomic="true"></p>
<div class="progress-line" aria-hidden="true"><span></span></div><p data-summary-note></p>
<ul data-summary></ul><div class="pack-actions"><button type="button" class="ink-button" data-add-pack>Dodaj kolejną kompozycję</button></div>
<section class="basket" aria-labelledby="basket-title"><h3 id="basket-title">Twój koszyk</h3>
<ul data-basket></ul>
<fieldset class="delivery-picker" data-delivery-picker hidden><legend>Dostawa w Polsce</legend>
<label><input type="radio" data-delivery-courier name="delivery-method" value="courier" checked> <span>Kurier na adres · <strong data-courier-fee></strong></span></label>
<label><input type="radio" data-delivery-locker name="delivery-method" value="locker" disabled> <span>Paczkomat® InPost · <strong data-locker-fee></strong></span></label>
<div data-locker-panel hidden>
<p data-point-summary class="point-receipt" aria-live="polite"></p>
<button type="button" class="ink-button" data-open-map hidden>Wybierz Paczkomat na mapie</button>
<label class="locker-id" for="locker-id">Kod automatu Paczkomat®</label>
<div class="locker-search"><input id="locker-id" data-point-id type="text" maxlength="32" autocapitalize="characters" spellcheck="false" autocomplete="off" aria-describedby="point-help"><button class="reset-set" data-find-point type="button">Sprawdź kod</button></div>
<p id="point-help" class="help">Wpisz oznaczenie z automatu, np. WRO01M. Przed płatnością pokażemy jego adres.</p>
<a class="text-link" data-locker-directory href="https://inpost.pl/znajdz-paczkomat" target="_blank" rel="noopener noreferrer" hidden>Znajdź kod w lokalizatorze InPost ↗</a>
<p data-point-status role="status" aria-live="polite"></p></div></fieldset>
<p data-totals aria-live="polite"></p></section>
<button type="button" class="reset-set" data-reset>Wyczyść wybór</button>
<div class="coupon-entry"><label for="winter-coupon">Kod rabatowy <small>(opcjonalnie)</small></label>
<div><input id="winter-coupon" data-coupon type="text" maxlength="64" autocapitalize="characters" spellcheck="false" aria-describedby="coupon-status"><button type="button" class="reset-set" data-apply-code>Sprawdź kod</button></div>
<p id="coupon-status" data-coupon-status role="status" aria-live="polite"></p></div>
<section data-live-facts hidden aria-label="Przed złożeniem zamówienia"><p><strong>Warunki zakupu</strong></p>
<p data-live-seller></p><p data-live-dispatch></p><p data-live-returns></p><p data-live-complaints></p>
<details><summary>Informacje o wybranych produktach</summary><div data-live-products></div></details>
<p class="live-links"><a data-terms-link>Regulamin sprzedaży</a> · <a data-returns-link>Zwroty i reklamacje</a> · <a data-privacy-link>Polityka prywatności</a></p>
<label class="legal-accept"><input type="checkbox" data-accept-terms> Akceptuję regulamin sprzedaży.</label></section>
<p data-payment-status role="status" aria-live="polite">Zakupy uruchomimy po potwierdzeniu dostępności.</p>
<button type="button" data-checkout class="ink-button" hidden>Przejdź do płatności testowej</button>
<a href="index.html#preorder" data-notify class="text-link">Powiadom mnie o sprzedaży ↗</a>
<small>Samo ułożenie kompozycji nie rezerwuje ozdób. Planowany początek nadań: 23 listopada 2026 r.</small></aside></div>
<dialog class="locker-map" data-map-dialog aria-labelledby="locker-map-title"><header><h2 id="locker-map-title">Wybierz Paczkomat®</h2>
<button type="button" class="ink-button" data-close-map autofocus>Zamknij mapę</button></header>
<p data-map-status role="status"></p><div data-map-host></div></dialog>
<dialog class="atelier-confirm" aria-labelledby="change-question"><h2 id="change-question"></h2>
<form method="dialog"><button class="ink-button" value="cancel" autofocus>Zachowaj wybór</button><button class="reset-set" value="ok" data-confirm-ok></button></form></dialog>
</div><noscript>Do komponowania zestawu włącz JavaScript. Możesz też przejść do listy premierowej.</noscript></section>'''
