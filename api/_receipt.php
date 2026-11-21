<?php
declare(strict_types=1);
function order_receipt(PDO $db,string $id,string $owner): array {
    if(!preg_match('/^w26_[a-f0-9]{24}$/D',$id))problem('NOT_FOUND',404,'Nie znaleziono zamówienia.');
    $o=row($db,'SELECT id,state,quote,owner FROM orders WHERE id=?',[$id]);
    if(!$o||!is_string($o['owner'])||!hash_equals($o['owner'],$owner))problem('NOT_FOUND',404,'Nie znaleziono zamówienia.');
    // No Stripe URL/query parameter can turn this into paid. P0's verified ledger is authoritative.
    if($o['state']!=='paid')return ['paid'=>false];
    $q=json_decode($o['quote'],true,512,JSON_THROW_ON_ERROR);$items=[];
    foreach($q['packs'] as $p)$items[]=['item_id'=>'WINTER26-SET-'.$p['size'],'item_name'=>'WINTER 26 / '.$p['size'].' szt.','price'=>$p['merchandise']/100,'quantity'=>1];
    return ['paid'=>true,'purchase'=>['transaction_id'=>$o['id'],'currency'=>'PLN','value'=>$q['merchandise']/100,'shipping'=>$q['shipping']/100,'items'=>$items]];
}
