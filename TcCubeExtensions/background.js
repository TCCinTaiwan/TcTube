console.log('background.js running...');

/**************************************************
* Chrome browserAction.onClicked Listener
**************************************************/
chrome.browserAction.onClicked.addListener(function(tab)
{
    console.log('InsertCSS browserAction click');
    chrome.tabs.insertCSS(
        tab.id,
        {
            file: "player.css",
            "allFrames": true
        }, function() {
            console.log('css file has inserted.');
        }
    );
});

chrome.commands.onCommand.addListener(function(command)
{
    console.debug('command is : ' + command);
    if (command == 'reload_extension') {
        cchrome.runtime.reload();
    }
});