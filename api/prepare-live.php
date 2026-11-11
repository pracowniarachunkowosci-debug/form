<?php
declare(strict_types=1);if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
require_once __DIR__.'/_common.php';
// Runs on an operator workstation or SSH account; NEVER generate a new DB over a running shop.
if(count($argv)<3 || !in_array($argv[1],['fingerprint','init-inventory'],true)){fwrite(STDERR,"php api/prepare-live.php fingerprint /private/public-settings.json [path-to-built-www]\nphp api/prepare-live.php init-inventory /private/physical-stock.json /private/NEW.sqlite\n");exit(2);}
$path=realpath($argv[2]);$root=realpath(dirname(__DIR__));if(!$path||under($path,$root))exit(2);
$input=json_decode(file_get_contents($path),true,512,JSON_THROW_ON_ERROR);
if($argv[1]==='fingerprint'){if(isset($argv[3])){$root=realpath($argv[3]);if(!$root)exit(2);} echo live_approval($input,$root)."\n";exit;}
if(count($argv)!==4 || !str_starts_with($argv[3],'/') || file_exists($argv[3]) || is_link($argv[3]) ||
    !is_dir(dirname($argv[3])) || under(realpath(dirname($argv[3])),$root))exit(2);
$keys=[];foreach(policy()['eligibleModelIds']as $m)foreach(['dual','red-matte','white','marble']as $col)$keys[]=$m.':'.$col;
if(!is_array($input)|| count($input)!==12 || array_diff($keys,array_keys($input)))exit(2);
foreach($input as $sku=>$n)if(!is_int($n)||$n<0)exit(2);
$db=database(['db_file'=>$argv[3]]);tx($db,function()use($db,$input){
    $db->prepare('INSERT INTO store_meta(name,value) VALUES(?,?)')->execute(['mode','live']);
    foreach($input as $sku=>$n)$db->prepare('INSERT INTO stock(sku,n) VALUES(?,?)')->execute([$sku,$n]);
});$db=null;echo "New, closed production inventory database created from supplied physical counts. Checkout has NOT been activated.\n";
