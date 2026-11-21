<?php
declare(strict_types=1);
require __DIR__.'/checkout-reconciliation.php';
function retry_error(string $code,callable $fn):void{
    try{$fn();throw new RuntimeException('expected '.$code);}catch(StoreError $e){need($e->kind===$code,'expected '.$code.', got '.$e->kind);}
}
[$db,$o,$t]=setup_fixture();$calls=0;
$transport=function()use(&$calls,$o){$calls++;return response_fixture(200,session_fixture($o));};
$first=stripe_session(config_fixture(),$o,$db,$transport,$t);
$input=['requestId'=>$o['req'],'selections'=>[['modelId'=>'full-soft','colorId'=>'marble']]];
$again=order($db,$o['req'],quote($input,policy()),null,null,config_fixture());
need(stripe_session(config_fixture(),$again,$db,$transport,$t+1)===$first&&$calls===1&&units($db)===1,'open session reused');
done('first redirect + same request + return without payment reuse one session');
// A declined card leaves Checkout open. No stock release or second Checkout is allowed.
need(stripe_session(config_fixture(),$again,$db,$transport,$t+2)===$first&&$calls===1,'declined card retry');
apply_event($db,event_fixture($o,'retryexpired','checkout.session.expired','unpaid'));
retry_error('ATTEMPT_RELEASED',fn()=>order($db,$o['req'],quote($input,policy()),null,null,config_fixture()));
need(units($db)===2,'expiry releases once');
$input['requestId']='12345678-1234-4321-8123-123456789abd';
$new=order($db,$input['requestId'],quote($input,policy()),null,null,config_fixture());
need($new['id']!==$o['id']&&units($db)===1,'explicit new ID after terminal attempt');
done('expiry + fresh attempt + inventory accounting');
foreach(['paid'=>'ORDER_PAID','pending'=>'PAYMENT_PENDING','review'=>'PAYMENT_REVIEW']as $state=>$code){
    [$db,$o,$t]=setup_fixture();$db->prepare('UPDATE orders SET state=? WHERE id=?')->execute([$state,$o['id']]);
    $input=['requestId'=>$o['req'],'selections'=>[['modelId'=>'full-soft','colorId'=>'marble']]];
    retry_error($code,fn()=>order($db,$o['req'],quote($input,policy()),null,null,config_fixture()));
    retry_error($code,fn()=>stripe_session(config_fixture(),$o,$db,fn()=>throw new RuntimeException('must not create'),$t));
    need(units($db)===1,'terminal check does not alter inventory');
}
done('paid/pending/review never create another payment');
foreach(['checkout.session.completed'=>'ORDER_PAID','checkout.session.expired'=>'ATTEMPT_RELEASED']as $kind=>$code){
    [$db,$o,$t]=setup_fixture();
    retry_error($code,fn()=>stripe_session(config_fixture(),$o,$db,function()use($db,$o,$kind){
        apply_event($db,event_fixture($o,'raceretry',$kind,$kind==='checkout.session.completed'?'paid':'unpaid'));
        return response_fixture(200,session_fixture($o));
    },$t));
}
done('webhook wins race before create response: typed safe result');
