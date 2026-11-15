<?php
declare(strict_types=1);require_once __DIR__.'/_common.php';
endpoint(function(){
    method('GET');$cfg=deployment();
    if($cfg['mode']!=='live'&&!is_tester())problem('TEST_ACCESS',403,'Ta funkcja jest dostępna tylko dla testera.');
    $id=point_id($_GET['id']??null);if(!inpost_settings($cfg)['locker_available'])point_unavailable();
    $db=database($cfg);if(!ledger_ok($db,$cfg['mode']))unavailable();
    if($cfg['mode']==='live') {
        $owner=visitor_id();$ip=hash_hmac('sha256',$_SERVER['REMOTE_ADDR']??'unknown',$cfg['abuse_hmac']);
        rate_buckets($db,[['point:'.$owner,30],['point:'.$ip,180]]);
    }
    return lookup_point($cfg,$id);
});
