# [:octocat:TcTube](https://github.com/TCCinTaiwan/TcTube)

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
| IE 11+ △ | Chrome 4.0+ ✔ | Firefox 16.0+ ✔ | Opera 15.0+ ✖ | Safari 4.0+ ✖ |

## Installation [↶]()
```bash
# Clone the repository
git clone https://github.com/TCCinTaiwan/TcTube
```
修改static/playlist.json，加入自己的歌
檔案要放在media/video/

## Usage [↶]()
run Server:
```bash
# Go into the directory
cd TcTube

# run server
python main.py
```

## Todo [↶]()
1. 部分歌曲無法調整時間Bug
2. 控制面板延遲
3. APP化
4. 資料庫
5. 頁面歷史
6. 播放清單
7. 影片嵌入支援
    - Vimeo.com
    - 優酷
    - 土豆網
    - 愛奇藝
    - FaceBook https://developers.facebook.com/docs/plugins/embedded-video-player
8. 影片預覽
9. SSL
10. 選項:
    - 下載檔名格式
11. mimetype:hachoir
12. IE9:
    - json
13. flv 不支援

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