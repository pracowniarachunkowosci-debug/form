<?php
declare(strict_types=1);require_once __DIR__.'/_common.php';
endpoint(function(){
    method('POST');$cfg=deployment();require_origin($cfg);$live=$cfg['mode']==='live';
    if(!$live && !is_tester())problem('TEST_ACCESS',403,'Ten checkout jest dostępny tylko dla testera.');
    if(strtolower(trim(explode(';',$_SERVER['CONTENT_TYPE']??'')[0]))!=='application/json')problem('MEDIA',415,'Nieprawidłowy typ danych.');
    $in=json_decode(body(8192),true);if(!is_array($in))problem('BAD_BODY',400,'Nieprawidłowe dane.');
    $q=quote($in,policy(),$live?$cfg['approvalVersion']:null);$db=database($cfg);
    if(!ledger_ok($db,$cfg['mode']))unavailable();
    $owner=null;if($live){$owner=visitor_id();rate($db,$cfg,$owner,$in['requestId']);}
    $o=order($db,$in['requestId'],$q,$owner,fn($id)=>lookup_point($cfg,$id));
    $s=stripe_session($cfg,$o);bind_session($db,$o,$s);
    return ['orderId'=>$o['id'],'url'=>$s['url'],'totalGrosz'=>json_decode($o['quote'],true)['total']];
});
