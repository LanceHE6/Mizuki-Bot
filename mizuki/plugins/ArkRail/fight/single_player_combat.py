# -*- coding = utf-8 -*-
# @File:single_player_combat.py
# @Author:Silence
# @Time:2023/5/15 19:11
# @Software:PyCharm
from typing import Type

from nonebot import on_command
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent
from .playing_manager import PlayingManager, new_instance
from ...Utils.PluginInfo import PluginInfo
from ..DB import is_map_exist, get_map_attribute, MapAttribute
from ...Currency.utils import change_user_lmc_num, change_user_sj_num

play = on_command("play", aliases={"作战"}, block=True, priority=1)
playing_user: list[int] = []  # 正在进行战斗的用户


async def is_playing(uid: int) -> bool:  # 判断用户是否正在进行战斗
    return uid in playing_user


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
        if len(message) > 1 and message[len(message) - 1] in ["作战失败", "作战成功"]:  # 删除战斗信息
            if message[len(message) - 1] == "作战成功":  # 获取奖励
                reward = await get_map_attribute(mid, MapAttribute.reward)
                #  reward[0]: str 奖励名称  reward[1]: int 奖励数量
                if reward[0] == "龙门币":
                    await change_user_lmc_num(uid, reward[1])
                elif reward[0] == "合成玉":
                    await change_user_sj_num(uid, reward[1])
            is_over = True
        for s in message:
            await handle.send(s)
        if is_over:
            await finish_playing()

    def is_doctor(e: GroupMessageEvent) -> bool:  # 判断触发atk,skill,run指令的用户是否跟触发play指令的用户相同
        return int(e.get_user_id()) == uid

    uid = int(event.get_user_id())
    mid = args.extract_plain_text().replace(' ', '')  # 获取命令后面跟着的纯文本内容

    if not await is_map_exist(mid):  # 判断地图是否存在
        await play.finish(MessageSegment.at(uid) + f"没有{mid}这张地图！")
    if await is_playing(uid):
        await play.finish("你还有正在进行的战斗哦！")

    pm: PlayingManager = await new_instance(uid, mid)  # 战斗数据
    playing_user.append(uid)  # 将用户id放进战斗中的用户id列表
    await send_status_message(pm, play)

    operate_atk = on_command("atk", aliases={"attack", "普通攻击", "普攻", "攻击"}, rule=is_doctor, block=True, priority=1)
    operate_skill = on_command("skill", aliases={"技能", "使用技能"}, rule=is_doctor, block=True, priority=1)
    operate_run = on_command("run", aliases={"逃跑", "润", "溜了"}, rule=is_doctor, block=True, priority=1)

    await send_message_and_is_over(await pm.is_enemy_turn(), play)

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
            obj_num = int(str(atk_args))  # 目标序号
            if op.atk_type_p in [0, 1, 2, 3, 6]:
                obj = pm.map_enemies_list[obj_num - 1]  # 目标对象
                if op.mocked and op.mocking_obj != obj:
                    await operate_atk.finish(
                        f"你被{pm.map_enemies_list.index(op.mocking_obj) + 1}.{op.mocking_obj.name}嘲讽了！\n只能以ta为攻击目标！")
                if 0 < obj_num <= len(pm.map_enemies_list):
                    await send_message_and_is_over(await pm.turn(op, 0, obj), operate_atk)
                else:
                    await operate_atk.finish("目标序号错误！\n/atk <敌人序号>")
            else: 
                obj = pm.player_ops_list[obj_num - 1]  # 目标对象
                if 0 < obj_num <= len(pm.player_ops_list):
                    await send_message_and_is_over(await pm.turn(op, 0, obj), operate_atk)
                else:
                    await operate_atk.finish("目标序号错误！\n/atk <友方序号>")
        await send_status_message(pm, operate_atk)
        await send_message_and_is_over(await pm.is_enemy_turn(), operate_atk)
        await operate_atk.finish()

    @operate_skill.handle()
    async def _(skill_args: Message = CommandArg()):
        if pm.all_ops_list[0] not in pm.player_ops_list:
            await operate_skill.finish("现在还不是你的回合哦！")
        if pm.all_ops_list[0].silent:
            await operate_skill.finish("你被沉默了，无法使用技能！")
        parm_str_list: list[str] = str(skill_args).split(" ")
        parm_list: list[int] = []
        for n in parm_str_list:
            if n.isdigit():
                parm_list.append(int(n) - 1)
            else:
                await operate_run.finish("参数错误！\n/skill <技能序号> [目标序号1] [目标序号2/友方序号]")
        skill_num = parm_list[0]  # 技能序号(原始)
        op = pm.all_ops_list[0]  # 行动干员
        skill = None  # 使用的技能
        if 0 <= skill_num < len(op.skills_list):
            skill = op.skills_list[skill_num]
        else:
            await operate_skill.finish("该技能不存在！")

        if skill.consume > pm.player_skill_count:
            await operate_skill.finish("您的技力点不足以释放这个技能！")

        if skill.obj_type in [1, 4]:  # 单攻或扩散技能
            if len(parm_list) >= 2 and 0 <= parm_list[1] < len(pm.map_enemies_list):
                obj1 = pm.map_enemies_list[parm_list[1]] if skill.obj_type == 1 else pm.player_ops_list[parm_list[1]]
                if skill.obj_type == 1 and op.mocked and op.mocking_obj != obj1:
                    await operate_atk.finish(
                        f"你被{pm.map_enemies_list.index(op.mocking_obj) + 1}.{op.mocking_obj.name}嘲讽了！\n只能以ta为攻击目标！")
                await send_message_and_is_over(await pm.turn(op, skill_num + 1, obj1), operate_skill)
            else:
                await operate_run.finish("参数不足或敌人序号错误！\n/skill <技能序号> <目标序号>")
        elif skill.obj_type in [2, 5]:  # 双攻技能
            if len(parm_list) >= 3 and 0 <= parm_list[1] < len(pm.map_enemies_list) and \
                    0 <= parm_list[2] < len(pm.map_enemies_list) and parm_list[1] != parm_list[2]:
                obj1 = pm.map_enemies_list[parm_list[1]] if skill.obj_type == 2 else pm.player_ops_list[parm_list[1]]
                obj2 = pm.map_enemies_list[parm_list[2]] if skill.obj_type == 2 else pm.player_ops_list[parm_list[2]]
                if skill.obj_type == 3 and op.mocked and op.mocking_obj != obj1 and op.mocking_obj != obj2:
                    await operate_atk.finish(
                        f"你被{pm.map_enemies_list.index(op.mocking_obj) + 1}.{op.mocking_obj.name}嘲讽了！\nta必须为攻击目标之一！")
                await send_message_and_is_over(await pm.turn(op, skill_num + 1, obj1, obj2), operate_skill)
            else:
                await operate_run.finish("参数不足或敌人序号错误！\n/skill <技能序号> <目标序号1> <目标序号2>")
        elif skill.obj_type == 7:  # 目标为一个敌人和一个友方的技能
            if len(parm_list) >= 3 and 0 <= parm_list[1] < len(pm.map_enemies_list) and \
                    0 <= parm_list[2] < len(pm.player_ops_list):
                obj1 = pm.map_enemies_list[parm_list[1]]
                obj2 = pm.player_ops_list[parm_list[2]]
                if op.mocked and op.mocking_obj != obj1:
                    await operate_atk.finish(
                        f"你被{pm.map_enemies_list.index(op.mocking_obj) + 1}.{op.mocking_obj.name}嘲讽了！\n只能以ta为攻击目标！")
                await send_message_and_is_over(await pm.turn(op, skill_num + 1, obj1, obj2), operate_skill)
            else:
                await operate_run.finish("参数不足或敌人序号错误！\n/skill <技能序号> <目标序号> <友方序号>")
        else:
            await send_message_and_is_over(await pm.turn(op, skill_num + 1), operate_skill)
        await send_status_message(pm, operate_skill)
        await send_message_and_is_over(await pm.is_enemy_turn(), operate_skill)
        await operate_skill.finish()

    @operate_run.handle()
    async def _():
        await operate_run.send(f"{event.sender.nickname}逃跑了！")
        # await play.finish()
        # await operate_run.finish()
        await finish_playing()

    async def finish_playing():
        """
        结束对战的方法
        """
        playing_user.remove(uid)
        await delete_handle(operate_run)
        await delete_handle(operate_atk)
        await delete_handle(operate_skill)

        async def del_pm():
            del pm

        await del_pm()


async def delete_handle(obj: Type[Matcher]):
    """
    删除响应器的方法

    :param obj: 要删除的响应器
    """
    obj.destroy()
    del obj


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
