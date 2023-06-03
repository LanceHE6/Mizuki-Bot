# -*- coding = utf-8 -*-
# @File:agar_info.py
# @Author:Hycer_Lance
# @Time:2023/5/30 20:57
# @Software:PyCharm

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from ...Utils.PluginInfo import PluginInfo
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
        "priority": 3
    }
    )

@show_agar_comm.handle()
async def _(event: GroupMessageEvent):
    uid = event.get_user_id()
    agar_num = await get_user_agar_num(uid)
    full_time = await get_agar_full_time(uid)
    reply = f"\n您的琼脂:\n{agar_num}/160\n"
    if full_time == 0:
        reply += "已满"
    else:
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
