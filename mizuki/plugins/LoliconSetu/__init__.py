# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/6/12 19:36
# @Software:PyCharm

from nonebot import on_regex
from nonebot.params import RegexDict
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, Bot, Message

from typing import Dict

from .Lolicon import Lolicon

setu_re = on_regex("^来(?P<num>.*?)(张|份)(?P<kw>.*?)(的|)(涩图|setu|色图|图)$")


# noinspection PyDefaultArgument
@setu_re.handle()
async def _(bot: Bot, event: GroupMessageEvent, data: Dict = RegexDict()):
    if not str(data["num"]).isdigit():
        await setu_re.finish("未知数量参数", at_sender=True)
    if data["num"] == "":
        get_num = 1
    else:
        get_num = int(data["num"])
    kw = data["kw"]
    lolicon = Lolicon(num=get_num, keyword=kw)
    setu_list = await lolicon.get_image()
    if isinstance(setu_list, str):
        await setu_re.finish(f"请求出错:{setu_list}")
    if get_num <= 2:
        reply = ""
        for setu in setu_list:
            reply += MessageSegment.image(await setu.get_url())
        await setu_re.finish(reply)
    else:
        reply = []
        # 转换为结点发送
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
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=reply)
