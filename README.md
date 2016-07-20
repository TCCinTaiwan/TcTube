# [:octocat:TcTube](https://github.com/TCCinTaiwan/TcTube)
[![Gitter](https://badges.gitter.im/TCCinTaiwan/TcTube.svg)](https://gitter.im/TCCinTaiwan/TcTube?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge) [![Build Status](https://travis-ci.org/TCCinTaiwan/TcTube.svg?branch=TCC)](https://travis-ci.org/TCCinTaiwan/TcTube)

## Contents [↶]()
* **[Introduction](#introduction)**
* **[Browser Support](#browser-support)**
* **[Installation](#installation)**
* **[Usage](#usage)**
* **[Todo](#todo)**
* **[Contributing](#contributing)**
* **[History](#history)**
* **[License](#license)**

## Introduction [↶]()
這是2016年暑假，我在系上實習，老師叫我們做的系統，我用去年寫的播放器加以改進。

## Browser Support [↶]()
| ![IE](https://raw.github.com/alrra/browser-logos/master/internet-explorer/internet-explorer_48x48.png) | ![Chrome](https://raw.github.com/alrra/browser-logos/master/chrome/chrome_48x48.png) | ![Firefox](https://raw.github.com/alrra/browser-logos/master/firefox/firefox_48x48.png) | ![Opera](https://raw.github.com/alrra/browser-logos/master/opera/opera_48x48.png) | ![Safari](https://raw.github.com/alrra/browser-logos/master/safari/safari_48x48.png) |
| --- | --- | --- | --- | --- |
| IE 9+ △ | Chrome 4.0+ ✔ | Firefox 16.0+ ✔ | Opera 15.0+ ✖ | Safari 4.0+ ✖ |

## Installation [↶]()
```bash
# Clone the repository
git clone https://github.com/TCCinTaiwan/TcTube
```
音樂檔案要放在 media/video/
修改 [static/playlist.json](static/playlist.json)，改成自己的歌
```json
[
    {
        "file": "filename.webm",
        "title": "Title",
        "artist": "Artist"
    }
]
```
## Usage [↶]()
run Server:
```bash
# Go into the directory
cd TcTube

# run server
python main.py
```

## Todo [↶]()
1. 資料庫
2. 控制面板延遲
3. APP化
4. 頁面歷史
5. 播放清單
6. 影片嵌入支援
    - Vimeo.com
    - 優酷 http://open.youku.com/tools
    - 土豆網
    - 愛奇藝
    - FaceBook https://developers.facebook.com/docs/plugins/embedded-video-player
    - flv
7. 影片預覽
8. SSL
9. 選項:
    - 下載檔名格式
10. mimetype:hachoir
11. Blob
12. 資料庫歌單
13. Youtube Rate onWeel
14. 時間進度Seekable

## Contributing [↶]()
1. Create an issue and describe your idea
2. Fork it!
3. Create your feature branch: `git checkout -b my-new-feature`
4. Commit your changes: `git commit -m 'Add some feature'`
5. Push to the branch: `git push origin my-new-feature`
6. Submit a Pull Request

## History [↶]()
For detailed changelog, check [Change Log](CHANGELOG.md).

## License [↶]()
check [License](LICENSE).