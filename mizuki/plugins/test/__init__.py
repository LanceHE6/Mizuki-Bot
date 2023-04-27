# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:52
# @Software:PyCharm

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from .player import *

info=on_command("info",aliases={"我的角色","角色","我的干员","干员"}, block=True, priority=2)

@info.handle()
async def _(event: GroupMessageEvent):
    uid = event.get_user_id()
    user = await player.new_instance(uid)
    user_info = await user.get_info()
    player_name = user_info["name"]
    player_level = user_info["level"]
    max_health = user_info["max_health"]
    attack = user_info["attack"]
    defence = user_info["defence"]
    crit_rate = user_info["crit_rate"]
    crit_damage = user_info["crit_damage"]
    reply =MessageSegment.at(uid)+ f"\n干员:{player_name}\n等级:{player_level}\n最大生命值:{max_health}\n攻击力:{attack}\n防御力:{defence}\n暴击率:{crit_rate}%\n暴击伤害:{crit_damage}%"
    await info.finish(reply)
    #player_skills = skills