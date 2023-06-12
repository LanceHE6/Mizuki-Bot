# -*- coding = utf-8 -*-
# @File:SessionManager.py
# @Author:Hycer_Lance
# @Time:2023/6/11 17:15
# @Software:PyCharm

import asyncio
from nonebot import get_driver, logger

from .Session import Session
from ..Utils.Timer import Timer

class SessionManager:

    def __init__(self):
        """
        构造一个会话管理类，将用户id与session关联
        """
        self.session_map: dict = {}

    async def get_session(self, uid: int or str) -> Session:
        """
        获取指定用户的session
        :param uid: uid
        :return: Session对象
        """
        return self.session_map[f"{uid}"]

    async def add_session(self, uid: int or str, session: Session):
        """
        添加session
        :param uid: uid
        :param session: Session
        :return: none
        """
        self.session_map[f"{uid}"] = session
        # 创建计时器
        timer = Timer(int(get_driver().config.timeout))
        asyncio.create_task(timer.start(self.remove_session, uid))

    async def remove_session(self, uid: int or str):
        """
        删除指定用户session
        :param uid: uid
        :return: none
        """
        self.session_map.pop(f"{uid}")
        logger.info(f"[ChatGPT] {uid} 用户Session已清除")

    async def is_session_exist(self, uid: int or str) -> bool:
        """
        判断指定用户session是否存在
        :param uid: uid
        :return: bool
        """
        if str(uid) in self.session_map.keys():
            return True
        return False
