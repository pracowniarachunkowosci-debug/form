// Exercise the real composer without a browser or external network; provider answers come from PHP fixtures.
const assert=require('node:assert/strict'), fs=require('node:fs'), path=require('node:path'), vm=require('node:vm');
const {spawnSync}=require('node:child_process');
const repo=path.resolve(__dirname,'..'),php=process.env.PF_PHP_BIN||path.join(repo,'.artifacts/tools/php/php.exe');
const provider=spawnSync(php,['-d','disable_functions=curl_init,curl_exec','-r',
  'require "api/_common.php"; $c=["mode"=>"test","inpost_points_mock"=>true]; $r=[]; foreach(array_keys(inpost_mock_fixtures()) as $id){try{$r[$id]=["ok"=>true,"body"=>lookup_point($c,$id)];}catch(StoreError $e){$r[$id]=["ok"=>false,"body"=>["message"=>$e->getMessage()]];}} echo json_encode(["settings"=>inpost_settings($c),"points"=>$r],JSON_THROW_ON_ERROR);'],{cwd:repo,encoding:'utf8'});
assert.equal(provider.status,0,provider.stderr);const fixture=JSON.parse(provider.stdout);
const html=fs.readFileSync(path.join(repo,'winter-zestaw-4.html'),'utf8'),js=fs.readFileSync(path.join(repo,'winter-config.js'),'utf8');
const options=html.match(/id="winter-options">([^<]+)<\/script>/)[1],notice=fixture.settings.points_notice;
class Element{
  constructor(tag){this.tag=tag;this.children=[];this.style={};this.hidden=false;this.disabled=false;this.value='';}
  append(...nodes){this.children.push(...nodes)} replaceChildren(...nodes){this.children=nodes}
  setAttribute(k,v){this[k]=v} focus(){} showModal(){this.open=true} close(){this.open=false;this.onclose?.()}
  addEventListener(){} remove(){}
  querySelectorAll(tag){return this.children.flatMap(c=>[...(c.tag===tag?[c]:[]),...c.querySelectorAll(tag)])}
}
async function run({mixed=false,local=false,bad=null}={}){
  const nodes={},created=[],builder=new Element('main'),head=new Element('head'),bodies=[],calls=[];
  const select=k=>nodes[k] ||= new Element('div');builder.querySelector=select;
  const doc={head,querySelector:s=>s==='#winter-options'?{textContent:options}:builder,querySelectorAll:()=>[],
    createElement:tag=>{const e=new Element(tag);created.push(e);return e}};
  const info={...fixture.settings,mode:'test',available:true,currency:'PLN',freeCourierFromOrnaments:6,
    smallOrderCourierGrosz:2049,locker_amount_grosze:1849,stock:{'full-soft:marble':100,'knitted-star:white':100},...(local?{local_mock_demo:true}:{})};
  if(bad==='live')info.mode='live';if(bad==='token')info.geowidget_token='unexpected-token';if(bad==='ids')info.test_points=[{id:'WRO01M',label:'real code'}];
  const location={search:mixed?'?size=2':'?size=1&model=full-soft&color=marble',protocol:'http:',hostname:'127.0.0.1',
    origin:'http://127.0.0.1:8787',href:'http://127.0.0.1:8787/winter-zestaw-4.html',assign(){throw new Error('No redirect permitted in mock UI test')}};
  const fetch=async(url,opts)=>{
    calls.push(url);assert(!/^https?:/.test(url),'all requests must be same-origin');
    if(url==='api/status.php')return {ok:true,headers:{get:()=> 'application/json'},json:async()=>info};
    if(url.startsWith('api/pickup-point.php?id=')){
      const response=fixture.points[decodeURIComponent(url.split('=')[1])]||{ok:false,body:{message:notice+' — nieznany kod testowy.'}};
      return {ok:response.ok,json:async()=>response.body};
    }
    assert.equal(url,'api/checkout.php');const body=JSON.parse(opts.body);bodies.push(body);
    return {ok:local,json:async()=>local?{local_demo:true,orderId:'w26_'+'a'.repeat(24),totalGrosz:body.delivery_method==='locker'?6849:7049}:{message:notice+' — kontrolowana odmowa płatności.'}};
  };
  let request=0;vm.runInNewContext(js,{document:doc,Intl,URL,URLSearchParams,location,setTimeout,clearTimeout,fetch,crypto:{randomUUID:()=> 'request-'+(++request)}});
  await new Promise(resolve=>setImmediate(resolve));
  const btn=select('[data-checkout]'),totals=select('[data-totals]'),picker=created.find(e=>e['data-test-point-picker']==='');
  assert(picker);assert.equal(head.children.length,0);
  if(bad){assert(btn.hidden);assert.equal(calls.length,1);return;}
  const banner=created.find(e=>e['data-points-mock-notice']==='');assert(!banner.hidden);assert.equal(banner.children[0].textContent,notice);
  assert.equal(picker.children.length,fixture.settings.test_points.length+1);
  const manual=async(id)=>{const field=select('[data-point-id]');field.value=id;field.oninput();await select('[data-find-point]').onclick()};
  const choose=async(id)=>{picker.value=id;await picker.onchange()};
  if(mixed){
    const find=(area,value)=>select(area).querySelectorAll('input').find(e=>String(e.value)===String(value));
    const fill=(n,model,color)=>{for(let i=0;i<n;i++){select('[data-slots]').children[i].onclick();find('[data-models]',model).onchange();find('[data-colors]',color).onchange()}};
    fill(2,'full-soft','marble');select('[data-add-pack]').onclick();find('[data-sizes]',4).onchange();fill(4,'knitted-star','white');
  }
  select('[data-delivery-locker]').onchange();assert(btn.disabled);assert(select('[data-open-map]').hidden);
  await select('[data-open-map]').onclick();assert.equal(head.children.length,0,'no Geowidget assets');
  assert(totals.textContent.includes(notice));assert.match(totals.textContent,mixed?/234,00/:/68,49/);
  await choose('TEST01M');assert(!btn.disabled);assert(select('[data-point-summary]').textContent.includes(fixture.points.TEST01M.body.address));
  await btn.onclick();const first=bodies.at(-1);assert.equal(first.pickup_point,'TEST01M');assert(!('pickup_address' in first));assert(!('inpost_points_mock' in first));
  await btn.onclick();assert.equal(bodies.at(-1).requestId,first.requestId,'same request on retry');
  if(mixed){assert.deepEqual(first.packs.map(p=>p.length),[2,4]);return;}
  await choose('TEST02M');assert(select('[data-point-summary]').textContent.includes(fixture.points.TEST02M.body.address));
  await btn.onclick();assert.notEqual(bodies.at(-1).requestId,first.requestId);
  await manual(' test01m ');assert(!btn.disabled);assert.equal(select('[data-point-id]').value,'TEST01M');
  for(const id of ['bad!','TESTUNKNOWN','TESTOFF','TESTBAD','TESTBROKEN','TESTERROR']){
    await manual(id);assert(btn.disabled);assert(select('[data-point-status]').textContent);assert.equal(select('[data-point-summary]').textContent,'');
  }
  select('[data-delivery-courier]').onchange();assert(!btn.disabled);assert.match(totals.textContent,/70,49/);
  await btn.onclick();assert.equal(bodies.at(-1).delivery_method,'courier');assert(!('pickup_point' in bodies.at(-1)));
  if(local)assert.match(select('[data-payment-status]').textContent,/zapisano w26_.*Bez płatności/);
  assert.equal(head.children.length,0,'no external scripts or map');
}
Promise.all([run(),run({mixed:true}),run({local:true}),...['live','token','ids'].map(bad=>run({bad}))])
  .then(()=>console.log('PASS: mock picker select/change/manual/errors, canonical server response, courier switch, 2+4, idempotency, local save and Live rejection. No browser/network.'))
  .catch(e=>{console.error(e);process.exitCode=1});
