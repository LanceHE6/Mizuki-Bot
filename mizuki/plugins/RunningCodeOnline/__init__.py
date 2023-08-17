# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/8/17 9:18
# @Software:PyCharm

from nonebot import on_command
from nonebot.params import CommandArg

from ..Utils.GroupAndGuildUtils import (GroupAndGuildMessageEvent,
                                        GroupAndGuildMessage,
                                        GroupAndGuildMessageSegment)
from ..Help.PluginInfo import PluginInfo
from .RunCode import RunCode

run_code = on_command("code", aliases={"代码", "run"}, priority=5, block=True)

__plugin_info__ = PluginInfo(
    plugin_name="RunningCodeOnline",
    name="在线运行代码",
    description="在线运行代码",
    usage="code<代码> ——在线运行代码",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 5,
        "guild_adapted": True
    }
)


@run_code.handle()
async def _(event: GroupAndGuildMessageEvent, user_input: GroupAndGuildMessage = CommandArg()):
    user_input = user_input.extract_plain_text()
    runcode = RunCode(user_input)
    result = await runcode.run()
    await run_code.finish(GroupAndGuildMessageSegment.at(event) + result)
