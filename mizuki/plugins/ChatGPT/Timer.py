# -*- coding = utf-8 -*-
# @File:Timer.py
# @Author:Hycer_Lance
# @Time:2023/6/11 18:49
# @Software:PyCharm

import asyncio

from nonebot.log import logger
from nonebot import get_driver

class Timer:
    def __init__(self, session_manager, uid: int or str):
        """
        构造一个计时器用于定期清除session
        :param session_manager: SessionManager对象
        :param uid: uid
        """
        self.session_manager = session_manager
        self.uid = uid
        self.timeout = get_driver().config.timeout

    async def start(self):
        """
        启动定时器
        :return: none
        """
        await asyncio.sleep(self.timeout)
        await self.session_manager.remove_session(self.uid)
        logger.info(f"[ChatGPT] {self.uid} 用户会话已清除")
