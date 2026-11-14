// Loopback HTTP smoke test for an already-running tests/inpost-mock-demo.php. Never accepts a remote URL.
const assert=require('node:assert/strict'),http=require('node:http'),path=require('node:path'),fs=require('node:fs');
const {randomUUID}=require('node:crypto'),{spawnSync}=require('node:child_process');
const repo=path.resolve(__dirname,'..'),db=process.argv[2],demoRoot=path.join(repo,'.artifacts/inpost-mock-demo');
assert(db&&fs.realpathSync(db).startsWith(fs.realpathSync(demoRoot)+path.sep),'Pass the isolated SQLite path printed by the demo launcher');
const request=(route,{method='GET',body,headers={}}={})=>new Promise((resolve,reject)=>{
  const req=http.request({hostname:'127.0.0.1',port:8787,path:route,method,headers:{...(body?{'Content-Type':'application/json',Origin:'http://127.0.0.1:8787'}:{}),...headers}},res=>{
    let raw='';res.setEncoding('utf8');res.on('data',chunk=>raw+=chunk);res.on('end',()=>resolve({status:res.statusCode,headers:res.headers,raw,json:()=>JSON.parse(raw)}));
  });req.on('error',reject);req.setTimeout(5000,()=>req.destroy(new Error('Loopback request timed out')));req.end(body?JSON.stringify(body):undefined);
});
(async()=>{
  const status=await request('/api/status.php'),info=status.json();assert.equal(status.status,200);assert.equal(info.mode,'test');assert.equal(info.points_provider,'mock');assert.equal(info.geowidget_token,null);
  const notice=info.points_notice;assert.match(notice,/TEST \/ MOCK/);const before=info.stock['full-soft:marble'];
  const page=await request('/winter-zestaw-4.html');assert.equal(page.status,200);assert.match(page.headers['content-security-policy'],/connect-src 'self'/);assert.match(page.headers['x-robots-tag'],/noindex/);
  const points={};for(const id of ['TEST01M','TEST02M']){const res=await request('/api/pickup-point.php?id='+encodeURIComponent(' '+id.toLowerCase()+' '));assert.equal(res.status,200);points[id]=res.json();assert.equal(points[id].id,id);assert(points[id].address.includes(notice));}
  for(const [id,code] of [['TESTOFF',422],['TESTBAD',422],['TESTUNKNOWN',422],['WRO01M',422],['TESTBROKEN',503],['TESTERROR',503]])assert.equal((await request('/api/pickup-point.php?id='+id)).status,code);
  assert.equal((await request('/api/pickup-point.php?id[]=TEST01M')).status,422);
  const slot={modelId:'full-soft',colorId:'marble'},base={requestId:randomUUID(),selections:[slot],delivery_method:'locker',pickup_point:'TEST01M'};
  const first=await request('/api/checkout.php',{method:'POST',body:base});assert.equal(first.status,200);const one=first.json();assert.equal(one.totalGrosz,6849);assert.equal(one.local_demo,true);assert(!('url' in one));
  assert.equal((await request('/api/checkout.php',{method:'POST',body:base})).json().orderId,one.orderId);
  assert.equal((await request('/api/checkout.php',{method:'POST',body:{...base,pickup_point:'TEST02M'}})).status,409);
  assert.equal((await request('/api/checkout.php',{method:'POST',body:{...base,requestId:randomUUID(),pickup_address:'Client invented address'}})).status,422);
  const second=(await request('/api/checkout.php',{method:'POST',body:{...base,requestId:randomUUID(),pickup_point:'TEST02M'}})).json();
  const courier=(await request('/api/checkout.php',{method:'POST',body:{requestId:randomUUID(),selections:[slot],delivery_method:'courier'}})).json();assert.equal(courier.totalGrosz,7049);
  const mixed=(await request('/api/checkout.php',{method:'POST',body:{requestId:randomUUID(),packs:[[slot,slot],[slot,slot,slot,slot]],delivery_method:'locker',pickup_point:'TEST02M'}})).json();assert.equal(mixed.totalGrosz,23400);
  assert.equal((await request('/api/status.php')).json().stock['full-soft:marble'],before-9,'single reservation per request');
  for(const route of ['/api/_inpost_mock.php','/api/seed-test.php','/api/webhook.php','/tests/fixtures/inpost-mock-router.php','/.artifacts/inpost-mock-demo/secret.sqlite'])assert.equal((await request(route)).status,404,route);
  assert.equal((await request('/api/status.php',{headers:{Host:'pracowniaform.com'}})).status,404);
  assert.equal((await request('/api/checkout.php',{method:'POST',body:base,headers:{Origin:'https://example.invalid'}})).status,403);
  const php=process.env.PF_PHP_BIN||path.join(repo,'.artifacts/tools/php/php.exe');
  const saved=spawnSync(php,['-r','require "api/_common.php"; $db=database(["db_file"=>$argv[1]]); if((row($db,"SELECT value FROM store_meta WHERE name=?",["demo"])["value"]??null)!=="points-mock-only")exit(2); $rows=[]; foreach(json_decode($argv[2],true) as $id)$rows[]=row($db,"SELECT id,state,quote FROM orders WHERE id=?",[$id]); echo json_encode($rows,JSON_THROW_ON_ERROR);',db,JSON.stringify([one.orderId,second.orderId,courier.orderId,mixed.orderId])],{cwd:repo,encoding:'utf8'});
  assert.equal(saved.status,0,saved.stderr);const rows=JSON.parse(saved.stdout),quotes=rows.map(r=>JSON.parse(r.quote));assert(rows.every(r=>r.state==='reserved'));
  assert.equal(quotes[0].pickup_address,points.TEST01M.address);assert.equal(quotes[1].pickup_address,points.TEST02M.address);
  assert.equal(quotes[2].pickup_point,null);assert(!('pickup_address' in quotes[2]));assert.equal(quotes[3].shipping,0);assert.equal(quotes[3].pickup_address,points.TEST02M.address);
  console.log('PASS: loopback UI/status/points/errors, origin/host guards, hidden internals, canonical SQLite order data, idempotent stock, courier and 2+4. No InPost/Stripe calls.');
})().catch(e=>{console.error(e);process.exitCode=1});
