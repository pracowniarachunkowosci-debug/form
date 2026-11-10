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
        dispatch = p.get('dispatch') or policy.get('dispatchStart')
        dispatch_notice = policy.get('dispatchNotice') or f'Nadawanie zamówień planujemy rozpocząć {dispatch}.'
        delivery_notice = policy.get('deliveryNotice', '')
        parts.append(f'<div class="purchase-terms"><p>{escape(policy["carrierNotice"])} · {price(policy["shippingPLN"])}</p>'
                     f'<p>{escape(dispatch_notice)} {escape(delivery_notice)}</p><p>Zwroty: {escape(policy["returnsSummary"])} '
                     f'<a href="{escape(policy["returnsPage"])}">Warunki zwrotu</a></p></div>'
                     f'<a class="editorial-button" href="{escape(link)}">Zamów w przedsprzedaży ↗</a>')
    else:
        parts.append(f'<a class="editorial-button" href="index.html#preorder">{escape(policy.get("preorderCta", "Powiadom mnie o przedsprzedaży"))} ↗</a>')
    return '<div class="purchase-panel">' + ''.join(parts) + '</div>'
