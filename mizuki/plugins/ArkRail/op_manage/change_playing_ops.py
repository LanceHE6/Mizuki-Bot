# -*- coding = utf-8 -*-
# @File:change_playing_ops.py
# @Author:Hycer_Lance
# @Time:2023/5/17 21:18
# @Software:PyCharm

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from ...Utils.PluginInfo import PluginInfo
from ..DB import get_oid_by_name, is_op_owned, change_user_playing_ops, get_op_attribute, OPAttribute
from .utils import str_to_list

change_comm = on_command("修改出战干员", aliases={"更改出战干员", "编队"}, block=True, priority=3)

__plugin_info__ = PluginInfo(
    plugin_name="ArkRail_change_playing_op",
    name="出战干员更改",
    description="根据用户发送的干员名字顺序修改出战干员",
    usage="编队 ——修改出战干员",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 3
    }
)


@change_comm.got('new_ops', prompt="请按照顺序发送4个干员名称(含空格)")
async def _(event: GroupMessageEvent, new_ops=Arg('new_ops')):
    if isinstance(new_ops, Message):
        new_ops = new_ops.extract_plain_text()
    uid = event.get_user_id()
    new_ops_list = await str_to_list(new_ops)
    if len(new_ops_list) != 4:
        await change_comm.finish("请发送4名干员名称", at_sender=True)
    oid_list = []
    op_name_str = ''
    for op_name in new_ops_list:
        oid = await get_oid_by_name(op_name)
        if oid == -1:  # 干员存在判断
            await change_comm.finish(f"没有名为 {op_name} 的干员", at_sender=True)
        if not await is_op_owned(uid, oid):  # 干员拥有判断
            await change_comm.finish(f"您尚未拥有干员 {op_name}", at_sender=True)
        name = await get_op_attribute(oid, OPAttribute.name)
        op_name_str += name + ' '
        oid_list.append(oid)

    await change_user_playing_ops(uid, oid_list)

    await change_comm.finish(f"已将出战干员改为 {op_name_str}", at_sender=True)
