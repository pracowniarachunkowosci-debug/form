<?php
declare(strict_types=1);
// Explicit opt-in integration probe. NOT part of the webroot/release or offline tests.
// Real Stripe Sandbox, local disposable SQLite; never evidence of LH deployment.
require_once __DIR__.'/../api/_common.php';
function probe_config(): array {
    $path=realpath(getenv('PF_STRIPE_PROBE_CONFIG')?:'');
    if(!$path || under($path,realpath(dirname(__DIR__)))) throw new RuntimeException('Private probe config required.');
    $cfg=json_decode(file_get_contents($path),true,512,JSON_THROW_ON_ERROR);
    if(($cfg['mode']??'')!=='test' || !preg_match('/^sk_test_[A-Za-z0-9]+$/D',$cfg['stripe_key']??'') ||
        ($cfg['origin']??'')!=='http://127.0.0.1:8788' || ($cfg['purpose']??'')!=='local-stripe-sandbox-probe' ||
        realpath(dirname($cfg['db_file']??''))!==dirname($path) || basename($cfg['db_file'])!=='stripe-probe.sqlite' ||
        is_link($cfg['db_file']) || (file_exists($cfg['db_file']) && realpath($cfg['db_file'])!==dirname($path).DIRECTORY_SEPARATOR.'stripe-probe.sqlite') ||
        realpath(dirname($cfg['signing_secret_file']??''))!==dirname($path) || basename($cfg['signing_secret_file'])!=='stripe-cli-whsec.txt' || is_link($cfg['signing_secret_file']))
        throw new RuntimeException('Isolated Sandbox probe required.');
    return $cfg;
}
function probe_get(array $cfg,string $sid): array {
    if(!preg_match('/^cs_test_[A-Za-z0-9]+$/D',$sid))throw new RuntimeException('Test session required.');
    $c=curl_init('https://api.stripe.com/v1/checkout/sessions/'.$sid.'?expand[]=payment_intent.payment_method');
    curl_setopt_array($c,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_CONNECTTIMEOUT=>5,CURLOPT_TIMEOUT=>20,
        CURLOPT_HTTPHEADER=>['Authorization: Bearer '.$cfg['stripe_key'],'Stripe-Version: 2026-02-25.clover']]);
    $raw=curl_exec($c);$code=curl_getinfo($c,CURLINFO_RESPONSE_CODE);
    if($code!==200)throw new RuntimeException('Stripe GET failed: '.$code);
    $s=json_decode($raw,true,512,JSON_THROW_ON_ERROR);
    if(($s['livemode']??null)!==false)throw new RuntimeException('Expected livemode=false');
    return $s;
}
$cfg=probe_config();$action=$argv[1]??'';
if(file_exists($cfg['db_file'])){
    // Check ownership before database() can execute any schema statement.
    $db=new PDO('sqlite:'.$cfg['db_file'],null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC]);
    if(!ledger_ok($db,'test') || (row($db,'SELECT value FROM store_meta WHERE name=?',['purpose'])['value']??null)!=='local-stripe-sandbox-probe')
        throw new RuntimeException('Not an owned Sandbox probe ledger');
}else{
    if(PHP_SAPI!=='cli'||$action!=='create')throw new RuntimeException('Create the explicit local probe first');
    $file=fopen($cfg['db_file'],'x');if(!$file)throw new RuntimeException('New database required');fclose($file);
    $db=database($cfg);tx($db,function()use($db){
        $db->exec("INSERT INTO store_meta VALUES ('mode','test'),('purpose','local-stripe-sandbox-probe')");
        foreach(['full-soft:marble','knitted-star:red-matte','knitted-medallion:white']as $sku)$db->prepare('INSERT INTO stock VALUES (?,20)')->execute([$sku]);
    });
}
if(PHP_SAPI==='cli-server'){
    if(!in_array($_SERVER['REMOTE_ADDR']??'',['127.0.0.1','::1'],true)||($_SERVER['HTTP_HOST']??'')!=='127.0.0.1:8788'){http_response_code(403);exit;}
    headers_private();
    $route=parse_url($_SERVER['REQUEST_URI'],PHP_URL_PATH);
    if($route==='/webhook'){
        endpoint(function()use($cfg,$db){
            method('POST');$raw=body(256*1024);
            $secret=is_file($cfg['signing_secret_file'])?trim(file_get_contents($cfg['signing_secret_file'])):'';
            if(!preg_match('/^whsec_[A-Za-z0-9]+$/D',$secret)||!verify_signature($raw,$_SERVER['HTTP_STRIPE_SIGNATURE']??'',$secret,time()))
                problem('SIGNATURE',400,'Invalid signature');
            $event=json_decode($raw,true,512,JSON_THROW_ON_ERROR);apply_event($db,$event,false);
            // Replay immediately to verify the actual signed event cannot mutate stock twice.
            $before=json_encode(stock($db));apply_event($db,$event,false);
            if($before!==json_encode(stock($db)))throw new RuntimeException('Replay changed stock');
            file_put_contents(dirname($cfg['db_file']).'/stripe-events.jsonl',json_encode([
                'id'=>$event['id'],'type'=>$event['type'],'livemode'=>$event['livemode'],
                'signature_verified'=>true,'replay_stock_unchanged'=>true])."\n",FILE_APPEND|LOCK_EX);
            return ['received'=>true];
        });
    }
    if($route==='/api/result.php'){
        header('Content-Type: text/html; charset=utf-8');
        echo '<!doctype html><html lang="pl"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Stripe Sandbox — lokalny test</title><h1>Powrót ze Stripe Sandbox</h1><p>Test lokalny. Bez płatności rzeczywistej i bez wdrożenia LH.</p><p>Status pochodzi z podpisanego webhooka:</p><ul>';
        foreach($db->query('SELECT id,state FROM orders')as $o)echo '<li>'.htmlspecialchars($o['id'].' — '.$o['state']).'</li>';
        echo '</ul>';exit;
    }
    http_response_code(404);exit;
}
if(PHP_SAPI!=='cli')exit;
if($action==='create'){
    $scenario=$argv[2]??'';
    if(!in_array($scenario,['card-courier','blik-mixed-locker'],true))throw new RuntimeException('Unknown scenario');
    if(!ledger_ok($db,'test'))throw new RuntimeException('Not test ledger');
    $request='12345678-1234-4123-8123-'.bin2hex(random_bytes(6));
    $v=['modelId'=>'full-soft','colorId'=>'marble'];$s=['modelId'=>'knitted-star','colorId'=>'red-matte'];$m=['modelId'=>'knitted-medallion','colorId'=>'white'];
    $input=['requestId'=>$request,'code'=>''];
    if($scenario==='card-courier')$input+=['selections'=>[$v],'delivery_method'=>'courier'];
    else $input+=['packs'=>[[$s,$m],[$v,$s,$m,$v]],'delivery_method'=>'locker','pickup_point'=>'TEST01A'];
    if(isset($argv[3])){
        $prior=row($db,'SELECT * FROM orders WHERE id=?',[$argv[3]]);
        if(!$prior || $prior['state']!=='reserved')throw new RuntimeException('Only own pending probe may be resumed');
        $input['requestId']=$request=$prior['req'];
    }
    $q=quote($input,policy());
    // Synthetic test point only, independent of real InPost network services.
    $o=order($db,$request,$q,null,fn($id)=>['id'=>$id,'address'=>'TEST / MOCK — Punkt testowy, ulica Testowa 1, 00-000 Miasto Testowe']);
    $before=json_encode(stock($db));$again=order($db,$request,$q,null,fn()=>throw new RuntimeException('Retry must reuse persisted point'));
    if($again['id']!==$o['id'] || $before!==json_encode(stock($db)))throw new RuntimeException('Reservation idempotency failed');
    $session=stripe_session($cfg,$o);bind_session($db,$o,$session);
    // Force the same actual API request also when resuming a cached order.
    $retryOrder=$o;$retryOrder['url']=null;
    $repeat=stripe_session($cfg,$retryOrder);
    if($session['id']!==$repeat['id'])throw new RuntimeException('Stripe idempotency failed');
    $session=probe_get($cfg,$session['id']);
    echo json_encode(['scenario'=>$scenario,'orderId'=>$o['id'],'sessionId'=>$session['id'],
        'url'=>$session['url'],'livemode'=>$session['livemode'],'currency'=>$session['currency'],
        'amount_total'=>$session['amount_total'],'shipping'=>$q['shipping'],'reservation_and_session_idempotency'=>true],JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT)."\n";
}elseif($action==='inspect'){
    $rows=[];
    foreach($db->query('SELECT * FROM orders')as $o){
        $q=json_decode($o['quote'],true);$s=$o['sid']?probe_get($cfg,$o['sid']):null;
        $rows[]=['orderId'=>$o['id'],'sessionId'=>$o['sid'],'state'=>$o['state'],'items'=>$q['items'],
            'totalGrosz'=>$q['total'],'shippingGrosz'=>$q['shipping'],'method'=>$q['delivery_method'],
            'pickup_point'=>$q['pickup_point'],'pickup_address'=>$q['pickup_address']??null,
            'stripe_payment_status'=>$s['payment_status']??null,'livemode'=>$s['livemode']??null,
            'payment_method'=>$s['payment_intent']['payment_method']['type']??null,
            'shipping_address_present'=>isset($s['collected_information']['shipping_details']['address'])||isset($s['shipping_details']['address'])];
    }
    echo json_encode(['environment'=>'LOCAL PHP + REAL STRIPE SANDBOX; NOT LH','orders'=>$rows,'stock'=>stock($db),
        'recorded_events'=>(int)$db->query('SELECT count(*) FROM events')->fetchColumn()],JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE)."\n";
}else{fwrite(STDERR,"Usage: php tests/stripe-sandbox-probe.php create card-courier|blik-mixed-locker | inspect\n");exit(2);}
