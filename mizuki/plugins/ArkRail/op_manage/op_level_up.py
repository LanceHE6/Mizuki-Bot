# -*- coding = utf-8 -*-
# @File:op_manage.py
# @Author:Hycer_Lance
# @Time:2023/5/16 17:36
# @Software:PyCharm

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from ...Utils.PluginInfo import PluginInfo
from ..DB import get_oid_by_name, get_user_all_ops, is_op_owned, change_user_op_level, get_op_attribute, OPAttribute
from ...Currency.utils import get_user_lmc_num, change_user_lmc_num
from .utils import get_cost_op

op_level_up = on_command("level_up", aliases={"干员升级", "升级", "升级干员"}, block=True, priority=1)

__plugin_info__ = PluginInfo(
    plugin_name="ArkRail_op_level_up",
    name="干员升级",
    description="干员升级",
    usage="干员升级<干员名> ——给指定干员升级",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 3
    }
)


@op_level_up.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    name = args.extract_plain_text().replace(' ', '')  # 获取命令后面跟着的纯文本内容
    if name == '':
        await op_level_up.finish("请在指令后跟干员名称", at_sender=True)
    uid = event.get_user_id()
    oid = await get_oid_by_name(name)

    # 判断干员是否存在
    if oid == -1:
        await op_level_up.finish(MessageSegment.at(uid) + f"没有找到名为 {name} 的干员")
    # 判断用户是否拥有该干员
    if not await is_op_owned(uid, oid):
        await op_level_up.finish(MessageSegment.at(uid) + "您未拥有该干员")
    user_all_ops = await get_user_all_ops(uid)
    op_name = await get_op_attribute(oid, OPAttribute.name)
    state["op_name"] = op_name
    state["uid"] = uid
    state["oid"] = oid
    op_level = None
    for no in user_all_ops:
        if user_all_ops[no]["oid"] == oid:
            op_level = user_all_ops[no]["level"]
    if op_level == 90:
        await op_level_up.finish("该干员已满级", at_sender=True)
    # 插入绘制干员等级图片函数
    user_lmc_num = await get_user_lmc_num(uid)
    state["user_lmc_num"] = user_lmc_num
    state["op_level"] = op_level
    level_up_to_5 = 5 - (op_level % 5) + op_level
    reply = f"\n目前干员等级:{op_level}"
    if level_up_to_5 >= 90:
        level_up_to_5 = 90
        reply += f"\n升到{level_up_to_5}级所需龙门币:{await get_cost_op(op_level, level_up_to_5)}"
    else:
        if level_up_to_5 + 5 >= 90:
            level_up_to_10 = 90
        else:
            level_up_to_10 = level_up_to_5 + 5
        reply += f"\n升到{level_up_to_5}级所需龙门币:{await get_cost_op(op_level, level_up_to_5)}\n升到{level_up_to_10}级所需龙门币:{await get_cost_op(op_level, level_up_to_10)}"

    reply += f"\n龙门币:{user_lmc_num}"

    await op_level_up.send(reply, at_sender=True)


@op_level_up.got("level", prompt="请发送目标等级")
async def got_level(state: T_State, level=Arg("level")):
    if isinstance(level, Message):
        level = int(level.extract_plain_text().split(' ')[0])
    uid = (state["uid"])
    if level < 1 or level > 90 or level < state["op_level"]:
        await op_level_up.finish(MessageSegment.at(uid) + "非法等级")
    cost = await get_cost_op(state["op_level"], level)
    if cost > state["user_lmc_num"]:
        await op_level_up.finish("龙门币余额不足", at_sender=True)

    await change_user_op_level(uid, state["oid"], level)
    await change_user_lmc_num(uid, -cost)
    await op_level_up.finish(f"已将 {state['op_name']} 升到{level}级\n消耗龙门币:{cost}", at_sender=True)
