<?php
declare(strict_types=1);
// This file contains validation only. No credentials, inventory or publisher approval are shipped.
function live_host(): bool {return in_array(strtolower($_SERVER['HTTP_HOST']??''),['pracowniaform.com','www.pracowniaform.com'],true);}
function approved_text(mixed $v,int $len=3): bool {
    return is_string($v) && strlen(trim($v))>=$len && strlen($v)<1800 && !preg_match('/TODO|TBD|example\.|placeholder|uzupełni|do potwierdzenia/i',$v);
}
function physical_page(string $root,mixed $url): string {
    if(!is_string($url)||!preg_match('#^/[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)*\.html$#D',$url)) unavailable();
    $f=realpath($root.$url);if(!$f||!under($f,$root)||!is_readable($f)||filesize($f)<100)unavailable();return $f;
}
function live_approval(array $c,string $root): string {
    $legal=[];foreach(['termsUrl','returnsUrl','privacyUrl']as $k)$legal[]=physical_page($root,$c[$k]??null);
    $listing=[];$models=policy()['eligibleModelIds'];
    foreach($models as $model){
        $row=$c['productInfo'][$model]??null;if(!is_array($row))unavailable();
        foreach(['name','material','dimensions','producer','address','email','warnings']as $field)if(!approved_text($row[$field]??null))unavailable();
        if(!filter_var($row['email'],FILTER_VALIDATE_EMAIL))unavailable();
        $listing[]=physical_page($root,$row['listingUrl']??null);
    }
    foreach(['dispatchNotice','sellerName','sellerContact','returnsSummary','complaintsSummary'] as $k)if(!approved_text($c[$k]??null))unavailable();
    $catalogPath=$root.'/data/winter26-products.json';$pricingPath=$root.'/data/winter26-pricing-pl.json';
    if(!is_readable($catalogPath)||!is_readable($pricingPath))unavailable();
    $catalog=json_decode(file_get_contents($catalogPath),true,512,JSON_THROW_ON_ERROR);$release=$catalog['release']??[];
    foreach(['salesApproved','sandboxPassed','sellerApproved','legalApproved'] as $k)if(($release[$k]??null)!==true)unavailable();
    $keys=[];foreach($models as $m)foreach(['dual','red-matte','white','marble']as $col)$keys[]=$m.':'.$col;
    $supplied=$c['approvedVariants']??null;if(!is_array($supplied)||count($supplied)!==count($keys)||array_diff($keys,$supplied))unavailable();
    foreach(['sandboxCardAndBlikPassed','stockAndDispatchVerified','legalAndProductListingsReviewed','durableOrderConfirmationReady','refundsAndFulfilmentReady']as $k)
        if(($c['operationalChecks'][$k]??null)!==true)unavailable();
    // Fingerprint the commercially meaningful public release, safety/legal content and customer-facing operator data. Never hash a secret into a browser field.
    $files=array_unique(array_merge($legal,$listing,[$catalogPath,$pricingPath,$root.'/winter-config.js',$root.'/winter-zestaw-4.html'],glob($root.'/api/*.php')?:[]));
    $hash=hash_init('sha256');foreach($files as $file){if(!is_readable($file))unavailable();hash_update($hash,basename($file).':'.hash_file('sha256',$file)."\n");}
    $fields=['origin','termsUrl','returnsUrl','privacyUrl','dispatchNotice','sellerName','sellerContact','returnsSummary','complaintsSummary','productInfo','approvedVariants','operationalChecks'];
    foreach($fields as $f)hash_update($hash,$f.':'.json_encode($c[$f],JSON_THROW_ON_ERROR)."\n");return hash_final($hash);
}
function live_config(bool $callbackOnly=false): array {
    $root=realpath($_SERVER['DOCUMENT_ROOT']??'');$file=realpath(config_path('live',$root?:__DIR__));
    if(!$root||!$file||under($file,$root)||!is_readable($file)||!live_host()||($_SERVER['HTTPS']??'off')==='off')unavailable();
    $c=json_decode(file_get_contents($file),true,512,JSON_THROW_ON_ERROR);
    if(!is_array($c)||($c['mode']??null)!=='live'||($c['origin']??'')!=='https://'.strtolower($_SERVER['HTTP_HOST'])||
       !preg_match('/^sk_live_[A-Za-z0-9]+$/D',$c['stripe_key']??'')||!preg_match('/^whsec_[A-Za-z0-9]+$/D',$c['webhook_secret']??''))unavailable();
    $path=$c['db_file']??'';$db=realpath($path);
    if(!$db||$path!==$db||under($db,$root)||!is_file($db)||!is_writable($db)||!is_writable(dirname($db))||
       !extension_loaded('pdo_sqlite')||!extension_loaded('curl'))unavailable();
    if($callbackOnly)return $c; // Honour outstanding sessions/webhooks even if new purchases are paused.
    if(!preg_match('/^[a-f0-9]{64}$/D',$c['abuse_hmac']??''))unavailable();
    $version=live_approval($c,$root);if(!hash_equals($version,$c['approvedReleaseSha256']??''))unavailable();
    $c['approvalVersion']=$version;return $c;
}
function deployment(bool $callbackOnly=false): array {if(live_host())return live_config($callbackOnly);return configuration();}
function ledger_ok(PDO $db,string $mode): bool {
    $r=row($db,'SELECT value FROM store_meta WHERE name=?',['mode']);return ($r['value']??null)===$mode;
}
function visitor_id(): string {
    session_name('pf_checkout_customer');ini_set('session.use_strict_mode','1');ini_set('session.use_only_cookies','1');
    session_set_cookie_params(['lifetime'=>0,'path'=>'/api/','secure'=>true,'httponly'=>true,'samesite'=>'Strict']);
    if(!session_start())unavailable();$_SESSION['visitor']??=bin2hex(random_bytes(18));
    $v=$_SESSION['visitor'];session_write_close();return $v;
}
function rate(PDO $db,array $cfg,string $id,string $request): void {
    $existing=row($db,'SELECT owner FROM orders WHERE req=?',[$request]);
    if($existing){
        if(!hash_equals($id,$existing['owner']??''))problem('REQUEST_CONFLICT',409,'Użyj nowej próby zamówienia.');
        return;
    }
    // REMOTE_ADDR is supplied by the web server, never by request headers.
    $ip=hash_hmac('sha256',$_SERVER['REMOTE_ADDR']??'unknown',$cfg['abuse_hmac']);
    rate_buckets($db,[[$id,3],[$ip,20]]);
}
function rate_buckets(PDO $db,array $limits): void {
    tx($db,function()use($db,$limits){
        $bucket=(int)floor(time()/600);
        $db->prepare('DELETE FROM attempts WHERE bucket<?')->execute([$bucket-1]);
        foreach($limits as [$k,$limit]){
            $db->prepare('INSERT INTO attempts(identity,bucket,n) VALUES(?,?,1) ON CONFLICT(identity,bucket) DO UPDATE SET n=n+1')->execute([$k,$bucket]);
            if((int)row($db,'SELECT n FROM attempts WHERE identity=? AND bucket=?',[$k,$bucket])['n']>$limit)problem('RATE',429,'Zbyt wiele prób. Spróbuj za kilka minut.');
        }
    });
}
function live_public_info(array $c): array {
    return array_intersect_key($c,array_flip(['termsUrl','returnsUrl','privacyUrl','dispatchNotice','returnsSummary','complaintsSummary','sellerName','sellerContact','productInfo','approvalVersion']));
}
