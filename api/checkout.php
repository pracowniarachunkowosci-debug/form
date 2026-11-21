<?php
declare(strict_types=1);require_once __DIR__.'/_common.php';require_once __DIR__.'/_sales.php';
endpoint(function(){
    try {
    method('POST');$cfg=deployment();require_origin($cfg);$live=$cfg['mode']==='live';
    if(!$live && !is_tester())problem('TEST_ACCESS',403,'Ten checkout jest dostępny tylko dla testera.');
    if(strtolower(trim(explode(';',$_SERVER['CONTENT_TYPE']??'')[0]))!=='application/json')problem('MEDIA',415,'Nieprawidłowy typ danych.');
    $in=json_decode(body(8192),true);if(!is_array($in))problem('BAD_BODY',400,'Nieprawidłowe dane.');
    $q=quote($in,policy(),($live||($cfg['legal_acceptance_required']??false))?$cfg['approvalVersion']:null);require_current_offer($q);$db=database($cfg);
    if(!ledger_ok($db,$cfg['mode']))unavailable();
    $owner=null;if($live){$owner=visitor_id();rate($db,$cfg,$owner,$in['requestId']);}
    $admission=sales_admission($cfg);
    try{$o=order($db,$in['requestId'],$q,$owner,fn($id)=>lookup_point($cfg,$id),$cfg);}
    finally{if(is_resource($admission))fclose($admission);}
    $s=stripe_session($cfg,$o,$db);
    return ['orderId'=>$o['id'],'url'=>$s['url'],'totalGrosz'=>json_decode($o['quote'],true)['total']];
    } catch(StoreError $e) {
        // A webhook may settle this exact order while checkout is in flight.
        if($e->kind==='ORDER_PAID')return ['state'=>'paid','message'=>'Zamówienie opłacone. Płatność została potwierdzona. Nie płać ponownie.'];
        throw $e;
    }
});
