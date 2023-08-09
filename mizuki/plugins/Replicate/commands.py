# -*- coding = utf-8 -*-
# @File:commands.py.py
# @Author:Hycer_Lance
# @Time:2023/8/8 14:12
# @Software:PyCharm

from nonebot import on_command, get_driver
from nonebot.params import Arg
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER

from pathlib import Path
import os

from .Replicate import Replicate
from .ModelsManager import ModelsManager
from ..Utils.GroupAndGuildMessageSegment import GroupAndGuildMessageEvent, GroupAndGuildMessageSegment
from ..Utils.GroupAndGuildMessageEvent import get_event_user_id
from ..Utils.CDManager import CDManager
from ..Help.PluginInfo import PluginInfo

ai_draw_comm = on_command("replicate", aliases={"ai作画", "ai作图", "ai绘图", "ai绘画"}, priority=2, block=True)
set_model = on_command("model", aliases={"更换模型", "setmodel"}, priority=2, block=True)
add_model = on_command("addmodel", aliases={"添加模型", "增加模型"}, priority=3, block=True, permission=SUPERUSER)
del_model = on_command("delmodel", aliases={"删除模型"}, priority=3, block=True, permission=SUPERUSER)

__plugin_info__ = [PluginInfo(
    plugin_name="Replicate_AI_Draw",
    name="replicate ai 作画",
    description="ai根据用户发送的描述创作图片",
    usage="ai绘图 ——replicate绘图",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 2,
        "guild_adapted": True
    }
), PluginInfo(
    plugin_name="Replicate_set_model",
    name="更换replicate模型",
    description="更换replicate模型",
    usage="model ——更换、删除replicate模型",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 2,
        "guild_adapted": True
    }
), PluginInfo(
    plugin_name="Replicate_add_model",
    name="添加replicate模型",
    description="添加replicate模型",
    usage="addmodel ——添加replicate绘图模型",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 3,
        "permission": "SUPERUSER",
        "guild_adapted": True
    }
)]

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


@set_model.handle()
async def _(event: GroupAndGuildMessageEvent, state: T_State):
    model_manager = ModelsManager()
    current_model_name = model_manager.get_current_model_name()
    model_list = model_manager.get_models_list()

    reply = "模型列表:\n"
    num = 1
    for model_name in model_list:
        reply += f"{num}.{model_name}\n"
        state[f"{num}"] = model_name
        num += 1
    reply += f"\n当前模型:{current_model_name}\n\n更换模型请发送’set<模型序号>‘\n删除模型请发送‘del<模型序号>’\n发送‘取消’以取消当前操作"
    await set_model.send(reply)


@set_model.got("comm")
async def _(event: GroupAndGuildMessageEvent, state: T_State, comm=Arg("comm")):
    comm = str(comm)
    model_manager = ModelsManager()
    if comm.startswith("set"):
        num = comm.replace("set", "").replace(" ", "")
        if num in state.keys():
            set_model_name = state[f"{num}"]
            current_model_name = model_manager.get_current_model_name()
            if set_model_name == current_model_name:
                await set_model.finish(f"当前模型已为:{set_model_name}")
            model_manager.set_current_model_by_name(set_model_name)
            version = model_manager.get_current_model_version()
            await set_model.finish(f"当前模型已更改为:{set_model_name}\n\nVersion:{version}")
        await set_model.finish("未知模型序号")
    elif comm.startswith("del"):
        uid = str(await get_event_user_id(event))
        print(get_driver().config.superusers)
        if uid not in get_driver().config.superusers:
            await set_model.finish(GroupAndGuildMessageSegment.at(event) + "您没有权限删除模型")
        num = comm.replace("del", "").replace(" ", "")
        if num in state.keys():
            del_model_name = state[f"{num}"]
            current_model_name = model_manager.get_current_model_name()
            if del_model_name == current_model_name:
                await set_model.finish("您不能删除当前正在使用的模型")
            model_manager.remove_model_by_name(del_model_name)
            await set_model.finish(f"模型{del_model_name}删除完成")
        await set_model.finish("未知模型序号")
    await set_model.finish("已取消操作")


@add_model.got("model_name", prompt="请发送模型名称")
async def _(event: GroupAndGuildMessageEvent, state: T_State, model_name=Arg("model_name")):
    model_name = str(model_name)
    state["model_name"] = model_name


@add_model.got("model_version", prompt="请发送模型version")
async def _(event: GroupAndGuildMessageEvent, state: T_State, model_version=Arg("model_version")):
    models_manager = ModelsManager()
    model_version = str(model_version)
    model_name = state["model_name"]
    models_manager.add_model(model_name, model_version)
    await add_model.finish(f"模型{model_name}添加完成")
