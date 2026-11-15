<?php
declare(strict_types=1);
// Local, no HTTP requests to Stripe, no tokens, no real transaction.
require_once __DIR__.'/../api/_common.php';
function check(bool $ok,string $why): void {if(!$ok) throw new RuntimeException($why);}
function expect_problem(string $kind,callable $fn): void {
    try{$fn();}catch(StoreError $e){check($e->kind===$kind,"expected $kind, got ".$e->kind);return;}
    throw new RuntimeException("expected failure $kind");
}
function req(array $models,string $letter): array {
    return ['requestId'=>'1234567'.$letter.'-1111-4111-8111-111111111111','code'=>'',
      'selections'=>array_map(fn($m)=>['modelId'=>$m,'colorId'=>'marble'],$models)];
}
function available(PDO $db,string $model): int{return (array)stock($db)===[]?0:((array)stock($db))[$model.':marble'];}
$p=policy();$v='full-soft';$m='knitted-medallion';$s='knitted-star';$q2=req([$v,$m],'a');
foreach([1=>5000,2=>8400,4=>15000,6=>22000,8=>29000] as $n=>$price){
  $q=quote(req(array_fill(0,$n,$v),'a'),$p);check($q['total']===$price+($n<6?2049:0),'price/threshold');
}
foreach(['dual','red-matte','white','marble']as $color)foreach([$v,$s,$m]as $model){check(valid_key($model.':'.$color,$p),'valid variant');}
check(!valid_key('helix:marble',$p),'retired model is excluded');
expect_problem('SIZE',fn()=>quote(req([$v,$s,$m],'a'),$p));
expect_problem('NO_PROMOTION',fn()=>quote(array_merge($q2,['code'=>'WINTER10']),$p));
expect_problem('BAD_REQUEST',fn()=>quote($q2+['total'=>1],$p));
expect_problem('VARIANT',fn()=>quote(req(['helix'],'a'),$p));
$two=$q2['selections'];$four=req([$s,$m,$v,$v],'c')['selections'];$six=req([$s,$s,$m,$m,$v,$v],'d')['selections'];
$multi=['requestId'=>$q2['requestId'],'packs'=>[$two,$four],'code'=>''];
$cart=quote($multi,$p);check($cart['total']===23400 && $cart['shipping']===0 && count($cart['packs'])===2,'2+4: two regular prices, free courier');
check($cart['items']['full-soft:marble']===3 && $cart['items']['knitted-medallion:marble']===2,'aggregate cross-pack stock');
$cart2=quote(array_merge($multi,['packs'=>[$six,[$two[0]]]]),$p);check($cart2['total']===27000 && $cart2['shipping']===0,'6+single: 270 PLN');
expect_problem('BAD_REQUEST',fn()=>quote($multi+['selections'=>$two],$p));
expect_problem('SIZE',fn()=>quote(array_merge($multi,['packs'=>[$two,array_slice($four,0,3)]]),$p));
expect_problem('SIZE',fn()=>quote(array_merge($multi,['packs'=>array_fill(0,11,$two)]),$p));
$multiLines=checkout_params(['id'=>'w26_test','quote'=>json_encode($cart),'created'=>time()],'https://sandbox.invalid');
check(array_column(array_column($multiLines['line_items'],'price_data'),'unit_amount')===[8400,15000],'Stripe preserves both pack prices');
unset($_SERVER['HTTP_HOST']);expect_problem('UNAVAILABLE',fn()=>configuration());
$db=database(['db_file'=>':memory:']);
foreach([$v=>3,$m=>1,$s=>1]as $k=>$n)$db->prepare('INSERT INTO stock VALUES (?,?)')->execute([$k.':marble',$n]);
$q=quote($q2,$p);$o=order($db,$q2['requestId'],$q);
check(available($db,$v)===2 && available($db,$m)===0,'reserved all SKUs');
check(order($db,$q2['requestId'],$q)['id']===$o['id'] && available($db,$v)===2,'retry without second reservation');
expect_problem('REQUEST_CONFLICT',fn()=>order($db,$q2['requestId'],quote(req([$s],'a'),$p)));
expect_problem('STOCK',fn()=>order($db,req([$s,$m],'b')['requestId'],quote(req([$s,$m],'b'),$p)));
check(available($db,$s)===1,'insufficient item rolls back earlier items');
$params=checkout_params($o,'https://sandbox.example.invalid');
check(array_sum(array_map(fn($i)=>$i['price_data']['unit_amount']*$i['quantity'],$params['line_items']))===10449,'Stripe payload total');
check($params['shipping_address_collection']['allowed_countries']===['PL'] && !isset($params['allow_promotion_codes']),'PL only, no public Stripe codes');
$session=['id'=>'cs_test_example','client_reference_id'=>$o['id'],'metadata'=>['orderId'=>$o['id']],'currency'=>'pln',
    'livemode'=>false,'object'=>'checkout.session','mode'=>'payment','amount_total'=>10449,'payment_status'=>'unpaid','payment_intent'=>'pi_example'];
bind_session($db,$o,['id'=>$session['id'],'url'=>'https://checkout.stripe.com/example']);
$event=['type'=>'checkout.session.completed','livemode'=>false,'id'=>'evt_abc','data'=>['object'=>$session]];
$raw=json_encode($event);$t=time();$sig='t='.$t.',v1='.hash_hmac('sha256',$t.'.'.$raw,'temporary-secret');
check(verify_signature($raw,$sig,'temporary-secret',$t),'valid signed event');
check(!verify_signature($raw,$sig,'temporary-secret',$t+301) && !verify_signature($raw.' ',$sig,'temporary-secret',$t),'stale/modified event rejected');
$bad=$event;$bad['data']['object']['amount_total']=1;expect_problem('EVENT_MISMATCH',fn()=>apply_event($db,$bad));
$bad=$event;$bad['livemode']=true;expect_problem('EVENT',fn()=>apply_event($db,$bad));
apply_event($db,$event);apply_event($db,$event);
check(row($db,'SELECT state FROM orders WHERE id=?',[$o['id']])['state']==='pending','completed is not paid');
$event['id']='evt_def';$event['type']='checkout.session.async_payment_failed';apply_event($db,$event);apply_event($db,$event);
check(available($db,$v)===3 && available($db,$m)===1,'release exactly once');
$event['id']='evt_late';$event['type']='checkout.session.async_payment_succeeded';$event['data']['object']['payment_status']='paid';apply_event($db,$event);
check(row($db,'SELECT state FROM orders WHERE id=?',[$o['id']])['state']==='review','late success after release needs review');
$r=req([$v,$v],'c');$o=order($db,$r['requestId'],quote($r,$p));
check(available($db,$v)===1,'duplicate variant within pack held twice');
$event['id']='evt_paid';$event['type']='checkout.session.completed';
$event['data']['object']['id']='cs_test_second';$event['data']['object']['client_reference_id']=$event['data']['object']['metadata']['orderId']=$o['id'];
apply_event($db,$event);
check(row($db,'SELECT state FROM orders WHERE id=?',[$o['id']])['state']==='paid','verified settled payment persisted');
$event['id']='evt_outoforder';$event['type']='checkout.session.expired';apply_event($db,$event);
check(available($db,$v)===1,'late expiration cannot release paid stock');
echo "PASS: all pack prices, 12 variants, shipping, inactive promo, server-only amounts, idempotent reservation, shortage rollback, Stripe payload, signed webhook, amount/mode checks and payment lifecycle. No network.\n";
