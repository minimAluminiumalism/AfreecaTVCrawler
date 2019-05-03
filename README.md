# AfreecaTVCrawler

~~*考虑到 AfreecaTV 的带宽质量堪忧，此脚本下载的视频几乎不可避免会出现片段丢失情况，因此不推荐使用。*~~

~~目前主要问题还是目标站点的服务器不断抛出 500 Internal Server Error 错误，这往往是 AfreecaTV 内部服务器错误而不是爬虫本身的问题，但是意味着大量 ts 文件会获取失败，用 wget 方法重复下载无法解决此问题。~~
~~目前新的思路是通过传统的 requests.get(url).content 方法获取 ts 文件，在遇到错误后它会获取到一个 800K 左右的非正常文件，而正常的 ts 文件大小为 2M 左右，故通过比较文件大小可以确定是否需要反复下载失败的文件。~~

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