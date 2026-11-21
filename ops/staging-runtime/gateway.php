<?php
declare(strict_types=1);
// PROPOSAL ONLY. Install once in a permanent, staging-only document root after approval.
// Do not deploy this as /api/checkout.php and do not put the gateway behind a moving symlink.
function pf_gateway_target(string $releases,string $release,string $uri): string {
    if(!preg_match('/^[a-z0-9][a-z0-9-]{7,79}$/D',$release))throw new RuntimeException('release');
    $path=parse_url($uri,PHP_URL_PATH);
    if(!is_string($path)||!preg_match('#^/api/(checkout|result|order-status|webhook|status|dispatch-quote|pickup-point|test-access)\.php$#D',$path))throw new RuntimeException('route');
    $file=$releases.'/'.$release.'/public'.$path;
    if(str_replace('\\','/',realpath($file)?:'')!==$file||!is_file($file))throw new RuntimeException('noncanonical target');
    return $file;
}
function pf_gateway_probe(string $entry,string $entryDir): void {
    $token=$_SERVER['HTTP_X_PF_RUNTIME_PROOF']??null;if($token===null)return;
    // Independent short-lived administrator capability; tester login alone is insufficient.
    // No token/config is generated or installed by this proposal.
    $file='/home/pf26/winter26/config/runtime-proof.json';
    $cfg=is_file($file)&&!is_link($file)?json_decode(file_get_contents($file),true):null;
    $valid=is_array($cfg)&&is_string($token)&&strlen($token)>=32&&strlen($token)<=256
        &&is_string($cfg['token_sha256']??null)&&preg_match('/^[a-f0-9]{64}$/D',$cfg['token_sha256'])
        &&hash_equals($cfg['token_sha256'],hash('sha256',$token))
        &&is_int($cfg['expires_at']??null)&&$cfg['expires_at']>time()&&$cfg['expires_at']<=time()+900
        &&($_SERVER['HTTP_HOST']??'')==='pf26.uber.space'&&($_SERVER['HTTPS']??'off')!=='off'
        &&($_SERVER['REQUEST_METHOD']??'')==='POST'&&PHP_SAPI==='fpm-fcgi'
        &&function_exists('is_tester')&&is_tester();
    if(!$valid){http_response_code(403);header('Cache-Control: no-store');exit;}
    $expected=$GLOBALS['pf_gateway_entry'];$root=dirname($expected,2);
    if($entry!==$expected||$entryDir!==dirname($expected)){
        http_response_code(503);header('Cache-Control: no-store');echo '{"proof":"wrong-entry"}';exit;
    }
    $states=[];foreach(['paid','pending','released','review'] as $state){
        try{checkout_state(['state'=>$state]);$states[$state]='ALLOWED';}catch(StoreError $e){$states[$state]=$e->kind;}
    }
    $included=array_values(array_filter(get_included_files(),fn($f)=>str_starts_with($f,$root.'/')));
    $cache=function_exists('opcache_get_status')?opcache_get_status(true):false;
    $keys=array_values(array_filter(array_keys($cache['scripts']??[]),fn($f)=>str_starts_with($f,$root.'/')));
    $hashes=[];foreach($included as $f)$hashes[substr($f,strlen($root)+1)]=hash_file('sha256',$f);
    header('Content-Type: application/json');header('Cache-Control: no-store');header('X-Content-Type-Options: nosniff');
    echo json_encode(['proof'=>'pf-runtime-v1','sapi'=>PHP_SAPI,'scriptFilename'=>$_SERVER['SCRIPT_FILENAME']??null,
        'entryFile'=>$entry,'entryDir'=>$entryDir,'entryCanonical'=>realpath($entry),'loadedCommon'=>(new ReflectionFunction('existing_order'))->getFileName(),
        'loadedStateGuard'=>(new ReflectionFunction('checkout_state'))->getFileName(),'stateChecks'=>$states,'includedHashes'=>$hashes,
        'opcacheScriptKeys'=>$keys,'opcacheKeysAvailable'=>is_array($cache),'settings'=>array_combine(
            ['opcache.revalidate_path','opcache.validate_timestamps','opcache.revalidate_freq','realpath_cache_ttl'],
            array_map('ini_get',['opcache.revalidate_path','opcache.validate_timestamps','opcache.revalidate_freq','realpath_cache_ttl']))]);exit;
}
function pf_gateway_run(): void {
    if(($_SERVER['HTTP_HOST']??'')!=='pf26.uber.space'||($_SERVER['HTTPS']??'off')==='off'){http_response_code(404);exit;}
    try{
        $pointer='/home/pf26/winter26/config/active-release.json';
        if(!is_file($pointer)||is_link($pointer))throw new RuntimeException('pointer');
        // Read ordinary data each request; PHP/realpath caches cannot freeze the release choice.
        $choice=json_decode(file_get_contents($pointer),true,8,JSON_THROW_ON_ERROR);
        $entry=pf_gateway_target('/var/www/virtual/pf26/winter26/releases',$choice['release']??'',$_SERVER['REQUEST_URI']??'');
    }catch(Throwable $e){http_response_code(503);header('Cache-Control: no-store');exit;}
    $GLOBALS['pf_gateway_entry']=$entry;
    $_SERVER['DOCUMENT_ROOT']=dirname($entry,2); // Legal/catalog checks use this immutable release too.
    require $entry;
}
// Includes in the offline tests define functions without serving a request.
if(realpath($_SERVER['SCRIPT_FILENAME']??'')===__FILE__)pf_gateway_run();
