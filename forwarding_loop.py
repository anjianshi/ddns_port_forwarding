# -*- coding: utf-8 -*-
import subprocess as sp
import re
import os
from loop import Loop
from logger import Logger
import config


for item in ["domain", "forwarding_local_port", "forwarding_remote_port"]:
    if getattr(config, item) is None:
        raise Exception("配置项 {} 不能为空".format(item))


base = os.path.dirname(os.path.abspath(__file__))
logger = Logger(base + "/connect.log", not config.debug)


class ForwardingLoop(Loop):
    """
    执行流程
    1. 每隔若干秒获取指定域名的解析结果
        1. 若得到的 IP 与当前的不同
            1. 结束正在执行的行为
            2. 尝试连接新 IP
                1. 若连接上了：
                    1. 每隔几秒钟检查一下连接状态，若断线则进入状态 1.1.2.2
                2. 如果没连接上：
                    1. 等待一段时间后回到状态 1.1.2
        2. 若相同，不做任何事
    """
    def init_timers(self):
        self.ip = None
        self.connection_proc = None

        self.check_connection_timeout_id = None
        self.reconnect_timeout_id = None

        self.set_interval(config.resolve_interval, self.resolve, True)
        self.set_interval(config.log_flush_interval, logger.flush)

    def on_exit(self):
        if self.connection_proc:
            self.disconnect()

    def resolve(self):
        new_ip = self.get_ip()
        if new_ip != self.ip:
            logger.info("got new ip {}".format(new_ip))
            self.ip = new_ip

            if self.connection_proc:
                self.disconnect()

            if self.check_connection_timeout_id:
                self.clear_timeout(self.check_connection_timeout_id)
                self.check_connection_timeout_id = None

            if self.reconnect_timeout_id:
                self.clear_timeout(self.reconnect_timeout_id)
                self.reconnect_timeout_id = None

            if self.ip:
                self.connect()

    def connect(self):
        server = "{}@{}".format(config.remote_ssh_user, self.ip) if config.remote_ssh_user is not None else self.ip

        args = [
            'ssh',
            # 使用 -N 参数禁止开启命令行，可以避免一些奇怪的关于输出的问题
            '-N',
            # 把 bind_address 设为 0.0.0.0 以使得公网主机是一个路由器时，路由器下属的各设备能通过路由器的 wan IP 访问远程转发的端口。
            # 如果不这样设，将只能在路由器内部，通过 127.0.0.1 访问远程转发的端口。
            # 详见 `man ssh` 中对 '-R' 参数的介绍。
            '-R', "0.0.0.0:{}:{}:{}".format(str(config.forwarding_remote_port), config.forwarding_host, str(config.forwarding_local_port)),
            server, "-p", str(config.remote_ssh_port),
            "-i", config.ssh_identity_file,
            '-o', 'ConnectTimeout={}'.format(config.connect_timeout),
            '-o', 'TCPKeepAlive=yes',
            '-o', 'ServerAliveInterval=30',
            '-o', 'ServerAliveCountMax=2',
            # 必须设置此项，在远程端口转发时才能成功指定 bind_address
            '-o', 'GatewayPorts=yes',
        ]
        if not config.strict_host_key_checking:
            # 来自： http://stackoverflow.com/a/3664010/2815178
            args += ['-o', 'UserKnownHostsFile=/dev/null', '-o', 'StrictHostKeyChecking=no']
        logger.debug("connecting `{}`".format(" ".join(args)))
        self.connection_proc = sp.Popen(args)
        self.check_connection_timeout_id = self.set_timeout(config.connect_timeout + 0.01, self.check_connection)

    def check_connection(self):
        if self.is_connected():
            logger.debug("connection confirmed")
            self.check_connection_timeout_id = self.set_timeout(config.check_connection_interval, self.check_connection)
        else:
            logger.info("connect failed or connection is break")
            self.connection_proc = None
            self.reconnect_timeout_id = self.set_timeout(config.reconnect_delay, self.connect)

    # =================

    def get_ip(self):
        logger.debug("resolving domain {}".format(config.domain))
        resp = sp.check_output(["dig", "@" + config.dns_server, config.domain])
        match = re.search(r"IN\tA\t((?:\d+\.)+\d+)", resp)
        return match.groups()[0] if match else None

    def is_connected(self):
        self.connection_proc.poll()
        return self.connection_proc.returncode is None

    def disconnect(self):
        logger.debug("disconnect")
        self.connection_proc.terminate()
        self.connection_proc = None
