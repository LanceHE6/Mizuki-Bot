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
        :param timeout 计时时间
        """
        self.timeout = timeout

    async def start(self, func: Callable, *args, **kwargs):
        """
        启动计时器，并在一段时间后执行一个操作
        :param func: 需要执行的操作（函数）
        :param args: 函数的参数
        :param kwargs: 函数的参数据
        :return: None
        """
        await asyncio.sleep(self.timeout)
        await func(*args, **kwargs)
