<?php
declare(strict_types=1);
function offered_variant(string $key): bool {
    return preg_match('/^(full-soft|knitted-star|knitted-medallion):(dual|red-matte|white|marble)$/D',$key)===1;
}
function require_current_offer(array $quote): void {
    if(($quote['delivery_method']??null)!=='locker')problem('DELIVERY_METHOD',422,'Dostawa jest dostępna wyłącznie do automatu Paczkomat InPost.');
    foreach(array_keys($quote['items']) as $key)if(!offered_variant($key))problem('VARIANT',422,'Wybrany wariant nie jest dostępny w ofercie.');
}
