"""Offline behavioral tests. No request is ever sent to Stripe."""
from copy import deepcopy
import json
from pathlib import Path
from store_gate import checkout_link
reg=json.loads((Path(__file__).resolve().parents[1]/'data/winter26-products.json').read_text(encoding='utf8'))
assert all(checkout_link(p,reg) is None for p in reg['products'])
s=deepcopy(reg);p=s['products'][0]
s['release'].update(salesApproved=True,legalApproved=True,sellerApproved=True,sandboxPassed=True,
    termsPage='terms.html',returnsPage='returns.html',returnsSummary='approved',complaintsSummary='approved',shippingPLN=10)
p.update(sku='fixture',material='fixture',color='fixture',dimensions='fixture',dispatch='fixture',status='ready',
         stock=1,grossPLN=20,photosApproved=True)
for k in p['gpsr']: p['gpsr'][k]='approved'
for im in p['photos']: im['kind']='fotografia'
url='https://buy.stripe.com/OfflineFixture'
p.update(stripePaymentLink=url,verifiedCheckout=dict(url=url,sku='fixture',pricePLN=20,shippingPLN=10,
    quantity=1,adjustableQuantity=False,currency='PLN',country='PL'))
assert checkout_link(p,s)==url
for k,v in [('grossPLN',19),('sku',None),('stock',0),('quantity',2),('photos',[]),('verifiedCheckout',None),
            ('stripePaymentLink',url+'?quantity=2'),('stripePaymentLink','https://buy.stripe.com.example.org/x'),
            ('stripePaymentLink','https://buy.stripe.com/test_123'),('type','zestaw')]:
    q=deepcopy(s); item=q['products'][0];item[k]=v
    assert checkout_link(item,q) is None,k
for field,val in [('salesApproved',False),('legalApproved',False),('sandboxPassed',False),('sellerApproved',False),('shippingPLN',12),('termsPage',None)]:
    q=deepcopy(s);q['release'][field]=val;assert checkout_link(q['products'][0],q) is None,field
q=deepcopy(s);q['products'][1]['stripePaymentLink']=url;assert checkout_link(q['products'][0],q) is None
q=deepcopy(s);q['products'][0]['gpsr']['warnings']=None;assert checkout_link(q['products'][0],q) is None
q=deepcopy(s);q['products'][0]['photos'][0]['kind']='wizualizacja';assert checkout_link(q['products'][0],q) is None
print('PASS: disabled catalog; complete isolated fixture; missing SKU/stock/GPSR/photo/approvals, stale price/shipping, duplicate/unsafe/test URL and unassembled set rejected.')
