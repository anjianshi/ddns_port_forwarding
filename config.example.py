# -*- coding: utf-8 -*-

# 内网机器（需要运行此脚本的机器）称为 local
# 外网机器（要通过此脚本连接的目标机器）称为 remote

# 是否以调试模式运行（会输出更多信息）
debug = True

# 每隔多少秒执行一次解析
resolve_interval = 60

# 通过哪个 DNS server 获取解析结果
# 如果使用的是自己的域名，可以使用域名解析服务商的域名服务器来解析，这样受缓存影响比较小
# 例如在万网买的域名，解析服务商使用的是 CloudXNS，那么就把 CloudXNS 要求你填写到万网管理界面中的“域名服务器”的域名（例如 lv3ns1.ffdns.net）作为这里的 dns_server
# 默认使用的是 DNSPOD 的 Public DNS
dns_server = '119.29.29.29'

# DDNS 绑定的域名（必填）
domain = None
remote_ssh_user = None  # 通过此用户名连接外网机器。为空则不指定用户名
remote_ssh_port = 22    # 通过此端口连接外网机器
connect_timeout = 5

forwarding_host = 'localhost'
forwarding_local_port = None        # 必填
forwarding_remote_port = None       # 必填

# 每隔多少秒检查一次连接状态
check_connection_interval = 1
# 连接失败后，间隔多少秒尝试重连
# 慎重设置此选项。此脚本在没有连接成功的情况下，会持续不断地重新连接，因此如果此数值设置得太小，有可能因连接太过频繁而被屏蔽；
# 如果设置得太大，则一旦连接断线，要等很长时间才能重新连接上。
reconnect_delay = 60

# 日志文件的缓冲区大小
log_buffer_size = 2048
