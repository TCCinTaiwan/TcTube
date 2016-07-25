console.log("Content Script is running...");
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    console(request);
    if (request.action == "getVideoUrls") {
        console.log("getVideoUrls");
        videos = document.getElementsByTagName("video");
        urls = [];
        for (var i = 0; i < videos.length; i++) {
            urls.append(videos[i].src);
        }
        sendResponse({data: urls, action: request.action});
    } else {
        sendResponse({}); // Send nothing..
    }
});