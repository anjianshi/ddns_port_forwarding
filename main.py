#!/usr/bin/python2
# -*- coding: utf-8 -*-
import os
import sys
from daemon import Daemon
from forwarding_loop import ForwardingLoop
import signal


class ForwardingDaemon(Daemon):
    def run(self):
        # 收到 SIGTERM 信号时，通知 loop 进行收尾工作（如关闭 SSH 连接）
        # 在 daemon 模式下如果不这样做，即使主进程结束了，SSH 子进程依然会继续运行
        self.exited = False

        def on_exit(*args):
            self.exited = True

        signal.signal(signal.SIGTERM, on_exit)

        ForwardingLoop(check_exit=lambda: self.exited, time_accuracy=0.1)

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    daemon = ForwardingDaemon(base + "/connect.pid")

    action = "start"
    for act_name in ["start", "stop", "restart", "run"]:    # 'run' is the forgegrand mode
        if act_name in sys.argv:
            action = act_name
            break
    getattr(daemon, action)()
