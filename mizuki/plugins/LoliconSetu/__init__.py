# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/6/12 19:36
# @Software:PyCharm

from nonebot import on_regex
from nonebot.params import RegexDict
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .Lolicon import Lolicon

from typing import Dict

setu_re = on_regex("^来(?P<num>.*?)(张|份)(?P<kw>.*?)(的|)(涩图|setu|色图|图)$")


# noinspection PyDefaultArgument
@setu_re.handle()
async def _(event: GroupMessageEvent, data: Dict = RegexDict()):

    print(data["num"])
    if not str(data["num"]).isdigit():
        await setu_re.finish("未知数量参数", at_sender=True)
    if data["num"] == "":
        get_num = 1
    else:
        get_num = int(data["num"])
    kw = data["kw"]
    lolicon = Lolicon(num=get_num, keyword=kw)
    setu_list = await lolicon.get_image()
    if get_num <= 2:
        for setu in setu_list:
            send_image = f"[CQ:image,file={await setu.get_url()}]"
            await setu_re.send(send_image)
    else:
        reply = "大于2张"
        # 转换为结点发送
        await setu_re.finish(reply, at_sender=True)
