<?php
declare(strict_types=1);
// Synthetic local acceptance only: never calls Stripe, never uses any real key.
require_once __DIR__.'/../api/_common.php';
function ensure(bool $ok,string $msg):void {if(!$ok)throw new RuntimeException($msg);}
function rejected(callable $f,string $kind='UNAVAILABLE'):void {try{$f();}catch(StoreError $e){ensure($e->kind===$kind,$e->kind);return;}throw new RuntimeException('expected failure: '.$kind);}
$tmp=sys_get_temp_dir().'/pf-gate-'.bin2hex(random_bytes(8));$root=$tmp.'/www';$private=$tmp.'/.pf-private';mkdir($root.'/data',0700,true);mkdir($root.'/api',0700);mkdir($private,0700);
try{
  $_SERVER['DOCUMENT_ROOT']=$root;$_SERVER['HTTPS']='on';$_SERVER['HTTP_HOST']='pracowniaform.com';
  putenv('PF_LIVE_CONFIG');$file=$private.'/winter26-live.json';$path=$private.'/stock.sqlite';
  $db=database(['db_file'=>$path]);ensure(!ledger_ok($db,'live'),'unknown ledger must be closed');
  $db->exec("INSERT INTO store_meta VALUES('mode','test')");ensure(!ledger_ok($db,'live'),'test stock refused for real orders');
  $db->exec("UPDATE store_meta SET value='live' WHERE name='mode'");
  $c=['origin'=>'https://pracowniaform.com','mode'=>'live','smallOrderCourierGrosz'=>1500,'approvalVersion'=>'unused','db_file'=>$path,
    'stripe_key'=>'sk_live_'.str_repeat('x',28),'webhook_secret'=>'whsec_'.str_repeat('x',24),'abuse_hmac'=>bin2hex(random_bytes(32)),
    'termsUrl'=>'/terms.html','returnsUrl'=>'/returns.html','privacyUrl'=>'/privacy.html','dispatchNotice'=>'Treść testu terminów','sellerName'=>'Syntetyczny sprzedawca',
    'sellerContact'=>'Kontakt syntetyczny','returnsSummary'=>'Opis próbny procedury zwrotów','complaintsSummary'=>'Opis próbny procedury reklamacji'];
  $c['productInfo']=[];$c['approvedVariants']=[];
  foreach(policy()['eligibleModelIds']as $m){
      $c['productInfo'][$m]=['name'=>$m,'material'=>'Materiał testowy','dimensions'=>'100 mm','producer'=>'Producent testowy','address'=>'Adres testowy nr trzy',
        'email'=>'tester@produkt.invalid','warnings'=>'Opis treści testowych','listingUrl'=>'/model.html'];
      foreach(['dual','red-matte','white','marble']as $color)$c['approvedVariants'][]=$m.':'.$color;
  }
  $c['operationalChecks']=array_fill_keys(['sandboxCardAndBlikPassed','stockAndDispatchVerified','legalAndProductListingsReviewed','durableOrderConfirmationReady','refundsAndFulfilmentReady'],true);
  file_put_contents($file,json_encode($c));rejected(fn()=>live_config());
  foreach(['terms.html','returns.html','privacy.html','model.html','winter-zestaw-4.html','winter-config.js','api/checkout.php']as $p)file_put_contents($root.'/'.$p,str_repeat("fixture\n",22));
  file_put_contents($root.'/data/winter26-pricing-pl.json',json_encode(policy()));$release=array_fill_keys(['salesApproved','legalApproved','sellerApproved','sandboxPassed'],true);
  file_put_contents($root.'/data/winter26-products.json',json_encode(['release'=>array_merge($release,['salesApproved'=>false])]));
  rejected(fn()=>live_approval($c,$root));
  file_put_contents($root.'/data/winter26-products.json',json_encode(['release'=>$release]));rejected(fn()=>live_config()); // no sign-off
  $c['approvedReleaseSha256']=live_approval($c,$root);file_put_contents($file,json_encode($c));
  $cfg=live_config();ensure($cfg['mode']==='live' && ledger_ok($db,'live'),'explicit sign-off only');
  $bad=$c;$bad['stripe_key']='sk_test_'.str_repeat('x',25);file_put_contents($file,json_encode($bad));rejected(fn()=>live_config());
  file_put_contents($file,json_encode($c));file_put_contents($root.'/terms.html','changed fixture',FILE_APPEND);
  rejected(fn()=>live_config());ensure(live_config(true)['mode']==='live','pending webhook must survive new release');
  $make=['requestId'=>'12345678-1234-4321-8123-123456789abc','code'=>'','selections'=>array_fill(0,6,['modelId'=>'full-soft','colorId'=>'marble'])];
  $ver=$cfg['approvalVersion'];rejected(fn()=>quote($make,policy(),$ver),'TERMS');
  $q=quote($make+['approvalVersion'=>$ver,'termsAccepted'=>true],policy(),$ver);ensure($q['total']===22000 && $q['shipping']===0,'6 at full price with courier');
  $db->exec("INSERT INTO stock VALUES('full-soft:marble',6)");$owner='owner-key';
  rate($db,$cfg,$owner,$make['requestId']);$o=order($db,$make['requestId'],$q,$owner);
  $params=checkout_params($o,$c['origin'],true);ensure(count($params['line_items'])===1 && !str_contains($params['line_items'][0]['price_data']['product_data']['name'],'TEST'),'live line item');
  rejected(fn()=>rate($db,$cfg,'other-owner',$make['requestId']),'REQUEST_CONFLICT');
  $evt=['id'=>'evt_six','type'=>'checkout.session.completed','livemode'=>true,'data'=>['object'=>['id'=>'cs_live_testfixture','livemode'=>true,
      'object'=>'checkout.session','mode'=>'payment','client_reference_id'=>$o['id'],'metadata'=>['orderId'=>$o['id']],'currency'=>'pln','amount_total'=>22000,'payment_status'=>'paid']]];
  rejected(fn()=>apply_event($db,$evt,false),'EVENT');apply_event($db,$evt,true);
  ensure(row($db,'SELECT state FROM orders WHERE id=?',[$o['id']])['state']==='paid','live event flow fixture');
  echo "PASS: real-mode gates deny missing legal docs, draft catalog, stale sign-off, mixed keys/stock and absent consent; signed-off synthetic six-item price/status verified offline. No Stripe call.\n";
}finally{
  $db=null;
  $it=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($tmp,FilesystemIterator::SKIP_DOTS),RecursiveIteratorIterator::CHILD_FIRST);
  foreach($it as $v)$v->isDir()?rmdir($v->getPathname()):unlink($v->getPathname());rmdir($tmp);
}
