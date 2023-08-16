# -*- coding = utf-8 -*-
# @File:agar_info.py
# @Author:Hycer_Lance
# @Time:2023/5/30 20:57
# @Software:PyCharm

from nonebot import on_command
from ...Utils.GroupAndGuildUtils import (GroupAndGuildMessageEvent,
                                         GroupAndGuildMessageSegment,
                                         GroupAndGuildMessageUtils)

from ...Help.PluginInfo import PluginInfo
from ..DB import get_user_agar_num, get_agar_full_time

show_agar_comm = on_command("琼脂", aliases={"体力"}, block=True, priority=3)

__plugin_info__ = PluginInfo(
    plugin_name="ArkRail_show_agar_info",
    name="琼脂值查询",
    description="查询琼脂值",
    usage="琼脂 ——查看当前琼脂值",
    extra={
        "author": "HycerLance",
        "version": "0.1.0",
        "priority": 3,
        "guild_adapted": True
    }
)


@show_agar_comm.handle()
async def _(event: GroupAndGuildMessageEvent):
    uid = await GroupAndGuildMessageUtils.get_event_user_id(event)
    if uid == 0:
        await show_agar_comm.finish("您还没有在频道中绑定QQ账号！")
    agar_num = await get_user_agar_num(uid)
    full_time = await get_agar_full_time(uid)
    reply = GroupAndGuildMessageSegment.at(event) + f"\n您的琼脂:\n{agar_num}/160\n"
    if not full_time == 0:
        reply += f"预计回满时间:{await minute_to_standard_str(full_time)}"
    await show_agar_comm.finish(reply, at_sender=True)


async def minute_to_standard_str(minute: int) -> str:
    """
    将分钟数转化为标准时间格式 xx小时xx分钟
    :param minute: 分钟
    :return:
    """
    if minute < 60:
        return f"{minute}分钟"
    else:
        m = minute % 60
        h = int((minute - m) / 60)
        return f"{h}小时{m}分钟"
