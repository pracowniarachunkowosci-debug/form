"""Build-time eligibility only. Stripe, not the browser, charges the configured price."""
import re
from pathlib import Path
def present(value):
    return isinstance(value,str) and value.strip().lower() not in ('','do potwierdzenia','w przygotowaniu')
def money(value):
    return type(value) in (float,int) and value>=0
def checkout_link(p, store):
    # A model-level URL cannot identify a chosen variant or a custom set.
    if 'variants' in p or p.get('id')=='zestaw-4': return None
    release=store['release']
    if not all(release.get(k) is True for k in ('salesApproved','sandboxPassed','legalApproved','sellerApproved')): return None
    if not all(present(release.get(k)) for k in ('termsPage','returnsPage','privacyPage','returnsSummary','complaintsSummary','delivery')): return None
    if not money(release.get('shippingPLN')): return None
    if not all(present(p.get(k)) for k in ('sku','material','color','dimensions','dispatch')): return None
    sku=p['sku']
    if not (p['status']=='ready' and p['photosApproved'] is True and p['photos'] and all(x['kind']=='fotografia' for x in p['photos'])): return None
    if not (type(p['stock']) is int and p['stock']>0 and money(p['grossPLN']) and p['grossPLN']>0 and p['quantity']==1): return None
    if not all(present(p['gpsr'].get(k)) for k in ('producer','address','email','identifier','warnings')): return None
    if p['type']=='zestaw' and not (p.get('setContents') and p['separateSetStock'] is True): return None
    link=p.get('stripePaymentLink')
    if not (isinstance(link,str) and re.fullmatch(r'https://buy\.stripe\.com/[a-zA-Z0-9]+',link) ): return None
    expected=dict(url=link,sku=sku,pricePLN=p['grossPLN'],shippingPLN=release['shippingPLN'],
                  quantity=1,adjustableQuantity=False,currency='PLN',country='PL')
    if p.get('verifiedCheckout')!=expected: return None
    if any(q is not p and (q.get('sku')==sku or q.get('stripePaymentLink')==link) for q in store['products']): return None
    return link
