ssh 远程端口转发是一种比较简单的实现内网穿透的方式，但它有一个缺点：我们把要连接的 IP 提前设置好。  
例如要在家里访问公司的电脑，就必须预先知道家里的 IP，万一家里的 IP 变了，那公司电脑就又要重新设置。  
虽然可以让公司电脑连到某个固定的服务器，然后在家里也连接那个服务器，但这往往会影响连接速度。  

此脚本就是用来解决这一问题。  
它会定时检查指定域名的解析结果，并连接到域名指向的那个 IP 上。我们可以在家里配置上 DDNS，这样任何时候 IP 发生变化，公司的电脑都会重新连接到最新的 IP 上。  


### 环境要求

1. 内网机器能够访问外网，能够运行 Python 2.7（OpenWRT 下要求安装 python-light 包）和 SSH（支持 Droptear）
2. 外网机器上要运行 ssh server 以实现端口转发
3. 一个公网域名

### 使用方法
把 config.example.py 复制为 config.py，修改里面的配置  
通过 ssh-agent 以及 ssh-add 预先配置好连接外网机器要用到的 ssh private key  
执行 `python main.py start`  

main.py 支持 start、stop、restart、run 命令，其中 run 是前台运行模式，便于进行调试。  
不指定命令时默认为 start  


### 注意事项

此脚本只支持通过 ssh key 登录，不支持密码登陆  

外网机器上可能要修改 `/etc/ssh/sshd_config`，添加 `GatewayPorts yes`  
（如果是 OpenWRT，要修改 `/etc/config/dropbear`，添加 `option GatewayPorts 'on'`）  

同时建议在 `/etc/ssh/sshd_config` 中（或在 `/etc/config/dropbear` 中以对应的格式）加上这两行：

```
ClientAliveInterval = 30
ClientAliveCountMax = 2
```

代表每 30 秒检查一下客户端是否还正常连接着，如果两次检查都失败，则断开连接。
具体数字可以自己设置。这样客户端意外断线后，远端就不会一直保持着连接了。

如果外网机器是一个 OpenWRT 路由器，要让它允许远程 ssh 登录。  
详见： http://blog.differentpla.net/blog/2015/05/27/openwrt-ssh-wan  
（安全起见，最好不要用 22 端口，另外禁止密码登录，只用 ssh key 登录）  

如果内网机器的 ssh 客户端是 dropbear（例如这是一个 openwrt 路由器），ssh key 需使用 dropbear 格式（使用 dropbearkey 创建）  


### 参考资料与鸣谢

- SSH 端口转发相关知识： http://blog.creke.net/722.html
- 利用托管在 CloudXNS 的自有域名实现 DDNS 的简单脚本：https://github.com/weicno/cloudxns-ddns
- daemon.py 来自： https://github.com/serverdensity/python-daemon
- 在外网机器上使用 `who -a` 结合 `ps aux|grep ssh` 可以辅助判断内网机器是否成功连接上来了
