# Mikan to Aria2
读取蜜柑计划的rss订阅，下载最新的动画！

---

## 使用方式

- 修改`config/config.default.yml`，重命名为`config.yml`保存到`config`文件夹下

- 或者: 使用环境变量`MTA_CONFIGPATH`指定配置文件，支持yml和json

- 给脚本加个crontab定时执行，例如：

```
*/30 * * * * python MikanToAria2/main.py
```

## 环境变量

- `MTA_CONFIGPATH` 配置文件路径，默认为`config/config.yml`
- `MTA_HISTORY_FILE` 指定历史保存文件路径
- `MTA_TORRENTS_DIR` 种子保存文件夹，默认为`torrents`
- `MTA_MAX_HISTORY` 最大加载历史记录，默认为300
- `MTA_USER_AGENT` 使用的user-agent
- `HTTP_PROXY` & `HTTPS_PROXY` 代理地址
- `MTA_ARIA2_HOST`,`MTA_ARIA2_PORT`,`MTA_ARIA2_SECRET` aria2配置

### config.yml 说明 (json也行)

#### aria2 (可选)

- `host` 你的aria2的rpc链接地址

- `port` rpc端口，默认为6800

- `secret` rpc密码

#### proxy (可选)

- `http` 一般是`http://127.0.0.1:1080`，socks5可以用`'socks5://127.0.0.1:1080'`

- `https` 同上，前缀是https,也可以用`'socks5://127.0.0.1:1080'`

#### mikan `list[dict, ...]`，每项含有以下key组成的字典

- `url` rss订阅链接，例如：https://mikanani.me/RSS/Bangumi?bangumiId=2359&subgroupid=370

- `rule` 可选，正则匹配，会匹配title，符合的才会下载

- `savedir` 可选，动画的保存路径，默认为番名


### Tip

ubuntu 使用ssr

```shell
sudo apt update
sudo apt install shadowsocks-libev
ss-local -s youserverip -p youserverport -k youserverpasswd -m aes-256-gcm -l 1080 -b 127.0.0.1 &
```
