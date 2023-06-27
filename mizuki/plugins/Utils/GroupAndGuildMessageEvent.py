# -*- coding = utf-8 -*-
# @File:GroupAndGuildMessageEvent.py
# @Author:Hycer_Lance
# @Time:2023/6/22 22:20
# @Software:PyCharm

from nonebot.adapters.qqguild import MessageEvent as GuildMessageEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent as GroupMessageEvent
from ..GuildBinding.utils import get_uid_by_guild_id
from typing import Union

GroupAndGuildMessageEvent: Union = Union[GuildMessageEvent, GroupMessageEvent]
"""
包含群消息事件和频道消息事件的总消息事件类型
"""


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
