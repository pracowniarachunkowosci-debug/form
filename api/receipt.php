<?php
declare(strict_types=1);require_once __DIR__.'/_common.php';require_once __DIR__.'/_receipt.php';
endpoint(function(){
    method('GET');$cfg=deployment(true);if($cfg['mode']!=='live')problem('NOT_FOUND',404,'Nie znaleziono zamówienia.');
    $owner=visitor_id();$db=new PDO('sqlite:'.$cfg['db_file'],null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
    $db->exec('PRAGMA query_only=ON');if(!ledger_ok($db,'live'))unavailable();
    return order_receipt($db,is_string($_GET['id']??null)?$_GET['id']:'',$owner);
});
