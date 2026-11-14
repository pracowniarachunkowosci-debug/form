<?php
declare(strict_types=1);

// Manager Paczek issues different credentials for the server-side Points API and for the browser map.
function inpost_token(mixed $value): bool {
    return is_string($value) && preg_match('/^[A-Za-z0-9._~+\/=:-]{8,8192}$/D',$value)===1;
}
function inpost_mock_notice(): string { return 'TEST / MOCK — bez połączenia z InPost'; }
function inpost_mock_enabled(array $cfg): bool {
    if(!array_key_exists('inpost_points_mock',$cfg))return false;
    // Explicit opt-in only. A malformed flag must never fall through to the real provider.
    if($cfg['inpost_points_mock']!==true || ($cfg['mode']??null)!=='test' || live_host() ||
       array_key_exists('inpost_points_token',$cfg) || array_key_exists('inpost_geowidget_token',$cfg))
        problem('POINTS_CONFIG',503,'Nieprawidłowa konfiguracja testowego adaptera Points.');
    return true;
}
function inpost_mock_fixtures(): array {
    static $fixtures=null;
    return $fixtures??=require __DIR__.'/_inpost_mock.php';
}
function inpost_settings(array $cfg): array {
    if(inpost_mock_enabled($cfg))return ['locker_available'=>true,'geowidget_token'=>null,
        'points_provider'=>'mock','points_notice'=>inpost_mock_notice(),
        'test_points'=>array_map(fn($id,$fixture)=>['id'=>$id,'label'=>$fixture['label']],
            array_keys(inpost_mock_fixtures()),array_values(inpost_mock_fixtures()))];
    $enabled=inpost_token($cfg['inpost_points_token']??null);
    $geo=$cfg['inpost_geowidget_token']??null;
    // In particular, do not leak a private API token accidentally copied to both settings.
    $public=$enabled && inpost_token($geo) && !hash_equals($cfg['inpost_points_token'],$geo)
        && !in_array($geo,[$cfg['stripe_key']??null,$cfg['webhook_secret']??null,$cfg['abuse_hmac']??null],true);
    return ['locker_available'=>$enabled,'geowidget_token'=>$public?$geo:null];
}
function delivery_rates(array $policy): array {
    $rates=['courier'=>$policy['smallOrderCourierGrosz']??null,'locker'=>$policy['smallOrderLockerGrosz']??null];
    foreach($rates as $rate)if(!is_int($rate)||$rate<=0||$rate>100000)unavailable();
    return $rates;
}
function point_id(mixed $id): string {
    $normalized=is_string($id)?strtoupper(trim($id)):'';
    if(!preg_match('/^[A-Z0-9][A-Z0-9_-]{2,31}$/D',$normalized))problem('PICKUP_POINT',422,'Podaj kod automatu Paczkomat® z listy InPost.');
    return $normalized;
}
function point_unavailable(): never {
    problem('POINTS_UNAVAILABLE',503,'Nie udało się potwierdzić punktu w InPost. Spróbuj ponownie lub wybierz kuriera.');
}
function point_invalid(): never {
    problem('PICKUP_POINT',422,'Ten automat nie jest dostępny do odbioru. Wybierz inny Paczkomat®.');
}
function canonical_point(string $id,array $result): array {
    if(!is_array($result['items']??null))point_unavailable();
    if(count($result['items'])!==1)point_invalid();
    $p=$result['items'][0]??null;$types=$p['type']??null;$functions=$p['functions']??null;
    // Query the domestic (PL) directory with the physical-lockers-only filter. Some real lockers only
    // report the broad "parcel_locker" type in their response. Never accept POP, virtual or disabled.
    if(!is_array($p)||($p['name']??null)!==$id||($p['status']??null)!=='Operating'||!is_array($types)||
       !array_intersect(['parcel_locker','parcel_locker_only'],$types)||array_intersect(['pop','parcel_locker_superpop'],$types)||
       !in_array($p['virtual']??null,[0,'0',false],true)||!is_array($functions)||!in_array('parcel_collect',$functions,true)||
       ($p['country']??'PL')!=='PL'||($p['address_details']['country_code']??'PL')!=='PL')point_invalid();
    $post=$p['address_details']['post_code']??null;$city=$p['address_details']['city']??null;$street=$p['address']['line1']??null;
    if(!is_string($post)||!preg_match('/^\d{2}-\d{3}$/D',$post)||!is_string($city)||!is_string($street))point_invalid();
    $city=trim($city);$street=trim($street);$address=$street.', '.$post.' '.$city;
    if($city===''||$street===''||strlen($address)>460||preg_match('/[\x00-\x1f\x7f]/',$address))point_invalid();
    return ['id'=>$id,'address'=>$address];
}
function lookup_point(array $cfg,string $id): array {
    $id=point_id($id);if(!inpost_settings($cfg)['locker_available'])point_unavailable();
    if(inpost_mock_enabled($cfg)){
        $fixture=inpost_mock_fixtures()[$id]??null;
        if(!$fixture)problem('PICKUP_POINT',422,inpost_mock_notice().' — nieznany kod testowy.');
        if(isset($fixture['error']))problem('POINTS_UNAVAILABLE',503,inpost_mock_notice().' — symulowana awaria API Points.');
        try{$point=canonical_point($id,$fixture['response']);}
        catch(StoreError $e){problem($e->kind,$e->status,inpost_mock_notice().' — '.$e->getMessage());}
        return $point+['provider'=>'mock','notice'=>inpost_mock_notice()];
    }
    // TEST codes cannot be sent to either real directory, even after disabling the mock.
    if(str_starts_with($id,'TEST'))point_invalid();
    if(!in_array($cfg['mode']??null,['test','live'],true))point_unavailable();
    $base=$cfg['mode']==='live'?'https://api.inpost.pl/v1/points':'https://sandbox-api-gateway-pl.easypack24.net/v1/points';
    $query=http_build_query(['name'=>$id,'type'=>'parcel_locker_only','functions'=>'parcel_collect','virtual'=>0,'per_page'=>1],'','&',PHP_QUERY_RFC3986);
    $ch=curl_init($base.'?'.$query);$raw='';
    curl_setopt_array($ch,[CURLOPT_HTTPHEADER=>['Accept: application/json','Authorization: Bearer '.$cfg['inpost_points_token']],
        CURLOPT_FOLLOWLOCATION=>false,CURLOPT_CONNECTTIMEOUT=>2,CURLOPT_TIMEOUT=>5,
        CURLOPT_WRITEFUNCTION=>static function($ch,string $part)use(&$raw):int {
            if(strlen($raw)+strlen($part)>65536)return 0;$raw.=$part;return strlen($part);
        }]);
    $ok=curl_exec($ch);$status=curl_getinfo($ch,CURLINFO_RESPONSE_CODE);
    if($ok===false||$status!==200)point_unavailable();
    $data=json_decode($raw,true);if(!is_array($data))point_unavailable();
    return canonical_point($id,$data);
}
