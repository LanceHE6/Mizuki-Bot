# -*- coding = utf-8 -*-
# @File:GroupAndGuildUtils.py
# @Author:Hycer_Lance
# @Time:2023/8/14 14:38
# @Software:PyCharm

from typing import Union
from nonebot.adapters.onebot.v11 import Message as GroupMessage
from nonebot.adapters.qqguild import Message as GuildMessage
from nonebot.adapters.qqguild import MessageEvent as GuildMessageEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent as GroupMessageEvent
from ..GuildBinding.utils import get_uid_by_guild_id
from nonebot.adapters.onebot.v11 import MessageSegment as GroupMessageSegment
from nonebot.adapters.qqguild import MessageSegment as GuildMessageSegment

GroupAndGuildMessage: Union = Union[GroupMessage, GuildMessage]
""""
包含群消息和频道消息的总消息类型
"""
GroupAndGuildMessageEvent: Union = Union[GuildMessageEvent, GroupMessageEvent]
"""
包含群消息事件和频道消息事件的总消息事件类型
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

    @staticmethod
    async def get_event_user_id(event: GroupAndGuildMessageEvent):
        """
        通过事件获取用户id的方法

        :param event: 事件
        :return: uid，当频道id没有绑定QQid时，返回0
        """
        if isinstance(event, GuildMessageEvent):
            uid = int(await get_uid_by_guild_id(event.get_user_id()))
        else:
            uid = int(event.get_user_id())
        return uid


class GroupAndGuildMessageSegment:
    """
    群聊频道消息字段处理类
    """

    @staticmethod
    def at(event: GroupAndGuildMessageEvent, uid: int = 0):
        """
        @成员消息生成

        :param event: 事件，用于判断是群事件还是频道事件
        :param uid: 用户id(不填默认@event发起者)
        :return: MessageSegment
        """
        if uid == 0:
            uid = event.get_user_id()
        if isinstance(event, GuildMessageEvent):
            message = GuildMessageSegment.mention_user(uid)
        else:
            message = GroupMessageSegment.at(uid)

        return message

    @staticmethod
    def image(event, path, is_url: bool = False):
        """
        图片消息生成

        :param event: 事件，用于判断是群事件还是频道事件
        :param path: 图片路径或图片url
        :param is_url: 是否为网络图片，默认为False
        :return: MessageSegment
        """
        if isinstance(event, GuildMessageEvent):
            img = GuildMessageSegment.file_image(path) if not is_url else GuildMessageSegment.image(path)
        else:
            img = GroupMessageSegment.image(path)

        return img
