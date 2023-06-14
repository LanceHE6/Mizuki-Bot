# -*- coding = utf-8 -*-
# @File:CDManager.py
# @Author:Hycer_Lance
# @Time:2023/6/14 11:33
# @Software:PyCharm

import asyncio

from .Timer import Timer
class CDManager:
    """
    一个CD管理类 用户与Timer的映射
    """
    def __init__(self, timeout: int):
        """
        构建一个CD管理器
        :param timeout: CD时长
        """
        self.__cd_map: dict = {}
        self.__timeout: int = timeout

    async def add_user(self, uid: int or str):
        """
        添加一个用户进入CD
        :param uid: uid
        :return: None
        """
        timer = Timer(self.__timeout)
        self.__cd_map[int(uid)] = timer
        asyncio.create_task(timer.start(self.remove_user, uid=uid))

    async def remove_user(self, uid: int or str):
        """
        CD结束
        :param uid: uid
        :return: None
        """
        self.__cd_map.pop(int(uid))

    async def is_in_cd(self, uid: int or str):
        """
        用户是否还在CD中
        :param uid: uid
        :return: None
        """
        if int(uid) in self.__cd_map.keys():
            return True
        return False

    async def get_remaining_time(self, uid: int or str):
        """
        获取剩余CD
        :param uid: uid
        :return: None
        """
        if await self.is_in_cd(uid):
            return self.__cd_map[int(uid)].remaining_time()
        return 0
