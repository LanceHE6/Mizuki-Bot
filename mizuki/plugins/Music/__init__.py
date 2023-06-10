# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/5/18 10:06
# @Software:PyCharm

import requests
import json

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from ..Utils.PluginInfo import PluginInfo

order_music = on_command("music", aliases={"点歌"}, block=True, priority=4)

__plugin_info__ = PluginInfo(
    plugin_name="Music",
    name="点歌",
    description="利用第三方api实现qq点歌",
    usage="点歌<歌名> ——QQ音乐点歌",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 4
    }
)


@order_music.handle()
async def _(state: T_State, args: Message = CommandArg()):
    music_name = args.extract_plain_text().replace(' ', '')
    if music_name == '':
        await order_music.finish("请在指令后跟歌名", at_sender=True)
    api = f'https://api.xingzhige.com/API/QQmusicVIP_new?msg={music_name}&limit=5'
    state['api'] = api
    index = json.loads(requests.get(api).content)
    if index["code"] != 0:
        await order_music.finish(index["msg"])
    reply = f'为你找到以下有关 {music_name} 的歌曲\n'
    i = 1
    index_list = []
    for song in index["data"]:
        index_list.append(i)
        reply += f'{i}.{song["song"]}——{song["singers"][0]}\n'
        i += 1
    state["index_list"] = index_list
    reply += '请发送序号选择\n发送 取消 退出选歌'
    await order_music.send(reply)


@order_music.got('no')
async def _(state: T_State, no=Arg('no')):
    if no.extract_plain_text() == "取消":
        await order_music.finish("已退出选歌", at_sender=True)
    if isinstance(no, Message):
        no = int(no.extract_plain_text())
    if no not in state["index_list"]:
        await order_music.finish("未知序号", at_sender=True)
    api = state['api'] + f'&n={no}'
    response = json.loads(requests.get(api).content)
    if response["code"] != 0:
        await order_music.finish(response["msg"])
    song_id = response["data"]["songid"]
    cq_code = f'[CQ:music,type=qq,id={song_id}]'
    await order_music.finish(Message(cq_code))
