# -*- coding = utf-8 -*-
# @File:commands.py
# @Author:Hycer_Lance
# @Time:2023/8/10 10:38
# @Software:PyCharm

from pathlib import Path

from nonebot import on_command
from nonebot.params import Arg

from .StableDiffusionAPI import StableDiffusionAPI
from ..Utils.GroupAndGuildMessageSegment import GroupAndGuildMessageSegment, GroupAndGuildMessageEvent
from ..Utils.GroupAndGuildMessageEvent import get_event_user_id
from ..Help.PluginInfo import PluginInfo
from ..Utils.CDManager import CDManager

ai_draw_comm = on_command("sd文生图", aliases={"文生图", "sd作图", "sd绘图", "sd绘画"}, priority=2, block=True)

__plugin_info__ = PluginInfo(
    plugin_name="Stable-diffusion-txt2img",
    name="sd ai 文生图",
    description="ai根据用户发送的描述创作图片",
    usage="sd绘图 ——sd文生图",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 2,
        "guild_adapted": True
    }
)

cd_manager = CDManager(30)

@ai_draw_comm.got("prompt", prompt="请发送作画描述")
async def _(event: GroupAndGuildMessageEvent, prompt=Arg("prompt")):
    uid = await get_event_user_id(event)
    if await cd_manager.is_in_cd(uid):
        await ai_draw_comm.finish(GroupAndGuildMessageSegment.at(event) +
                                  f"冷却中...剩余:{await cd_manager.get_remaining_time(uid)}s")
    await ai_draw_comm.send("开始生成，请耐心等待...")

    img_path = await StableDiffusionAPI.txt2img(prompt=prompt)

    if isinstance(img_path, Path):
        await ai_draw_comm.send(
            GroupAndGuildMessageSegment.at(event) + GroupAndGuildMessageSegment.image(event, img_path))
        # os.remove(img_path)
        await cd_manager.add_user(uid)
        await ai_draw_comm.finish()
    else:
        await cd_manager.add_user(uid)
        await ai_draw_comm.finish(GroupAndGuildMessageSegment.at(event)
                                  + img_path)
