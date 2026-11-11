<?php
declare(strict_types=1);require_once __DIR__.'/_common.php';
endpoint(function(){
    method('POST');$cfg=deployment(true);$raw=body(256*1024);
    if(!verify_signature($raw,$_SERVER['HTTP_STRIPE_SIGNATURE']??'',$cfg['webhook_secret'],time()))problem('SIGNATURE',400,'Nieprawidłowy podpis.');
    $e=json_decode($raw,true);if(!is_array($e))problem('EVENT',400,'Nieprawidłowe zdarzenie.');
    $db=database($cfg);if(!ledger_ok($db,$cfg['mode']))unavailable();apply_event($db,$e,$cfg['mode']==='live');return ['received'=>true];
});
