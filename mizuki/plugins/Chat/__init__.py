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

# 思知机器人
data = {
    "appid": "daea57f1906444d87c408a74d1b7ea9f",
    "userid": "9URYu8cD",
    "spoken": ""
}
chat = on_message(rule=to_me(), priority=2, block=True)


@chat.handle()
async def reply(event: Event):
    data["spoken"] = str(event.get_message())
    api = 'https://api.ownthink.com/bot'
    result = json.loads(requests.post(url=api, data=json.dumps(data)).content)
    message = result['data']['info']['text']
    await chat.finish(MessageSegment.at(event.get_user_id()) + Message(message))

