# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/8/8 14:12
# @Software:PyCharm

from nonebot import on_command
from nonebot.params import Arg

from pathlib import Path
import os

from .Replicate import Replicate
from ..Utils.GroupAndGuildMessageSegment import GroupAndGuildMessageEvent, GroupAndGuildMessageSegment
from ..Utils.GroupAndGuildMessageEvent import get_event_user_id
from ..Utils.CDManager import CDManager
from ..Help.PluginInfo import PluginInfo

ai_draw_comm = on_command("replicate", aliases={"ai作画", "ai作图", "ai绘图", "ai绘画"}, priority=2, block=True)

__plugin_info__ = PluginInfo(
    plugin_name="Replicate_AI_Draw",
    name="replicate ai 作画",
    description="根据用户发送的描述创作图片采用stability-ai/sdxl模型",
    usage="ai绘图 ——replicate绘图",
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
    replicate = Replicate()
    await ai_draw_comm.send("开始作画，请稍等...")
    img_path = await replicate.get_img_path(prompt)
    if isinstance(img_path, Path):
        await ai_draw_comm.send(
            GroupAndGuildMessageSegment.at(event) + GroupAndGuildMessageSegment.image(event, img_path))
        os.remove(img_path)
        await cd_manager.add_user(uid)
        await ai_draw_comm.finish()
    else:
        await cd_manager.add_user(uid)
        await ai_draw_comm.finish(GroupAndGuildMessageSegment.at(event)
                                  + img_path)
