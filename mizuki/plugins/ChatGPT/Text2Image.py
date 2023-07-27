# -*- coding = utf-8 -*-
# @File:Text2Image.py
# @Author:Hycer_Lance
# @Time:2023/7/27 14:05
# @Software:PyCharm

from nonebot import on_command
from nonebot.params import Arg

from pathlib import Path
import os

from .AIDraw import AIDraw
from ..Utils.GroupAndGuildMessageSegment import GroupAndGuildMessageEvent, GroupAndGuildMessageSegment
from ..Help.PluginInfo import PluginInfo

ai_draw_comm = on_command("ai绘图", aliases={"ai作画", "dall", "ai作图"}, priority=2, block=True)

__plugin_info__ = PluginInfo(
    plugin_name="ChatGPT_Dall_AIDraw",
    name="ChatGPT Dall绘图",
    description="根据用户发送的描述创作图片",
    usage="ai绘图 ——ChatGPT绘图",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 2,
        "guild_adapted": True
    }
)


@ai_draw_comm.got("prompt", prompt="请发送作画描述")
async def _(event: GroupAndGuildMessageEvent, prompt=Arg("prompt")):
    ai_draw = AIDraw(prompt)
    await ai_draw_comm.send("开始作画，请稍等...")
    img_url = await ai_draw.get_image()
    if isinstance(img_url, Path):
        await ai_draw_comm.send(
            GroupAndGuildMessageSegment.at(event) + GroupAndGuildMessageSegment.image(event, img_url))
        os.remove(img_url)
        await ai_draw_comm.finish()
    else:
        await ai_draw_comm.finish(GroupAndGuildMessageSegment.at(event) + img_url)
