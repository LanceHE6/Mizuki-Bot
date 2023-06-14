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
from ..DB import is_map_exist, get_map_attribute, MapAttribute, user_agar
from ...Currency.utils import change_user_lmc_num, change_user_sj_num
from .draw_image import draw_player_fight_image

play = on_command("play", aliases={"作战"}, block=True, priority=1)
playing_user: list[int] = []  # 正在进行战斗的用户
MAX_PLAYING_PERSON = 3  # 最大同时作战人数


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
    async def send_message_and_is_over(messages: list[str], handle):
        """
        发送消息并判断战斗时候结束所使用的的函数

        :param messages: 要发送的信息列表
        :param handle: 用于发送消息
        """
        is_over: bool = False
        if len(messages) > 1 and messages[len(messages) - 1] in ["作战失败", "作战成功"]:  # 删除战斗信息
            if messages[len(messages) - 1] == "作战成功":  # 获取奖励
                consume = await get_map_attribute(mid, MapAttribute.consume)
                if not await user_agar(uid, consume):
                    reward = await get_map_attribute(mid, MapAttribute.reward)
                    #  reward[0]: str 奖励名称  reward[1]: int 奖励数量
                    if reward[0] == "龙门币":
                        await change_user_lmc_num(uid, reward[1])
                    elif reward[0] == "合成玉":
                        await change_user_sj_num(uid, reward[1])
                else:
                    await handle.send("您的琼脂不足，无法获取关卡奖励！")
            is_over = True
            await handle.send(messages[len(messages) - 1])
        if is_over:
            await finish_playing()

    def is_doctor(e: GroupMessageEvent) -> bool:  # 判断触发atk,skill,run指令的用户是否跟触发play指令的用户相同
        return int(e.get_user_id()) == uid

    if len(playing_user) > MAX_PLAYING_PERSON:
        playing_user_name = ""
        for u in playing_user:
            playing_user_name += f"{u} "
        await play.finish(f"当前作战人数较多，请稍后再进行作战哦！\n{playing_user_name}正在进行作战...")

    uid = int(event.get_user_id())
    mid = args.extract_plain_text().replace(' ', '')  # 获取命令后面跟着的纯文本内容

    if not await is_map_exist(mid):  # 判断地图是否存在
        await play.finish(MessageSegment.at(uid) + f"没有{mid}这张地图！")
    if await is_playing(uid):
        await play.finish("你还有正在进行的战斗哦！")

    pm: PlayingManager = await new_instance(uid, mid)  # 战斗数据
    playing_user.append(uid)  # 将用户id放进战斗中的用户id列表

    operate_atk = on_command("atk", aliases={"attack", "普通攻击", "普攻", "攻击"}, rule=is_doctor, block=True, priority=1)
    operate_skill = on_command("skill", aliases={"技能", "使用技能"}, rule=is_doctor, block=True, priority=1)
    operate_run = on_command("run", aliases={"逃跑", "润", "溜了"}, rule=is_doctor, block=True, priority=1)

    # 先进行一次判断，如果是敌人先手则敌方先行动
    message = await pm.is_enemy_turn()
    await send_message_and_is_over(message, play)
    await send_status_image(pm, message)  # 绘制战斗数据图片

    # 后面就是命令定义了

    @operate_atk.handle()
    async def _(atk_args: Message = CommandArg()):
        """
        干员普攻指令/atk [目标序号(int)]
        :param atk_args: [目标序号(int)]，只有当干员的攻击类型为“不攻击”时才能为空
        """
        message_atk: list[str] = []  # 消息列表
        # 判断是否是我方回合，如果不是的话则退出当前方法
        if pm.all_list[0] not in pm.all_ops_list:
            await operate_atk.finish(f"现在是{pm.all_list[0].name}的回合哦！")

        # 获取当前行动干员
        op = pm.all_list[0]

        # 根据行动干员攻击类型的不同做出不同的操作
        if op.atk_type_p == 9:  # 9代表不攻击，不攻击的干员不需要参数
            message_atk = await pm.turn(op, 0)
            await send_message_and_is_over(message_atk, operate_atk)

        # 如果输入的参数无法转换为数字
        elif not str(atk_args).isdigit():
            await operate_atk.finish("参数错误！\n/atk <目标序号>\ntip:不普攻的干员才可以不选目标")

        # 正常普攻干员的普攻逻辑在下面
        else:
            obj_num = int(str(atk_args))  # 目标序号

            # 如果干员的攻击目标是敌人(如果是治疗型干员的话“攻击”目标就是我方干员了)
            if op.atk_type_p in [0, 1, 2, 3, 6, 7, 8]:

                # 如果输入的参数不合理(超出敌人列表索引范围)
                if not 0 < obj_num <= len(pm.all_enemies_list):
                    await operate_atk.finish("目标序号错误！\n/atk <敌人序号>")

                # 目标对象
                obj = pm.all_enemies_list[obj_num - 1]

                # 如果干员被嘲讽的话，就只能以嘲讽对象为攻击目标
                if op.mocked and op.mocking_obj != obj:
                    await operate_atk.finish(
                        f"你被{pm.all_enemies_list.index(op.mocking_obj) + 1}.{op.mocking_obj.name}嘲讽了！\n只能以ta为攻击目标！")

                # 不能以隐匿状态下的敌人为目标
                elif obj.hidden:
                    await operate_atk.finish(f"{obj.name}处于隐匿状态，无法被选中！")

                # 进行普攻
                message_atk = await pm.turn(op, 0, obj)
                await send_message_and_is_over(message_atk, operate_atk)

            # 如果干员的攻击目标是我方干员
            else:

                # 如果输入的参数不合理(超出我方干员列表索引范围)
                if not 0 < obj_num <= len(pm.all_ops_list):
                    await operate_atk.finish("目标序号错误！\n/atk <友方序号>")

                # 目标对象
                obj = pm.all_ops_list[obj_num - 1]

                # 进行普攻
                message_atk = await pm.turn(op, 0, obj)
                await send_message_and_is_over(message_atk, operate_atk)

        # 我方行动后判断是否是敌方干员回合，如果是则让敌方干员行动
        message2 = await pm.is_enemy_turn()
        message_atk += message2
        await send_message_and_is_over(message2, operate_atk)

        # 再次等到我方干员回合再绘制战斗状态图
        await send_status_image(pm, message_atk)

        # 方法结束
        await operate_atk.finish()

    @operate_skill.handle()
    async def _(skill_args: Message = CommandArg()):
        """
        干员释放技能指令/skill <技能序号(int)> [目标序号1(int)] [目标序号2(int)]

        目标类型列表
        0:自身  1:单个敌人  2:两个敌人  3:所有敌人  4:单个我方  5:两个我方  6:所有我方  7:单个敌方和单个我方

        :param skill_args: <技能序号(int)> [目标序号1(int)] [目标序号2(int)]，技能序号必填，根据技能类型选填目标序号
        """
        message_skill: list[str] = []  # 消息列表

        # 判断是否是我方干员回合
        if pm.all_list[0] not in pm.all_ops_list:
            await operate_skill.finish("现在还不是你的回合哦！")

        # 如果干员被沉默则无法使用技能
        if pm.all_list[0].silent:
            await operate_skill.finish("你被沉默了，无法使用技能！")

        # 将命令参数字符串分解为参数列表(str型)
        parm_str_list: list[str] = str(skill_args).split(" ")

        # 参数列表(int型)
        parm_list: list[int] = []

        # 将str型参数列表转换为int型参数列表
        for n in parm_str_list:

            # 判断输入的参数是否是数字
            if n.isdigit():
                # 将str型参数转换为int型参数(因为skill列表索引从0开始，所以要-1)
                parm_list.append(int(n) - 1)
            else:
                await operate_run.finish("参数错误！\n/skill <技能序号> [目标序号1] [目标序号2/友方序号]")

        skill_num = parm_list[0]  # 技能序号(int)
        op = pm.all_list[0]  # 行动干员
        skill = None  # 使用的技能

        # 判断技能序号输入是否正确
        if 0 <= skill_num < len(op.skills_list):
            # 获取干员要使用的技能
            skill = op.skills_list[skill_num]
        else:
            await operate_skill.finish("该技能不存在！")

        # 判断玩家当前技力点是否足够
        if skill.consume > pm.player_skill_count:
            await operate_skill.finish("您的技力点不足以释放这个技能！")

        # 判断技能是否在持续时间内
        elif skill.count > 0:
            await operate_skill.finish("该技能还在持续时间内！")

        # 以下是技能释放逻辑
        # 单体技能
        if skill.obj_type in [1, 4]:
            # 如果参数大于两个 且 ((技能对敌 且 敌人序号参数正确) 或 (技能对友 且 友方序号参数正确))
            if len(parm_list) >= 2 and \
                    ((skill.obj_type == 1 and 0 <= parm_list[1] < len(pm.all_enemies_list)) or
                     (skill.obj_type == 4 and 0 <= parm_list[1] < len(pm.ops_list))):

                # 获取目标
                obj1 = pm.all_enemies_list[parm_list[1]] if skill.obj_type == 1 else pm.all_ops_list[parm_list[1]]

                # 如果是对敌技能且干员被嘲讽则只能以被嘲讽者为目标
                if skill.obj_type == 1 and op.mocked and op.mocking_obj != obj1:
                    await operate_atk.finish(
                        f"你被{pm.all_enemies_list.index(op.mocking_obj) + 1}.{op.mocking_obj.name}嘲讽了！\n只能以ta为攻击目标！")

                # 不能以隐匿状态下的敌人为目标
                elif obj1.hidden:
                    await operate_atk.finish(f"{obj1.name}处于隐匿状态，无法被选中！")

                # 干员释放技能
                message_skill = await pm.turn(op, skill_num + 1, obj1)
                await send_message_and_is_over(message_skill, operate_skill)

            # 参数错误则退出方法
            else:
                await operate_run.finish("参数不足或序号错误！\n/skill <技能序号> <目标序号>")

        # 双目标技能(对敌或对友)
        elif skill.obj_type in [2, 5]:
            # 如果参数大于3个 且 两个目标参数不相同 且 ((对敌技能 且 两个敌方目标参数正确) 或 (对友技能 且 两个友方目标参数正确))
            if len(parm_list) >= 3 and \
                    parm_list[1] != parm_list[2] and\
                    ((skill.obj_type == 2 and
                      0 <= parm_list[1] < len(pm.all_enemies_list) and
                      0 <= parm_list[2] < len(pm.all_enemies_list)) or
                     (skill.obj_type == 5 and
                      0 <= parm_list[1] < len(pm.all_ops_list) and
                      0 <= parm_list[2] < len(pm.all_ops_list))):

                # 获取两个目标
                obj1 = pm.all_enemies_list[parm_list[1]] if skill.obj_type == 2 else pm.all_ops_list[parm_list[1]]
                obj2 = pm.all_enemies_list[parm_list[2]] if skill.obj_type == 2 else pm.all_ops_list[parm_list[2]]

                # 如果为对敌技能则嘲讽对象必须为目标之一
                if skill.obj_type == 3 and op.mocked and op.mocking_obj != obj1 and op.mocking_obj != obj2:
                    await operate_atk.finish(f"你被{pm.all_enemies_list.index(op.mocking_obj) + 1}.{op.mocking_obj.name}嘲讽了！\nta必须为攻击目标之一！")

                # 不能以隐匿状态下的敌人为目标
                elif obj1.hidden:
                    await operate_atk.finish(f"{obj1.name}处于隐匿状态，无法被选中！")

                # 不能以隐匿状态下的敌人为目标
                elif obj2.hidden:
                    await operate_atk.finish(f"{obj2.name}处于隐匿状态，无法被选中！")

                # 干员释放技能
                message_skill = await pm.turn(op, skill_num + 1, obj1, obj2)
                await send_message_and_is_over(message_skill, operate_skill)

            # 参数错误则退出方法
            else:
                await operate_run.finish("参数不足或序号错误！\n/skill <技能序号> <目标序号1> <目标序号2>")

        # 双目标技能(对敌且对友)
        elif skill.obj_type == 7:
            # 如果参数大于3个 且 参数1(敌方单位)正确 且 参数2(友方单位)正确
            if len(parm_list) >= 3 and \
                    0 <= parm_list[1] < len(pm.all_enemies_list) and \
                    0 <= parm_list[2] < len(pm.all_ops_list):

                # 获取两个目标
                obj1 = pm.all_enemies_list[parm_list[1]]
                obj2 = pm.all_ops_list[parm_list[2]]

                # 如果干员被嘲讽则只能以被嘲讽者为目标
                if op.mocked and op.mocking_obj != obj1:
                    await operate_atk.finish(f"你被{pm.all_enemies_list.index(op.mocking_obj) + 1}.{op.mocking_obj.name}嘲讽了！\n只能以ta为攻击目标！")

                # 不能以隐匿状态下的敌人为目标
                elif obj1.hidden:
                    await operate_atk.finish(f"{obj1.name}处于隐匿状态，无法被选中！")

                # 干员释放技能
                message_skill = await pm.turn(op, skill_num + 1, obj1, obj2)
                await send_message_and_is_over(message_skill, operate_skill)

            # 参数错误则退出方法
            else:
                await operate_run.finish("参数不足或敌人序号错误！\n/skill <技能序号> <目标序号> <友方序号>")

        # 不需要指定目标的技能(全体类技能或目标是自己的技能)
        else:
            # 干员释放技能
            message_skill = await pm.turn(op, skill_num + 1)
            await send_message_and_is_over(message_skill, operate_skill)

        # 干员释放技能后判断是否是敌方干员回合，如果是则敌方行动
        message2 = await pm.is_enemy_turn()
        message_skill += message2
        await send_message_and_is_over(message2, operate_skill)

        # 绘制战斗数据
        await send_status_image(pm, message_skill)

        # 方法结束
        await operate_skill.finish()

    @operate_run.handle()
    async def _():
        """
        撤退命令/run，可直接退出作战
        """
        await operate_run.send(f"{event.sender.nickname}战略性撤退了！")
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


async def send_status_image(pm: PlayingManager, message_list=None):
    """
    发送所有参战人员状态图片的函数

    :param pm: PlayingManage对象，包含了这场战斗的所有数据
    :param message_list: 消息列表
    """
    await draw_player_fight_image(pm, message_list)  # 绘制战斗图片
    for op in pm.all_list:  # 清空伤害列表
        op.damage_list.clear()
