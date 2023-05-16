# -*- coding = utf-8 -*-
# @File:single_player_combat.py
# @Author:Silence
# @Time:2023/5/15 19:11
# @Software:PyCharm
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent
from .playing_manager import PlayingManager, new_instance
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

    pm: PlayingManager = await new_instance(uid, mid)

    reply1 = "我方干员："
    for op in pm.player_ops_list:
        reply1 += f"\n{op.name}     血量：{op.health}"
    reply1 += f"\n我方剩余技力点：{pm.player_skill_count}"

    reply2 = "敌方干员："
    for op in pm.map_enemies_list:
        reply2 += f"\n{op.name}     血量：{op.health}"
    reply2 += f"\n敌方剩余技力点：{pm.enemy_skill_count}"

    reply3 = "行动顺序："
    for op in pm.all_ops_list:
        reply3 += f"\n{op.name}     速度：{op.speed}"
    await play.send(reply1)
    await play.send(reply2)
    await play.finish(reply3)
