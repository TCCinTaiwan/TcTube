<?php
    for ($i = 1; $i < $argc; $i++) {
        $get = preg_split("/=/", $argv[$i]);
        $_GET[$get[0]] = $get[1];
    }
    echo "Hello\n";
    ob_flush();
    flush();
    sleep(1);
    if (isset($_GET['name'])) {
        echo $_GET['name'];
    } else {
        echo "World!";
    }
    ob_flush();
    flush();
?>