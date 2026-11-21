<?php
declare(strict_types=1);
// Explicit server-side owner-approved policy gate. Never read the fulfilment mode from a customer request.
function production_enabled(array $cfg): bool {
    $mode=$cfg['fulfillment_mode']??'inventory';
    if($mode==='inventory')return false;
    if($mode!=='made_to_order'||($cfg['production_on_order_approved']??false)!==true||!dispatch_enabled($cfg))unavailable();
    return true;
}
function production_notice(): string {
    return 'Zamówienia przygotowujemy na bieżąco. Zazwyczaj nadajemy je w ciągu 3 dni roboczych, maksymalnie w ciągu 7 dni roboczych od potwierdzenia płatności. Termin dotyczy nadania, nie doręczenia.';
}
function production_offered(): array {
    $out=[];foreach(policy()['eligibleModelIds']as $model)foreach(['dual','red-matte','white','marble']as $color){
        $sku=$model.':'.$color;if(offered_variant($sku))$out[]=$sku;
    }return $out;
}
function production_plan(array $q): array {
    $lines=[];$items=$q['items'];ksort($items);
    foreach($items as $sku=>$quantity){
        if(!offered_variant($sku))problem('VARIANT',422,'Wybrany wariant nie jest dostępny w ofercie.');
        $lines[]=['sku'=>$sku,'quantity'=>$quantity,'units'=>[]];
    }
    return ['version'=>'production-on-order-7-v1','kind'=>'made_to_order','inventoryAccounting'=>'none',
        'maxBusinessDays'=>7,'basis'=>'confirmed_payment','businessDays'=>'Monday-Friday excluding Polish statutory holidays',
        'text'=>production_notice(),'lines'=>$lines];
}
function production_snapshot(array $q): bool {
    $d=$q['dispatch']??[];
    return ($d['version']??'')==='production-on-order-7-v1'&&($d['inventoryAccounting']??'')==='none'
        &&($d['kind']??'')==='made_to_order'&&($d['maxBusinessDays']??null)===7;
}
