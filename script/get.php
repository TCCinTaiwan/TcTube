<?
    for ($i = 1; $i < $argc; $i++) {
        $get = preg_split("/=/", $argv[$i]);
        $_GET[$get[0]] = $get[1];
    }
    var_dump($_GET);
?>