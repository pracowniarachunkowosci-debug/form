<?php
declare(strict_types=1);
// Additive CLI migration only. No stock is created or inferred from catalog availability.
const DISPATCH_VERSION='dispatch-3-7-7-v1';
function dispatch_enabled(array $cfg): bool {return ($cfg['mode']??'test')==='live'||($cfg['dispatch_required']??false)===true;}
// Sandbox demonstration records only the agreed order terms. No inventory allocation tables.
function dispatch_snapshot_migrate(PDO $db): void {
    tx($db,function()use($db){$db->exec("CREATE TABLE IF NOT EXISTS dispatch_snapshots (
      order_id TEXT PRIMARY KEY, snapshot TEXT NOT NULL, sha256 TEXT NOT NULL, accepted_release TEXT NOT NULL);
      CREATE TRIGGER IF NOT EXISTS dispatch_snapshot_no_update BEFORE UPDATE ON dispatch_snapshots BEGIN SELECT RAISE(ABORT,'IMMUTABLE_DISPATCH'); END;
      CREATE TRIGGER IF NOT EXISTS dispatch_snapshot_no_delete BEFORE DELETE ON dispatch_snapshots BEGIN SELECT RAISE(ABORT,'IMMUTABLE_DISPATCH'); END;
      CREATE TRIGGER IF NOT EXISTS dispatch_quote_no_update BEFORE UPDATE OF quote ON orders
      WHEN EXISTS(SELECT 1 FROM dispatch_snapshots WHERE order_id=OLD.id) AND NEW.quote IS NOT OLD.quote
      BEGIN SELECT RAISE(ABORT,'IMMUTABLE_ORDER_QUOTE'); END;
      CREATE TRIGGER IF NOT EXISTS dispatch_order_no_delete BEFORE DELETE ON orders
      WHEN EXISTS(SELECT 1 FROM dispatch_snapshots WHERE order_id=OLD.id)
      BEGIN SELECT RAISE(ABORT,'IMMUTABLE_DISPATCH_ORDER'); END;");});
}
function dispatch_sandbox_plan(PDO $db,array $cfg,array $q): array {
    if(($cfg['mode']??'')!=='test'||($cfg['origin']??'')!=='https://pf26.uber.space')unavailable();
    if(!row($db,"SELECT name FROM sqlite_master WHERE type='table' AND name='dispatch_snapshots'",[]))unavailable();
    $kind=$cfg['sandbox_dispatch_kind']??'made_to_order';
    if(!in_array($kind,['ready','made_to_order','mixed'],true))unavailable();
    $days=$kind==='ready'?3:7;$lines=[];$items=$q['items'];ksort($items);
    foreach($items as $sku=>$qty)$lines[]=['sku'=>$sku,'quantity'=>$qty,'units'=>[]];
    return ['version'=>DISPATCH_VERSION,'kind'=>$kind,'maxBusinessDays'=>$days,'basis'=>'confirmed_payment',
      'businessDays'=>'Monday-Friday excluding Polish statutory holidays','text'=>dispatch_message($days),
      'lines'=>$lines,'evidenceScope'=>'sandbox simulation; no real stock allocation'];
}
function dispatch_migrate(PDO $db): void {
    tx($db,function()use($db){$db->exec("CREATE TABLE IF NOT EXISTS dispatch_policy (
      sku TEXT PRIMARY KEY, made_to_order INTEGER NOT NULL CHECK(made_to_order IN(0,1)), evidence TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS dispatch_units (
      unit_id TEXT PRIMARY KEY, sku TEXT NOT NULL, evidence TEXT NOT NULL, order_id TEXT);
      CREATE INDEX IF NOT EXISTS dispatch_units_available ON dispatch_units(sku,order_id);
      CREATE TABLE IF NOT EXISTS dispatch_snapshots (
      order_id TEXT PRIMARY KEY, snapshot TEXT NOT NULL, sha256 TEXT NOT NULL, accepted_release TEXT NOT NULL);
      CREATE TRIGGER IF NOT EXISTS dispatch_snapshot_no_update BEFORE UPDATE ON dispatch_snapshots BEGIN SELECT RAISE(ABORT,'IMMUTABLE_DISPATCH'); END;
      CREATE TRIGGER IF NOT EXISTS dispatch_snapshot_no_delete BEFORE DELETE ON dispatch_snapshots BEGIN SELECT RAISE(ABORT,'IMMUTABLE_DISPATCH'); END;
      CREATE TRIGGER IF NOT EXISTS dispatch_quote_no_update BEFORE UPDATE OF quote ON orders
      WHEN EXISTS(SELECT 1 FROM dispatch_snapshots WHERE order_id=OLD.id) AND NEW.quote IS NOT OLD.quote
      BEGIN SELECT RAISE(ABORT,'IMMUTABLE_ORDER_QUOTE'); END;
      CREATE TRIGGER IF NOT EXISTS dispatch_order_no_delete BEFORE DELETE ON orders
      WHEN EXISTS(SELECT 1 FROM dispatch_snapshots WHERE order_id=OLD.id)
      BEGIN SELECT RAISE(ABORT,'IMMUTABLE_DISPATCH_ORDER'); END;
      CREATE TRIGGER IF NOT EXISTS dispatch_release_units AFTER UPDATE OF state ON orders
      WHEN NEW.state='released' AND OLD.state IN ('reserved','pending','reconcile')
      BEGIN UPDATE dispatch_units SET order_id=NULL WHERE order_id=NEW.id; END;");});
}
function dispatch_schema(PDO $db): void {
    foreach(['dispatch_policy','dispatch_units','dispatch_snapshots']as $name)
        if(!row($db,"SELECT name FROM sqlite_master WHERE type='table' AND name=?",[$name]))problem('DISPATCH_UNAVAILABLE',503,'Nie można teraz potwierdzić terminu nadania.');
}
function dispatch_message(int $days): string {return 'Nadanie maksymalnie w ciągu '.$days.' dni roboczych od potwierdzenia płatności. Termin dotyczy nadania, nie doręczenia.';}
function dispatch_plan(PDO $db,array $q): array {
    dispatch_schema($db);$lines=[];$ready=0;$made=0;$items=$q['items'];ksort($items);
    foreach($items as $sku=>$quantity){
        $s=$db->prepare("SELECT unit_id FROM dispatch_units WHERE sku=? AND order_id IS NULL AND trim(evidence)<>'' ORDER BY unit_id LIMIT ?");
        $s->bindValue(1,$sku);$s->bindValue(2,$quantity,PDO::PARAM_INT);$s->execute();$units=array_column($s->fetchAll(),'unit_id');
        $r=count($units);$m=$quantity-$r;$policy=row($db,'SELECT * FROM dispatch_policy WHERE sku=?',[$sku]);
        if($m>0&&(!$policy||(int)$policy['made_to_order']!==1||trim($policy['evidence'])===''))
            problem('DISPATCH_UNAVAILABLE',409,'Nie można teraz potwierdzić terminu dla wybranej ilości. Zmień koszyk lub skontaktuj się ze sklepem.');
        $lines[]=['sku'=>$sku,'quantity'=>$quantity,'ready'=>$r,'madeToOrder'=>$m,'units'=>$units,'productionEvidence'=>$m?$policy['evidence']:null];$ready+=$r;$made+=$m;
    }
    $kind=$made===0?'ready':($ready===0?'made_to_order':'mixed');$days=$made===0?3:7;
    return ['version'=>DISPATCH_VERSION,'kind'=>$kind,'maxBusinessDays'=>$days,'basis'=>'confirmed_payment','businessDays'=>'Monday-Friday excluding Polish statutory holidays','text'=>dispatch_message($days),'lines'=>$lines];
}
function dispatch_key(array $cfg): string {
    $key=$cfg['dispatch_hmac']??$cfg['abuse_hmac']??'';
    if(!is_string($key)||!preg_match('/^[a-f0-9]{64}$/D',$key))problem('DISPATCH_UNAVAILABLE',503,'Nie można teraz potwierdzić terminu nadania.');return $key;
}
function dispatch_proof(array $cfg,array $q,array $plan,string $owner,int $expires): string {
    unset($q['dispatchToken'],$q['pickup_address']);
    $hash=hash('sha256',json_encode([$q,$plan,$owner],JSON_THROW_ON_ERROR));
    return $expires.'.'.$hash.'.'.hash_hmac('sha256',$expires.'.'.$hash,dispatch_key($cfg));
}
function dispatch_context(PDO $db,array $cfg,array $q): array {
    $plan=production_enabled($cfg)?production_plan($q):(($cfg['dispatch_strategy']??'')==='sandbox_order_terms'?dispatch_sandbox_plan($db,$cfg,$q):dispatch_plan($db,$q));
    if(isset($cfg['legal_documents']))$plan['documents']=$cfg['legal_documents'];
    $p=policy();$rates=delivery_rates($p);$free=$q['size']>=$p['freeCourierFromOrnaments'];
    $plan['offeredDeliveryGrosz']=['courier'=>$free?0:$rates['courier']];
    if(inpost_settings($cfg)['locker_available'])$plan['offeredDeliveryGrosz']['locker']=$free?0:$rates['locker'];
    return $plan;
}
function dispatch_preview(PDO $db,array $cfg,array $q,string $owner,int $now): array {
    $plan=dispatch_context($db,$cfg,$q);
    return ['kind'=>$plan['kind'],'maxBusinessDays'=>$plan['maxBusinessDays'],'text'=>$plan['text'],
        'token'=>dispatch_proof($cfg,$q,$plan,$owner,$now+300),'expiresAt'=>$now+300];
}
function dispatch_reserve(PDO $db,array $cfg,array $q,string $owner,string $id,int $now): array {
    $plan=dispatch_context($db,$cfg,$q);$proof=$q['dispatchToken']??'';
    if(!is_string($proof)||!preg_match('/^([0-9]{10})\.[a-f0-9]{64}\.[a-f0-9]{64}$/D',$proof,$m)||
       (int)$m[1]<$now||(int)$m[1]>$now+300||!hash_equals(dispatch_proof($cfg,$q,$plan,$owner,(int)$m[1]),$proof))
        problem('DISPATCH_CHANGED',409,'Sprawdź ponownie termin nadania i zaakceptuj podsumowanie. Płatność nie została rozpoczęta.');
    foreach($plan['lines']as $line)foreach($line['units']as $unit){
        $s=$db->prepare('UPDATE dispatch_units SET order_id=? WHERE unit_id=? AND order_id IS NULL');$s->execute([$id,$unit]);
        if($s->rowCount()!==1)problem('DISPATCH_CHANGED',409,'Dostępność gotowych produktów zmieniła się. Sprawdź termin ponownie.');
    }
    $json=json_encode($plan,JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR);
    $db->prepare('INSERT INTO dispatch_snapshots VALUES(?,?,?,?)')->execute([$id,$json,hash('sha256',$json),$q['acceptedRelease']??'']);
    return $plan+['sha256'=>hash('sha256',$json)];
}
