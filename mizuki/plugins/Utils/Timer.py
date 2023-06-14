# -*- coding = utf-8 -*-
# @File:Timer.py
# @Author:Hycer_Lance
# @Time:2023/6/12 18:46
# @Software:PyCharm

import asyncio
from typing import Callable

class Timer:
    """
    一个计时器
    """
    def __init__(self, timeout: int):
        """
        构造一个计时器
        :param timeout: 计时时间
        """
        self.timeout = timeout
        self.start_time = None

    async def start(self, func: Callable, *args, **kwargs):
        """
        启动计时器，并在一段时间后执行一个操作
        :param func: 需要执行的操作（函数）
        :param args: 函数的参数
        :param kwargs: 函数的参数
        :return: None
        """
        # 记录开始时间
        self.start_time = asyncio.get_event_loop().time()
        await asyncio.sleep(self.timeout)
        await func(*args, **kwargs)

    def remaining_time(self):
        """
        计算剩余冷却时间
        :return: 剩余冷却时间
        """
        if self.start_time is None:
            return 0
        elapsed_time = asyncio.get_event_loop().time() - self.start_time
        remaining_time = max(0, self.timeout - elapsed_time)
        return int(remaining_time)

