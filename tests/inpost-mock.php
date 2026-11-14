<?php
declare(strict_types=1);
require_once __DIR__.'/../api/_common.php';
function mock_check(bool $ok,string $why):void {if(!$ok)throw new RuntimeException($why);}
function mock_rejected(string $kind,callable $fn):void {
    try{$fn();}catch(StoreError $e){mock_check($e->kind===$kind,'expected '.$kind.', got '.$e->kind);return;}
    throw new RuntimeException('expected '.$kind);
}
$mockCfg=['mode'=>'test','inpost_points_mock'=>true];$mockInfo=inpost_settings($mockCfg);
mock_check($mockInfo['locker_available']&&$mockInfo['geowidget_token']===null&&$mockInfo['points_provider']==='mock','explicit mock, no widget');
mock_check($mockInfo['points_notice']===inpost_mock_notice(),'public provenance');
foreach($mockInfo['test_points'] as $point)mock_check(str_starts_with($point['id'],'TEST')&&array_keys($point)===['id','label'],'only synthetic IDs and labels, no address from picker');
foreach([null,false,0,1,'true','mock',[],['url'=>'https://example.invalid']] as $flag){
    mock_rejected('POINTS_CONFIG',fn()=>inpost_settings(['mode'=>'test','inpost_points_mock'=>$flag]));
    mock_rejected('POINTS_CONFIG',fn()=>lookup_point(['mode'=>'live','inpost_points_mock'=>$flag],'TEST01M'));
}
foreach(['live','unknown',null] as $mode)mock_rejected('POINTS_CONFIG',fn()=>lookup_point(['mode'=>$mode,'inpost_points_mock'=>true],'TEST01M'));
foreach(['inpost_points_token','inpost_geowidget_token'] as $key)
    mock_rejected('POINTS_CONFIG',fn()=>lookup_point($mockCfg+[$key=>'never-use-this-token'],'TEST01M'));
$savedHost=$_SERVER['HTTP_HOST']??null;$_SERVER['HTTP_HOST']='pracowniaform.com';
try{mock_rejected('POINTS_CONFIG',fn()=>lookup_point($mockCfg,'TEST01M'));}
finally{if($savedHost===null)unset($_SERVER['HTTP_HOST']);else $_SERVER['HTTP_HOST']=$savedHost;}
foreach(['test','live'] as $mode)mock_rejected('PICKUP_POINT',fn()=>lookup_point(['mode'=>$mode,'inpost_points_token'=>'synthetic-token'],'TEST01M'));
$firstPoint=lookup_point($mockCfg,' test01m ');$secondPoint=lookup_point($mockCfg,'TEST02M');
mock_check($firstPoint['id']==='TEST01M'&&$secondPoint['id']==='TEST02M'&&$firstPoint['address']!==$secondPoint['address'],'manual normalization and distinct selections');
mock_check(str_contains($firstPoint['address'],inpost_mock_notice()),'canonical address carries durable provenance');
foreach(['WRO01M','TESTUNKNOWN','TESTOFF','TESTBAD','https://example.invalid','../TEST01M'] as $id)
    mock_rejected('PICKUP_POINT',fn()=>lookup_point($mockCfg,$id));
foreach(['TESTBROKEN','TESTERROR'] as $id)mock_rejected('POINTS_UNAVAILABLE',fn()=>lookup_point($mockCfg,$id));
$mockPolicy=policy();$mockSlot=['modelId'=>'full-soft','colorId'=>'marble'];
$mockInput=['requestId'=>'12345678-1111-4111-8111-111111111111','selections'=>[$mockSlot],'delivery_method'=>'locker','pickup_point'=>' test01m '];
foreach([1=>5000,2=>8400,4=>15000,6=>22000,8=>29000] as $size=>$price){
    foreach(['locker'=>1849,'courier'=>2049] as $method=>$fee){
        $input=array_merge($mockInput,['selections'=>array_fill(0,$size,$mockSlot),'delivery_method'=>$method]);
        if($method==='courier')unset($input['pickup_point']);
        $quote=quote($input,$mockPolicy);
        mock_check($quote['total']===$price+($size>=6?0:$fee),'all unchanged prices and delivery thresholds');
    }
}
$mixed=$mockInput;unset($mixed['selections']);$mixed['packs']=[array_fill(0,2,$mockSlot),array_fill(0,4,$mockSlot)];
$mixedQuote=quote($mixed,$mockPolicy);mock_check($mixedQuote['total']===23400&&$mixedQuote['shipping']===0,'2+4 aggregates free delivery');
mock_rejected('BAD_REQUEST',fn()=>quote($mockInput+['pickup_address'=>'Client invented address'],$mockPolicy));
mock_rejected('BAD_REQUEST',fn()=>quote($mockInput+['inpost_points_mock'=>true],$mockPolicy));
$mockDb=database(['db_file'=>':memory:']);$mockDb->exec("INSERT INTO stock VALUES('full-soft:marble',80)");
foreach(['TESTOFF'=>'PICKUP_POINT','TESTBAD'=>'PICKUP_POINT','TESTERROR'=>'POINTS_UNAVAILABLE','TESTBROKEN'=>'POINTS_UNAVAILABLE'] as $id=>$kind){
    $bad=quote(array_merge($mockInput,['pickup_point'=>$id]),$mockPolicy);
    mock_rejected($kind,fn()=>order($mockDb,$mockInput['requestId'],$bad,null,fn($id)=>lookup_point($mockCfg,$id)));
    mock_check((int)$mockDb->query('SELECT COUNT(*) FROM orders')->fetchColumn()===0&&(int)$mockDb->query('SELECT n FROM stock')->fetchColumn()===80,'failed lookup never reserves');
}
$mockQuote=quote($mockInput,$mockPolicy);
$mockOrder=order($mockDb,$mockInput['requestId'],$mockQuote,null,fn($id)=>lookup_point($mockCfg,$id));
$savedMock=json_decode($mockOrder['quote'],true);
mock_check($savedMock['pickup_point']==='TEST01M'&&$savedMock['pickup_address']===$firstPoint['address'],'saved canonical ID/address and mock provenance');
$mockRetry=order($mockDb,$mockInput['requestId'],$mockQuote,null,fn()=>throw new RuntimeException('retry must not resolve again'));
mock_check($mockRetry['id']===$mockOrder['id']&&(int)$mockDb->query('SELECT n FROM stock')->fetchColumn()===79,'idempotent reservation');
mock_rejected('REQUEST_CONFLICT',fn()=>order($mockDb,$mockInput['requestId'],quote(array_merge($mockInput,['pickup_point'=>'TEST02M']),$mockPolicy)));
$courier=$mockInput;$courier['delivery_method']='courier';unset($courier['pickup_point']);
mock_rejected('REQUEST_CONFLICT',fn()=>order($mockDb,$mockInput['requestId'],quote($courier,$mockPolicy)));
$courier['requestId']='22345678-1111-4111-8111-111111111111';
$courierOrder=order($mockDb,$courier['requestId'],quote($courier,$mockPolicy),null,fn()=>throw new RuntimeException('courier never resolves a point'));
$courierSaved=json_decode($courierOrder['quote'],true);
mock_check($courierSaved['pickup_point']===null&&!isset($courierSaved['pickup_address'])&&$courierSaved['total']===7049,'courier clears point and uses courier rate');
$mockParams=checkout_params($mockOrder,'https://test.invalid');
mock_check($mockParams['metadata']['pickup_point']==='TEST01M'&&$mockParams['metadata']['pickup_address']===$firstPoint['address'],'payment metadata retains canonical provenance');
mock_check(str_contains($mockParams['custom_text']['submit']['message'],inpost_mock_notice()),'checkout explicitly discloses mock');
echo "PASS: MOCK Points explicit opt-in, Live/malformed/token guards, TEST-only fixtures/errors, prices/2+4, canonical order address, courier switch and idempotency. No network.\n";
