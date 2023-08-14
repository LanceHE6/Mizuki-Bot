# -*- coding = utf-8 -*-
# @File:__init__.py
# @Author:Hycer_Lance
# @Time:2023/6/26 16:27
# @Software:PyCharm

from nonebot import on_command
from nonebot.params import CommandArg

from nonebot.adapters.qqguild import MessageEvent as GuildMessageEvent
from .utils import set_guild_bind
from ..Help.PluginInfo import PluginInfo

guild_bind = on_command("用户绑定", aliases={"bind", "绑定qq"}, block=True, priority=2)

__plugin_info__ = PluginInfo(
    plugin_name="GuildBing",
    name="频道用户绑定",
    description="频道用户绑定",
    usage="bind<QQ号> ——频道用户绑定qq(频道指令)",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 2,
        "guild_adapted": True
    }
)


@guild_bind.handle()
async def _(event: GuildMessageEvent, args=CommandArg()):
    gid = event.get_user_id()
    uid = str(args)
    if not uid.isdigit():
        await guild_bind.finish("未知QQ号")
    await set_guild_bind(uid, gid)
    await guild_bind.finish("用户绑定成功")
