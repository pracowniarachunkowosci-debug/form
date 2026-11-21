<?php
declare(strict_types=1);
// Creation is allowed only on the purchase/dispatch path. Status never creates identity.
function checkout_identity(string $mode,bool $create=false): array {
    if(!in_array($mode,['test','live'],true))unavailable();
    $name=$mode==='test'?'pf_winter_sandbox':'pf_checkout_customer';
    if(!$create&&empty($_COOKIE[$name]))return ['tester'=>false,'owner'=>null];
    session_name($name);ini_set('session.use_strict_mode','1');ini_set('session.use_only_cookies','1');
    session_set_cookie_params(['lifetime'=>0,'path'=>'/api/','secure'=>true,'httponly'=>true,'samesite'=>'Strict']);
    if(!session_start($create?[]:['read_and_close'=>true]))unavailable();
    $tester=($_SESSION['tester_until']??0)>time();
    if($create&&($mode==='live'||$tester))$_SESSION['visitor']??=bin2hex(random_bytes(18));
    $owner=$_SESSION['visitor']??null;
    if($create)session_write_close();
    return ['tester'=>$tester,'owner'=>is_string($owner)&&preg_match('/^[a-f0-9]{36}$/D',$owner)?$owner:null];
}
function checkout_test_owner(): string {
    $identity=checkout_identity('test',true);
    if(!$identity['tester']||$identity['owner']===null)problem('TEST_ACCESS',403,'Wymagany dostęp testera.');
    return $identity['owner'];
}
