"""Customer-facing summary for one SKU; uses the same checkout gate as the order footer."""
from html import escape
from store_gate import checkout_link

def price(value):
    return f'{value:.2f} zł'.replace('.', ',')

def facts(rows):
    return ''.join(f'<div><dt>{escape(label)}</dt><dd>{escape(str(value))}</dd></div>'
                   for label, value in rows if value is not None and str(value).strip())

def purchase_panel(p, store):
    policy = store['release']
    link = checkout_link(p, store)
    parts = []
    if 'variants' not in p and p['grossPLN'] is not None:
        parts.append(f'<p class="detail-price">{price(p["grossPLN"])} brutto</p>')
    if link:
        parts.append(f'<div class="purchase-terms"><p>{escape(policy["delivery"])} · {price(policy["shippingPLN"])}<br>'
                     f'Nadanie: {escape(p["dispatch"])}</p><p>Zwroty: {escape(policy["returnsSummary"])} '
                     f'<a href="{escape(policy["returnsPage"])}">Warunki zwrotu</a></p></div>'
                     f'<a class="editorial-button" href="{escape(link)}">Kup ↗</a>')
    else:
        parts.append('<a class="editorial-button" href="index.html#preorder">Powiadom mnie ↗</a>')
    return '<div class="purchase-panel">' + ''.join(parts) + '</div>'
