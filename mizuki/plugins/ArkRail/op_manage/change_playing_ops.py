# -*- coding = utf-8 -*-
# @File:change_playing_ops.py
# @Author:Hycer_Lance
# @Time:2023/5/17 21:18
# @Software:PyCharm

from nonebot import on_command
from nonebot.params import Arg

from ...Help.PluginInfo import PluginInfo
from ..DB import get_oid_by_name, is_op_owned, change_user_playing_ops, get_op_attribute, OPAttribute
from .utils import str_to_list
from ...Utils.GroupAndGuildUtils import (GroupAndGuildMessageEvent,
                                         GroupAndGuildMessageSegment,
                                         GroupAndGuildMessage,
                                         GroupAndGuildMessageUtils)

change_comm = on_command("修改出战干员", aliases={"更改出战干员", "编队"}, block=True, priority=3)

__plugin_info__ = PluginInfo(
    plugin_name="ArkRail_change_playing_op",
    name="出战干员更改",
    description="根据用户发送的干员名字顺序修改出战干员",
    usage="编队 ——修改出战干员",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 3,
        "guild_adapted": True
    }
)


@change_comm.got('new_ops', prompt="请按照顺序发送至多4个干员的名称(空格隔开)")
async def _(event: GroupAndGuildMessageEvent, new_ops=Arg('new_ops')):
    if isinstance(new_ops, GroupAndGuildMessage):
        new_ops = new_ops.extract_plain_text()
    uid = await GroupAndGuildMessageUtils.get_event_user_id(event)
    new_ops_list = await str_to_list(new_ops)
    if len(new_ops_list) > 4:
        await change_comm.finish(GroupAndGuildMessageSegment.at(event) + "最多编入4名干员哦")
    if len(new_ops_list) == 0:
        await change_comm.finish(GroupAndGuildMessageSegment.at(event) + "队伍中至少编入一名干员")
    oid_list = []
    op_name_str = ''
    for op_name in new_ops_list:
        oid = await get_oid_by_name(op_name)
        if oid == -1:  # 干员存在判断
            await change_comm.finish(GroupAndGuildMessageSegment.at(event) + f"没有名为 {op_name} 的干员")
        if not await is_op_owned(uid, oid):  # 干员拥有判断
            await change_comm.finish(GroupAndGuildMessageSegment.at(event) + f"您尚未拥有干员 {op_name}")
        name = await get_op_attribute(oid, OPAttribute.name)
        op_name_str += name + ' '
        oid_list.append(oid)

    await change_user_playing_ops(uid, oid_list)

    await change_comm.finish(GroupAndGuildMessageSegment.at(event) + f"已将出战干员改为 {op_name_str}")
