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
assert checkout_link(p,s) is None  # even a fully approved parent must not sell an unspecified color
p.pop('variants')  # legacy, single fixed SKU exercises PR13 gates independently
assert checkout_link(p,s)==url
# Render the real detail template outside the served tree. This fixture never becomes a live CTA.
from tempfile import TemporaryDirectory
from shutil import copyfile
import subprocess, sys
root=Path(__file__).resolve().parents[1]
with TemporaryDirectory() as tmp:
    dest=Path(tmp)
    for rel in ['scripts/render_store.py','scripts/store_gate.py','scripts/store_panel.py','scripts/config_catalog.py','data/store-media.json','winter-26.html','sitemap.xml']:
        (dest/rel).parent.mkdir(exist_ok=True)
        copyfile(root/rel,dest/rel)
    def render():
        (dest/'data/winter26-products.json').write_text(json.dumps(s),encoding='utf8')
        subprocess.run([sys.executable,'scripts/render_store.py'],cwd=dest,check=True,capture_output=True)
        return (dest/'winter-knitted-star.html').read_text(encoding='utf8')
    html=render()
    panel=html.split('class="purchase-panel"',1)[1].split('<dl class="facts">',1)[0]
    buy=f'href="{url}">Kup'
    assert html.count(buy)==2
    for expected in ('20,00 zł brutto','Kurier na terenie Polski','10,00 zł','Nadanie: fixture','Zwroty: approved','href="returns.html"'):
        assert panel.index(expected)<panel.index(buy),expected
    assert 'sprzedaż nieaktywna' not in html
    p['stock']=0
    blocked=render()
    assert url not in blocked and 'Powiadom mnie' in blocked
    p['stock']=1
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
