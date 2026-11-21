const assert=require('node:assert/strict');
const {harness}=require('./checkout-retry-ui.cjs');
const key='pf-w26-checkout-attempt-v1';
const tick=()=>new Promise(r=>setImmediate(r));
const radios=(h,selector)=>h.get(selector).querySelectorAll('input');
const selected=(h,selector)=>radios(h,selector).find(x=>x.checked)?.value;
function assertSnapshot(h){
 assert.equal(selected(h,'[data-sizes]'),1);
 assert.equal(selected(h,'[data-models]'),'full-soft');
 assert.equal(selected(h,'[data-colors]'),'marble');
 assert.equal(h.get('[data-point-id]').value,'TEST01M');
 assert.match(h.get('[data-totals]').textContent,/68,49/);
 assert.match(h.get('[data-dispatch-summary]').textContent,/Synthetic dispatch/);
 assert.equal(h.get('[data-basket]').children.length,1);
 for(const s of ['[data-sizes]','[data-models]','[data-colors]'])assert(radios(h,s).every(x=>x.disabled));
 for(const s of ['[data-point-id]','[data-delivery-locker]','[data-open-map]','[data-add-pack]','[data-reset]','[data-accept-terms]'])assert(h.get(s).disabled,s);
}
(async()=>{
 const a=await harness(new Map(),true);const submit=a.click();const original=structuredClone(a.requests[0]);
 a.finish('NETWORK');await submit;assertSnapshot(a);
 // Exercise handlers directly too: custom gallery controls may dispatch synthetic events.
 radios(a,'[data-sizes]').find(x=>x.value===4).onchange();
 radios(a,'[data-models]').find(x=>x.value==='knitted-star').onchange();
 radios(a,'[data-colors]').find(x=>x.value==='white').onchange();
 a.get('[data-add-pack]').onclick();a.get('[data-reset]').onclick();
 for(const b of a.get('[data-basket]').querySelectorAll('button'))b.onclick();
 a.get('[data-point-id]').value='TEST02M';a.get('[data-point-id]').oninput();await a.get('[data-find-point]').onclick();
 a.get('[data-delivery-locker]').onchange();a.get('[data-prev]').onclick();
 assertSnapshot(a);assert.equal(a.quotes.length,1);assert.deepEqual(JSON.parse(a.storage.get(key)).payload,original);
 const retry=a.click();await a.click();assert.equal(a.requests.length,2);assert.deepEqual(a.requests[1],original);a.finish();await retry;
 assert(a.get('[data-checkout]').disabled);a.events.pageshow({persisted:true});assert(!a.get('[data-checkout]').disabled);assert(!a.root.inert);assertSnapshot(a);
 // Refresh/reopen on a different configurator URL must restore the submitted basket.
 const b=await harness(a.storage,true,'?size=8&model=knitted-star&color=white');assertSnapshot(b);assert.equal(b.quotes.length,0);
 const pending=b.click();assert.deepEqual(b.requests[0],original);b.finish('PAYMENT_PENDING');await pending;assertSnapshot(b);
 const c=await harness(b.storage,true,'?size=4');assertSnapshot(c);
 const expired=c.click();c.finish('ATTEMPT_RELEASED');await expired;await tick();
 assert.equal(c.storage.size,0);assert(!c.get('[data-point-id]').disabled);assert(!c.get('[data-open-map]').disabled);
 assert.equal(c.requests.length,1,'no automatic new checkout');
 const newAttempt=c.click();assert.notEqual(c.requests[1].requestId,original.requestId);c.finish('ORDER_PAID');await newAttempt;assertSnapshot(c);
 assert(c.get('[data-checkout]').disabled);await c.click();assert.equal(c.requests.length,2);
 // Legacy persisted attempts lack UI context: keep original contents, do not invent a date.
 const legacy=JSON.parse(c.storage.get(key));delete legacy.ui;delete legacy.blocked;c.storage.set(key,JSON.stringify(legacy));
 const d=await harness(c.storage,true,'?size=8');assert.equal(selected(d,'[data-sizes]'),1);assert.match(d.get('[data-dispatch-summary]').textContent,/zapisanej próbie/);
 const multi=structuredClone(legacy);const item={modelId:'full-soft',colorId:'marble'};
 delete multi.payload.selections;multi.payload.packs=[[item],[item,item]];multi.total=15249;
 const store=new Map([[key,JSON.stringify(multi)]]);const m=await harness(store,true,'?size=8');
 assert.equal(m.get('[data-basket]').children.length,2);assert.equal(selected(m,'[data-sizes]'),2);
 assert.match(m.get('[data-totals]').textContent,/3 szt\./);assert.match(m.get('[data-totals]').textContent,/152,49/);
 for(const b of m.get('[data-basket]').querySelectorAll('button')){assert(b.disabled);b.onclick();}
 assert.deepEqual(JSON.parse(store.get(key)).payload,multi.payload);
 // A stale BFCache page/response must not erase a newer operation in this tab.
 const old=await harness(new Map(),true);const oldRequest=old.click();
 const newer=JSON.parse(old.storage.get(key));newer.id='12345678-1234-4321-8123-999999999999';newer.payload.requestId=newer.id;
 old.storage.set(key,JSON.stringify(newer));old.events.pageshow({persisted:true});
 old.finish('ATTEMPT_RELEASED');await oldRequest;assert.equal(JSON.parse(old.storage.get(key)).id,newer.id);
 const latest=old.click();assert.equal(old.requests[1].requestId,newer.id);old.finish('PAYMENT_PENDING');await latest;
 console.log('PASS basket lock: size/model/color/packs/delivery/point/dispatch, refresh/reopen, BFCache back, pending, released explicit new attempt, paid. No network.');
})().catch(e=>{console.error(e);process.exitCode=1});
