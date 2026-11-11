<?php
declare(strict_types=1);if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
require_once __DIR__.'/_common.php';
// Separate sandbox database; only a new, empty stock ledger may be initialized.
if(count($argv)!==2){fwrite(STDERR,"Usage: php api/seed-test.php /private/config.json\n");exit(2);}
$path=realpath($argv[1]);$cfg=$path?json_decode(file_get_contents($path),true):null;
if(!$cfg || !str_starts_with($cfg['stripe_key']??'','sk_test_') || !isset($cfg['sandbox_stock']) || !is_array($cfg['sandbox_stock']) || !$cfg['sandbox_stock'])exit(2);
$root=realpath(dirname(__DIR__));$directory=realpath(dirname($cfg['db_file']??''));
if(!$directory || under($directory,$root) || under($path,$root) || !str_starts_with($cfg['db_file'],'/') || is_link($cfg['db_file'])){fwrite(STDERR,"Private config and database required.\n");exit(2);}
$db=database($cfg);tx($db,function()use($db,$cfg){
    if($db->query('SELECT COUNT(*) FROM stock')->fetchColumn() || $db->query('SELECT COUNT(*) FROM orders')->fetchColumn())throw new RuntimeException('Existing stock/orders; not reseeding.');
    $db->prepare('INSERT INTO store_meta(name,value) VALUES(?,?)')->execute(['mode','test']);
    foreach($cfg['sandbox_stock'] as $sku=>$n){if(!is_string($sku)||!valid_key($sku,policy())||!is_int($n)||$n<0||$n>10000)throw new RuntimeException('Invalid test stock');$db->prepare('INSERT INTO stock(sku,n) VALUES(?,?)')->execute([$sku,$n]);}
});echo "Sandbox stock initialized.\n";
