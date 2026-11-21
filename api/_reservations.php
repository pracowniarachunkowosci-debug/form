<?php
declare(strict_types=1);
// No schema changes in HTTP requests. Run the backed-up CLI migration before deploying.
const RESERVATION_STRIPE_VERSION='2026-02-25.clover';
const RESERVATION_REPLAY_SECONDS=23*3600; // Strictly inside Stripe API v1's >=24h retention.
const RESERVATION_LEASE_SECONDS=120; // Longer than one POST or the bounded GET scan.

function reservation_migrate(PDO $db): void {
    tx($db,function()use($db){$db->exec("CREATE TABLE IF NOT EXISTS checkout_operations (
      order_id TEXT PRIMARY KEY, idempotency_key TEXT UNIQUE NOT NULL,
      request_body TEXT, body_sha256 TEXT, api_version TEXT NOT NULL,
      status TEXT NOT NULL, uncertain INTEGER NOT NULL DEFAULT 0,
      first_attempt INTEGER, attempts INTEGER NOT NULL DEFAULT 0, checks INTEGER NOT NULL DEFAULT 0,
      next_check INTEGER NOT NULL, lease_token TEXT, lease_until INTEGER NOT NULL DEFAULT 0,
      escalated_at INTEGER, last_code TEXT);
      CREATE INDEX IF NOT EXISTS checkout_operations_due ON checkout_operations(next_check);
      CREATE TABLE IF NOT EXISTS reservation_history (
      seq INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL, at INTEGER NOT NULL,
      code TEXT NOT NULL, details TEXT NOT NULL);
      CREATE INDEX IF NOT EXISTS reservation_history_order ON reservation_history(order_id,seq)");});
}
function reservation_require_schema(PDO $db): void {
    foreach(['checkout_operations','reservation_history']as $name)
        if(!row($db,"SELECT name FROM sqlite_master WHERE type='table' AND name=?",[$name]))unavailable();
}
function reservation_held(string $state): bool {return in_array($state,['reserved','reconcile','pending'],true);}
function reservation_history(PDO $db,string $id,string $code,int $now,array $details=[]): void {
    // Callers pass only bounded internal reason/status codes, never response bodies or credentials.
    $db->prepare('INSERT INTO reservation_history(order_id,at,code,details) VALUES(?,?,?,?)')->execute([$id,$now,$code,json_encode($details,JSON_THROW_ON_ERROR)]);
}
function reservation_prepare(PDO $db,array $o,array $cfg,int $now): void {
    $body=http_build_query(checkout_params($o,$cfg['origin'],($cfg['mode']??'test')==='live'),'','&',PHP_QUERY_RFC3986);
    $db->prepare("INSERT INTO checkout_operations(order_id,idempotency_key,request_body,body_sha256,api_version,status,next_check) VALUES(?,?,?,?,?,'prepared',?)")
        ->execute([$o['id'],$o['id'],$body,hash('sha256',$body),RESERVATION_STRIPE_VERSION,$now]);
    reservation_history($db,$o['id'],'RESERVED',$now);
}
function reservation_release(PDO $db,array $o,string $reason,int $now): bool {
    // Must be called under BEGIN IMMEDIATE, with a fresh row and authoritative evidence.
    if(!reservation_held($o['state']))return false;
    $q=json_decode($o['quote'],true,512,JSON_THROW_ON_ERROR);
    // Fulfilment accounting is frozen in the original snapshot, never in today's config.
    if(!production_snapshot($q))foreach($q['items']as $sku=>$n){
        $s=$db->prepare('UPDATE stock SET n=n+? WHERE sku=?');$s->execute([$n,$sku]);
        if($s->rowCount()!==1)unavailable();
    }
    $db->prepare("UPDATE orders SET state='released' WHERE id=?")->execute([$o['id']]);
    reservation_history($db,$o['id'],$reason,$now);
    return true;
}
function reservation_observed(PDO $db,string $id,string $state,int $now): void {
    $terminal=in_array($state,['paid','released','review'],true);
    $db->prepare('UPDATE checkout_operations SET status=?, uncertain=0, lease_token=NULL, lease_until=0, escalated_at=NULL, next_check=?, last_code=? WHERE order_id=?')
        ->execute([$terminal?'terminal':'session',$now+300,'SESSION_'.strtoupper($state),$id]);
    if($state==='review')$db->prepare('UPDATE checkout_operations SET escalated_at=COALESCE(escalated_at,?) WHERE order_id=?')->execute([$now,$id]);
    if(!$terminal){
        $o=row($db,'SELECT created FROM orders WHERE id=?',[$id]);
        if($now>=(int)$o['created']+3600){
            $db->prepare('UPDATE checkout_operations SET escalated_at=COALESCE(escalated_at,?),last_code=? WHERE order_id=?')->execute([$now,'SESSION_STILL_ACTIVE_AFTER_DEADLINE',$id]);
            reservation_history($db,$id,'ACTIVE_SESSION_ESCALATED',$now);
        }
    }
}
function reservation_claim(PDO $db,array $cfg,string $id,int $now,bool $immediate=false): ?array {
    reservation_require_schema($db);
    return tx($db,function()use($db,$id,$now,$immediate){
        $o=row($db,'SELECT * FROM orders WHERE id=?',[$id]);
        if(!$o || !reservation_held($o['state']))return null;
        $op=row($db,'SELECT * FROM checkout_operations WHERE order_id=?',[$id]);
        if(!$op){
            // A pre-migration reservation has no durable exact request. Never reconstruct/re-POST it.
            $db->prepare("INSERT INTO checkout_operations(order_id,idempotency_key,api_version,status,uncertain,next_check,escalated_at) VALUES(?,?,?,'escalated',1,?,?)")
                ->execute([$id,$id,RESERVATION_STRIPE_VERSION,$now,$now]);
            reservation_history($db,$id,'LEGACY_RECONCILE',$now);
            $op=row($db,'SELECT * FROM checkout_operations WHERE order_id=?',[$id]);
        }
        if((int)$op['lease_until']>$now || (!$immediate && (int)$op['next_check']>$now))return null;
        $token=bin2hex(random_bytes(16));
        $db->prepare('UPDATE checkout_operations SET lease_token=?,lease_until=?,checks=checks+1 WHERE order_id=?')->execute([$token,$now+RESERVATION_LEASE_SECONDS,$id]);
        return ['order'=>$o,'operation'=>$op,'token'=>$token];
    });
}
function reservation_curl_result(int $errno,int $status,int $requestBytes,float $pretransfer,?array $body,array $headers): array {
    // Timeout is not generally proof of non-delivery. Zero emitted request bytes AND no
    // pretransfer, with one of these connection-stage failures, is the narrow exception.
    $notSent=$status===0 && $requestBytes===0 && $pretransfer===0.0 && in_array($errno,[5,6,7,28,35,60],true);
    return ['status'=>$status,'body'=>$body,'headers'=>$headers,'not_sent'=>$notSent,'code'=>$notSent?'CONNECT_NOT_SENT':($errno?'TRANSPORT_UNKNOWN':'HTTP')];
}
function reservation_key_valid(string $key,bool $live): bool {
    // Match the deployment gate: restricted keys are supported, without crossing modes.
    return preg_match($live?'/^(?:sk|rk)_live_[A-Za-z0-9]+$/D':'/^(?:sk|rk)_test_[A-Za-z0-9]+$/D',$key)===1;
}
function reservation_http(array $cfg,string $method,string $path,?string $body,?string $key,string $version): array {
    $live=($cfg['mode']??'test')==='live';
    if(!reservation_key_valid($cfg['stripe_key']??'',$live))
        return ['not_sent'=>true,'status'=>0,'body'=>null,'headers'=>[],'code'=>'LOCAL_KEY'];
    $curl=null;$executing=false;$headers=[];
    try{
        if(!preg_match('#^/v1/checkout/sessions(?:/cs_(?:test|live)_[A-Za-z0-9]+)?(?:\?.*)?$#D',$path))throw new RuntimeException();
        $curl=curl_init('https://api.stripe.com'.$path);if($curl===false)throw new RuntimeException();
        $hh=['Stripe-Version: '.$version,'Authorization: Bearer '.$cfg['stripe_key'],'Content-Type: application/x-www-form-urlencoded'];
        if($key!==null)$hh[]='Idempotency-Key: '.$key;
        $opts=[CURLOPT_RETURNTRANSFER=>true,CURLOPT_CONNECTTIMEOUT=>4,CURLOPT_TIMEOUT=>14,
            CURLOPT_FOLLOWLOCATION=>false,CURLOPT_SSL_VERIFYPEER=>true,CURLOPT_SSL_VERIFYHOST=>2,
            CURLOPT_HTTPHEADER=>$hh,CURLOPT_HEADERFUNCTION=>static function($ch,$line)use(&$headers){
                if(str_starts_with($line,'HTTP/'))$headers=[];
                $parts=explode(':',$line,2);if(count($parts)===2)$headers[strtolower(trim($parts[0]))]=trim($parts[1]);return strlen($line);
            }];
        if($method==='POST'){$opts[CURLOPT_POST]=true;$opts[CURLOPT_POSTFIELDS]=$body;}
        elseif($method!=='GET')throw new RuntimeException();
        if(!curl_setopt_array($curl,$opts))throw new RuntimeException();
        $executing=true;$raw=curl_exec($curl);$decoded=is_string($raw)?json_decode($raw,true):null;
        $size=curl_getinfo($curl,CURLINFO_REQUEST_SIZE);$pre=curl_getinfo($curl,CURLINFO_PRETRANSFER_TIME);
        return reservation_curl_result(curl_errno($curl),(int)curl_getinfo($curl,CURLINFO_RESPONSE_CODE),
            is_int($size)?$size:-1,is_float($pre)?$pre:-1.0,is_array($decoded)?$decoded:null,$headers);
    }catch(Throwable $e){
        return ['not_sent'=>!$executing,'status'=>0,'body'=>null,'headers'=>[],'code'=>$executing?'TRANSPORT_UNKNOWN':'LOCAL_SETUP'];
    }finally{if($curl instanceof CurlHandle)unset($curl);}
}
function reservation_rejected(array $r): bool {
    if(($r['headers']['stripe-should-retry']??'')==='true' ||
       !preg_match('/^req_[A-Za-z0-9]+$/D',$r['headers']['request-id']??''))return false;
    $e=$r['body']['error']??[];$type=$e['type']??'';$code=$e['code']??'';
    if($r['status']===401 && $type==='authentication_error')return true;
    if($r['status']===403 && $type==='permission_error')return true;
    // Do not infer absence from arbitrary 4xx, 409, 429, idempotency_error or a retry hint.
    return $r['status']===400 && $type==='invalid_request_error' &&
        in_array($code,['parameter_missing','parameter_unknown','parameter_invalid_empty','parameter_invalid_integer','parameter_invalid_string_blank','parameter_invalid_boolean','url_invalid'],true);
}
function reservation_session_valid(array $o,array $s,bool $live): bool {
    $q=json_decode($o['quote'],true,512,JSON_THROW_ON_ERROR);
    return ($s['livemode']??null)===$live && ($s['object']??'')==='checkout.session' && ($s['mode']??'')==='payment'
        && preg_match($live?'/^cs_live_[A-Za-z0-9]+$/D':'/^cs_test_[A-Za-z0-9]+$/D',$s['id']??'')
        && ($s['client_reference_id']??null)===$o['id'] && ($s['metadata']['orderId']??null)===$o['id']
        && ($s['currency']??'')==='pln' && ($s['amount_total']??null)===$q['total']
        && ($o['sid']===null || $o['sid']===$s['id'])
        && (($q['delivery_method']??'courier')!=='locker' ||
            (($s['metadata']['delivery_method']??'')==='locker' && ($s['metadata']['pickup_point']??'')===$q['pickup_point']))
        && in_array($s['status']??'', ['open','complete','expired'],true)
        && in_array($s['payment_status']??'', ['paid','unpaid'],true)
        && (($s['payment_status']==='paid') ? $s['status']==='complete' : true)
        && ($s['status']!=='open' || (is_string($s['url']??null) && str_starts_with($s['url'],'https://checkout.stripe.com/')));
}
function reservation_apply_session(PDO $db,array $o,array $s,int $now): void {
    $state=$o['state'];
    if($s['status']==='complete' && $s['payment_status']==='paid')$state=in_array($state,['released','review'],true)?'review':'paid';
    elseif(reservation_held($state)){
        if($s['status']==='expired') {reservation_release($db,$o,'STRIPE_EXPIRED_RELEASE',$now);$state='released';}
        elseif($s['status']==='complete')$state='pending';
        elseif($state!=='pending')$state='reserved'; // An older open observation cannot reopen a pending payment.
    }
    $pi=is_string($s['payment_intent']??null)?$s['payment_intent']:null;
    $db->prepare('UPDATE orders SET state=?,sid=?,url=COALESCE(?,url),pi=COALESCE(?,pi) WHERE id=?')
        ->execute([$state,$s['id'],$s['url']??null,$pi,$o['id']]);
    reservation_history($db,$o['id'],'SESSION_OBSERVED',$now,['status'=>$s['status'],'payment'=>$s['payment_status'],'state'=>$state]);
    reservation_observed($db,$o['id'],$state,$now);
}
function reservation_scan(array $cfg,array $o,array $op,callable $http): array {
    $cursor=null;$found=[];
    for($page=0;$page<5;$page++){
        $query=['limit'=>100,'created'=>['gte'=>max(0,(int)$o['created']-300)]];
        if($cursor!==null)$query['starting_after']=$cursor;
        $r=$http($cfg,'GET','/v1/checkout/sessions?'.http_build_query($query,'','&',PHP_QUERY_RFC3986),null,null,$op['api_version']);
        $list=$r['body']??null;
        if(($r['status']??0)!==200 || !is_array($list) || !is_array($list['data']??null) || !is_bool($list['has_more']??null))return ['code'=>'LOOKUP_FAILED'];
        foreach($list['data']as $s){
            if(!is_array($s))return ['code'=>'LOOKUP_INVALID'];
            if(($s['client_reference_id']??null)===$o['id'] || ($s['metadata']['orderId']??null)===$o['id'])$found[]=$s;
        }
        if(count($found)>1)return ['code'=>'MULTIPLE_SESSIONS'];
        if(!$list['has_more'])return count($found)===1?['session'=>$found[0]]:['code'=>'NOT_FOUND_NOT_PROOF'];
        $last=end($list['data']);$next=$last['id']??null;
        if(!is_string($next)||$next===$cursor||!preg_match('/^cs_(?:test|live)_[A-Za-z0-9]+$/D',$next))return ['code'=>'LOOKUP_INVALID'];
        $cursor=$next;
    }
    return ['code'=>'LOOKUP_INCOMPLETE']; // A bounded/incomplete scan can never prove absence.
}
function reservation_reconcile(PDO $db,array $cfg,string $id,?callable $transport=null,?int $clock=null,?string $knownSession=null): array {
    if($knownSession!==null&&!preg_match('/^cs_(?:test|live)_[A-Za-z0-9]+$/D',$knownSession))problem('SESSION_ID',400,'Nieprawidłowy identyfikator sesji.');
    $now=$clock??time();$http=$transport??'reservation_http';$claim=reservation_claim($db,$cfg,$id,$now,$knownSession!==null);
    if(!$claim)return ['code'=>'BUSY_OR_NOT_DUE'];
    $o=$claim['order'];$op=$claim['operation'];$token=$claim['token'];$result=[];$trace=null;
    try{
        if($o['sid']!==null || $knownSession!==null){
            $r=$http($cfg,'GET','/v1/checkout/sessions/'.($knownSession??$o['sid']),null,null,$op['api_version']);
            $result=($r['status']??0)===200 && is_array($r['body']??null)?['session'=>$r['body']]:['code'=>'RETRIEVE_FAILED'];
        }elseif($o['state']==='pending'){
            // Missing reference is an operational inconsistency, never permission to POST again.
            $result=['code'=>'PENDING_SESSION_MISSING'];
        }else{
            $first=$op['first_attempt']===null?null:(int)$op['first_attempt'];
            $canReplay=$op['request_body']!==null && ($first===null || ($now>=$first && $now-$first<RESERVATION_REPLAY_SECONDS)) && (int)$op['attempts']<8;
            if($canReplay){
                if(!hash_equals($op['body_sha256']??'',hash('sha256',$op['request_body'])))$result=['code'=>'BODY_CHANGED'];
                elseif(!$op['uncertain'] && $first===null && $now>=(int)$o['created']+1800)$result=['release'=>'LOCAL_EXPIRED_UNSENT'];
                else{
                    // Persist uncertainty BEFORE sending; a process crash cannot turn a sent request into "never sent".
                    $sent=tx($db,function()use($db,$id,$token,$now){
                        $op=row($db,'SELECT * FROM checkout_operations WHERE order_id=?',[$id]);
                        $order=row($db,'SELECT * FROM orders WHERE id=?',[$id]);
                        if($op['lease_token']!==$token || !in_array($order['state'],['reserved','reconcile'],true) || $order['sid']!==null)return false;
                        $db->prepare("UPDATE checkout_operations SET status='sending',uncertain=1,first_attempt=COALESCE(first_attempt,?),attempts=attempts+1 WHERE order_id=?")->execute([$now,$id]);
                        $db->prepare("UPDATE orders SET state='reconcile' WHERE id=?")->execute([$id]);
                        reservation_history($db,$id,'CREATE_ATTEMPT',$now);return true;
                    });
                    if(!$sent)return ['code'=>'SUPERSEDED'];
                    $r=$http($cfg,'POST','/v1/checkout/sessions',$op['request_body'],$op['idempotency_key'],$op['api_version']);
                    $trace=['http'=>(int)($r['status']??0),'notSent'=>($r['not_sent']??false)===true];
                    foreach(['reason'=>$r['code']??'','stripeCode'=>$r['body']['error']['code']??'','request'=>$r['headers']['request-id']??'']as $k=>$v)
                        if(is_string($v)&&preg_match('/^[a-zA-Z0-9_]{1,100}$/D',$v))$trace[$k]=$v;
                    if(($r['status']??0)===200 && is_array($r['body']??null))$result=['session'=>$r['body']];
                    elseif(!$op['uncertain'] && (($r['not_sent']??false) || reservation_rejected($r)))
                        $result=['release'=>($r['not_sent']??false)?'LOCAL_NOT_SENT_RELEASE':'STRIPE_REJECTED_RELEASE','http'=>(int)($r['status']??0)];
                    else $result=['code'=>'CREATE_UNKNOWN','http'=>(int)($r['status']??0)];
                }
            }else $result=['code'=>'REPLAY_DISABLED'];
            // Recovery after an earlier unknown result uses metadata/listing, not a fresh operation.
            if(!isset($result['session']) && !isset($result['release']) && $op['uncertain']){
                $scan=reservation_scan($cfg,$o,$op,$http);
                if(isset($scan['session']) || !in_array($result['code']??'',['BODY_CHANGED','REPLAY_DISABLED'],true))$result=$scan;
            }
        }
    }catch(Throwable $e){$result=['code'=>'RECOVERY_EXCEPTION'];}
    return tx($db,function()use($db,$cfg,$id,$token,$now,$result,$trace){
        $op=row($db,'SELECT * FROM checkout_operations WHERE order_id=?',[$id]);
        $o=row($db,'SELECT * FROM orders WHERE id=?',[$id]);
        // Fencing also protects a newer worker or an already-processed webhook from a stale reply.
        if($op['lease_token']!==$token){
            // A valid settlement is never discarded, even if expiration/a newer worker won the lease.
            // Stale open/error responses still have no authority to change inventory or state.
            if(isset($result['session']) && ($result['session']['payment_status']??'')==='paid' &&
               reservation_session_valid($o,$result['session'],($cfg['mode']??'test')==='live')){
                reservation_apply_session($db,$o,$result['session'],$now);return ['code'=>'SETTLEMENT_OBSERVED'];
            }
            return ['code'=>'SUPERSEDED'];
        }
        if($trace!==null)reservation_history($db,$id,'CREATE_RESULT',$now,$trace);
        if(isset($result['session']) && reservation_session_valid($o,$result['session'],($cfg['mode']??'test')==='live')){
            reservation_apply_session($db,$o,$result['session'],$now);return ['code'=>'SESSION_RECOVERED'];
        }
        if(isset($result['release']) && $o['sid']===null && reservation_held($o['state'])){
            reservation_release($db,$o,$result['release'],$now);reservation_observed($db,$id,'released',$now);return ['code'=>'RELEASED'];
        }
        $code=isset($result['session'])?'SESSION_MISMATCH':($result['code']??'UNRESOLVED');
        $escalate=$now>=(int)$o['created']+3600 || (int)$op['checks']>=6 || in_array($code,['BODY_CHANGED','MULTIPLE_SESSIONS','SESSION_MISMATCH','REPLAY_DISABLED'],true);
        $delay=min(3600,30*(2**min(7,max(0,(int)$op['checks']-1))));
        $db->prepare('UPDATE checkout_operations SET status=?,uncertain=1,next_check=?,lease_token=NULL,lease_until=0,last_code=?,escalated_at=CASE WHEN ? THEN COALESCE(escalated_at,?) ELSE escalated_at END WHERE order_id=?')
            ->execute([$escalate?'escalated':'unknown',$now+$delay,$code,$escalate?1:0,$now,$id]);
        if(in_array($o['state'],['reserved','reconcile'],true))$db->prepare("UPDATE orders SET state='reconcile' WHERE id=?")->execute([$id]);
        reservation_history($db,$id,$escalate?'ESCALATED':'RECONCILE_REQUIRED',$now,['reason'=>$code]);
        return ['code'=>$escalate?'ESCALATED':'RECONCILE_REQUIRED'];
    });
}
function stripe_session(array $cfg,array $o,?PDO $db=null,?callable $transport=null,?int $now=null): array {
    if($db===null)unavailable(); // The unsafe, untracked transport is no longer callable.
    $current=row($db,'SELECT * FROM orders WHERE id=?',[$o['id']])??$o;
    checkout_state($current,true);
    // A pending customer's explicit check retrieves the saved session immediately.
    // The existing lease still fences simultaneous requests and webhook races.
    $known=$current['state']==='pending'?$current['sid']:null;
    $now??=time();reservation_reconcile($db,$cfg,$o['id'],$transport,$now,$known);
    $fresh=row($db,'SELECT * FROM orders WHERE id=?',[$o['id']]);
    checkout_state($fresh);
    if($fresh['state']==='reserved' && is_string($fresh['url']) && $now<(int)$fresh['created']+3600)return ['id'=>$fresh['sid'],'url'=>$fresh['url']];
    problem('RECONCILE',409,'Sprawdzamy wynik tej próby płatności. Ponów tę samą próbę za chwilę; nie składaj nowej.');
}
