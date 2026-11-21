<?php
declare(strict_types=1);
require_once __DIR__.'/../api/_common.php';require_once __DIR__.'/../api/_order_status.php';require_once __DIR__.'/../api/_checkout_identity.php';
function check(bool $ok,string $label):void{if(!$ok)throw new RuntimeException($label);}
function denied(string $kind,int $status,callable $fn):array{
 try{$fn();throw new RuntimeException('access allowed: '.$kind);}catch(StoreError $e){check($e->kind===$kind&&$e->status===$status,$kind.' / '.$e->kind);return [$e->kind,$e->status,$e->getMessage()];}
}
// Separate process: real PHP session handling, no output before session headers.
if(($argv[1]??'')==='identity'){
 $dir=$argv[2];session_save_path($dir);$_COOKIE=[];
 check(checkout_identity('test')===['tester'=>false,'owner'=>null],'anonymous test');
 check(checkout_identity('live')===['tester'=>false,'owner'=>null],'anonymous live');
 check(count(glob($dir.'/sess_*'))===0,'read creates no session');
 session_name('pf_winter_sandbox');session_id('fixtureowner');session_start();$_SESSION=['tester_until'=>time()+60,'visitor'=>str_repeat('a',36)];session_write_close();
 $_COOKIE['pf_winter_sandbox']='fixtureowner';$file=$dir.'/sess_fixtureowner';$hash=hash_file('sha256',$file);
 check(checkout_identity('test')['owner']===str_repeat('a',36),'session-bound tester');
 check(hash_file('sha256',$file)===$hash,'read does not rewrite session');
 check(checkout_test_owner()===str_repeat('a',36),'dispatch and checkout retain identity');
 session_name('pf_winter_sandbox');session_id('fixtureexpired');session_start();$_SESSION=['tester_until'=>time()-60,'visitor'=>str_repeat('b',36)];session_write_close();$_COOKIE['pf_winter_sandbox']='fixtureexpired';
 check(checkout_identity('test')['tester']===false,'expired tester rejected');
 denied('TEST_ACCESS',403,fn()=>checkout_test_owner());
 $owners=[];foreach(['newtesterone','newtestertwo']as $sid){
  session_name('pf_winter_sandbox');session_id($sid);session_start();$_SESSION=['tester_until'=>time()+60];session_write_close();$_COOKIE['pf_winter_sandbox']=$sid;
  check(checkout_identity('test')['owner']===null,'status does not generate missing owner');
  $owners[]=checkout_test_owner();check(checkout_test_owner()===end($owners),'stable owner on purchase paths');
 }
 check($owners[0]!==$owners[1]&&strlen($owners[0])===36,'tester isolation');
 echo "PASS real session identity\n";exit;
}
$dir=sys_get_temp_dir().'/pf-status-security-'.bin2hex(random_bytes(6));mkdir($dir,0700);
try{
 $request='12345678-1234-4321-8123-123456789abc';$owner=str_repeat('a',36);$other=str_repeat('b',36);
 $cfg=['mode'=>'test','db_file'=>$dir.'/test.sqlite'];$db=database($cfg);
 $db->exec("INSERT INTO store_meta VALUES('mode','test');INSERT INTO stock VALUES('full-soft:dual',16)");
 $db->prepare("INSERT INTO orders(id,req,quote,created,state,owner,sid,pi) VALUES('synthetic',?,'{}',1,'paid',?,'cs_test_SYNTHETIC','pi_SYNTHETIC')")->execute([$request,$owner]);
 $raw=json_encode(['requestId'=>$request]);$identity=['tester'=>true,'owner'=>$owner];
 $snapshot=fn()=>hash_file('sha256',$cfg['db_file']);$before=$snapshot();
 denied('TEST_ACCESS',403,fn()=>order_status_handle($cfg,$raw,['tester'=>false,'owner'=>$owner]));
 denied('TEST_ACCESS',403,fn()=>order_status_handle($cfg,$raw,[]));
 denied('AUTH_REQUIRED',401,fn()=>order_status_handle($cfg,$raw,['tester'=>true]));
 $foreign=denied('NOT_FOUND',404,fn()=>order_status_handle($cfg,$raw,['tester'=>true,'owner'=>$other]));
 $missing=denied('NOT_FOUND',404,fn()=>order_status_handle($cfg,str_replace('789abc','789abd',$raw),$identity));check($foreign===$missing,'no existence oracle');
 foreach(['{"sid":"cs_test_SYNTHETIC"}','{"requestId":"cs_test_SYNTHETIC"}','{"requestId":[]}','null','[]','{bad',json_encode(['requestId'=>$request,'sid'=>'cs_test_SYNTHETIC']),json_encode(['requestId'=>$request.'\n']),json_encode(['requestId'=>"' OR 1=1 --"])] as $bad)denied('BAD_REQUEST',422,fn()=>order_status_handle($cfg,$bad,$identity));
 denied('BAD_BODY',400,fn()=>order_status_handle($cfg,str_repeat('x',257),$identity));
 check($snapshot()===$before,'denied requests do not write');
 foreach(['paid','pending','released','review'] as $state){
  $db->prepare('UPDATE orders SET state=?')->execute([$state]);$before=$snapshot();
  $result=order_status_handle($cfg,$raw,$identity);check($result['state']===$state,'state '.$state);
  check(array_keys($result)===['state','message'],'minimal response');check(!str_contains(json_encode($result),'SYNTHETIC'),'no SID/PI');
  check($snapshot()===$before,'successful read does not write');
 }
 $db->exec('UPDATE orders SET owner=NULL');denied('NOT_FOUND',404,fn()=>order_status_handle($cfg,$raw,$identity));
 $db->prepare('UPDATE orders SET owner=?')->execute([$owner]);
 $live=$cfg;$live['mode']='live';denied('AUTH_REQUIRED',401,fn()=>order_status_handle($live,$raw,[]));
 denied('UNAVAILABLE',503,fn()=>order_status_handle($live,$raw,$identity));
 $db->exec("UPDATE store_meta SET value='live'");check(order_status_handle($live,$raw,['owner'=>$owner])['state']==='review','live owner without tester role');
 denied('NOT_FOUND',404,fn()=>order_status_handle($live,$raw,['owner'=>$other]));
 $db->exec("UPDATE store_meta SET value='test'");
 $db->exec('BEGIN EXCLUSIVE');denied('UNAVAILABLE',503,fn()=>order_status_handle($cfg,$raw,$identity));$db->exec('ROLLBACK');
 $missingCfg=$cfg;$missingCfg['db_file']=$dir.'/missing.sqlite';denied('UNAVAILABLE',503,fn()=>order_status_handle($missingCfg,$raw,$identity));check(!file_exists($missingCfg['db_file']),'no database creation');
 $badCfg=$cfg;$badCfg['db_file']=$dir.'/corrupt.sqlite';file_put_contents($badCfg['db_file'],'not SQLite');denied('UNAVAILABLE',503,fn()=>order_status_handle($badCfg,$raw,$identity));
 $_SERVER['REQUEST_METHOD']='GET';denied('METHOD',405,fn()=>method('POST'));
 $_SERVER['HTTP_ORIGIN']='https://foreign.invalid';denied('ORIGIN',403,fn()=>require_origin(['origin'=>'https://pf26.uber.space']));
 $cmd=escapeshellarg(PHP_BINARY).' '.escapeshellarg(__FILE__).' identity '.escapeshellarg($dir);exec($cmd,$lines,$code);check($code===0,'identity child: '.implode(' ',$lines));
 check($db->query('SELECT count(*) FROM orders')->fetchColumn()===1&&$db->query('SELECT n FROM stock')->fetchColumn()===16,'no second order / stock mutation');
 echo implode("\n",$lines)."\nPASS status security: unauthenticated, expired tester, foreign owner, legacy NULL, SID rejection, malformed IDs, minimal response, unavailable/locked/corrupt DB; no writes or Stripe.\n";
}finally{$db=null;foreach(glob($dir.'/*') as $file)unlink($file);rmdir($dir);}
