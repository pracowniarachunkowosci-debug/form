<?php
declare(strict_types=1);
// No schema initialization, reconciliation, sales gate or Stripe requests on this path.
function order_status_database(array $cfg): PDO {
    if(!is_file($cfg['db_file']))unavailable();
    $flags=class_exists('Pdo\\Sqlite')?constant('Pdo\\Sqlite::ATTR_OPEN_FLAGS'):PDO::SQLITE_ATTR_OPEN_FLAGS;
    $readOnly=class_exists('Pdo\\Sqlite')?constant('Pdo\\Sqlite::OPEN_READONLY'):PDO::SQLITE_OPEN_READONLY;
    $db=new PDO('sqlite:'.$cfg['db_file'],null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC,$flags=>$readOnly]);
    $db->exec('PRAGMA query_only=ON');
    $db->exec('PRAGMA busy_timeout=1000');
    return $db;
}
function order_status_read(PDO $db,string $request,?string $owner): array {
    if(!preg_match('/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/iD',$request))problem('BAD_REQUEST',422,'Nieprawidłowy identyfikator próby.');
    $o=row($db,'SELECT state,owner FROM orders WHERE req=?',[$request]);
    if(!$o||!is_string($owner)||!preg_match('/^[a-f0-9]{36}$/D',$owner)||!is_string($o['owner'])||!hash_equals($o['owner'],$owner))problem('NOT_FOUND',404,'Nie potwierdzono statusu tej próby. Zachowaj ją i spróbuj ponownie.');
    $messages=['paid'=>'Zamówienie opłacone. Płatność została potwierdzona. Nie płać ponownie.',
        'pending'=>'Płatność jest przetwarzana. Sprawdź status ponownie; nie rozpoczynaj kolejnej płatności.',
        'released'=>'Próba została bezpiecznie zakończona bez płatności. Możesz rozpocząć nową próbę.',
        'review'=>'Płatność wymaga sprawdzenia przez sklep. Skontaktuj się z nami; nie płać ponownie.',
        'reserved'=>'Płatność nie jest jeszcze potwierdzona. Możesz kontynuować tę samą próbę.',
        'reconcile'=>'Sprawdzamy wynik tej próby. Zachowaj jej identyfikator i nie rozpoczynaj nowej płatności.'];
    $state=$o['state'];if(!isset($messages[$state]))unavailable();
    return ['state'=>$state,'message'=>$messages[$state]];
}
function order_status_handle(array $cfg,string $raw,array $identity): array {
    if(!in_array($cfg['mode']??null,['test','live'],true))unavailable();
    if($cfg['mode']==='test'&&($identity['tester']??false)!==true)problem('TEST_ACCESS',403,'Zaloguj się jako tester, aby sprawdzić status.');
    $owner=$identity['owner']??null;
    if(!is_string($owner)||!preg_match('/^[a-f0-9]{36}$/D',$owner))problem('AUTH_REQUIRED',401,'Brakuje sesji właściciela zamówienia. Skontaktuj się ze sklepem; nie płać ponownie.');
    if(strlen($raw)>256)problem('BAD_BODY',400,'Nieprawidłowe żądanie.');
    $in=json_decode($raw,true);
    if(!is_array($in)||array_keys($in)!==['requestId']||!is_string($in['requestId'])||!preg_match('/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/iD',$in['requestId']))problem('BAD_REQUEST',422,'Nieprawidłowe dane.');
    try{
        $db=order_status_database($cfg);if(!ledger_ok($db,$cfg['mode']))unavailable();
        return order_status_read($db,$in['requestId'],$owner);
    }catch(PDOException $e){unavailable();}
}
