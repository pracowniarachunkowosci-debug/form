// Run the shipped controller with an isolated DOM/transport. No external requests.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const js=fs.readFileSync('winter-config.js','utf8');
const options=fs.readFileSync('winter-zestaw-4.html','utf8').match(/id="winter-options">([^<]+)<\/script>/)[1];
class Element{
 constructor(tag){Object.assign(this,{tag,children:[],style:{},hidden:false,disabled:false,checked:false,value:''})}
 append(...n){this.children.push(...n)} replaceChildren(...n){this.children=n} setAttribute(k,v){this[k]=v}
 focus(){} scrollIntoView(){} showModal(){} close(){} addEventListener(){} remove(){}
 querySelectorAll(tag){return this.children.flatMap(c=>[...(c.tag===tag?[c]:[]),...c.querySelectorAll(tag)])}
}
let uuid=0;
async function harness(storage=new Map()){
 const nodes={},root=new Element('main'),get=s=>nodes[s]||=new Element('div');root.querySelector=get;
 const requests=[],redirects=[];let finish;
 const info={mode:'test',available:true,currency:'PLN',freeCourierFromOrnaments:6,locker_available:true,locker_amount_grosze:1849,
   points_provider:'inpost',inpost_environment:'production',points_notice:'',geowidget_token:null,stock:{'full-soft:marble':20}};
 const fetch=async(url,opts)=>{
   if(url==='/api/status.php')return {ok:true,headers:{get:()=> 'application/json'},json:async()=>info};
   if(url.startsWith('/api/pickup-point.php'))return {ok:true,json:async()=>({id:'TEST01M',address:'Synthetic test point'})};
   assert.equal(url,'/api/checkout.php');requests.push(JSON.parse(opts.body));
   return new Promise(resolve=>finish=(error=null)=>resolve({ok:!error,json:async()=>error?{error,message:error}:{url:'https://checkout.stripe.com/c/pay/test',totalGrosz:6849,orderId:'w26_fixture'}}));
 };
 vm.runInNewContext(js,{document:{querySelector:s=>s==='#winter-options'?{textContent:options}:root,querySelectorAll:()=>[],createElement:t=>new Element(t),head:new Element('head')},
 Intl,URL,URLSearchParams,setTimeout,clearTimeout,queueMicrotask,fetch,crypto:{randomUUID:()=>`12345678-1234-4321-8123-${String(++uuid).padStart(12,'0')}`},
 sessionStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},
 location:{search:'?size=1&model=full-soft&color=marble',hostname:'example.test',protocol:'https:',origin:'https://example.test',href:'https://example.test/',assign:u=>redirects.push(u)}});
 await new Promise(r=>setImmediate(r));
 get('[data-point-id]').value='TEST01M';get('[data-point-id]').oninput();await get('[data-find-point]').onclick();
 return {get,requests,redirects,storage,finish:e=>finish(e),click:()=>get('[data-checkout]').onclick()};
}
(async()=>{
 const a=await harness();const first=a.click();await a.click();assert.equal(a.requests.length,1,'double click');assert(a.get('[data-checkout]').disabled);
 a.finish('RECONCILE');await first;assert(!a.get('[data-checkout]').disabled);
 const retry=a.click();assert.deepEqual(a.requests[1],a.requests[0]);a.finish();await retry;assert.equal(a.redirects.length,1);
 const b=await harness(a.storage);const returned=b.click();assert.deepEqual(b.requests[0],a.requests[0],'return navigation keeps exact operation');b.finish('ATTEMPT_RELEASED');await returned;
 assert.equal(b.storage.size,0);const fresh=b.click();assert.notEqual(b.requests[1].requestId,b.requests[0].requestId);b.finish('PAYMENT_PENDING');await fresh;
 const pending=b.click();assert.deepEqual(b.requests[2],b.requests[1]);b.finish('ORDER_PAID');await pending;assert(b.get('[data-checkout]').disabled);await b.click();assert.equal(b.requests.length,3);
 console.log('PASS UI: first redirect, double click, unknown retry, return persistence, released/new ID, pending, paid lock. No network.');
})().catch(e=>{console.error(e);process.exitCode=1});
