<?php
declare(strict_types=1);
require_once __DIR__.'/_live.php';
require_once __DIR__.'/_inpost.php';
final class StoreError extends RuntimeException {
    function __construct(public string $kind, public int $status, string $msg) { parent::__construct($msg); }
}
function problem(string $kind,int $status,string $msg): never { throw new StoreError($kind,$status,$msg); }
function unavailable(): never { problem('UNAVAILABLE',503,'Płatności nie są teraz dostępne.'); }
function headers_private(): void { header('Cache-Control: no-store'); header('X-Robots-Tag: noindex, nofollow'); header('X-Content-Type-Options: nosniff'); }
function send_json(array $data,int $status=200): never { headers_private(); header('Content-Type: application/json; charset=utf-8'); http_response_code($status); echo json_encode($data,JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR); exit; }
function endpoint(callable $fn): never {
    try { send_json($fn()); }
    catch(StoreError $e) { send_json(['error'=>$e->kind,'message'=>$e->getMessage()],$e->status); }
    catch(Throwable $e) { error_log('WINTER26 checkout: '.get_class($e)); send_json(['error'=>'UNAVAILABLE','message'=>'Usługa płatności jest niedostępna.'],503); }
}
function method(string $m): void { if(($_SERVER['REQUEST_METHOD']??'')!==$m){header('Allow: '.$m);problem('METHOD',405,'Nieobsługiwana metoda.');} }
function under(string $file,string $root): bool {
    if(DIRECTORY_SEPARATOR==='\\'){
        $file=strtolower(str_replace('\\','/',$file));
        $root=strtolower(str_replace('\\','/',$root));
    }
    return $file===$root || str_starts_with($file,rtrim($root,'/').'/');
}
function config_path(string $mode,string $root): string {
    $env=$mode==='live'?'PF_LIVE_CONFIG':'PF_TEST_CONFIG';
    // LH without environment-variable support: sibling directory outside this site's WWW root.
    return getenv($env)?:dirname($root).'/.pf-private/winter26-'.$mode.'.json';
}
function configuration(): array {
    $root=realpath($_SERVER['DOCUMENT_ROOT']??''); $path=realpath(config_path('test',$root?:__DIR__));
    if(!$root || !$path || under($path,$root) || !is_readable($path)) unavailable();
    $cfg=json_decode(file_get_contents($path),true,512,JSON_THROW_ON_ERROR);
    if(!is_array($cfg)) unavailable();
    $origin=$cfg['origin']??'';
    if(!is_string($origin) || !preg_match('#^https://[a-z0-9.-]+$#D',$origin) ||
        !str_contains(substr($origin,8),'.') || in_array(substr($origin,8),['pracowniaform.com','www.pracowniaform.com'],true) ||
        $origin!=='https://'.strtolower($_SERVER['HTTP_HOST']??'') || ($_SERVER['HTTPS']??'off')==='off') unavailable();
    if(!preg_match('/^sk_test_[A-Za-z0-9]+$/D',$cfg['stripe_key']??'') || !preg_match('/^whsec_[A-Za-z0-9]+$/D',$cfg['webhook_secret']??'') ||
       !preg_match('/^[a-f0-9]{64}$/D',$cfg['login_sha256']??'')) unavailable();
    $dir=realpath(dirname($cfg['db_file']??''));
    if(!$dir || under($dir,$root) || !is_writable($dir) || !str_starts_with($cfg['db_file'],'/') ||
       is_link($cfg['db_file']) || !extension_loaded('pdo_sqlite') || !extension_loaded('curl')) unavailable();
    $cfg['mode']='test';return $cfg;
}
function browser_session(): void {
    session_name('pf_winter_sandbox'); ini_set('session.use_strict_mode','1'); ini_set('session.use_only_cookies','1');
    session_set_cookie_params(['lifetime'=>0,'path'=>'/api/','secure'=>true,'httponly'=>true,'samesite'=>'Strict']);
    if(!session_start()) unavailable();
}
function is_tester(): bool { browser_session(); $ok=($_SESSION['tester_until']??0)>time(); session_write_close(); return $ok; }
function require_origin(array $cfg): void {
    if(($_SERVER['HTTP_ORIGIN']??'')!==$cfg['origin']) problem('ORIGIN',403,'Nieprawidłowe źródło żądania.');
}
function body(int $max): string {
    $raw=file_get_contents('php://input',false,null,0,$max+1);
    if($raw===false || strlen($raw)>$max) problem('BAD_BODY',400,'Nieprawidłowe żądanie.');
    return $raw;
}
function policy(): array {
    $path=dirname(__DIR__).'/data/winter26-pricing-pl.json';
    if(!is_readable($path)) unavailable();
    return json_decode(file_get_contents($path),true,512,JSON_THROW_ON_ERROR);
}
function valid_key(string $key,array $p): bool {
    $pair=explode(':',$key);
    return count($pair)===2 && in_array($pair[0],$p['eligibleModelIds'],true)
      && in_array($pair[1],['dual','red-matte','white','marble'],true);
}
function quote(array $in,array $p,?string $version=null): array {
    if($version!==null && (($in['termsAccepted']??null)!==true || !hash_equals($version,is_string($in['approvalVersion']??null)?$in['approvalVersion']:'')))problem('TERMS',422,'Odśwież zamówienie i zaakceptuj aktualne warunki.');
    if(array_diff(array_keys($in),array_merge(['selections','packs','code','requestId','delivery_method','pickup_point'],$version===null?[]:['termsAccepted','approvalVersion'])) || !is_string($in['requestId']??null) ||
       !preg_match('/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/iD',$in['requestId'])) problem('BAD_REQUEST',422,'Nieprawidłowe dane zamówienia.');
    if(!is_string($in['code']??'') || trim($in['code']??'')!=='') problem('NO_PROMOTION',422,'Nie ma teraz aktywnej promocji.');
    if(array_key_exists('selections',$in)===array_key_exists('packs',$in))problem('BAD_REQUEST',422,'Wybierz kompozycję albo listę kompozycji.');
    $packs=array_key_exists('packs',$in)?$in['packs']:[$in['selections']];
    if(!is_array($packs)||!array_is_list($packs)||count($packs)<1||count($packs)>10)problem('SIZE',422,'Koszyk obsługuje od 1 do 10 kompozycji.');
    $items=[];$ordered=[];$packRows=[];$count=0;$subtotal=0;
    foreach($packs as $slots){
        if(!is_array($slots)||!array_is_list($slots)||!in_array(count($slots),[1,2,4,6,8],true))problem('SIZE',422,'Wybierz 1, 2, 4, 6 albo 8 ozdób w każdej kompozycji.');
        $members=[];$groups=[];
        foreach($slots as $slot){
            if(!is_array($slot)||count($slot)!==2||!is_string($slot['modelId']??null)||!is_string($slot['colorId']??null))problem('VARIANT',422,'Wybierz wzór i kolor każdej ozdoby.');
            $key=$slot['modelId'].':'.$slot['colorId'];if(!valid_key($key,$p))problem('VARIANT',422,'Ten wariant nie jest dostępny w cenniku.');
            $items[$key]=($items[$key]??0)+1;$groups[$key]=($groups[$key]??0)+1;$ordered[]=$key;$members[]=$key;
        }
        $n=count($slots);$price=$n===1?$p['singleGrossGrosz']:$p['setGrossGrosz'][$n];
        if(!is_int($price)||$price<=0||$p['currency']!=='PLN')unavailable();
        $packRows[]=['size'=>$n,'members'=>$members,'items'=>$groups,'merchandise'=>$price];$count+=$n;$subtotal+=$price;
    }
    $method=array_key_exists('delivery_method',$in)?$in['delivery_method']:'courier';
    if(!in_array($method,['locker','courier'],true))problem('DELIVERY_METHOD',422,'Wybierz sposób dostawy.');
    if($method==='courier' && array_key_exists('pickup_point',$in))problem('DELIVERY_METHOD',422,'Przy dostawie kurierem nie podawaj punktu odbioru.');
    $id=$method==='locker'?point_id($in['pickup_point']??null):null;
    $delivery=$count>=$p['freeCourierFromOrnaments']?0:delivery_rates($p)[$method];
    return ['size'=>$count,'packs'=>$packRows,'items'=>$items,'ordered'=>$ordered,'merchandise'=>$subtotal,'delivery_method'=>$method,'pickup_point'=>$id,'shipping'=>$delivery,'total'=>$subtotal+$delivery,'acceptedRelease'=>$version];
}
function database(array $cfg): PDO {
    $db=new PDO('sqlite:'.$cfg['db_file'],null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC]);
    $db->exec('PRAGMA busy_timeout=5000');
    $db->exec("CREATE TABLE IF NOT EXISTS stock (sku TEXT PRIMARY KEY, n INTEGER NOT NULL CHECK(n>=0));
      CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, req TEXT UNIQUE NOT NULL, quote TEXT NOT NULL,
      created INTEGER NOT NULL, state TEXT NOT NULL, sid TEXT UNIQUE, url TEXT, pi TEXT, owner TEXT);
      CREATE TABLE IF NOT EXISTS store_meta(name TEXT PRIMARY KEY,value TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS attempts(identity TEXT NOT NULL,bucket INTEGER NOT NULL,n INTEGER NOT NULL,PRIMARY KEY(identity,bucket));
      CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY)");
    return $db;
}
function tx(PDO $db,callable $fn): mixed {
    $db->exec('BEGIN IMMEDIATE'); try{$r=$fn();$db->exec('COMMIT');return $r;}catch(Throwable $e){$db->exec('ROLLBACK'); throw $e;}
}
function row(PDO $db,string $sql,array $args): ?array {$s=$db->prepare($sql);$s->execute($args);return $s->fetch()?:null;}
function stock(PDO $db): object { $a=[]; foreach($db->query('SELECT sku,n FROM stock') as $r) $a[$r['sku']]=(int)$r['n'];return (object)$a; }
function existing_order(array $old,array $q,?string $owner): array {
    $stored=json_decode($old['quote'],true,512,JSON_THROW_ON_ERROR);
    if($old['owner']!==$owner || $stored['acceptedRelease']!==$q['acceptedRelease'] ||
       array_column($stored['packs'],'members')!==array_column($q['packs'],'members') ||
       ($stored['delivery_method']??'courier')!==$q['delivery_method'] || ($stored['pickup_point']??null)!==$q['pickup_point'])
        problem('REQUEST_CONFLICT',409,'Identyfikator już oznacza inne zamówienie lub dostawę.');
    if($old['state']!=='reserved')problem('FINISHED',409,'Ta próba została zakończona.');
    return $old;
}
function order(PDO $db,string $req,array $q,?string $owner=null,?callable $resolve=null): array {
    if($old=row($db,'SELECT * FROM orders WHERE req=?',[$req]))return existing_order($old,$q,$owner);
    if($q['delivery_method']==='locker'){
        if($resolve===null)point_unavailable();
        // Do not wait for an external service under a write lock or reserve stock before validation.
        $point=$resolve($q['pickup_point']);
        if(($point['id']??null)!==$q['pickup_point'] || !is_string($point['address']??null) || $point['address']==='')point_unavailable();
        $q['pickup_address']=$point['address'];
    }
    return tx($db,function() use($db,$req,$q,$owner){
        if($old=row($db,'SELECT * FROM orders WHERE req=?',[$req]))return existing_order($old,$q,$owner);
        foreach($q['items'] as $k=>$n){ $s=$db->prepare('UPDATE stock SET n=n-? WHERE sku=? AND n>=?'); $s->execute([$n,$k,$n]);
          if($s->rowCount()!==1) problem('STOCK',409,'Brakuje wybranego wariantu. Odśwież dostępność.'); }
        $id='w26_'.bin2hex(random_bytes(12));$now=time();
        $db->prepare("INSERT INTO orders(id,req,quote,created,owner,state) VALUES(?,?,?,?,?,'reserved')")->execute([$id,$req,json_encode($q,JSON_THROW_ON_ERROR),$now,$owner]);
        return row($db,'SELECT * FROM orders WHERE id=?',[$id]);
    });
}
function checkout_params(array $o,string $origin,bool $live=false): array {
    $q=json_decode($o['quote'],true);$prefix=$live?'':'TEST • ';
    $names=['full-soft'=>'VASE','knitted-star'=>'Gwiazda','knitted-medallion'=>'Medalion'];$colors=['dual'=>'dual','red-matte'=>'czerwony matowy','white'=>'biały','marble'=>'marble'];
    $locker=($q['delivery_method']??'courier')==='locker';
    $meta=['orderId'=>$o['id'],'delivery_method'=>$locker?'locker':'courier'];
    if($locker)$meta+=['pickup_point'=>$q['pickup_point'],'pickup_address'=>$q['pickup_address']];
    $label=$locker?'Paczkomat® InPost '.$q['pickup_point']:'Kurier InPost';
    $lines=[];
    foreach($q['packs'] as $pack){
        $labels=[];foreach($pack['items'] as $sku=>$n){[$m,$c]=explode(':',$sku);$labels[]=$n.' × '.$names[$m].' ('.$colors[$c].')';}
        $lines[]=['quantity'=>1,'price_data'=>['currency'=>'pln','unit_amount'=>$pack['merchandise'],'product_data'=>[
            'description'=>implode('; ',$labels),'name'=>$prefix.'WINTER 26 • '.($pack['size']===1?'1 ozdoba':'zestaw '.$pack['size'].' ozdób').($q['shipping']===0?' • '.$label.' w cenie':'')]]];
    }
    if($q['shipping']>0)$lines[]=['quantity'=>1,'price_data'=>['currency'=>'pln','unit_amount'=>$q['shipping'],'product_data'=>['name'=>$prefix.$label]]];
    $details=$locker?['name_collection'=>['individual'=>['enabled'=>'true','optional'=>'false']]]:
        ['shipping_address_collection'=>['allowed_countries'=>['PL']]];
    if($locker)$details['custom_text']=['submit'=>['message'=>$label.' — '.$q['pickup_address']]];
    return $details+['mode'=>'payment','client_reference_id'=>$o['id'],'metadata'=>$meta,
    'payment_intent_data'=>['metadata'=>$meta],'payment_method_types'=>['card','blik'],
    'phone_number_collection'=>['enabled'=>'true'],
    'line_items'=>$lines,
    'success_url'=>$origin.'/api/result.php','cancel_url'=>$origin.'/api/result.php?cancel=1',
    'expires_at'=>(int)$o['created']+3600];
}
function stripe_session(array $cfg,array $o): array {
    if(time()>=(int)$o['created']+3600) problem('RECONCILE',409,'Sesja wygasła. Sprawdź stan próby w Sandbox.');
    if($o['url'])return ['url'=>$o['url'],'id'=>$o['sid']];
    $curl=curl_init('https://api.stripe.com/v1/checkout/sessions');
    curl_setopt_array($curl,[CURLOPT_POST=>true,CURLOPT_RETURNTRANSFER=>true,CURLOPT_CONNECTTIMEOUT=>4,CURLOPT_TIMEOUT=>14,
       CURLOPT_POSTFIELDS=>http_build_query(checkout_params($o,$cfg['origin'],($cfg['mode']??'test')==='live'),'','&',PHP_QUERY_RFC3986),
       CURLOPT_HTTPHEADER=>['Stripe-Version: 2026-02-25.clover','Authorization: Bearer '.$cfg['stripe_key'],'Idempotency-Key: '.$o['id'],'Content-Type: application/x-www-form-urlencoded']]);
    $raw=curl_exec($curl); $status=curl_getinfo($curl,CURLINFO_RESPONSE_CODE);
    $s=is_string($raw)?json_decode($raw,true):null;
    if($status!==200 || !is_array($s)) {error_log('WINTER26 Stripe HTTP '.(int)$status.' order '.$o['id']); problem('STRIPE_UNAVAILABLE',503,'Nie utworzono potwierdzonej sesji. Ponów tę samą próbę.');}
    $q=json_decode($o['quote'],true);
    $live=($cfg['mode']??'test')==='live';
    if(($s['livemode']??null)!==$live || !preg_match($live?'/^cs_live_[A-Za-z0-9]+$/D':'/^cs_test_[A-Za-z0-9]+$/D',$s['id']??'') ||
        !str_starts_with($s['url']??'','https://checkout.stripe.com/') || ($s['client_reference_id']??null)!==$o['id'] ||
        ($s['amount_total']??null)!==$q['total'] || ($s['currency']??'')!=='pln') unavailable();
    return $s;
}
function bind_session(PDO $db,array $o,array $s): void {
    $q=$db->prepare("UPDATE orders SET sid=?,url=? WHERE id=? AND (sid IS NULL OR sid=?) AND state='reserved'");
    $q->execute([$s['id'],$s['url'],$o['id'],$s['id']]); if(!$q->rowCount()) problem('FINISHED',409,'Ta próba została zakończona.');
}
function verify_signature(string $raw,string $header,string $secret,int $now): bool {
    $v1=[];$ts=null;foreach(explode(',',$header)as $part){$pair=explode('=',trim($part),2); if(count($pair)!==2)continue;
        if($pair[0]==='t' && preg_match('/^[0-9]+$/D',$pair[1]))$ts=$pair[1]; if($pair[0]==='v1')$v1[]=$pair[1];}
    if($ts===null || abs($now-(int)$ts)>300)return false;
    $want=hash_hmac('sha256',$ts.'.'.$raw,$secret);foreach($v1 as $sig){if(hash_equals($want,$sig))return true;}return false;
}
function apply_event(PDO $db,array $e,bool $live=false): void {
    $kind=$e['type']??'';if(!in_array($kind,['checkout.session.completed','checkout.session.expired','checkout.session.async_payment_succeeded','checkout.session.async_payment_failed'],true))return;
    $s=$e['data']['object']??[];if(($e['livemode']??null)!==$live||($s['livemode']??null)!==$live||!preg_match('/^evt_[A-Za-z0-9]+$/D',$e['id']??'')||
       ($s['object']??'')!=='checkout.session')problem('EVENT',400,'Nieprawidłowe zdarzenie.');
    $id=$s['client_reference_id']??''; if(!is_string($id)||!str_starts_with($id,'w26_'))return; // Other Sandbox integrations may share this account.
    tx($db,function() use($db,$e,$s,$kind,$id,$live){
        if(row($db,'SELECT id FROM events WHERE id=?',[$e['id']]))return;
        $o=row($db,'SELECT * FROM orders WHERE id=?',[$id]);if(!$o)problem('EVENT_ORDER',409,'Nie znaleziono zamówienia.');
        $q=json_decode($o['quote'],true);
        if((($q['delivery_method']??'courier')==='locker' &&
            (($s['metadata']['delivery_method']??null)!=='locker'||($s['metadata']['pickup_point']??null)!==$q['pickup_point'])) ||
           ($s['metadata']['orderId']??'')!==$id || ($s['mode']??'')!=='payment' || ($s['amount_total']??null)!==$q['total'] ||
           ($s['currency']??'')!=='pln' || !preg_match($live?'/^cs_live_[A-Za-z0-9]+$/D':'/^cs_test_[A-Za-z0-9]+$/D',$s['id']??'') ||
           ($o['sid']!==null && $o['sid']!==$s['id']))problem('EVENT_MISMATCH',409,'Niezgodność danych płatności.');
        $state=$o['state'];$next=$state;
        if(in_array($kind,['checkout.session.completed','checkout.session.async_payment_succeeded'],true) && ($s['payment_status']??'')==='paid'){
            if(in_array($state,['released','review'],true)) $next='review'; else $next='paid';
        }elseif($kind==='checkout.session.completed' && $state==='reserved')$next='pending';
        elseif(in_array($kind,['checkout.session.expired','checkout.session.async_payment_failed'],true) && in_array($state,['pending','reserved'],true)){
            foreach($q['items'] as $k=>$n)$db->prepare('UPDATE stock SET n=n+? WHERE sku=?')->execute([$n,$k]);$next='released';
        }
        $db->prepare('UPDATE orders SET state=?, sid=?, pi=COALESCE(?,pi) WHERE id=?')->execute([$next,$s['id'],$s['payment_intent']??null,$id]);
        $db->prepare('INSERT INTO events(id) VALUES(?)')->execute([$e['id']]);
    });
}
