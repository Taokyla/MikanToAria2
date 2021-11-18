# Mikan to Aria2
读取蜜柑计划的rss订阅，下载最新的动画！

---

## 使用方式

- 修改`config/config.default.yml`，重命名为`config.yml`保存到`config`文件夹下

- 给脚本加个crontab定时执行，例如：

```
*/30 * * * * python MikanToAria2/main.py
```

### config.yml 说明

#### aria2

- `host` 你的aria2的rpc链接地址

- `port` rpc端口，默认为6800

- `secret` rpc密码

#### proxy
- `http` 一般是`http://127.0.0.1:1080`，socks5可以用`'socks5://127.0.0.1:1080'`

- `https` 同上，前缀是https,也可以用`'socks5://127.0.0.1:1080'`

#### mikan

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
