console.log("Content Script is running...");
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    console.log(request);
    if (request.action == "getVideoUrls") {
        console.log("getVideoUrls");
        videos = document.getElementsByTagName("video");
        urls = [];
        for (var i = 0; i < videos.length; i++) {
            urls.push(videos[i].src);
        }
        sendResponse({data: urls, action: request.action});
    } else {
        sendResponse({});
    }
});