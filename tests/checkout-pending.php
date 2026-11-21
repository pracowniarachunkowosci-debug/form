<?php
declare(strict_types=1);
require __DIR__.'/checkout-retry.php';
function pending_fixture():array{
    [$db,$o,$t]=setup_fixture();
    apply_event($db,event_fixture($o,'blikstarted','checkout.session.completed','unpaid'));
    need(state($db,$o)==='pending'&&units($db)===1,'BLIK awaiting settlement retains reservation');
    return [$db,$o,$t];
}
function pending_request(PDO $db,array $o):array{
    return order($db,$o['req'],quote(['requestId'=>$o['req'],'selections'=>[['modelId'=>'full-soft','colorId'=>'marble']]],policy()),null,null,config_fixture());
}
foreach(['waiting','success','expired','failure','timeout','stale-open']as $scenario){
    [$db,$o,$t]=pending_fixture();$calls=[];$again=pending_request($db,$o);
    $http=function($cfg,$method,$path,$body,$key)use(&$calls,$o,$scenario){
        $calls[]=[$method,$path];need($method==='GET'&&$path==='/v1/checkout/sessions/cs_test_fixture'&&$body===null&&$key===null,'pending uses saved SID, GET only');
        if($scenario==='timeout')return timeout_fixture();
        $status=$scenario==='expired'?'expired':($scenario==='stale-open'?'open':'complete');
        $s=session_fixture($o,$status,$scenario==='success'?'paid':'unpaid');$s['payment_method_types']=['blik'];
        return response_fixture(200,$s);
    };
    retry_error($scenario==='success'?'ORDER_PAID':($scenario==='expired'?'ATTEMPT_RELEASED':'PAYMENT_PENDING'),
        fn()=>stripe_session(config_fixture(),$again,$db,$http,$t+1));
    need(count($calls)===1,'explicit check reads even before scheduled next_check');
    need($db->query('SELECT COUNT(*) FROM orders')->fetchColumn()===1,'no new order');
    need((int)row($db,'SELECT attempts FROM checkout_operations',[])['attempts']===0,'no create attempt');
    if($scenario==='failure'){
        $event=event_fixture($o,'blikfailed','checkout.session.async_payment_failed','unpaid');
        apply_event($db,$event);apply_event($db,$event);
        apply_event($db,event_fixture($o,'laterexpired','checkout.session.expired','unpaid'));
        need(state($db,$o)==='released'&&units($db)===2,'confirmed failure releases exactly once');
    }elseif($scenario==='waiting'){
        apply_event($db,event_fixture($o,'bliksucceeded','checkout.session.async_payment_succeeded','paid'));
        retry_error('ORDER_PAID',fn()=>pending_request($db,$o));
        need(units($db)===1&&state($db,$o)==='paid','async settlement retains sold units');
    }else need(units($db)===($scenario==='expired'?2:1),'no early or double release');
    done('pending '.$scenario.': saved SID only, no second payment');
}
// Pending without SID must never replay a durable CREATE body (even in the CLI path).
[$db,$o,$t]=pending_fixture();$db->exec('UPDATE orders SET sid=NULL');
$db->exec('UPDATE checkout_operations SET next_check=0');
retry_error('PAYMENT_PENDING',fn()=>stripe_session(config_fixture(),pending_request($db,$o),$db,fn()=>throw new RuntimeException('NO HTTP ALLOWED'),$t+1));
need(state($db,$o)==='pending'&&units($db)===1,'missing SID remains held');
need((int)row($db,'SELECT attempts FROM checkout_operations',[])['attempts']===0,'pending missing SID cannot POST');
done('pending missing reference: no create or release');
// Two concurrent customer checks are fenced by the same lease.
[$db,$o,$t]=pending_fixture();$calls=(object)['n'=>0];
retry_error('PAYMENT_PENDING',fn()=>stripe_session(config_fixture(),pending_request($db,$o),$db,function()use($db,$o,$t,&$calls){
    $calls->n++;
    retry_error('PAYMENT_PENDING',fn()=>stripe_session(config_fixture(),pending_request($db,$o),$db,fn()=>throw new RuntimeException('second HTTP'),$t+1));
    return response_fixture(200,session_fixture($o,'complete','unpaid'));
},$t+1));
need($calls->n===1&&units($db)===1,'single in-flight GET');done('pending double check: one GET');
foreach(['success','failure']as $kind){
    [$db,$o,$t]=pending_fixture();
    retry_error($kind==='success'?'ORDER_PAID':'ATTEMPT_RELEASED',fn()=>stripe_session(config_fixture(),pending_request($db,$o),$db,function()use($db,$o,$kind){
        apply_event($db,event_fixture($o,'duringget','checkout.session.async_payment_'.($kind==='success'?'succeeded':'failed'),$kind==='success'?'paid':'unpaid'));
        return response_fixture(200,session_fixture($o,'complete','unpaid'));
    },$t+1));
    need(units($db)===($kind==='success'?1:2),'webhook wins stale GET without double inventory change');
    done('pending webhook '.$kind.' races stale GET');
}
