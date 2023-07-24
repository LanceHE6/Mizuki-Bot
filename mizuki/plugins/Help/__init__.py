# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/5/15 7:56
# @Software:PyCharm

from .PluginInfo import PluginInfo
from .draw_img import draw_help_img
from ..Utils.GroupAndGuildMessageSegment import (GroupAndGuildMessageSegment,
                                                 GroupAndGuildMessageEvent,
                                                 GuildMessageEvent)

from nonebot import on_command

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
async def _(event: GroupAndGuildMessageEvent):
    if isinstance(event, GuildMessageEvent):
        img_path = await draw_help_img(True)
        await help_comm.finish(
            GroupAndGuildMessageSegment.at(event) + GroupAndGuildMessageSegment.image(event, img_path))
    img_path = await draw_help_img()
  print("test")
    await help_comm.finish(GroupAndGuildMessageSegment.at(event) + GroupAndGuildMessageSegment.image(event, img_path))
