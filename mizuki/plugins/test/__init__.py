# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:52
# @Software:PyCharm

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from .player import *
from .skill import *

info = on_command("info", aliases={"我的角色", "角色", "我的干员", "干员"}, block=True, priority=2)
s_info = on_command("skill", aliases={"我的技能", "技能"}, block=True, priority=2)


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
    reply = MessageSegment.at(
        uid) + f"\n干员:{player_name}\n等级:{player_level}\n最大生命值:{max_health}\n攻击力:{attack}\n防御力:{defence}\n暴击率:{crit_rate}%\n暴击伤害:{crit_damage}% "
    await info.finish(reply)
    # player_skills = skills


@s_info.handle()
async def _(event: GroupMessageEvent):
    uid = event.get_user_id()
    skills = await skill.new_instance_list(uid)
    reply = MessageSegment.at(uid) + "您拥有的技能:"
    for i in range(len(skills)):
        skill_info = await skills[i].get_info()
        skill_name = skill_info["name"]
        skill_quality = skill_info["quality"]
        skill_level = skill_info["level"]
        skill_info = skill_info["skill_info"]
        reply += f"\n{skill_name}\n星级:{skill_quality}\n等级:{skill_level}\n技能详情:{skill_info}"
    await info.finish(reply)
