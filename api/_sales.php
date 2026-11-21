<?php
declare(strict_types=1);
// Admission lock only. Existing payments, webhooks and P0 reconciliation remain independent.
function sales_admission(array $cfg) {
    $path=$cfg['sales_control_file']??null;
    if($path===null&&($cfg['mode']??'test')==='test')return null;
    $root=realpath($_SERVER['DOCUMENT_ROOT']??dirname(__DIR__));
    $real=is_string($path)?realpath($path):false;
    if(!$root||!$real||$real!==$path||is_link($path)||under($real,$root)||!is_file($real))unavailable();
    $file=@fopen($real,'rb');if(!$file||!@flock($file,LOCK_SH)){if($file)fclose($file);unavailable();}
    $raw=stream_get_contents($file,4097);$state=json_decode($raw,true);
    if(strlen($raw)>4096||!is_array($state)||($state['schema']??null)!==1||($state['paused']??null)!==false){
        fclose($file);problem('SALES_PAUSED',503,'Przyjmowanie nowych zamówień jest chwilowo wstrzymane. Opłacone zamówienia realizujemy.');
    }
    return $file;
}
