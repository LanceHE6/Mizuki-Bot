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

    await send_status_message(pm, play)

    atk = on_command("atk", aliases={"attack", "普通攻击", "普攻", "攻击"}, block=True, priority=1)
    skill = on_command("skill", aliases={"技能", "使用技能"}, block=True, priority=1)
    run = on_command("run", aliases={"逃跑", "润", "溜了"}, block=True, priority=1)

    await send_message_list(await pm.is_enemy_turn(), play)

    @atk.handle()
    async def _(args: Message = CommandArg()):
        if pm.all_ops_list[0] not in pm.player_ops_list:
            await atk.finish("现在还不是你的回合哦！")
        enemy_num = args.extract_plain_text().replace(' ', '')  # 获取命令后面跟着的纯文本内容
        await atk.send(await pm.turn(pm.all_ops_list[0], 0, pm.map_enemies_list[int(enemy_num) - 1]))
        await send_status_message(pm, atk)
        await send_message_list(await pm.is_enemy_turn(), atk)
        await atk.finish()

    @skill.handle()
    async def _(args: Message = CommandArg()):
        if pm.all_ops_list[0] not in pm.player_ops_list:
            await skill.finish("现在还不是你的回合哦！")
        enemy_num = args.extract_plain_text().replace(' ', '')  # 获取命令后面跟着的纯文本内容
        skill_num = 0
        if pm.all_ops_list[0].skills_list[skill_num].consume > pm.player_skill_count:
            await skill.finish("您的技力点不足以释放这个技能！")
        await skill.send(await pm.turn(pm.all_ops_list[0], skill_num + 1, pm.map_enemies_list[int(enemy_num) - 1]))
        await send_status_message(pm, skill)
        await send_message_list(await pm.is_enemy_turn(), skill)
        await skill.finish()


async def send_message_list(message: list[str], handle):
    """
    发送消息所使用的的函数

    :param message: 要发送的信息列表
    :param handle: 用于发送消息
    """
    if not len(message):
        return
    for s in message:
        await handle.send(s)


async def send_status_message(pm: PlayingManager, handle):
    """
    返回所有参战人员状态的函数

    :param pm: PlayingManage对象，包含了这场战斗的所有数据
    :param handle: 用于发送消息
    :return: 一个字符串列表，表示参战人员状态信息
    """
    i = 1
    reply1 = "我方干员："
    for op in pm.player_ops_list:
        reply1 += f"\n{i}.{op.name}     血量：{op.health}"
        i += 1
    reply1 += f"\n我方剩余技力点：{pm.player_skill_count}"

    j = 1
    reply2 = "敌方干员："
    for op in pm.map_enemies_list:
        reply2 += f"\n{j}.{op.name}     血量：{op.health}"
        j += 1
    reply2 += f"\n敌方剩余技力点：{pm.enemy_skill_count}"

    k = 1
    reply3 = "行动顺序："
    for op in pm.all_ops_list:
        reply3 += f"\n{k}.{op.name}     速度：{op.speed_p}"
        k += 1

    await handle.send(reply1)
    await handle.send(reply2)
    await handle.send(reply3)
