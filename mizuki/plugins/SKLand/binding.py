# -*- coding = utf-8 -*-
# @File:binding.py
# @Author:Hycer_Lance
# @Time:2023/9/9 9:29
# @Software:PyCharm

from typing import Union

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.params import Arg
from nonebot.adapters.onebot.v11 import PrivateMessageEvent

from ..Utils.GroupAndGuildUtils import (GroupAndGuildMessageEvent,
                                        GroupAndGuildMessageSegment,
                                        GroupAndGuildMessageUtils)
from ..Help.PluginInfo import PluginInfo
from .SKLand import SKLand

binding_by_token_comm = on_command("skland绑定", aliases={"skbinding", "森空岛绑定"}, block=True, priority=3)

__plugin_info__ = PluginInfo(
    plugin_name="SKLand_binding",
    name="森空岛绑定",
    description="利用token绑定森空岛账号",
    usage="森空岛绑定 ——绑定森空岛账号",
    extra={
        "author": "Hycer_Lance",
        "version": "1.0.0",
        "priority": 3,
        "guild_adapted": True
    }
)

@binding_by_token_comm.handle()
async def _(event: Union[GroupAndGuildMessageEvent, PrivateMessageEvent], state: T_State):
    if isinstance(event, GroupAndGuildMessageEvent):
        state["is_group"] = True
        await binding_by_token_comm.send(GroupAndGuildMessageSegment.at(event) + "请发送鹰角网络凭证token")
    else:
        state["is_group"] = False
        await binding_by_token_comm.send("请发送鹰角网络凭证token")


@binding_by_token_comm.got("token")
async def _(event: Union[GroupAndGuildMessageEvent, PrivateMessageEvent], state: T_State, token=Arg("token")):
    if isinstance(event, GroupAndGuildMessageEvent):
        qid = str(await GroupAndGuildMessageUtils.get_event_user_id(event))
    else:
        qid = event.get_user_id()
    token = str(token)
    skland = SKLand()
    result = await skland.binding_by_token(qid, token)
    if 0 in result:
        reply = f"绑定成功\nUID:{skland.binding_arknights_role['uid']}\n" \
                f"角色:{skland.binding_arknights_role['nickName']}\n" \
                f"服务器:{skland.binding_arknights_role['channelName']}"
    else:
        reply = result[1]
    if state["is_group"]:
        reply += "\n当前处于公共聊天区域，为了您的账号安全建议撤回token"
    await binding_by_token_comm.finish(reply)
