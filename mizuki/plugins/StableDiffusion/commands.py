# -*- coding = utf-8 -*-
# @File:commands.py
# @Author:Hycer_Lance
# @Time:2023/8/10 10:38
# @Software:PyCharm

from nonebot import on_command, Bot
from nonebot.params import Arg
from nonebot.typing import T_State

from .StableDiffusion import StableDiffusion
from ..Utils.GroupAndGuildUtils import (GroupAndGuildMessageSegment,
                                        GroupAndGuildMessageEvent,
                                        GroupAndGuildMessageUtils)
from ..Help.PluginInfo import PluginInfo
from ..Utils.QQ import QQ

txt2image_comm = on_command("sd文生图", aliases={"文生图", "sd作图", "sd绘图", "sd绘画"}, priority=2, block=True)
model_manage = on_command("sd_model", aliases={"sd_models", "sd模型", "sd模型管理", "sd模型列表"}, priority=2,
                          block=True)
get_progress = on_command("sd进度", aliases={"sd_progress"}, priority=2, block=True)

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
), PluginInfo(
    plugin_name="Stable-diffusion-progress",
    name="sd获取当前任务进度",
    description="sd获取当前任务进度",
    usage="sd进度 ——获取当前任务进度",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 2,
        "guild_adapted": True
    }
)]

sd = StableDiffusion()


@txt2image_comm.got("prompt", prompt="请发送作画描述")
async def _(event: GroupAndGuildMessageEvent, bot: Bot, prompt=Arg("prompt")):
    if not len(sd.tasks) == 0:
        await txt2image_comm.send(
            GroupAndGuildMessageSegment.at(event) + f"当前有{len(sd.tasks)}个任务正在进行中,您的任务将进行排队")
    prompt = str(prompt)
    await sd.add_txt2img(event, bot, prompt)
    await sd.run()

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


@get_progress.handle()
async def _(event: GroupAndGuildMessageEvent):
    if len(sd.tasks) == 0 and (await sd.get_progress()) == 0.0:
        await get_progress.finish("当前未进行任何任务")
    uid = await GroupAndGuildMessageUtils.get_event_user_id(sd.tasks[0][0])
    qq = QQ(uid)
    nick_name = qq.get_nickname()
    current_task = sd.tasks[0][2]
    task_type = current_task.task_type
    task_prompt = current_task.prompt
    progress = await sd.get_progress()
    await get_progress.finish(f"当前任务\n"
                              f"用户:{nick_name}\n"
                              f"类型:{task_type}\n"
                              f"prompt:{task_prompt}\n"
                              f"进度:{round(progress * 100, 1)}%")
