<?php
declare(strict_types=1);
require __DIR__.'/checkout-pending.php';require_once __DIR__.'/../api/_order_status.php';
foreach(['paid','pending','released','review'] as $state){
 [$db,$o,$t]=setup_fixture();
 if($state==='paid'){
  $e=event_fixture($o,'statuspaid','checkout.session.completed','paid');apply_event($db,$e);apply_event($db,$e);
 }else $db->prepare('UPDATE orders SET state=? WHERE id=?')->execute([$state,$o['id']]);
 $before=$db->query('SELECT total_changes()')->fetchColumn();$stock=units($db);
 for($i=0;$i<5;$i++){
  $status=order_status_read($db,$o['req'],null);need($status['state']===$state,'status '.$state);
  need(array_keys($status)===['state','message'],'no SID, PI, URL or customer data');
 }
 need($db->query('SELECT total_changes()')->fetchColumn()===$before,'status is read only');
 need(units($db)===$stock&&$db->query('SELECT count(*) FROM orders')->fetchColumn()===1,'no stock or order changes');
 retry_error('NOT_FOUND',fn()=>order_status_read($db,$o['req'],'another-visitor'));
 retry_error('BAD_REQUEST',fn()=>order_status_read($db,'invalid',null));
 if($state==='paid'){
  need(str_contains($status['message'],'Zamówienie opłacone'),'paid positive confirmation');
  retry_error('ORDER_PAID',fn()=>stripe_session(config_fixture(),$o,$db,fn()=>throw new RuntimeException('NO STRIPE CALL'),$t+1));
  apply_event($db,event_fixture($o,'lateexpired','checkout.session.expired','unpaid'));
  need(state($db,$o)==='paid'&&units($db)===$stock,'paid never released by stale expiry');
 }
 done('read-only customer status '.$state);
}
$file=tempnam(sys_get_temp_dir(),'pf-status-');
$cfg=['db_file'=>$file];$rw=database($cfg);$rw=null;
$ro=order_status_database($cfg);
try{$ro->exec("INSERT INTO store_meta VALUES('should-not-write','no')");throw new RuntimeException('write allowed');}catch(PDOException $e){need(str_contains(strtolower($e->getMessage()),'readonly'),'sqlite opened read only');}
$ro=null;unlink($file);done('SQLite status connection rejects writes');
