<?php
declare(strict_types=1);
// Offline fixtures mirror the documented PL Points response. No InPost or payment account is contacted.
require_once __DIR__.'/../api/_common.php';
function ensure(bool $ok,string $msg):void {if(!$ok)throw new RuntimeException($msg);}
function fails(string $kind,callable $f):void {try{$f();}catch(StoreError $e){ensure($kind===$e->kind,$kind.' != '.$e->kind);return;}throw new RuntimeException('Expected '.$kind);}
$p=policy();$slot=['modelId'=>'full-soft','colorId'=>'marble'];$id='WRO01M';
$one=['requestId'=>'12345678-1111-4111-8111-111111111111','selections'=>[$slot]];
$locker=$one+['delivery_method'=>'locker','pickup_point'=>' wro01m '];
$point=['name'=>$id,'type'=>['parcel_locker'],'status'=>'Operating','virtual'=>'0','functions'=>['parcel_collect'],
    'address_details'=>['post_code'=>'53-600','city'=>'Wrocław'],'address'=>['line1'=>'Testowa 1']];
$fixture=fn(string $code)=>canonical_point($code,['items'=>[$point]]);
ensure(!inpost_settings([])['locker_available'],'unconfigured locker off');
ensure(inpost_settings(['inpost_points_token'=>'private-token'])===['locker_available'=>true,'geowidget_token'=>null],'manual point ID without map');
ensure(inpost_settings(['inpost_points_token'=>'private-token','inpost_geowidget_token'=>'private-token'])['geowidget_token']===null,'private token never exposed');
ensure(inpost_settings(['inpost_points_token'=>'private-token','inpost_geowidget_token'=>'public-geo'])['geowidget_token']==='public-geo','geo public only');
fails('POINTS_UNAVAILABLE',fn()=>lookup_point([],$id));
foreach([['status'=>'NonOperating'],['type'=>['parcel_locker','pop']],['type'=>['parcel_locker_superpop']],['virtual'=>1],
    ['country'=>'FR'],['functions'=>['parcel_send']],['name'=>'WRO02M'],['address_details'=>['city'=>'Paris','post_code'=>'75004']]]as $bad)
    fails('PICKUP_POINT',fn()=>canonical_point($id,['items'=>[array_merge($point,$bad)]]));
fails('PICKUP_POINT',fn()=>canonical_point($id,['items'=>[]]));fails('POINTS_UNAVAILABLE',fn()=>canonical_point($id,[]));
ensure($fixture($id)===['id'=>$id,'address'=>'Testowa 1, 53-600 Wrocław'],'canonical InPost address');
fails('PICKUP_POINT',fn()=>quote($one+['delivery_method'=>'locker'],$p));
fails('PICKUP_POINT',fn()=>quote($one+['delivery_method'=>'locker','pickup_point'=>['id'=>$id]],$p));
fails('DELIVERY_METHOD',fn()=>quote($one+['pickup_point'=>$id],$p));
fails('DELIVERY_METHOD',fn()=>quote($one+['delivery_method'=>'post-office'],$p));
$single=quote($locker,$p);
ensure($single['total']===6849&&$single['shipping']===1849&&quote($one,$p)['total']===7049,'single courier vs locker');
foreach([5=>1849,6=>0,8=>0] as $n=>$fee){
    $in=$locker;unset($in['selections']);$in['packs']=$n===5?[array_fill(0,4,$slot),[$slot]]:($n===6?[array_fill(0,4,$slot),array_fill(0,2,$slot)]:[array_fill(0,8,$slot)]);
    ensure(quote($in,$p)['shipping']===$fee,'combined threshold');
}
$db=database(['db_file'=>':memory:']);$db->exec("INSERT INTO stock VALUES('full-soft:marble',8)");
fails('POINTS_UNAVAILABLE',fn()=>order($db,$one['requestId'],$single,null,fn()=>point_unavailable()));
ensure((int)$db->query('SELECT COUNT(*) FROM orders')->fetchColumn()===0&&(int)$db->query('SELECT n FROM stock')->fetchColumn()===8,'no reservation when InPost down');
$order=order($db,$one['requestId'],$single,null,$fixture);
$q=json_decode($order['quote'],true);ensure($q['pickup_point']===$id&&$q['pickup_address']==='Testowa 1, 53-600 Wrocław','durable address outside browser');
$retry=order($db,$one['requestId'],$single,null,fn()=>point_unavailable());ensure($retry['id']===$order['id'],'idempotent even during directory outage');
fails('REQUEST_CONFLICT',fn()=>order($db,$one['requestId'],quote($one,$p)));
fails('REQUEST_CONFLICT',fn()=>order($db,$one['requestId'],array_merge($single,['pickup_point'=>'WRO02M'])));
$s=checkout_params($order,'https://test.invalid');
ensure(!isset($s['shipping_address_collection']) && $s['phone_number_collection']['enabled']==='true' && $s['name_collection']['individual']===['enabled'=>'true','optional'=>'false'] && !isset($s['custom_fields']),'locker asks for recipient, no home shipping address');
ensure($s['metadata']['pickup_point']===$id && $s['payment_intent_data']['metadata']['pickup_address']===$q['pickup_address'],'operator sees pickup in payment');
ensure(str_contains($s['custom_text']['submit']['message'],$q['pickup_address']) && $s['line_items'][1]['price_data']['unit_amount']===1849,'checkout shows correct pickup and price');
$session=['id'=>'cs_test_fixture','client_reference_id'=>$order['id'],'metadata'=>$s['metadata'],'currency'=>'pln','mode'=>'payment',
    'payment_status'=>'paid','amount_total'=>6849,'livemode'=>false,'object'=>'checkout.session'];
$event=['id'=>'evt_locker','type'=>'checkout.session.completed','livemode'=>false,'data'=>['object'=>$session]];
$bad=$event;$bad['data']['object']['metadata']['pickup_point']='WRO02M';fails('EVENT_MISMATCH',fn()=>apply_event($db,$bad));
apply_event($db,$event);ensure(row($db,'SELECT state FROM orders WHERE id=?',[$order['id']])['state']==='paid','verified paid with correct delivery');
require __DIR__.'/inpost-mock.php';
echo "PASS: rates, combined threshold, active PL locker only, lookup failure, canonical fulfilment, Stripe fields and idempotency. No network.\n";
