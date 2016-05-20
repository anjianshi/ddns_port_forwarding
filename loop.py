# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import time


def run_forever():
    return False


class Loop(object):
    """
    在一个无限循环中定时、定期执行指定任务
    check_exit():  当此函数返回 True 时结束 loop
    time_accuracy: 每隔多少秒执行一次基础循环，设为 0 或负数则没有间隔。此值越小， timeout 和 interval 的触发时间就越准确，但也越占用 CPU。

    额外的参数会被传给 init_timers 方法
    """
    def __init__(self, check_exit=run_forever, time_accuracy=0.01, *args, **kwargs):
        self.check_exit = check_exit
        self.time_accuracy = time_accuracy
        self.start()

    def init_timers(self, *args, **kwargs):
        """在此方法中通过 set_timeout、set_interval 注册要定时、定期执行的内容"""
        raise Exception("not implement")

    def on_exit(self):
        """loop exit 前会调用此方法"""
        pass

    def start(self, *args, **kwargs):
        self.timeouts = {}      # { id: (time, callback), ... }
        self.next_timeout_id = 1

        self.intervals = {}     # { id: (interval, next_time, callback), ... }
        self.next_interval_id = 1

        self.init_timers(*args, **kwargs)

        while not self.check_exit():
            for timeout_id, (target_time, callback) in self.timeouts.items():
                if target_time <= datetime.now():
                    callback()
                    self.clear_timeout(timeout_id)

            for interval_id, (interval, next_time, callback) in self.intervals.items():
                if next_time <= datetime.now():
                    callback()
                    self.intervals[interval_id] = (interval, datetime.now() + timedelta(seconds=interval), callback)

            if self.time_accuracy >= 0:
                time.sleep(self.time_accuracy)

        self.on_exit()

    def set_timeout(self, timeout, callback):
        id = self.next_timeout_id
        self.timeouts[id] = (datetime.now() + timedelta(seconds=timeout), callback)
        self.next_timeout_id += 1
        return id

    def clear_timeout(self, id):
        if id in self.timeouts:
            del self.timeouts[id]

    def set_interval(self, interval, callback, run_at_once=False):
        if run_at_once:
            callback()

        id = self.next_interval_id
        self.intervals[id] = (interval, datetime.now() + timedelta(seconds=interval), callback)
        return id

    def clear_interval(self, id):
        if id in self.intervals:
            del self.intervals[id]
