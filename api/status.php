<?php
declare(strict_types=1);require_once __DIR__.'/_common.php';require_once __DIR__.'/_sales.php';
endpoint(function(){
    method('GET');$closed=['mode'=>'closed','available'=>false,'currency'=>'PLN','locker_available'=>false,'locker_amount_grosze'=>null,'geowidget_token'=>null,'smallOrderCourierGrosz'=>null,'freeCourierFromOrnaments'=>6,'stock'=>(object)[]];
    try{$cfg=deployment();$live=$cfg['mode']==='live';if(!$live&&!is_tester())return $closed;$points=inpost_settings($cfg);if($live)visitor_id();$p=policy();$rates=delivery_rates($p);$db=database($cfg);if(!ledger_ok($db,$cfg['mode']))return $closed;$production=production_enabled($cfg);$offered=$production?production_offered():[];$stock=$production?(object)[]:(object)array_filter((array)stock($db),fn($n,$key)=>offered_variant($key),ARRAY_FILTER_USE_BOTH);}
    catch(Throwable $e){return $closed+($e instanceof StoreError && $e->kind==='POINTS_CONFIG'?
        ['notice'=>'Walidacja punktów InPost jest niedostępna. Bez potwierdzonego automatu nie można złożyć zamówienia.']:[]);}
    try{$admission=sales_admission($cfg);if(is_resource($admission))fclose($admission);}
    catch(Throwable $e){return $closed+['notice'=>'Przyjmowanie nowych zamówień jest chwilowo wstrzymane.'];}
    return $points+(($live||($cfg['legal_acceptance_required']??false))?live_public_info($cfg):[])+['legal_acceptance_required'=>$live||($cfg['legal_acceptance_required']??false),'mode'=>$cfg['mode'],'available'=>$production?count($offered)>0:count(array_filter((array)$stock,fn($n)=>$n>0))>0,'fulfillment_mode'=>$production?'made_to_order':'inventory','offered_variants'=>$offered,'currency'=>$p['currency'],
        'delivery_methods'=>['locker'],'locker_amount_grosze'=>$rates['locker'],'freeCourierFromOrnaments'=>$p['freeCourierFromOrnaments'],'stock'=>$stock,'dispatch_required'=>dispatch_enabled($cfg)];
});
