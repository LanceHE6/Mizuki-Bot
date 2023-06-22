# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/6/12 19:36
# @Software:PyCharm
import os

from nonebot import on_regex
from nonebot.params import RegexDict
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, Bot, Message
from nonebot.adapters.qqguild import MessageSegment as GuildMessageSegment
from nonebot.adapters.qqguild import MessageEvent as GuildMessageEvent

from typing import Dict

from .Lolicon import Lolicon
from ..Utils.CDManager import CDManager
from ..Utils.MBot import MBot

setu_re = on_regex("^来(?P<num>.*?)(张|份)(?P<kw>.*?)(的|)(涩图|setu|色图|图)$")
setu_re_guild = on_regex("^来(张|份)(?P<kw>.*?)(的|)(涩图|setu|色图|图)$")

user_cd_manager = CDManager(60)  # 用户冷却管理器
group_cd_manager = CDManager(60)  # 群冷却管理器


# noinspection PyDefaultArgument
@setu_re.handle()
async def _(bot: Bot, event: GroupMessageEvent, data: Dict = RegexDict()):
    uid = event.get_user_id()
    gid = event.group_id
    mbot = MBot(bot)
    if await user_cd_manager.get_cooling_num() == 3:
        await group_cd_manager.add_user(gid)
    if await group_cd_manager.is_in_cd(gid):
        remain_time = await group_cd_manager.get_remaining_time(uid)
        await setu_re.finish(f"群冷却中,剩余 {remain_time} s", at_sender=True)
    if await user_cd_manager.is_in_cd(uid):
        remain_time = await user_cd_manager.get_remaining_time(uid)
        await setu_re.finish(f"用户冷却中,剩余 {remain_time} s", at_sender=True)
    if data["num"] == "" or data["num"] is None:
        get_num = 1
    elif not str(data["num"]).isdigit():
        get_num = 1
        await setu_re.finish("未知数量参数", at_sender=True)
    else:
        get_num = int(data["num"])
    if get_num > 5:
        await setu_re.finish("一次最多要5张哦", at_sender=True)
    kw = data["kw"]
    lolicon = Lolicon(num=get_num, keyword=kw)
    setu_list = await lolicon.get_image()
    if isinstance(setu_list, str):
        await setu_re.finish(f"请求出错:{setu_list}")
    if get_num <= 2:
        reply = ""
        for setu in setu_list:
            reply += MessageSegment.image(await setu.get_url()) + f"{await setu.get_title()}"
        await user_cd_manager.add_user(uid)
        await setu_re.finish(reply)
    else:
        reply = []
        # 转换为转发消息结点发送
        for setu in setu_list:
            meta_node = {
                "type": "node",
                "data": {
                    "name": "老色批",
                    "uin": f"{event.get_user_id()}",
                    "content": Message(f"[CQ:image,file={await setu.get_url()}]") +
                               Message(f"{await setu.get_title()}")
                }
            }
            reply.append(meta_node)
        await user_cd_manager.add_user(uid)
        await mbot.send_group_forward_msg(group_id=event.group_id, messages=reply)


# noinspection PyDefaultArgument
@setu_re.handle()
async def _(event: GuildMessageEvent, data: Dict = RegexDict()):
    uid = event.get_user_id()
    if await user_cd_manager.is_in_cd(uid):
        remain_time = await user_cd_manager.get_remaining_time(uid)
        await setu_re.finish(f"用户冷却中,剩余 {remain_time} s", at_sender=True)
    kw = data["kw"]
    lolicon = Lolicon(num=1, keyword=kw)
    setu_list = await lolicon.get_image()
    setu_path_list = await lolicon.get_path()
    if isinstance(setu_list, str):
        await setu_re.finish(f"请求出错:{setu_list}")
    reply = ""
    for setu_path, setu in zip(setu_path_list, setu_list):
        reply += GuildMessageSegment.file_image(setu_path) + f"{await setu.get_title()}"
        await setu_re.send(reply)
        os.remove(setu_path)

    await user_cd_manager.add_user(uid)
