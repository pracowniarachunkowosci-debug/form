<?php
declare(strict_types=1);require_once __DIR__.'/_common.php';
endpoint(function(){
    method('GET');$closed=['mode'=>'closed','available'=>false,'currency'=>'PLN','locker_available'=>false,'locker_amount_grosze'=>null,'geowidget_token'=>null,'smallOrderCourierGrosz'=>null,'freeCourierFromOrnaments'=>6,'stock'=>(object)[]];
    try{$cfg=deployment();$live=$cfg['mode']==='live';if(!$live&&!is_tester())return $closed;if($live)visitor_id();$p=policy();$rates=delivery_rates($p);$db=database($cfg);if(!ledger_ok($db,$cfg['mode']))return $closed;$stock=stock($db);}
    catch(Throwable $e){return $closed;}
    return inpost_settings($cfg)+($live?live_public_info($cfg):[])+['mode'=>$cfg['mode'],'available'=>count(array_filter((array)$stock,fn($n)=>$n>0))>0,'currency'=>$p['currency'],
        'smallOrderCourierGrosz'=>$rates['courier'],'locker_amount_grosze'=>$rates['locker'],'freeCourierFromOrnaments'=>$p['freeCourierFromOrnaments'],'stock'=>$stock];
});
