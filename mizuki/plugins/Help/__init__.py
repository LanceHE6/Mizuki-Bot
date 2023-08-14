# -*- coding = utf-8 -*-
# @File:__init__.py
# @Author:Hycer_Lance
# @Time:2023/5/15 7:56
# @Software:PyCharm

import glob
import os

from .PluginInfo import PluginInfo, plugin_info_path
from .draw_img import draw_help_img
from ..Utils.GroupAndGuildUtils import (GroupAndGuildMessageSegment,
                                        GroupAndGuildMessageEvent,
                                        GuildMessageEvent)

from nonebot import on_command, get_driver

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
    await help_comm.finish(GroupAndGuildMessageSegment.at(event) + GroupAndGuildMessageSegment.image(event, img_path))


driver = get_driver()


@driver.on_shutdown
def _():
    """
    在nonebot关闭时删除data文件夹中的所有插件数据
    """
    for infile in glob.glob(os.path.join(plugin_info_path, '*.json')):
        os.remove(infile)
