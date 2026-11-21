<?php
declare(strict_types=1);require __DIR__.'/../ops/staging-runtime/gateway.php';
function need_route(bool $ok):void{if(!$ok)throw new RuntimeException('routing assertion');}
$tmp=sys_get_temp_dir().'/pf-routing-'.bin2hex(random_bytes(6));mkdir($tmp);$tmp=str_replace('\\','/',realpath($tmp));
try{
 foreach(['release-a123','release-b123'] as $release){mkdir($tmp.'/'.$release);mkdir($tmp.'/'.$release.'/public');mkdir($tmp.'/'.$release.'/public/api');file_put_contents($tmp.'/'.$release.'/public/api/checkout.php','<?php return '.var_export($release,true).';');}
 foreach(['release-a123','release-b123','release-a123'] as $release){$target=pf_gateway_target($tmp,$release,'/api/checkout.php');need_route((require $target)===$release);if(in_array('--cached',$argv,true))need_route(opcache_is_script_cached($target));}
 foreach([['../outside','/api/checkout.php'],['release-a123','/api/checkout.php/extra'],['release-a123','/api/_common.php'],['release-a123','/api/%63heckout.php'],['release-a123','/api/../../other.php']] as [$r,$u]){
  try{pf_gateway_target($tmp,$r,$u);throw new LogicException('unsafe route');}catch(RuntimeException $e){}
 }
 echo "PASS immutable absolute routing A/B/A, traversal, private scripts, path-info and encoded route rejection. No server changes.".(in_array('--cached',$argv,true)?' OPcache hits verified; timestamp validation and path revalidation disabled.':'')."\n";
}finally{foreach(['release-a123','release-b123']as $r){unlink($tmp.'/'.$r.'/public/api/checkout.php');rmdir($tmp.'/'.$r.'/public/api');rmdir($tmp.'/'.$r.'/public');rmdir($tmp.'/'.$r);}rmdir($tmp);}
