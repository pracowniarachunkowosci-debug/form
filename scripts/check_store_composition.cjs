// Offline DOM exercise for the real composer. No Stripe request or order is created.
const assert = require('node:assert/strict');
const fs = require('node:fs'), vm = require('node:vm'), path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root,'winter-zestaw-4.html'),'utf8');
const js = fs.readFileSync(path.join(root,'winter-config.js'),'utf8');
const options = html.match(/id="winter-options">([^<]+)<\/script>/)[1];
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.style={};this.hidden=false;this.disabled=false;this.value='';}
  append(...nodes){this.children.push(...nodes)}
  replaceChildren(...nodes){this.children=nodes}
  setAttribute(k,v){this[k]=v}
  focus(){}
  showModal(){this.open=true}
  close(){this.open=false;this.onclose?.()}
  addEventListener(type,fn){(this.listeners ||= {})[type]=fn}
  remove(){}
  querySelectorAll(tag){return this.children.flatMap(c=>[...(c.tag===tag?[c]:[]),...c.querySelectorAll(tag)])}
}
async function test(mode,pair=null,lockerFlow=false){
  const nodes={}, builder=new Element('main');let body,redirect;
  const select=k=>nodes[k] ||= new Element('div');
  builder.querySelector=select;
  const head=new Element('head');head.append=(...nodes)=>{head.children.push(...nodes);nodes.find(n=>n.tag==='script')?.onload()};
  const doc={head,querySelector:s=>s==='#winter-options'?{textContent:options}:builder,
    querySelectorAll:()=>[],createElement:tag=>new Element(tag)};
  const isLive=['live','bad-live','wrong-amount','insecure','external-terms'].includes(mode), canEnter=isLive||mode==='test';
  const expectedOpen=['test','live','wrong-amount'].includes(mode);
  const modelIds=JSON.parse(options).models.map(m=>m.id);
  const read={mode:isLive?'live':mode,available:canEnter,currency:'PLN',freeCourierFromOrnaments:6,smallOrderCourierGrosz:2049,locker_available:!!lockerFlow,locker_amount_grosze:1849,geowidget_token:lockerFlow==='map'?'public-geo-key':'',
    stock:{'full-soft:marble':pair?pair[0]:2,'knitted-star:white':pair?pair[1]:2},termsUrl:'/terms.html',returnsUrl:mode==='external-terms'?'//example.org/returns':'/returns.html',privacyUrl:'/privacy.html',
    sellerName:'Testowy sprzedawca',sellerContact:'Testowy kontakt',dispatchNotice:'Nadanie testowe',returnsSummary:'Zwroty',complaintsSummary:'Reklamacje',
    approvalVersion:(mode==='bad-live'?'':'f'.repeat(64)),productInfo:Object.fromEntries(modelIds.map(id=>[id,Object.fromEntries(['name','material','dimensions','producer','address','email','warnings'].map(k=>[k,'Test '+k]))]))};
  const fakeFetch=async(url,opts)=>{if(url==='api/status.php')return {ok:true,headers:{get:()=>mode==='static'?'text/html':'application/json'},json:async()=>read};
    if(url.startsWith('api/pickup-point.php?id=')){
      const id=url.split('=')[1],ok=['WRO01M','WRO02M'].includes(id);return {ok,json:async()=>ok?{id,address:'Próbna 1, 50-001 Wrocław'}:{message:'Automat niedostępny.'}};
    }
    assert.equal(url,'api/checkout.php');body=JSON.parse(opts.body);
    if(isLive)return {ok:true,json:async()=>({url:'https://checkout.stripe.com/c/pay/test',totalGrosz:mode==='wrong-amount'?5000:body.delivery_method==='locker'?6849:7049})};
    return {ok:false,json:async()=>({message:'Próba odrzucona przez serwer.'})}};
  const location={search:pair?'?size='+pair[0]:expectedOpen?'?size=1&model=full-soft&color=marble':'',protocol:mode==='insecure'?'http:':'https:',
    origin:'https://example.test',href:'https://example.test/winter-zestaw-4.html',assign(url){redirect=url}};
  vm.runInNewContext(js,{document:doc,Intl,URL,URLSearchParams,location,setTimeout,clearTimeout,fetch:fakeFetch,crypto:{randomUUID:(()=>{let idx=0;return ()=> 'test-order-id-'+(++idx)})()}});
  await new Promise(ok=>setImmediate(ok));
  const btn=select('[data-checkout]'),code=select('[data-coupon]'),totals=select('[data-totals]');
  assert.equal(select('[data-delivery-picker]').hidden,!expectedOpen);
  assert.equal(select('[data-delivery-locker]').disabled,!lockerFlow);
  assert.equal(head.children.length,0);
  const verifyPoint=async(id)=>{
    const field=select('[data-point-id]');field.value=id;field.oninput();await select('[data-find-point]').onclick();
  };
  if(lockerFlow&&!pair){
    const courier=select('[data-delivery-courier]'),locker=select('[data-delivery-locker]');
    locker.onchange();assert(btn.disabled);assert.match(totals.textContent,/68,49/);assert.equal(head.children.length,0);
    const map=select('[data-open-map]');
    assert.equal(map.hidden,lockerFlow!=='map');
    await verifyPoint('FAKE17');assert(btn.disabled);assert.match(select('[data-point-status]').textContent,/niedostępny/);
    await verifyPoint('wro01m');assert(!btn.disabled);assert.match(select('[data-point-summary]').textContent,/WRO01M.*Próbna 1/);
    await btn.onclick();assert.equal(body.delivery_method,'locker');assert.equal(body.pickup_point,'WRO01M');const first=body.requestId;
    assert(!JSON.stringify(body).includes('Próbna'));
    if(lockerFlow==='map'){
      await map.onclick();
      const script=head.children.find(n=>n.tag==='script');assert.match(script.src,/sandbox-easy-geowidget/);
      select('[data-close-map]').onclick();assert.match(select('[data-point-summary]').textContent,/WRO01M/);
      await map.onclick();assert.equal(head.children.length,2);
      const widget=select('[data-map-host]').children[0];assert.equal(widget.token,'public-geo-key');assert.equal(widget.config,'parcelCollect');
      let pick;widget.listeners['inpost.geowidget.init']({detail:{api:{changePointsType:t=>assert.equal(t,'PARCEL_LOCKER'),addPointSelectedCallback:cb=>{pick=cb}}}});
      pick({name:'WRO02M',address:{line1:'Never trust this address'}});await new Promise(ok=>setImmediate(ok));
      assert.match(select('[data-point-summary]').textContent,/WRO02M.*Próbna 1/);
    } else {
      const input=select('[data-point-id]');input.value='WRO02M';input.oninput();assert(btn.disabled);
      await verifyPoint(input.value);
    }
    await btn.onclick();assert.equal(body.pickup_point,'WRO02M');assert.notEqual(body.requestId,first);
    courier.onchange();assert(!btn.disabled);assert.match(totals.textContent,/70,49/);await btn.onclick();assert.equal(body.delivery_method,'courier');assert(!('pickup_point' in body));
    return;
  }
  if(pair){
    const [first,second]=pair;
    const find=(area,val)=>select(area).querySelectorAll('input').find(r=>String(r.value)===String(val));
    const choose=(n,model,color)=>{
      for(let i=0;i<n;i++){select('[data-slots]').children[i].onclick();find('[data-models]',model).onchange();const c=find('[data-colors]',color);assert(!c.disabled);c.onchange()}
    };
    choose(first,'full-soft','marble');
    select('[data-add-pack]').onclick();
    find('[data-sizes]',second).onchange();
    find('[data-models]','full-soft').onchange();assert(find('[data-colors]','marble').disabled);
    choose(second,'knitted-star','white');
    const expected=(first===2&&second===4)?23400:27000;
    assert.equal(select('[data-basket]').children.length,2);assert.match(totals.textContent,new RegExp('Razem: '+(expected/100)+',00'));
    assert.match(totals.textContent,/Kurier InPost w Polsce w cenie/);assert(!btn.disabled);
    if(lockerFlow){
      select('[data-delivery-locker]').onchange();assert(btn.disabled);assert.match(totals.textContent,/Paczkomat® InPost w Polsce w cenie/);
      assert.match(totals.textContent,new RegExp('Razem: '+(expected/100)+',00'));await verifyPoint('WRO01M');assert(!btn.disabled);
    }
    await btn.onclick();
    assert(!('selections' in body));assert.deepEqual(body.packs.map(p=>p.length),pair);
    select('[data-basket]').children[0].querySelectorAll('button')[0].onclick();
    assert.equal(select('[data-basket]').children.length,1);
    assert.match(totals.textContent,lockerFlow?/Paczkomat® InPost: 18,49/:/Kurier InPost: 20,49/);
    assert(!btn.disabled);return;
  }
  if(expectedOpen){
    assert(!btn.hidden);
    if(isLive){
      assert(btn.disabled);
      assert(!select('[data-live-facts]').hidden);
      assert.match(select('[data-live-dispatch]').textContent,/Nadanie/);
      assert.equal(select('[data-terms-link]').href,'/terms.html');
      const consent=select('[data-accept-terms]');consent.checked=true;consent.onchange();
    }
    assert(!btn.disabled);assert.match(totals.textContent,/70,49/);
    code.value='niedostepny';code.oninput();assert(btn.disabled);
    code.value='';code.oninput();await btn.onclick();assert.deepEqual(body,{selections:[{modelId:'full-soft',colorId:'marble'}],delivery_method:'courier',code:'',requestId:'test-order-id-1',...(isLive?{termsAccepted:true,approvalVersion:read.approvalVersion}:{})});
    if(mode==='wrong-amount'){assert(!redirect);assert.match(select('[data-payment-status]').textContent,/Kwota/)}
    else if(isLive){assert.equal(redirect,'https://checkout.stripe.com/c/pay/test')}
    else assert.match(select('[data-payment-status]').textContent,/odrzucona/);
  }else{
    assert(btn.hidden);assert.match(totals.textContent,/220/);assert.match(totals.textContent,/Kurier InPost w Polsce w cenie/);
    const find=(area,id)=>select(area).querySelectorAll('input').find(r=>r.value===id);
    find('[data-models]','full-soft').onchange();find('[data-colors]','marble').onchange();
    assert.equal(select('[data-count]').textContent,'Modele: 1/6 · Kolory: 1/6');
    code.value='WINTER10';code.oninput();select('[data-apply-code]').onclick();
    assert.match(select('[data-coupon-status]').textContent,/Brak aktywnej promocji/);
    assert.match(totals.textContent,/220/);assert(btn.hidden&&!body);
  }
}
Promise.all([...['static','closed','test','live','bad-live','insecure','external-terms','wrong-amount'].map(mode=>test(mode)),test('test',[2,4]),test('test',[6,1]),test('test',null,'manual'),test('test',null,'map'),test('test',[2,4],'manual')]).then(()=>console.log('PASS: regular prices, public selections, disabled code, closed static fallback, test checkout and live gating: HTTPS, disclosures, approved legal links, explicit consent, server amount check and a Stripe redirect; mixed carts 2+4/6+1, stock across packs, removal and shipping recalculation, map selection/cancel, manual ID confirmation, destination rejection and new idempotency keys for changed destinations.')).catch(e=>{console.error(e);process.exitCode=1});
