<?php
declare(strict_types=1);require_once __DIR__.'/_common.php';require_once __DIR__.'/_sales.php';
require_once __DIR__.'/_checkout_identity.php';
endpoint(function(){
    method('POST');$cfg=deployment();require_origin($cfg);$live=$cfg['mode']==='live';
    if(!$live&&!is_tester())problem('TEST_ACCESS',403,'Wymagany dostęp testera.');
    if(!dispatch_enabled($cfg))problem('DISPATCH_UNAVAILABLE',503,'Termin nadania nie jest jeszcze skonfigurowany.');
    if(strtolower(trim(explode(';',$_SERVER['CONTENT_TYPE']??'')[0]))!=='application/json')problem('MEDIA',415,'Nieprawidłowy typ danych.');
    $in=json_decode(body(8192),true);if(!is_array($in))problem('BAD_BODY',400,'Nieprawidłowe dane.');
    // Preview records no consent and no order. The final checkout independently requires acceptance.
    $q=quote($in,policy(),($live||($cfg['legal_acceptance_required']??false))?$cfg['approvalVersion']:null);require_current_offer($q);$db=database($cfg);
    if(!ledger_ok($db,$cfg['mode']))unavailable();
    $owner=$live?visitor_id():checkout_test_owner();$lock=sales_admission($cfg);
    try{return tx($db,fn()=>dispatch_preview($db,$cfg,$q,$owner,time()));}
    finally{if(is_resource($lock))fclose($lock);}
});
