# AfreecaTVCrawler


已经加入 gevent 并发协程，下载功能基本可用，经测试，3000 个分片组成的直播下载后丢失的 ts 分片可以控制在 20 个以内。此后的脚本将不再需要借助东亚地区（日韩） VPS 加速，中国大陆可以直接下载（需使用代理）。

功能仍在完善中，任何问题请提 issue。


## 参数说明

pool_size：设置协程池的大小，机器内存为 512MB 时建议设置为不大于 20，机器内存为 1G 时，可以设置为大于 50。注意，过多的连接数会因为占用过多的内存而被系统杀死。

stream url：直播的 URL，格式与以下类似：http://vod.afreecatv.com/PLAYER/STATION/42586962


## Usage

```
cd ~/AfreecaTVCrawler

sudo -H pip3 install -r requirements.txt

cd src/

python3 Afreeca_Crawler.py
```
如果的你的机器上只安装了 Python3 而没有 Python2（一般是 Windows），将以上命令中的 ```python3```  改为  ```python```。


## Notification

AfreecaTV 在中国已被屏蔽，如果你选择本地下载，为避免超时错误，必须先设置代理，将流量指向本地的代理端口。

### 设置代理

macOS

对于大多数的编辑器而言，只需要将 Shadowsocks 或 ShadowsocksR 切换为全局模式即可。

Windows

无经验，请查阅相关资料。