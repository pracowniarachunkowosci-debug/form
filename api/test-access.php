<?php
declare(strict_types=1);require_once __DIR__.'/_common.php';headers_private();
header("Content-Security-Policy: default-src 'none'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'");
try{
    $cfg=configuration();
    $failed=false;
    if(($_SERVER['REQUEST_METHOD']??'')==='POST'){
        require_origin($cfg);$input=$_POST['token']??null;
        if(!is_string($input)||strlen($input)>512||!hash_equals($cfg['login_sha256'],hash('sha256',$input))){http_response_code(403);$failed=true;}
        else{browser_session();session_regenerate_id(true);$_SESSION['tester_until']=time()+4*3600;session_write_close();header('Location: /winter-zestaw-4.html?size=6#kompozycja',true,303);exit;}
    }else method('GET');
}catch(Throwable $e){http_response_code(404);exit;}
?><!doctype html><html lang="pl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Test zakupowy WINTER 26</title><main><h1>Dostęp do testu zakupowego</h1><p>W tym sklepie testowym nie są pobierane pieniądze ani wysyłane produkty. Używaj wyłącznie danych testowych.</p><?php if($failed){echo '<p role="alert">Niepoprawny token testera.</p>';} ?><form method="post"><label>Token testera <input required type="password" name="token" maxlength="512" autocomplete="off"></label><button>Wejdź do sklepu testowego</button></form></main></html>
