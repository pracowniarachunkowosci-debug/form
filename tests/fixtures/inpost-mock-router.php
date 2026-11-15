<?php
declare(strict_types=1);
// Never a hosted endpoint: this file only runs as the explicit CLI demo router.
if(PHP_SAPI!=='cli-server'||getenv('PF_INPOST_MOCK_DEMO')!=='1'||
   !in_array($_SERVER['REMOTE_ADDR']??'',['127.0.0.1','::1'],true)||
   !in_array($_SERVER['HTTP_HOST']??'',['127.0.0.1:8787','localhost:8787'],true)){
    http_response_code(404);exit;
}
require_once __DIR__.'/../../api/_common.php';
headers_private();
header("Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-src 'none'; form-action 'none'; object-src 'none'; base-uri 'none'");
$repo=dirname(__DIR__,2);$path=rawurldecode(parse_url($_SERVER['REQUEST_URI'],PHP_URL_PATH)?:'/');
if($path==='/'){header('Location: /winter-zestaw-4.html?size=1&model=full-soft&color=marble#kompozycja',true,302);exit;}
if(in_array($path,['/api/status.php','/api/pickup-point.php','/api/checkout.php'],true))endpoint(function()use($repo,$path){
    $dbPath=realpath(getenv('PF_INPOST_MOCK_DEMO_DB')?:'');$demoRoot=realpath($repo.'/.artifacts/inpost-mock-demo');
    if(!$dbPath||!$demoRoot||!under($dbPath,$demoRoot)||!is_file($dbPath))unavailable();
    $db=database(['db_file'=>$dbPath]);
    if(!ledger_ok($db,'test')||(row($db,'SELECT value FROM store_meta WHERE name=?',['demo'])['value']??null)!=='points-mock-only')unavailable();
    $cfg=['mode'=>'test','inpost_points_mock'=>true];
    if($path==='/api/status.php'){
        method('GET');$p=policy();$rates=delivery_rates($p);
        return inpost_settings($cfg)+['mode'=>'test','local_mock_demo'=>true,'available'=>true,'currency'=>$p['currency'],
            'smallOrderCourierGrosz'=>$rates['courier'],'locker_amount_grosze'=>$rates['locker'],
            'freeCourierFromOrnaments'=>$p['freeCourierFromOrnaments'],'stock'=>stock($db)];
    }
    if($path==='/api/pickup-point.php'){method('GET');return lookup_point($cfg,point_id($_GET['id']??null));}
    method('POST');require_origin(['origin'=>'http://'.$_SERVER['HTTP_HOST']]);
    if(strtolower(trim(explode(';',$_SERVER['CONTENT_TYPE']??'')[0]))!=='application/json')problem('MEDIA',415,'JSON required');
    $input=json_decode(body(8192),true);if(!is_array($input))problem('BAD_BODY',400,'Invalid demo request');
    $quote=quote($input,policy());
    $order=order($db,$input['requestId'],$quote,null,fn($id)=>lookup_point($cfg,$id));
    return ['local_demo'=>true,'orderId'=>$order['id'],'totalGrosz'=>json_decode($order['quote'],true)['total']];
});
// Serve only the existing public UI assets. Never expose API source, tests, configs or SQLite.
$isAsset=str_starts_with($path,'/assets/');
$allowed=preg_match('#^/[a-z0-9-]+\.(?:html|css|js|svg)$#D',$path)||
    preg_match('#^/assets/[A-Za-z0-9_./-]+\.(?:avif|webp|jpg|jpeg|png|svg|woff2?)$#D',$path);
$file=$allowed?realpath($repo.$path):false;$allowedRoot=$isAsset?realpath($repo.'/assets'):$repo;
if(!$file||!is_file($file)||!$allowedRoot||!under($file,$allowedRoot)){
    http_response_code(404);exit;
}
// The built-in static handler drops router headers, so stream these allowlisted files here.
$types=['html'=>'text/html; charset=utf-8','css'=>'text/css; charset=utf-8','js'=>'application/javascript; charset=utf-8',
    'svg'=>'image/svg+xml','avif'=>'image/avif','webp'=>'image/webp','jpg'=>'image/jpeg','jpeg'=>'image/jpeg',
    'png'=>'image/png','woff'=>'font/woff','woff2'=>'font/woff2'];
header('Content-Type: '.$types[strtolower(pathinfo($file,PATHINFO_EXTENSION))]);
readfile($file);exit;
