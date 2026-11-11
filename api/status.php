<?php
declare(strict_types=1);require_once __DIR__.'/_common.php';
endpoint(function(){
    method('GET');$closed=['mode'=>'closed','available'=>false,'currency'=>'PLN','smallOrderCourierGrosz'=>null,'freeCourierFromOrnaments'=>6,'stock'=>(object)[]];
    try{$cfg=deployment();$live=$cfg['mode']==='live';if(!$live&&!is_tester())return $closed;if($live)visitor_id();$p=policy();$db=database($cfg);if(!ledger_ok($db,$cfg['mode']))return $closed;$stock=stock($db);}
    catch(Throwable $e){return $closed;}
    return ($live?live_public_info($cfg):[])+['mode'=>$cfg['mode'],'available'=>count(array_filter((array)$stock,fn($n)=>$n>0))>0,'currency'=>$p['currency'],
        'smallOrderCourierGrosz'=>$cfg['smallOrderCourierGrosz'],'freeCourierFromOrnaments'=>$p['freeCourierFromOrnaments'],'stock'=>$stock];
});
