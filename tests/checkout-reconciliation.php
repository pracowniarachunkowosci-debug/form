<?php
declare(strict_types=1);
require_once __DIR__.'/../api/_common.php';
function need(bool $ok,string $why):void{if(!$ok)throw new RuntimeException($why);}
function config_fixture():array{return ['mode'=>'test','origin'=>'https://pf26.uber.space','stripe_key'=>'sk_test_ISOLATEDFIXTURE'];}
function setup_fixture(?string $path=null):array{
    $db=database(['db_file'=>$path??':memory:']);reservation_migrate($db);
    $db->exec("INSERT INTO stock VALUES('full-soft:marble',2); INSERT INTO store_meta VALUES('mode','test')");
    $in=['requestId'=>'12345678-1234-4321-8123-123456789abc','selections'=>[['modelId'=>'full-soft','colorId'=>'marble']]];
    $o=order($db,$in['requestId'],quote($in,policy()),null,null,config_fixture());
    return [$db,$o,(int)$o['created']];
}
function state(PDO $db,array $o):string{return row($db,'SELECT state FROM orders WHERE id=?',[$o['id']])['state'];}
function units(PDO $db):int{return (int)$db->query('SELECT n FROM stock')->fetchColumn();}
function session_fixture(array $o,string $status='open',string $payment='unpaid'):array{
    return ['id'=>'cs_test_fixture','object'=>'checkout.session','livemode'=>false,'mode'=>'payment',
        'client_reference_id'=>$o['id'],'metadata'=>checkout_params($o,'https://pf26.uber.space')['metadata'],
        'amount_total'=>json_decode($o['quote'],true)['total'],'currency'=>'pln','status'=>$status,'payment_status'=>$payment,
        'expires_at'=>(int)$o['created']+3600,'url'=>$status==='open'?'https://checkout.stripe.com/c/pay/fixture':null,'payment_intent'=>'pi_fixture'];
}
function response_fixture(int $status,?array $body=null,bool $notSent=false):array{return ['status'=>$status,'body'=>$body,'not_sent'=>$notSent,'headers'=>['request-id'=>'req_fixture'],'code'=>$notSent?'LOCAL_SETUP':'HTTP'];}
function timeout_fixture():array{return response_fixture(0);}
function list_fixture(array $items=[],bool $more=false):array{return response_fixture(200,['object'=>'list','data'=>$items,'has_more'=>$more]);}
function event_fixture(array $o,string $id,string $kind='checkout.session.completed',string $payment='paid'):array{
    return ['id'=>'evt_'.$id,'type'=>$kind,'livemode'=>false,'data'=>['object'=>session_fixture($o,$kind==='checkout.session.expired'?'expired':'complete',$payment)]];
}
function rejection_fixture():array{return response_fixture(400,['error'=>['type'=>'invalid_request_error','code'=>'parameter_missing']]);}
function history_codes(PDO $db):array{return $db->query('SELECT code FROM reservation_history ORDER BY seq')->fetchAll(PDO::FETCH_COLUMN);}
function done(string $name):void{echo 'PASS '.$name,"\n";}

// Real two-process lease test; transport is a file barrier, never HTTP.
if(($argv[1]??'')==='worker'){
    $path=$argv[2];$gate=$argv[3];$db=database(['db_file'=>$path]);$o=$db->query('SELECT * FROM orders')->fetch();
    $transport=function($cfg,$method,$path,$body,$key,$version)use($gate,$o){
        file_put_contents($gate.'.calls','POST'."\n",FILE_APPEND|LOCK_EX);file_put_contents($gate.'.started','1');
        $deadline=microtime(true)+10;while(!is_file($gate.'.release')&&microtime(true)<$deadline)usleep(10000);
        if(!is_file($gate.'.release'))throw new RuntimeException('fixture barrier timeout');
        return response_fixture(200,session_fixture($o));
    };
    echo json_encode(reservation_reconcile($db,config_fixture(),$o['id'],$transport));exit;
}

[$db,$o,$t]=setup_fixture();
reservation_reconcile($db,config_fixture(),$o['id'],fn()=>response_fixture(0,null,true),$t);
need(state($db,$o)==='released'&&units($db)===2,'local setup releases exactly once');
need(in_array('LOCAL_NOT_SENT_RELEASE',history_codes($db),true),'local cause persisted');done('01 local failure before dispatch + history');

[$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>rejection_fixture(),$t);
need(state($db,$o)==='released'&&units($db)===2,'definitive rejection release');
need(in_array('STRIPE_REJECTED_RELEASE',history_codes($db),true),'rejection cause persisted');done('02 definitive Stripe validation refusal');

$r=reservation_curl_result(28,0,0,0.0,null,[]);need($r['not_sent'],'pre-connect timeout known not sent');
need(!reservation_curl_result(28,0,200,0.01,null,[])['not_sent'],'sent timeout not safe');
need(!reservation_curl_result(28,0,0,0.01,null,[])['not_sent'],'completed pretransfer is ambiguous');
[$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>$r,$t);
need(state($db,$o)==='released'&&units($db)===2,'pre-send timeout releases');done('03 timeout proven before sending');

[$db,$o,$t]=setup_fixture();$requests=[];$created=0;$saved=null;
$transport=function($cfg,$method,$path,$body,$key,$version)use(&$requests,&$created,&$saved,$o){
    need($method==='POST','retry should replay');$requests[]=[$key,$body,$version];
    if($saved===null){$created++;$saved=session_fixture($o);return timeout_fixture();}
    return response_fixture(200,$saved);
};
reservation_reconcile($db,config_fixture(),$o['id'],$transport,$t);
need(state($db,$o)==='reconcile'&&units($db)===1,'unknown outcome held');
$cfg=config_fixture();$cfg['origin']='https://changed.invalid';
reservation_reconcile($db,$cfg,$o['id'],$transport,$t+31);
need($created===1&&count($requests)===2&&$requests[0]===$requests[1],'same key/body/version after config change');
need(row($db,'SELECT sid FROM orders',[])['sid']==='cs_test_fixture'&&units($db)===1,'sid recovered');
done('04 timeout after Stripe creation; 06 identical durable idempotency request');

// A repeated browser request never reserves stock twice, even while its result is unknown.
[$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>timeout_fixture(),$t);
$input=['requestId'=>$o['req'],'selections'=>[['modelId'=>'full-soft','colorId'=>'marble']]];
$again=order($db,$o['req'],quote($input,policy()),null,null,config_fixture());
need($again['id']===$o['id']&&units($db)===1&&$db->query('SELECT COUNT(*) FROM orders')->fetchColumn()===1,'client retry reuses reservation');
try{stripe_session(config_fixture(),$again,$db,fn()=>throw new RuntimeException('backoff must prevent dispatch'),$t+1);throw new RuntimeException('expected reconcile');}
catch(StoreError $e){need($e->kind==='RECONCILE','friendly pending outcome');}done('client retry while unknown: same order, no second deduction');

[$db,$o,$t]=setup_fixture();$five=fn($cfg,$method)=>$method==='POST'?response_fixture(500,['error'=>['type'=>'api_error']]):list_fixture();
reservation_reconcile($db,config_fixture(),$o['id'],$five,$t);
reservation_reconcile($db,config_fixture(),$o['id'],$five,$t+3601);
need(state($db,$o)==='reconcile'&&units($db)===1,'500 and absence never release');
need(row($db,'SELECT status FROM checkout_operations',[])['status']==='escalated','hour deadline escalates');
need(in_array('ESCALATED',history_codes($db),true),'escalation recorded');
reservation_reconcile($db,config_fixture(),$o['id'],fn($cfg,$method)=>$method==='POST'?response_fixture(500):list_fixture([session_fixture($o)]),$t+7200);
need(row($db,'SELECT sid FROM orders',[])['sid']==='cs_test_fixture'&&units($db)===1,'cached 500 recovered via metadata scan');
done('05 5xx, metadata recovery, bounded escalation; 11 unknown remains held');

[$db,$o,$t]=setup_fixture();
$event=event_fixture($o,'early');
reservation_reconcile($db,config_fixture(),$o['id'],function()use($db,$event,$o){
    need(row($db,'SELECT sid FROM orders WHERE id=?',[$o['id']])['sid']===null,'webhook really precedes sid persistence');
    need($event['data']['object']['client_reference_id']===$o['id'] && $event['data']['object']['metadata']['orderId']===$o['id'],'both webhook references bind the exact reservation');
    $raw=json_encode($event,JSON_THROW_ON_ERROR);$sent=time();$secret='isolated-webhook-fixture';
    $header='t='.$sent.',v1='.hash_hmac('sha256',$sent.'.'.$raw,$secret);
    need(verify_signature($raw,$header,$secret,$sent),'early webhook has a valid signature');
    need(!verify_signature($raw.' ',$header,$secret,$sent),'modified early webhook is rejected');
    apply_event($db,json_decode($raw,true,512,JSON_THROW_ON_ERROR));
    need(row($db,'SELECT sid FROM orders WHERE id=?',[$o['id']])['sid']==='cs_test_fixture','webhook atomically recovers sid through order metadata');
    return response_fixture(200,session_fixture($o));
},$t);
need(state($db,$o)==='paid'&&units($db)===1,'webhook wins over late open response');
need($db->query('SELECT COUNT(*) FROM orders')->fetchColumn()===1,'early webhook creates no second order');
$count=count(history_codes($db));apply_event($db,$event);apply_event($db,$event);
need(count(history_codes($db))===$count && $db->query('SELECT COUNT(*) FROM events')->fetchColumn()===1,'duplicate webhook no history/inventory duplication');
done('07 signed webhook before null sid: exact metadata binding, one order; 08 duplicate webhook');

[$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>timeout_fixture(),$t);
reservation_reconcile($db,config_fixture(),$o['id'],fn()=>response_fixture(200,session_fixture($o,'complete','unpaid')),$t+31);
need(state($db,$o)==='pending'&&units($db)===1,'unpaid complete not paid');
reservation_reconcile($db,config_fixture(),$o['id'],fn()=>response_fixture(200,session_fixture($o,'complete','unpaid')),$t+7200);
need(state($db,$o)==='pending'&&units($db)===1,'local expiry cannot release pending payment');
need(row($db,'SELECT escalated_at FROM checkout_operations',[])['escalated_at']!==null,'long pending payment requires operator attention');
apply_event($db,event_fixture($o,'latepaid','checkout.session.async_payment_succeeded'));
apply_event($db,event_fixture($o,'lateexpired','checkout.session.expired','unpaid'));
need(state($db,$o)==='paid'&&units($db)===1,'late success paid once, late expiry cannot release');done('12 delayed payment; pending and out-of-order events');

[$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>response_fixture(200,session_fixture($o)),$t);
reservation_reconcile($db,config_fixture(),$o['id'],fn()=>response_fixture(200,session_fixture($o)),$t+3601);
need(state($db,$o)==='reserved'&&units($db)===1,'Stripe open survives local expiry');
reservation_reconcile($db,config_fixture(),$o['id'],fn()=>response_fixture(200,session_fixture($o,'expired')),$t+4000);
reservation_reconcile($db,config_fixture(),$o['id'],fn()=>throw new RuntimeException('no network for terminal'),$t+5000);
apply_event($db,event_fixture($o,'expired','checkout.session.expired','unpaid'));
need(state($db,$o)==='released'&&units($db)===2,'expired unpaid releases once');
apply_event($db,event_fixture($o,'anomaly','checkout.session.async_payment_succeeded'));
need(state($db,$o)==='review'&&units($db)===2,'contradictory late payment escalates, no second stock movement');done('10 safe release, duplicate expiry, late anomaly');

foreach([23*3600-1,23*3600,24*3600-1,24*3600,24*3600+1,7*24*3600] as $age){
    [$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>timeout_fixture(),$t);
    $frozen=row($db,'SELECT * FROM checkout_operations',[]);$calls=[];
    reservation_reconcile($db,config_fixture(),$o['id'],function($cfg,$method,$path,$body,$key,$version)use(&$calls,$frozen){
        $calls[]=$method;
        if($method==='POST'){
            need($key===$frozen['idempotency_key'] && $body===$frozen['request_body'] && $version===$frozen['api_version'],'retained-key replay uses exact persisted operation');
            return response_fixture(500);
        }
        need($key===null && $body===null,'read-only recovery carries no create body or key');
        return list_fixture();
    },$t+$age);
    need($calls===($age<23*3600?['POST','GET']:['GET']),'POST is forbidden from exact 23h cutoff, including at/after 24h pruning');
    need(units($db)===1 && state($db,$o)==='reconcile','empty lookup never proves absence');
    need(row($db,'SELECT first_attempt FROM checkout_operations',[])['first_attempt']===$frozen['first_attempt'],'retry window is never reset');
}
done('retention boundaries: 22:59:59 same-key replay; 23h/24h/24h+1s/7d GET only');
[$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>timeout_fixture(),$t);
$calls=[];$objects=1;
reservation_reconcile($db,config_fixture(),$o['id'],function($cfg,$method)use(&$calls,&$objects,$o){
    $calls[]=$method;
    if($method==='POST'){$objects++;return response_fixture(200,session_fixture($o));} // A pruned key would create a second object.
    return list_fixture([session_fixture($o,'complete','paid')]);
},$t+24*3600+1);
need($calls===['GET'] && $objects===1 && state($db,$o)==='paid' && units($db)===1,'pruned-key fixture recovers paid session without a new creation');
need(row($db,'SELECT sid FROM orders',[])['sid']==='cs_test_fixture','sid recovered after retention');
done('after Stripe key pruning: GET recovers original paid session, no second object');

foreach([rejection_fixture(),response_fixture(0,null,true),response_fixture(409,['error'=>['type'=>'idempotency_error']]),response_fixture(429)]as $failure){
    [$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>timeout_fixture(),$t);
    reservation_reconcile($db,config_fixture(),$o['id'],fn($cfg,$method)=>$method==='POST'?$failure:list_fixture(),$t+31);
    need(state($db,$o)==='reconcile'&&units($db)===1,'later refusal or local error cannot negate earlier uncertainty');
}done('no release on subsequent local/4xx/409/429 after uncertainty');

[$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>timeout_fixture(),$t);
$bad=session_fixture($o);$bad['livemode']=true;
reservation_reconcile($db,config_fixture(),$o['id'],fn()=>response_fixture(200,$bad),$t+31);
need(state($db,$o)==='reconcile'&&units($db)===1,'mode mismatch not accepted');done('wrong mode/response cannot settle or release');

[$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>timeout_fixture(),$t);
$a=session_fixture($o);$b=$a;$b['id']='cs_test_second';
reservation_reconcile($db,config_fixture(),$o['id'],fn($cfg,$method)=>$method==='POST'?response_fixture(500):list_fixture([$a,$b]),$t+31);
need(row($db,'SELECT last_code FROM checkout_operations',[])['last_code']==='MULTIPLE_SESSIONS'&&units($db)===1,'multiple sessions escalated');done('multiple matches never guessed');

// Expired lease: a slow original worker cannot undo the replacement worker's result.
[$db,$o,$t]=setup_fixture();
reservation_reconcile($db,config_fixture(),$o['id'],function()use($db,$o,$t){
    reservation_reconcile($db,config_fixture(),$o['id'],fn()=>response_fixture(200,session_fixture($o)),$t+121);
    return response_fixture(0,null,true);
},$t);
need(state($db,$o)==='reserved'&&units($db)===1&&row($db,'SELECT sid FROM orders',[])['sid']==='cs_test_fixture','stale lease fenced');done('stale worker cannot release newer session');

[$db,$o,$t]=setup_fixture();
reservation_reconcile($db,config_fixture(),$o['id'],function()use($db,$o){
    apply_event($db,event_fixture($o,'expiryDuringRead','checkout.session.expired','unpaid'));
    return response_fixture(200,session_fixture($o,'complete','paid'));
},$t);
need(state($db,$o)==='review'&&units($db)===2,'positive late settlement not discarded by fencing');done('late paid API response after expiry escalates review');

[$db,$o,$t]=setup_fixture();
reservation_reconcile($db,config_fixture(),$o['id'],fn()=>throw new RuntimeException('expired unsent must not dispatch'),$t+3601);
need(state($db,$o)==='released'&&units($db)===2,'durably prepared, never-sent expired reservation released');done('expired never-sent operation needs no Stripe call');

[$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>timeout_fixture(),$t);
$calls=[];$answer=reservation_reconcile($db,config_fixture(),$o['id'],function($cfg,$method,$path)use(&$calls,$o){$calls[]=[$method,$path];return response_fixture(200,session_fixture($o));},$t+1,'cs_test_fixture');
need($answer['code']==='SESSION_RECOVERED'&&$calls===[['GET','/v1/checkout/sessions/cs_test_fixture']]&&units($db)===1,'operator id verified via GET only');done('operator-known session recovered without creating another');

[$db,$o,$t]=setup_fixture();reservation_reconcile($db,config_fixture(),$o['id'],fn()=>timeout_fixture(),$t);
$foreign=session_fixture($o);$foreign['client_reference_id']='w26_another';
reservation_reconcile($db,config_fixture(),$o['id'],fn()=>response_fixture(200,$foreign),$t+1,'cs_test_fixture');
need(state($db,$o)==='reconcile'&&row($db,'SELECT sid FROM orders',[])['sid']===null,'foreign operator session rejected');done('foreign session cannot be attached');

[$db,$o,$t]=setup_fixture();$db->exec('DELETE FROM checkout_operations; DELETE FROM reservation_history');
$calls=[];reservation_reconcile($db,config_fixture(),$o['id'],function($cfg,$method)use(&$calls){$calls[]=$method;return list_fixture();},$t+7200);
need($calls===['GET']&&state($db,$o)==='reconcile'&&units($db)===1,'legacy request with missing immutable payload is never reconstructed');done('legacy orphan is discoverable/escalated, never guessed safe');

// Freeze exact original payload and preserve original four-order ledger through additive migration.
$tmp=sys_get_temp_dir().DIRECTORY_SEPARATOR.'pf-reconcile-'.bin2hex(random_bytes(8));mkdir($tmp,0700);
try{
    $file=$tmp.DIRECTORY_SEPARATOR.'parallel.sqlite';[$db,$o,$t]=setup_fixture($file);$db=null;
    $gate=$tmp.DIRECTORY_SEPARATOR.'gate';$desc=[0=>['pipe','r'],1=>['pipe','w'],2=>['pipe','w']];
    $p1=proc_open([PHP_BINARY,__FILE__,'worker',$file,$gate],$desc,$pipes1);fclose($pipes1[0]);
    $deadline=microtime(true)+8;while(!is_file($gate.'.started')&&microtime(true)<$deadline)usleep(10000);
    need(is_file($gate.'.started'),'first worker reached network boundary');
    $p2=proc_open([PHP_BINARY,__FILE__,'worker',$file,$gate],$desc,$pipes2);fclose($pipes2[0]);
    $r2=stream_get_contents($pipes2[1]);$e2=stream_get_contents($pipes2[2]);fclose($pipes2[1]);fclose($pipes2[2]);need(proc_close($p2)===0,$e2);
    file_put_contents($gate.'.release','1');$r1=stream_get_contents($pipes1[1]);$e1=stream_get_contents($pipes1[2]);fclose($pipes1[1]);fclose($pipes1[2]);need(proc_close($p1)===0,$e1);
    need(json_decode($r2,true)['code']==='BUSY_OR_NOT_DUE'&&json_decode($r1,true)['code']==='SESSION_RECOVERED','concurrent lease result');
    need(count(file($gate.'.calls'))===1,'only one transport dispatch');$db=database(['db_file'=>$file]);need(units($db)===1,'single reservation under concurrency');$db=null;
    done('09 real concurrent RECONCILE processes on one SQLite');

    $file=$tmp.DIRECTORY_SEPARATOR.'legacy.sqlite';$db=database(['db_file'=>$file]);
    $db->exec("INSERT INTO store_meta VALUES('mode','test'); INSERT INTO stock VALUES('full-soft:marble',19)");
    foreach(['paid','paid','paid','released']as $i=>$s)$db->prepare('INSERT INTO orders(id,req,quote,created,state) VALUES(?,?,?,?,?)')->execute(['w26_'.str_repeat((string)$i,24),'legacy'.$i,'{}',123,$s]);
    $tables=['stock','orders','store_meta','attempts','events'];$before=[];foreach($tables as $name)$before[$name]=$db->query('SELECT * FROM '.$name)->fetchAll();$db=null;
    $cfg=config_fixture()+['db_file'=>$file];$cfgFile=$tmp.DIRECTORY_SEPARATOR.'config.json';file_put_contents($cfgFile,json_encode($cfg));$backup=$tmp.DIRECTORY_SEPARATOR.'backup.sqlite';
    $proc=proc_open([PHP_BINARY,__DIR__.'/../scripts/reconcile-reservations.php','--config',$cfgFile,'--migrate','--backup',$backup],$desc,$pipes);fclose($pipes[0]);$stdout=stream_get_contents($pipes[1]);$stderr=stream_get_contents($pipes[2]);fclose($pipes[1]);fclose($pipes[2]);need(proc_close($proc)===0,$stderr);
    need(json_decode($stdout,true)['migrated']===true&&is_file($backup),'CLI migration + private backup');
    $db=database(['db_file'=>$file]);$copy=new PDO('sqlite:'.$backup,null,null,[PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC]);
    foreach($tables as $name){need($db->query('SELECT * FROM '.$name)->fetchAll()===$before[$name],'legacy rows unchanged');need($copy->query('SELECT * FROM '.$name)->fetchAll()===$before[$name],'backup rows retained');}
    need($db->query('SELECT COUNT(*) FROM checkout_operations')->fetchColumn()===0&&$db->query('SELECT COUNT(*) FROM reservation_history')->fetchColumn()===0,'no historical backfill');$copy=null;$db=null;
    done('additive migration + backup; three paid and one released fixture unchanged');

    $file=$tmp.DIRECTORY_SEPARATOR.'status.sqlite';[$db,$o,$t]=setup_fixture($file);
    reservation_reconcile($db,config_fixture(),$o['id'],fn()=>timeout_fixture(),$t);
    reservation_reconcile($db,config_fixture(),$o['id'],fn($cfg,$method)=>$method==='POST'?response_fixture(500):list_fixture(),$t+3601);$db=null;
    file_put_contents($cfgFile,json_encode(config_fixture()+['db_file'=>$file]));
    $proc=proc_open([PHP_BINARY,'-d','disable_functions=curl_init,curl_exec',__DIR__.'/../scripts/reconcile-reservations.php','--config',$cfgFile,'--status','--order',$o['id'],'--history'],$desc,$pipes);
    fclose($pipes[0]);$stdout=stream_get_contents($pipes[1]);$stderr=stream_get_contents($pipes[2]);fclose($pipes[1]);fclose($pipes[2]);need(proc_close($proc)===2,'escalated status must alert via exit 2');
    $lines=explode("\n",trim($stdout));need(json_decode($lines[0],true)['attentionRequired']===1,'operator attention count');
    need(count(json_decode($lines[1],true)['history'])>0,'operator receives reason history');
    need(!str_contains($stdout,'sk_test_')&&!str_contains($stdout,'request_body')&&!str_contains($stdout,'checkout.stripe.com'),'no credentials or checkout URL in operator output');
    done('operator status/history and exit 2 escalation, network disabled');
    $db=database(['db_file'=>$file]);
    $db->prepare("UPDATE checkout_operations SET next_check=?,lease_until=0,escalated_at=NULL,status='unknown'")->execute([time()-301]);$db=null;
    $proc=proc_open([PHP_BINARY,'-d','disable_functions=curl_init,curl_exec',__DIR__.'/../scripts/reconcile-reservations.php','--config',$cfgFile,'--status'],$desc,$pipes);
    fclose($pipes[0]);$stdout=stream_get_contents($pipes[1]);$stderr=stream_get_contents($pipes[2]);fclose($pipes[1]);fclose($pipes[2]);need(proc_close($proc)===2,'overdue queue must alert even without an escalated order');
    $status=json_decode(trim($stdout),true);need($status['attentionRequired']===0&&$status['backlogAlert']===true&&$status['oldestDueLagSeconds']>=301,'queue lag detected independently of reservation escalation');
    done('scheduler backlog over 5 minutes: exit 2 without falsely healthy heartbeat');
}finally{
    $db=null;
    $real=realpath($tmp);need($real!==false&&str_starts_with($real,realpath(sys_get_temp_dir()).DIRECTORY_SEPARATOR.'pf-reconcile-'),'scoped cleanup');
    foreach(new DirectoryIterator($real)as $p)if(!$p->isDot()){need($p->isFile()&&!$p->isLink(),'only own regular fixture files');unlink($p->getPathname());}
    rmdir($real);
}
echo "PASS all reconciliation scenarios; zero network calls, no staging data.\n";
