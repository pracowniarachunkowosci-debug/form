<?php
declare(strict_types=1);
// Synthetic source data, not a public API. Included only by the explicit test adapter.
if(realpath($_SERVER['SCRIPT_FILENAME']??'')===__FILE__){http_response_code(404);exit;}
$make=static fn(string $id,string $street)=>['name'=>$id,'type'=>['parcel_locker'],'status'=>'Operating',
    'virtual'=>0,'country'=>'PL','functions'=>['parcel_collect'],
    'address_details'=>['post_code'=>'00-000','city'=>'Miasto Testowe'],
    'address'=>['line1'=>'TEST / MOCK — bez połączenia z InPost — '.$street]];
$first=$make('TEST01M','Fikcyjna 1');$second=$make('TEST02M','Fikcyjna 2');
return [
    'TEST01M'=>['label'=>'TEST01M — punkt syntetyczny A','response'=>['items'=>[$first]]],
    'TEST02M'=>['label'=>'TEST02M — punkt syntetyczny B','response'=>['items'=>[$second]]],
    'TESTOFF'=>['label'=>'TESTOFF — punkt nieczynny','response'=>['items'=>[array_merge($make('TESTOFF','Fikcyjna 3'),['status'=>'NonOperating'])]]],
    'TESTBAD'=>['label'=>'TESTBAD — nieprawidłowe dane adresu','response'=>['items'=>[array_merge($make('TESTBAD','Fikcyjna 4'),['address_details'=>['city'=>'Miasto Testowe','post_code'=>'invalid']])]]],
    'TESTBROKEN'=>['label'=>'TESTBROKEN — wadliwa odpowiedź API','response'=>['items'=>null]],
    'TESTERROR'=>['label'=>'TESTERROR — symulowana awaria API','error'=>'unavailable'],
];
