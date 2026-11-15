<?php
declare(strict_types=1);
// Install outside DocumentRoot. Sandbox-only operator/scheduler entry point.
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
$api=realpath(__DIR__.'/../api')?:realpath(__DIR__.'/../public/api');
if(!$api){fwrite(STDERR,"APPLICATION_NOT_FOUND\n");exit(1);}
require_once $api.'/_common.php';
try{
    $args=getopt('',['config:','migrate','backup:','status','once','limit:','order:','session:','history']);
    if(array_diff(array_keys($args),['config','migrate','backup','status','once','limit','order','session','history']))throw new RuntimeException('ARGUMENTS');
    $actions=array_intersect(['migrate','status','once'],array_keys($args));if(count($actions)!==1)throw new RuntimeException('CHOOSE_MIGRATE_STATUS_OR_ONCE');
    $path=realpath($args['config']??'');$root=realpath(__DIR__.'/..');
    if(!$path || under($path,$root))throw new RuntimeException('PRIVATE_CONFIG_REQUIRED');
    $cfg=json_decode(file_get_contents($path),true,512,JSON_THROW_ON_ERROR);
    if(($cfg['origin']??'')!=='https://pf26.uber.space' || !preg_match('/^sk_test_[A-Za-z0-9]+$/D',$cfg['stripe_key']??'') || ($cfg['mode']??'test')!=='test')throw new RuntimeException('PF26_SANDBOX_ONLY');
    $cfg['mode']='test';$file=realpath($cfg['db_file']??'');
    if(!$file || under($file,$root)||is_link($cfg['db_file']))throw new RuntimeException('PRIVATE_DATABASE_REQUIRED');
    umask(0077);
    // Open existing database without database() and its bootstrap DDL; never seed/create a ledger here.
    $db=new PDO('sqlite:'.$file,null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC]);
    $db->exec('PRAGMA busy_timeout=5000');if(!ledger_ok($db,'test'))throw new RuntimeException('TEST_LEDGER_REQUIRED');
    if(isset($args['migrate'])){
        $backup=$args['backup']??'';$dir=realpath(dirname($backup));
        if(!$dir || under($dir,$root) || file_exists($backup) || is_link($backup) || !str_ends_with($backup,'.sqlite'))throw new RuntimeException('NEW_PRIVATE_BACKUP_REQUIRED');
        // VACUUM INTO produces a consistent SQLite snapshot, including committed WAL content.
        $db->exec('VACUUM INTO '.$db->quote($backup));chmod($backup,0600);
        $copy=new PDO('sqlite:'.$backup);$copy->exec('PRAGMA query_only=ON');
        if($copy->query('PRAGMA integrity_check')->fetchColumn()!=='ok')throw new RuntimeException('BACKUP_INTEGRITY');
        $copy=null;reservation_migrate($db);
        echo json_encode(['migrated'=>true,'backupCreated'=>true,'existingRowsUpdated'=>0]),"\n";exit;
    }
    reservation_require_schema($db);
    $now=time();$limit=filter_var($args['limit']??20,FILTER_VALIDATE_INT,['options'=>['min_range'=>1,'max_range'=>100]]);
    if($limit===false)throw new RuntimeException('LIMIT');
    $filter=$args['order']??null;if($filter!==null&&!preg_match('/^w26_[a-f0-9]{24}$/D',$filter))throw new RuntimeException('ORDER_ID');
    if(isset($args['history']) && (!isset($args['status']) || $filter===null))throw new RuntimeException('HISTORY_REQUIRES_STATUS_AND_ORDER');
    $session=$args['session']??null;
    if($session!==null && (!isset($args['once']) || $filter===null || !preg_match('/^cs_test_[A-Za-z0-9]+$/D',$session)))throw new RuntimeException('SANDBOX_SESSION_AND_ORDER_REQUIRED');
    if(isset($args['once'])){
        $sql="SELECT o.id FROM orders o LEFT JOIN checkout_operations c ON c.order_id=o.id
          WHERE o.state IN ('reserved','reconcile','pending')";
        $params=[];
        if($session===null){$sql.=' AND (c.order_id IS NULL OR (c.next_check<=? AND c.lease_until<=?))';$params=[$now,$now];}
        if($filter!==null){$sql.=' AND o.id=?';$params[]=$filter;}
        $sql.=' ORDER BY COALESCE(c.next_check,o.created),o.id LIMIT '.(int)$limit;
        $q=$db->prepare($sql);$q->execute($params);$ids=$q->fetchAll(PDO::FETCH_COLUMN);$counts=[];
        foreach($ids as $id){$result=reservation_reconcile($db,$cfg,$id,null,null,$session);$code=$result['code'];$counts[$code]=($counts[$code]??0)+1;}
        echo json_encode(['checked'=>count($ids),'results'=>$counts]),"\n";
    }
    $q=$db->prepare("SELECT o.id,o.created,o.state,c.status,c.last_code,c.first_attempt,c.attempts,c.next_check,c.escalated_at
      FROM orders o LEFT JOIN checkout_operations c ON c.order_id=o.id
      WHERE ".($filter===null?"o.state IN ('reserved','reconcile','pending','review')":"o.id=?")." ORDER BY o.created");
    $q->execute($filter===null?[]:[$filter]);
    $rows=$q->fetchAll();$attention=array_filter($rows,fn($r)=>$r['state']==='review' || (reservation_held($r['state']) && ($r['escalated_at']!==null || $r['status']===null)));
    $due=$db->prepare("SELECT MIN(CASE WHEN c.order_id IS NULL THEN o.created ELSE MAX(c.next_check,c.lease_until) END) FROM orders o LEFT JOIN checkout_operations c ON c.order_id=o.id WHERE o.state IN ('reserved','reconcile','pending')".($filter===null?'':' AND o.id=?'));
    $due->execute($filter===null?[]:[$filter]);$oldest=$due->fetchColumn();
    $lag=$oldest===null?0:max(0,$now-(int)$oldest);$backlog=$lag>300;
    echo json_encode(['reservationsCount'=>count($rows),'attentionRequired'=>count($attention),'oldestDueLagSeconds'=>$lag,'backlogAlert'=>$backlog,'reservations'=>$rows]),"\n";
    if(isset($args['history'])){
        $q=$db->prepare('SELECT at,code,details FROM reservation_history WHERE order_id=? ORDER BY seq DESC LIMIT 100');$q->execute([$filter]);
        echo json_encode(['history'=>$q->fetchAll()]),"\n";
    }
    exit($attention||$backlog?2:0); // Alert on escalations AND a queue whose oldest due item is over 5 minutes late.
}catch(Throwable $e){
    // Exception text may contain paths, SQL or upstream details; never print it.
    fwrite(STDERR,"RESERVATION_WORKER_FAILED ".get_class($e)."\n");exit(1);
}
