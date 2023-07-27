# -*- coding = utf-8 -*-
# @File:cmd.py
# @Author:Hycer_Lance
# @Time:2023/7/26 17:53
# @Software:PyCharm

from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg

import os

from ..Help.PluginInfo import PluginInfo
from ..Utils.GroupAndGuildMessageEvent import GroupAndGuildMessageEvent

cmd = on_command("cmd", aliases={"命令行"}, block=True, priority=2, permission=SUPERUSER)

__plugin_info__ = PluginInfo(
    plugin_name="cmd",
    name="命令行",
    description="在宿主机上执行单条cmd指令",
    usage="cmd<command> ——执行单条cmd指令",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 2,
        "permission": "SUPERUSER"
    }
)


@cmd.handle()
async def _(event: GroupAndGuildMessageEvent, args=CommandArg()):
    command = str(args)
    output = os.popen(command)
    output_list = output.readlines()
    reply = ""
    for line in output_list:
        reply += line
    if reply == "":
        await cmd.finish("指令执行出错")
    await cmd.finish(reply)
