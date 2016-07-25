chrome.tabs.query({}, function(tabs) {
    console.log(tabs);
    for (var i = 0; i < tabs.length; i++)
    {
        console.log(tabs[i].url, tabs[i].title);
    }
    chrome.tabs.getSelected(null, function(tab) {
        chrome.tabs.sendMessage(
            tab.id,
            {action: "getVideoUrls"},
            function(response) {
                console.log(response);
            }
        );
    });
});