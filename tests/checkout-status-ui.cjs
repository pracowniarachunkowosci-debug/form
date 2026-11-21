const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {harness}=require('./checkout-retry-ui.cjs');
const key='pf-w26-checkout-attempt-v1',tick=()=>new Promise(r=>setImmediate(r));
function stored(){return new Map([[key,JSON.stringify({id:'12345678-1234-4321-8123-123456789abc',total:6849,payload:{requestId:'12345678-1234-4321-8123-123456789abc',selections:[{modelId:'full-soft',colorId:'marble'}],delivery_method:'locker',pickup_point:'TEST01M'},ui:{point:{id:'TEST01M',address:'Synthetic'}}})]])}
(async()=>{
 const race=await harness();const submit=race.click();race.finish({state:'paid',message:'confirmed'});await submit;
 assert.equal(race.redirects.length,0);assert.equal(race.requests.length,1);assert(race.get('[data-checkout]').disabled);assert.match(race.get('[data-payment-status]').textContent,/Zamówienie opłacone/);
 for(const state of ['paid','pending','released','review']){
  const storage=stored(),h=await harness(storage,false,undefined,state,true);await tick();
  assert.equal(h.requests.length,0,'opening configurator never calls checkout');
  if(state==='paid'){assert.match(h.get('[data-payment-status]').textContent,/Zamówienie opłacone/);assert.equal(h.get('[data-checkout]').textContent,'Zamówienie opłacone');assert(h.get('[data-checkout]').disabled);}
  if(state==='review')assert(h.get('[data-checkout]').disabled);
  if(state==='released')assert.equal(storage.size,0,'confirmed release permits a later deliberate new attempt');
  await h.click();assert.equal(h.requests.length,0,'status check while paused cannot create');
  h.events.pageshow({persisted:true});await tick();assert.equal(h.requests.length,0);
  const reload=await harness(storage,false,undefined,state,true);await tick();assert.equal(reload.requests.length,0);
  if(state==='paid')assert.match(reload.get('[data-payment-status]').textContent,/Zamówienie opłacone/);
 }
 const offline=await harness(stored(),false,undefined,'NETWORK');await tick();await offline.click();assert.equal(offline.requests.length,0);assert.equal(offline.storage.size,1);
 // Execute actual return-page controller: direct return, refresh button, BFCache and reload.
 for(const state of ['paid','pending','released','review']){
  const storage=stored();let calls=0;const nodes={h1:{},'[data-order-message]':{},'[data-order-refresh]':{}},events={};
  const context={document:{querySelector:()=>({querySelector:s=>nodes[s]})},window:{addEventListener:(n,f)=>events[n]=f},sessionStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},fetch:async(url,opts)=>{assert.equal(url,'/api/order-status.php');assert.equal(Object.keys(JSON.parse(opts.body)).join(),'requestId');calls++;return {ok:true,json:async()=>({state,message:state==='paid'?'Zamówienie opłacone. Płatność została potwierdzona.':state})}}};
  const js=fs.readFileSync('winter-payment-result.js','utf8');vm.runInNewContext(js,context);await tick();
  if(state==='paid')assert.equal(nodes.h1.textContent,'Zamówienie opłacone');
  await nodes['[data-order-refresh]'].onclick();await events.pageshow();vm.runInNewContext(js,context);await tick();
  assert.equal(calls,4);if(state==='paid')assert.equal(nodes.h1.textContent,'Zamówienie opłacone');
 }
 const template=fs.readFileSync('api/result.php','utf8');for(const token of ['data-order-result','data-order-message','data-order-refresh','/winter-payment-result.js'])assert(template.includes(token));
 console.log('PASS actual return/configurator controllers: paid/pending/released/review, reload, history, paused sales, paid race, no second checkout/Stripe request.');
})().catch(e=>{console.error(e);process.exitCode=1});
