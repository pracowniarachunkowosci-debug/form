<?php
declare(strict_types=1);
require_once __DIR__.'/_common.php';require_once __DIR__.'/_order_status.php';
endpoint(function(){
    method('POST');$cfg=deployment(true);require_origin($cfg);
    if($cfg['mode']==='test'&&!is_tester())problem('TEST_ACCESS',403,'Zaloguj się jako tester, aby sprawdzić status.');
    if(strtolower(trim(explode(';',$_SERVER['CONTENT_TYPE']??'')[0]))!=='application/json')problem('MEDIA',415,'Nieprawidłowy typ danych.');
    $in=json_decode(body(256),true);
    if(!is_array($in)||array_keys($in)!==['requestId']||!is_string($in['requestId']))problem('BAD_REQUEST',422,'Nieprawidłowe dane.');
    $db=order_status_database($cfg);if(!ledger_ok($db,$cfg['mode']))unavailable();
    return order_status_read($db,$in['requestId'],$cfg['mode']==='live'?visitor_id():null);
});
