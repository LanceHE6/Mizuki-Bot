# -*- coding = utf-8 -*-
# @File:GroupAndGuildMessageEvent.py
# @Author:Hycer_Lance
# @Time:2023/6/22 22:20
# @Software:PyCharm

from nonebot.adapters.qqguild import MessageEvent as GuildMessageEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent as GroupMessageEvent
from typing import Union

GroupAndGuildMessageEvent: Union = Union[GuildMessageEvent, GroupMessageEvent]
"""
包含群消息事件和频道消息事件的总消息事件类型
"""
