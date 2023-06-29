# -*- coding = utf-8 -*-
# @File:GroupAndGuildMessage.py
# @Author:Hycer_Lance
# @Time:2023/6/29 21:23
# @Software:PyCharm

from nonebot.adapters.onebot.v11 import Message as GroupMessage
from nonebot.adapters.qqguild import Message as GuildMessage
from typing import Union

GroupAndGuildMessage: Union = Union[GroupMessage, GuildMessage]
""""
包含群消息和频道消息的总消息类型
"""


class GroupAndGuildMessageUtils:
    """
    处理消息对象工具类
    """

    @staticmethod
    def get_extract_plain_text(message: GroupAndGuildMessage) -> str:
        """
        获取消息类纯文本信息
        :param message: GroupAndGuildMessage
        :return: 消息文本
        """
        if isinstance(message, GroupMessage):
            return message.extract_plain_text()
        return message.extract_plain_text()
