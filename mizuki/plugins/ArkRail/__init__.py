# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:52
# @Software:PyCharm

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, Message
from nonebot.params import CommandArg, ArgPlainText
from .DB import is_in_table, get_user_playing_ops, get_user_all_ops, get_op_attribute, get_oid_by_name, OPAttribute
from .DB import is_op_owned
from .operator import new_instance, Operator

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
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    uid = int(event.get_user_id())
    if not await is_in_table(uid):
        await op_info.send(MessageSegment.at(uid) + "欢迎加入方舟铁道，您已获得新手礼包(包含4名强力干员)！")

    name = args.extract_plain_text().replace(' ', '')  # 获取命令后面跟着的纯文本内容
    oid = await get_oid_by_name(name)
    if oid == -1:
        await op_detail.finish(MessageSegment.at(uid) + f"没有名为{name}的干员")

    op: Operator
    if await is_op_owned(uid, oid):
        # 玩家拥有该干员
        tip = "干员的详细信息为："
        user_all_ops = await get_user_all_ops(uid)
        index = "1"
        for i in user_all_ops:
            if user_all_ops[i]["oid"] == oid:
                index = i
                break

        select_op = user_all_ops[index]
        oid = select_op["oid"]
        level = select_op["level"]
        skills_level = select_op["skills_level"]
        op = await operator.new_instance(oid, level, skills_level)
    else:
        tip = "您未拥有该干员，以下是该干员的初始状态信息"
        op = await operator.new_instance(oid, 1, [0, 0, 0])
        pass
        # 玩家未拥有该干员

    reply_op_info = MessageSegment.at(uid) + f"{tip}\n" \
                                             f"{op.name}\n等级：{op.level}  星级：{op.stars}\n" \
                                             f"职业：{op.profession}\n最大生命值：{op.max_health}\n" \
                                             f"攻击力：{op.atk}\n攻击方式：{op.atk_type_str}\n" \
                                             f"防御力：{op.defence}\n法抗：{op.res}\n" \
                                             f"暴击率：{100 * op.crit_r}%\n暴击伤害：{100 * op.crit_d}%\n" \
                                             f"速度：{op.speed}"
    op_skills_list = op.skills_list
    reply_skills_info = MessageSegment.at(uid) + f"{op.name}的技能数据为："
    i = 1
    for skill in op_skills_list:
        reply_skills_info += f"\n\n{i}. {skill.name}  等级：{skill.level}\n" \
                             f"技力消耗：{int(skill.consume)}\n" \
                             f"{skill.detail}"
        i += 1
    await op_detail.send(reply_op_info)
    await op_detail.send(reply_skills_info)
    await op_detail.finish()
