# -*- coding = utf-8 -*-
# @File:single_player_combat.py
# @Author:Silence
# @Time:2023/5/15 19:11
# @Software:PyCharm
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent
from playing_manager import PlayingManager, new_instance
from ...Utils.PluginInfo import PluginInfo
from ..DB import is_map_exist

play = on_command("play", aliases={"作战"}, block=True, priority=1)

__plugin_info__ = PluginInfo(
    plugin_name="ArkRail_play",
    name="单人作战",
    description="进行单人作战",
    usage="play <关卡编号> ——进行单人作战",
    extra={
        "author": "Silence",
        "version": "0.1.0",
        "priority": 1
    }
)


@play.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    uid = int(event.get_user_id())
    mid = args.extract_plain_text().replace(' ', '')  # 获取命令后面跟着的纯文本内容

    if not await is_map_exist(mid):
        await play.finish(MessageSegment.at(uid) + f"没有{mid}这张地图！")

    pm = new_instance(uid, mid)
