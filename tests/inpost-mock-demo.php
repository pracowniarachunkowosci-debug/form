<?php
declare(strict_types=1);
// CLI-only, loopback-only offline demo. Never upload this launcher or its router.
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
require_once __DIR__.'/../api/_common.php';
if(count($argv)!==1){fwrite(STDERR,"Usage: php tests/inpost-mock-demo.php\n");exit(2);}
$repo=dirname(__DIR__);$directory=$repo.'/.artifacts/inpost-mock-demo';
if(!is_dir($directory)&&!mkdir($directory,0700,true))throw new RuntimeException('Cannot create isolated demo directory');
$lock=fopen($directory.'/launcher.lock','c');
if(!$lock||!flock($lock,LOCK_EX|LOCK_NB)){
    fwrite(STDERR,"Another mock demo launcher is active. No database created.\n");exit(2);
}
$process=null;$db=null;$dbPath=null;$createdDb=false;$ready=false;
register_shutdown_function(static function()use(&$process,&$db,&$dbPath,&$createdDb,&$ready,$lock){
    // Own proc_open handle only: never terminate a PID discovered by port or process name.
    if(is_resource($process)){
        if(proc_get_status($process)['running'])proc_terminate($process);
        proc_close($process);$process=null;
    }
    $db=null;
    if($createdDb&&!$ready&&is_file($dbPath))unlink($dbPath);
    flock($lock,LOCK_UN);fclose($lock);
});
if(function_exists('sapi_windows_set_ctrl_handler'))sapi_windows_set_ctrl_handler(static function(int $event):void {exit(130);});
if(function_exists('pcntl_async_signals')){
    pcntl_async_signals(true);pcntl_signal(SIGINT,static fn()=>exit(130));pcntl_signal(SIGTERM,static fn()=>exit(143));
}
// Check the fixed loopback port BEFORE creating any SQLite file (also covers older launchers).
$socket=@stream_socket_client('tcp://127.0.0.1:8787',$socketError,$socketMessage,0.5);
if(is_resource($socket)){
    fclose($socket);fwrite(STDERR,"127.0.0.1:8787 is occupied. Existing server untouched; no database created.\n");exit(2);
}
if(!in_array($socketError,[61,111,10061],true)){
    fwrite(STDERR,"Cannot establish that loopback port 8787 is free. No database created.\n");exit(2);
}
$run=bin2hex(random_bytes(12));$dbPath=$directory.'/'.$run.'.sqlite';$logPath=$directory.'/'.$run.'.server.log';
$newDb=fopen($dbPath,'x');if(!$newDb)throw new RuntimeException('Cannot create new demo database');
$createdDb=true;fclose($newDb);
$db=database(['db_file'=>$dbPath]);
tx($db,function()use($db){
    $db->exec("INSERT INTO store_meta VALUES('mode','test'),('demo','points-mock-only')");
    foreach(policy()['eligibleModelIds'] as $model)foreach(['dual','red-matte','white','marble'] as $color)
        $db->prepare('INSERT INTO stock VALUES(?,?)')->execute([$model.':'.$color,100]);
});$db=null;
putenv('PF_INPOST_MOCK_DEMO=1');putenv('PF_INPOST_MOCK_DEMO_DB='.realpath($dbPath));
$command=[PHP_BINARY];if(php_ini_loaded_file())array_push($command,'-c',php_ini_loaded_file());
array_push($command,'-d','allow_url_fopen=0','-d','disable_functions=curl_init,curl_exec,fsockopen,pfsockopen,stream_socket_client',
    '-S','127.0.0.1:8787','-t',$repo,__DIR__.'/fixtures/inpost-mock-router.php');
$process=proc_open($command,[0=>STDIN,1=>STDOUT,2=>['file',$logPath,'ab']],$pipes,$repo,null,
    ['bypass_shell'=>true,'create_process_group'=>true]);
if(!is_resource($process))throw new RuntimeException('Cannot start local PHP server');
$deadline=microtime(true)+5;
do{
    $state=proc_get_status($process);clearstatcache(true,$logPath);
    $ready=$state['running']&&str_contains((string)file_get_contents($logPath),'Development Server (http://127.0.0.1:8787) started');
    if($ready)break;
    if(!$state['running']||microtime(true)>=$deadline){
        fwrite(STDERR,"Mock server failed to start; new database will be removed. Log: ".$logPath."\n");exit(1);
    }
    usleep(50000);
}while(true);
echo inpost_mock_notice()."\nBrak Stripe, płatności i przesyłek. Izolowane stany syntetyczne.\n";
echo "UI: http://127.0.0.1:8787/winter-zestaw-4.html?size=1&model=full-soft&color=marble#kompozycja\n";
echo 'Server PID: '.$state['pid'].'; SQLite (reserved): '.realpath($dbPath)."\nLog: ".$logPath."\nCtrl+C kończy tylko ten serwer.\n";
// Polling keeps Ctrl+C handlers responsive, unlike blocking indefinitely in proc_close().
do{usleep(100000);$state=proc_get_status($process);}while($state['running']);
$exitCode=$state['exitcode'];proc_close($process);$process=null;
exit($exitCode>=0?$exitCode:1);
