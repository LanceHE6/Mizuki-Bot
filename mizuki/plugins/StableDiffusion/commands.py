# -*- coding = utf-8 -*-
# @File:commands.py
# @Author:Hycer_Lance
# @Time:2023/8/10 10:38
# @Software:PyCharm

from pathlib import Path

from nonebot import on_command
from nonebot.params import Arg
from nonebot.typing import T_State

from .StableDiffusion import StableDiffusion
from ..Utils.GroupAndGuildUtils import (GroupAndGuildMessageSegment,
                                        GroupAndGuildMessageEvent,
                                        GroupAndGuildMessageUtils)
from ..Help.PluginInfo import PluginInfo
from ..Utils.CDManager import CDManager

txt2image_comm = on_command("sd文生图", aliases={"文生图", "sd作图", "sd绘图", "sd绘画"}, priority=2, block=True)
model_manage = on_command("sd_model", aliases={"sd_models", "sd模型", "sd模型管理", "sd模型列表"}, priority=2,
                          block=True)

__plugin_info__ = [PluginInfo(
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
), PluginInfo(
    plugin_name="Stable-diffusion-model-manage",
    name="sd模型管理",
    description="sd模型管理",
    usage="sd模型 ——sd模型管理",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 2,
        "guild_adapted": True
    }
)]

cd_manager = CDManager(30)
sd = StableDiffusion()
occupied = False  # 占用标签


@txt2image_comm.handle()
async def _(event: GroupAndGuildMessageEvent):
    # CD判断
    uid = await GroupAndGuildMessageUtils.get_event_user_id(event)
    if await cd_manager.is_in_cd(uid):
        await txt2image_comm.finish(GroupAndGuildMessageSegment.at(event) +
                                    f"冷却中...剩余:{await cd_manager.get_remaining_time(uid)}s")

    # 任务进行中判断
    global occupied
    if not occupied:
        occupied = True
    else:
        await txt2image_comm.finish(GroupAndGuildMessageSegment.at(event) + "当前有绘图任务正在进行中")


@txt2image_comm.got("prompt", prompt="请发送作画描述")
async def _(event: GroupAndGuildMessageEvent, prompt=Arg("prompt")):
    global occupied
    uid = await GroupAndGuildMessageUtils.get_event_user_id(event)
    await txt2image_comm.send("开始生成，请耐心等待...")

    img_path = await sd.txt2img(prompt)

    if isinstance(img_path, Path):
        await txt2image_comm.send(
            GroupAndGuildMessageSegment.at(event) + GroupAndGuildMessageSegment.image(event, img_path))
        # os.remove(img_path)
        await cd_manager.add_user(uid)
        occupied = False  # 解除占用
        await txt2image_comm.finish()
    else:
        await cd_manager.add_user(uid)
        occupied = False  # 解除占用
        await txt2image_comm.finish(GroupAndGuildMessageSegment.at(event)
                                    + img_path)


@model_manage.handle()
async def _(event: GroupAndGuildMessageEvent, state: T_State):
    models_list = sd.get_models_list()
    current_model_title = sd.get_current_model_title()
    if isinstance(models_list, str) or "请求出错" in current_model_title:
        await model_manage.finish("请求模型信息出错")
    state["model_list"] = models_list
    state["current_model_title"] = current_model_title
    reply = "模型列表\n"
    number = 1
    for model_title in models_list:
        reply += f"{number}.{model_title}\n"
        number += 1
    reply += f"\n当前模型:{current_model_title}\n\n若需修改模型请发送set <模型序号>"
    await model_manage.send(reply)


@model_manage.got("model_num")
async def _(event: GroupAndGuildMessageEvent, state: T_State, model_num=Arg("model_num")):
    if str(model_num).startswith("set"):
        model_num = int(str(model_num).replace("set", "").replace(" ", ""))
        if model_num == "" or model_num > len(list(state["model_list"])) or model_num < 1:
            await model_manage.finish("未知模型序号")
        else:
            if state["model_list"][model_num - 1] == state["current_model_title"]:
                await model_manage.finish("当前模型正在使用")
            result = await sd.set_model(state["model_list"][model_num - 1])
            if result == 0:
                await model_manage.finish(f"修改成功,当前模型为{state['model_list'][model_num - 1]}")
