# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/8/17 9:18
# @Software:PyCharm

from nonebot import on_command
from nonebot.params import Arg, CommandArg
from nonebot.typing import T_State

from ..Utils.GroupAndGuildUtils import (GroupAndGuildMessageEvent,
                                        GroupAndGuildMessageSegment,
                                        GroupAndGuildMessage)
from ..Help.PluginInfo import PluginInfo
from .RunCode import RunCode, LanguageTypeError

run_code = on_command("code", aliases={"代码", "run"}, priority=5, block=True)

__plugin_info__ = PluginInfo(
    plugin_name="RunningCodeOnline",
    name="在线运行代码",
    description="在线运行代码",
    usage="code<语言名称> ——在线运行代码",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 5,
        "guild_adapted": True
    }
)


@run_code.handle()
async def _(event: GroupAndGuildMessageEvent, state: T_State, lang: GroupAndGuildMessage = CommandArg()):
    lang = lang.extract_plain_text()
    if lang == "":
        await run_code.finish(GroupAndGuildMessageSegment.at(event) + "请在指令后跟语言名称")
    try:
        runcode = RunCode(str(lang))
    except LanguageTypeError as e:
        await run_code.finish(GroupAndGuildMessageSegment.at(event) + e)
        return
    state["lang"] = runcode.get_language()
    state["runcode"] = runcode
    await run_code.send(GroupAndGuildMessageSegment.at(event) + f"请发送{state['lang']}代码")


@run_code.got("code_str")
async def _(event: GroupAndGuildMessageEvent, state: T_State, code_str=Arg("code_str")):
    runcode = state["runcode"]
    result = await runcode.run(str(code_str))
    await run_code.finish(GroupAndGuildMessageSegment.at(event) + result)
