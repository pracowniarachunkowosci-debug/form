"""No synthetic commerce or photos are written to the catalog."""
from copy import deepcopy
from pathlib import Path
import json
from config_catalog import catalog_data
root=Path(__file__).resolve().parents[1]
store=json.loads((root/'data/winter26-products.json').read_bytes())
media=json.loads((root/'data/store-media.json').read_bytes())
pricing=json.loads((root/'data/winter26-pricing-pl.json').read_bytes())
store['configuration']['colors']=[]
for model in store['products']:
    if model['type']=='pojedynczy': model['variants']=[]
p=store['products'][0]
sid='fixture-only'
store['configuration']['colors'].append(dict(id=sid,label='Fixture',hex='#765432',approved=True))
v=dict(colorId=sid,sku=sid,stock=2,grossGrosz=100,available=True,status='draft',photoAsset=None)
p['variants']=[v]
def published():
    return catalog_data(store,media,pricing)['models'][0]['variants']
assert not published()
v['status']='approved';assert published()[0]['grossGrosz']==100
store['configuration']['colors'][0]['approved']=False;assert not published()
store['configuration']['colors'][0]['approved']=True
v['photoAsset']=p['photos'][0]['asset']
try: published()
except AssertionError: pass
else: raise AssertionError('A concept image was accepted as a color photograph')
p['photos'][0]['kind']='fotografia'
try: published()
except AssertionError: pass
else: raise AssertionError('Photo without a matching color was accepted')
p['photos'][0]['colorId']=sid
assert published()[0]['photo']['image'].endswith('.webp')
store['products'][1]['variants']=[deepcopy(v)]
try: published()
except AssertionError: pass
else: raise AssertionError('Duplicate physical SKU was accepted')
print('PASS: draft suppression, approved variants, physical photo only and unique SKU.')
