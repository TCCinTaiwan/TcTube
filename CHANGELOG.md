# TcTube

## [↶Back to ReadMe](README.md)

## 0.3.2
* 2016-08-19
    - 增加upgrade.py
    - 更新函式庫版本
    - 更新nginx設定檔
* 2016-08-18
    - nginx.conf加註解
* 2016-08-16
    - Fuck upstream_addr and sendfile!
* 2016-08-08
    - 測試負載平衡
* 2016-08-05
    - 修正播放器音量移不上去問題
    - 修正路徑錯誤問題
    - 該死的載入圖片
    - 回報播放時間測試版
    - Online API 結構微調
    - 簡單頁面歷史

## 0.3.1
* 2016-08-04
    - 簡單跑馬燈消失
* 2016-08-03
    - 修正dtree歪掉問題
    - soket修正
* 2016-08-02
    - Linux支持
    - 已登入重導向
    - 表格樣式更新
    - Chat前導片
* 2016-08-01
    - 放棄使用GUI
    - 調整Nginx為主要Server轉址到Flask
    - 修理路徑問題
    - 效能調整
    - IP判別更新
    - API 增加:
        + 連線人數
        + 標頭

## 0.3.0
* 2016-07-31
    - 套用GUI

## 0.2.9
* 2016-07-31
    - 加入colorama
    ```
    Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    Style: DIM, NORMAL, BRIGHT, RESET_ALL
    ```
    - 測試Server GUI
* 2016-07-30
    - 修正播放清單到網頁JavaScript中，'會變成&#39;問題
    - 加入截圖
    - 推播

## 0.2.8
* 2016-07-29
    - 密碼開始加密
    - 寫測試檔
* 2016-07-28
    - 加入壓縮
    - 加入cache_control
    - 更新requirements.txt、setup.py
    - 加入API

## 0.2.7
* 2016-07-27
    - 播放清單改用資料庫儲存
    - 修正JavaScript播放清單程式
    - 資料庫更新
    - 加入選單部分圖示
    - 更新Installation指示
    - 管理公告草稿

## 0.2.6
* 2016-07-26
    - TcCube 擴充套件抓影片
    - 跑馬燈、選單使用資料庫
* 2016-07-25
    - setup.py草稿
    - ReadMe加入Coding Style
* 2016-07-23
    - 初步Chrome Extensions

## 0.2.5
* 2016-07-22
    - 簡單加入跑馬燈
    - 登入權限
    - 加入dTree選單
    - 更改logout觸發方式
    - requirements草稿
    - 首頁基本版型
    - dTree onclick()
    - 修正未登入重導向錯誤Bug

## 0.2.4
* 2016-07-21
    - 修正全螢幕不同步問題(F11)
    - 面板功能部分修補:
        + 影像同步
        + 一起換首

## 0.2.3
* 2016-07-20
    - 整理Login logout功能
    - 修正isUndefined($) 導致影片不能播放Bug
    - 取消使用isUndefined，因為會有錯誤
* 2016-07-19
    - Login部分功能
* 2016-07-18
    - 分離CSS Javascript
    - 開始使用isUndefined
    - ChangLog使用倒敘法
    - SQL草稿

## 0.2.2
* 2016-07-17
    - IE9 部分JavaScript支援
    - 修正/video/<int> 亂導引Bug
    - 按鍵:
        * 0~9: 跳到播放時間0% ~ 90%
    - 修正Youtube iframe IE不能載入Bug
* 2016-07-16
    - 上傳Github
* 2016-07-15
    - IE webm:
        * https://tools.google.com/dlpage/webmmf/
    - onWheel IE支援
    - Youtube影片IE跳過

## 0.2.1
* 2016-07-14
    - 簡單多檔案上傳
* 2016-07-13
    - 加入Nginx，來當Http File Server
    - 更新檔案清單顯示

## 0.2.0
* 2016-07-12
    - Loading影片時顯示控制欄
    - Adblock 偵測
    - 加入Youtube速率
    - 修改部分jQuery為javascript
    - CSS翻修成全畫面
* 2016-07-10
    - 使用Youtube API
    - 秘訣:
        * 停用ADBlock
        * 安裝Google Cast
    - 按鍵:
        * Ctrl ←: 上一首
        * Ctrl →: 下一首
        * Shift 滾輪: 播放速度
        * ←: 往前
        * →: 往後
        * +: 增加音量
        * -: 減少音量
        * (speace): 播放/暫停
* 2016-07-09
    - Youtube(部分支援)

## 0.1.0
* 2016-07-09
    - 播放清單JSON檔
    - 視窗化
* 2016-07-08
    - 自適應多組Size
    - 無法Seek提示
* 2016-07-07
    - 修正排版
    - 前端Debug訊息群組化
* 2016-07-06
    - 系上實習說要用到網頁撥放器，就把原本php版改成Pyhton版

## 0.0.0
* 2015-08-04
    - 看到Youtube改版
    - 於是我就心血來潮...