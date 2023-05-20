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

__plugin_info__ = [
    PluginInfo(
        plugin_name="ArkRail_play",
        name="单人作战",
        description="进行单人作战",
        usage="play <关卡编号> ——进行单人作战",
        extra={
            "author": "Silence",
            "version": "0.1.0",
            "priority": 1
        }
    ),
    PluginInfo(
        plugin_name="ArkRail_play_atk",
        name="普攻",
        description="对敌人进行普通攻击",
        usage="atk [目标序号] ——(作战中)进行普攻",
        extra={
            "author": "Silence",
            "version": "0.1.0",
            "priority": 1
        }
    ),
    PluginInfo(
        plugin_name="ArkRail_play_skill",
        name="使用技能",
        description="使用干员的技能",
        usage="skill <技能序号> [目标序号1] [目标序号2] ——(作战中)使用技能",
        extra={
            "author": "Silence",
            "version": "0.1.0",
            "priority": 1
        }
    ),
    PluginInfo(
        plugin_name="ArkRail_play_run",
        name="逃跑",
        description="逃跑",
        usage="run ——(作战中)逃跑",
        extra={
            "author": "Silence",
            "version": "0.1.0",
            "priority": 1
        }
    )
]


@play.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    async def send_message_and_is_over(message: list[str], handle):
        """
        发送消息并判断战斗时候结束所使用的的函数

        :param message: 要发送的信息列表
        :param handle: 用于发送消息
        """
        is_over: bool = False
        if len(message) > 1 and message[len(message) - 1] in ["作战失败", "作战成功"]:
            if message[len(message) - 1] == "作战成功":
                pass  # 获取奖励
            del pm  # 删除战斗信息
            is_over = True
        for s in message:
            await handle.send(s)
        if is_over:
            await play.finish()

    uid = int(event.get_user_id())
    mid = args.extract_plain_text().replace(' ', '')  # 获取命令后面跟着的纯文本内容

    if not await is_map_exist(mid):
        await play.finish(MessageSegment.at(uid) + f"没有{mid}这张地图！")

    pm: PlayingManager = await new_instance(uid, mid)

    await send_status_message(pm, play)

    operate_atk = on_command("atk", aliases={"attack", "普通攻击", "普攻", "攻击"}, block=True, priority=1)
    operate_skill = on_command("skill", aliases={"技能", "使用技能"}, block=True, priority=1)
    operate_run = on_command("run", aliases={"逃跑", "润", "溜了"}, block=True, priority=1)

    await send_message_and_is_over(await pm.is_enemy_turn(play), play)

    @operate_atk.handle()
    async def _(atk_args: Message = CommandArg()):
        if pm.all_ops_list[0] not in pm.player_ops_list:
            await operate_atk.finish("现在还不是你的回合哦！")
        op = pm.all_ops_list[0]  # 行动干员
        if op.atk_type_p == 7:
            await send_message_and_is_over(await pm.turn(op, 0), operate_atk)
        elif not str(atk_args).isdigit():
            await operate_atk.finish("参数错误！\n/atk <目标序号>\ntip:不普攻的干员可以不选目标")
        else:
            obj_num = int(str(atk_args))
            if op.atk_type_p in [0, 1, 2, 3, 6]:
                if 0 < obj_num <= len(pm.map_enemies_list):
                    await send_message_and_is_over(await pm.turn(op, 0, pm.map_enemies_list[obj_num - 1]), operate_atk)
                else:
                    await operate_atk.finish("目标序号错误！\n/atk <敌人序号>")
            else:
                if 0 < obj_num <= len(pm.player_ops_list):
                    await send_message_and_is_over(await pm.turn(op, 0, pm.player_ops_list[obj_num - 1]), operate_atk)
                else:
                    await operate_atk.finish("目标序号错误！\n/atk <友方序号>")
        await send_status_message(pm, operate_atk)
        await send_message_and_is_over(await pm.is_enemy_turn(play), operate_atk)
        await operate_atk.finish()

    @operate_skill.handle()
    async def _(skill_args: Message = CommandArg()):
        if pm.all_ops_list[0] not in pm.player_ops_list:
            await operate_skill.finish("现在还不是你的回合哦！")
        parm_str_list: list[str] = str(skill_args).split(" ")
        parm_list: list[int] = []
        for n in parm_str_list:
            if n.isdigit():
                parm_list.append(int(n) - 1)
            else:
                await operate_run.finish("参数错误！\n/skill <技能序号> [目标序号1] [目标序号2/友方序号]")
        skill_num = parm_list[0] - 1  # 技能序号
        op = pm.all_ops_list[0]  # 行动干员
        skill = None  # 使用的技能

        if 0 <= skill_num < len(op.skills_list):
            skill = op.skills_list[skill_num]
        else:
            await operate_skill.finish("该技能不存在！")

        if skill.consume > pm.player_skill_count:
            await operate_skill.finish("您的技力点不足以释放这个技能！")

        await operate_skill.send(str(skill.obj_type))
        if skill.obj_type in [1, 4]:
            if len(parm_list) >= 2 and 0 <= parm_list[1] < len(pm.map_enemies_list):
                obj1 = pm.map_enemies_list[parm_list[1]] if skill.obj_type == 1 else pm.player_ops_list[parm_list[1]]
                await send_message_and_is_over(await pm.turn(op, skill_num + 1, obj1), operate_skill)
            else:
                await operate_run.finish("参数不足或敌人序号错误！\n/skill <技能序号> <目标序号>")
        elif skill.obj_type in [2, 5]:
            if len(parm_list) >= 3 and 0 <= parm_list[1] < len(pm.map_enemies_list) and \
                    0 <= parm_list[2] < len(pm.map_enemies_list) and parm_list[1] != parm_list[2]:
                obj1 = pm.map_enemies_list[parm_list[1]] if skill.obj_type == 2 else pm.player_ops_list[parm_list[1]]
                obj2 = pm.map_enemies_list[parm_list[2]] if skill.obj_type == 2 else pm.player_ops_list[parm_list[2]]
                await send_message_and_is_over(await pm.turn(op, skill_num + 1, obj1, obj2), operate_skill)
            else:
                await operate_run.finish("参数不足或敌人序号错误！\n/skill <技能序号> <目标序号1> <目标序号2>")
        elif skill.obj_type == 7:
            if len(parm_list) >= 3 and 0 <= parm_list[1] < len(pm.map_enemies_list) and \
                    0 <= parm_list[2] < len(pm.player_ops_list):
                obj1 = pm.map_enemies_list[parm_list[1]]
                obj2 = pm.player_ops_list[parm_list[2]]
                await send_message_and_is_over(await pm.turn(op, skill_num + 1, obj1, obj2), operate_skill)
            else:
                await operate_run.finish("参数不足或敌人序号错误！\n/skill <技能序号> <目标序号> <友方序号>")
        else:
            await send_message_and_is_over(await pm.turn(op, skill_num + 1), operate_skill)
        await send_status_message(pm, operate_skill)
        await send_message_and_is_over(await pm.is_enemy_turn(play), operate_skill)
        await operate_skill.finish()

    @operate_run.handle()
    async def _():
        await operate_run.send(f"{uid}逃跑了！")
        del pm
        await play.finish()
        await operate_run.finish()


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
