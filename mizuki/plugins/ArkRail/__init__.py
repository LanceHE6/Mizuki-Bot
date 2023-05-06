# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:52
# @Software:PyCharm

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from .DB import is_in_table, get_user_playing_ops, get_user_all_ops, get_op_attribute, OPAttribute
from .operator import new_instance

op_info = on_command("info", aliases={"我的干员", "干员"}, block=True, priority=2)
op_info_all = on_command("info all", aliases={"所有角色", "所有干员"}, block=True, priority=2)
op_detail = on_command("detail", aliases={"干员信息", "干员详情"}, block=True, priority=2)


@op_info.handle()
async def _(event: GroupMessageEvent):
    uid = int(event.get_user_id())
    if not await is_in_table(uid):
        await op_info.send(MessageSegment.at(uid) + "欢迎加入方舟铁道，您已获得新手礼包(包含4名强力干员)！")
    playing_ops = await get_user_playing_ops(uid)
    reply = MessageSegment.at(uid) + "您的出战干员为："
    i = 1
    for op in playing_ops:
        oid = playing_ops[op]["oid"]
        level = playing_ops[op]["level"]
        name = await get_op_attribute(oid, OPAttribute.name)
        reply += f"\n{i}. {name}  等级：{level}"
        i += 1

    await op_info.finish(reply)
    # player_skills = skills


@op_info_all.handle()
async def _(event: GroupMessageEvent):
    uid = int(event.get_user_id())
    if not await is_in_table(uid):
        await op_info_all.send(MessageSegment.at(uid) + "欢迎加入方舟铁道，您已获得新手礼包(包含4名强力干员)！")
    all_ops = await get_user_all_ops(uid)
    reply = MessageSegment.at(uid) + "您拥有的所有干员："

    for op in all_ops:
        oid = all_ops[op]["oid"]
        level = all_ops[op]["level"]
        name = await get_op_attribute(oid, OPAttribute.name)
        reply += f"\n{name}  等级：{level}"

    await op_info_all.finish(reply)


@op_detail.handle()
async def _(event: GroupMessageEvent):
    uid = int(event.get_user_id())
    if not await is_in_table(uid):
        await op_info.send(MessageSegment.at(uid) + "欢迎加入方舟铁道，您已获得新手礼包(包含4名强力干员)！")

    playing_ops = await get_user_playing_ops(uid)
    first_op = playing_ops["1"]
    oid = first_op["oid"]
    level = first_op["level"]
    skills_level = first_op["skills_level"]
    op = await operator.new_instance(oid, level, skills_level)
    reply_op_info = MessageSegment.at(uid) + "您的第一个出战干员的详细信息为：\n" \
                                             f"{op.name}\n等级：{op.level}  最大生命值：{op.max_health}\n" \
                                             f"攻击力：{op.atk}  攻击方式：{op.atk_type_str}\n" \
                                             f"防御力：{op.defence}  法抗：{op.res}" \
                                             f"暴击率：{op.crit_r}  暴击伤害：{op.crit_d}" \
                                             f"速度：{op.speed}"
    op_skills_list = op.skills_list
    reply_skills_info = MessageSegment.at(uid) + "干员技能数据为："
    i = 1
    for skill in op_skills_list:
        reply_skills_info += f"\n{i}. {skill.name}  等级：{skill.level}\n" \
                             f"{skill.detail}"
    await op_detail.send(reply_op_info)
    await op_detail.send(reply_skills_info)
    await op_detail.finish()
