<?php
declare(strict_types=1);
require_once __DIR__.'/_common.php';require_once __DIR__.'/_order_status.php';require_once __DIR__.'/_checkout_identity.php';
endpoint(function(){
    method('POST');$cfg=deployment(true);require_origin($cfg);
    if(strtolower(trim(explode(';',$_SERVER['CONTENT_TYPE']??'')[0]))!=='application/json')problem('MEDIA',415,'Nieprawidłowy typ danych.');
    return order_status_handle($cfg,body(256),checkout_identity($cfg['mode']));
});
