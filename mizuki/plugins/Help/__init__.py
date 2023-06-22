# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/5/15 7:56
# @Software:PyCharm

from ..Utils.PluginInfo import PluginInfo
from .draw_img import draw_help_img

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.adapters.qqguild import MessageEvent as GuildMessageEvent
from nonebot.adapters.qqguild import MessageSegment as GuildMessageSegment

help_comm = on_command("help", aliases={"帮助", "帮助菜单", "指令"}, block=True, priority=2)

__plugin_info__ = PluginInfo(
    plugin_name="Help",
    name="指令菜单",
    description="查看指令菜单",
    usage="help ——查看指令菜单",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 2,
        "guild_adapted": True
    }
)


@help_comm.handle()
async def _(event: GroupMessageEvent):
    uid = event.get_user_id()
    img_path = await draw_help_img()
    await help_comm.finish(MessageSegment.at(uid) + MessageSegment.image(img_path))


@help_comm.handle()
async def _(event: GuildMessageEvent):
    img_path = await draw_help_img(guild_command=True)
    await help_comm.finish(GuildMessageSegment.file_image(img_path))
