# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/5/1 14:10
# @Software:PyCharm

from nonebot import on_message, on_command
from nonebot.rule import *
from nonebot.adapters.onebot.v11 import MessageEvent
from ..Utils.PluginInfo import PluginInfo

from .SessionManager import Session, SessionManager

chat = on_message(rule=to_me(), priority=2, block=True)
rm_session = on_command("rm_session", aliases={"清除会话记录", "清除聊天记录", "重置聊天", "重置聊天记录"}, priority=2, block=True)

__plugin_info__ = [PluginInfo(
    plugin_name="ChatGPT",
    name="ChatGPT",
    description="与bot愉快的聊天吧",
    usage="@bot<内容> ——与bot聊天",
    extra={
        "author": "Hycer_Lance",
        "version": "0.2.0",
        "priority": 2
    }
), PluginInfo(
    plugin_name="ChatGPT_rm_session",
    name="重置聊天",
    description="重置用户ChatGPT聊天",
    usage="重置聊天 ——重置与bot的聊天记录",
    extra={
        "author": "Hycer_Lance",
        "version": "0.2.0",
        "priority": 2
    }
)]

session_manager = SessionManager()

@chat.handle()
async def reply(event: MessageEvent):
    uid = event.get_user_id()
    # 判断当前用户会话是否存在
    if not await session_manager.is_session_exist(uid):
        # 不存在则添加进会话管理中
        await session_manager.add_session(uid, Session())
        session = await session_manager.get_session(uid)
    else:
        session = await session_manager.get_session(uid)

    user_content = str(event.get_message())
    await session.add_user_content(user_content)
    response = await session.get_response()
    await chat.finish(response, at_sender=True)

@rm_session.handle()
async def _(event: MessageEvent):
    uid = event.get_user_id()
    if not await session_manager.is_session_exist(uid):
        await rm_session.finish("你还没有和我聊过天哦", at_sender=True)
    await session_manager.remove_session(uid)
    await rm_session.finish("聊天已重置", at_sender=True)
