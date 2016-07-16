<?php
for ($i = 1; $i <= 10; $i++):
    sleep(1);
    echo "Count = $i\n";
    ob_flush();
    flush();
endfor;
?>