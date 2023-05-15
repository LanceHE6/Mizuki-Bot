# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/5/1 14:10
# @Software:PyCharm
import requests
import json
from nonebot import on_message
from nonebot.rule import *
from nonebot.adapters.onebot.v11 import Message, Event, MessageSegment
from ..Utils.PluginInfo import PluginInfo

# 思知机器人
data = {
    "appid": "daea57f1906444d87c408a74d1b7ea9f",
    "userid": "9URYu8cD",
    "spoken": ""
}
chat = on_message(rule=to_me(), priority=2, block=True)

__plugin_info__ = PluginInfo(
    plugin_name="Chat",
    name="Chat",
    description="与bot愉快的聊天吧",
    usage="@bot<内容> ——与bot聊天",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 2
    }
)

@chat.handle()
async def reply(event: Event):
    data["spoken"] = str(event.get_message())
    api = 'https://api.ownthink.com/bot'
    result = json.loads(requests.post(url=api, data=json.dumps(data)).content)
    message = result['data']['info']['text']
    await chat.finish(MessageSegment.at(event.get_user_id()) + Message(message))

