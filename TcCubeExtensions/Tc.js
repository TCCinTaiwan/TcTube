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
                if (typeof response !== "undefined"){
                    if (response.data.length > 0) {
                        video.src = response.data[0];
                    } else {
                        window.close();
                    }
                } else {
                    window.close();
                }
            }
        );
    });
});