# -*- coding = utf-8 -*-
# @File:playing_manager.py
# @Author:Silence
# @Time:2023/5/11 11:32
# @Software:PyCharm
import copy
import random

from ..effect import Effect
from ..operator import Operator, get_operator_list, get_enemies_list
from ..skill import Skill, new_skill_instance


class PlayingManager:

    def __init__(self):
        self.all_ops_list: list[Operator] = []  # 玩家干员列表
        self.all_enemies_list: list[Operator] = []  # 敌方干员列表
        # 所有干员列表，用于计算干员出手顺序
        self.all_list: list[Operator] = []
        self.player_skill_count = 20  # 我方初始技力点
        self.enemy_skill_count = 10  # 敌方初始技力点

    async def is_enemy_turn(self) -> list[str]:
        """
        判断是否为敌人回合，如果是则敌人行动，直到玩家回合为止

        :return 返回战斗消息
        """
        move_op = self.all_list[0]  # 当前行动者
        messages: list[str] = []  # 返回的战斗信息
        result_message: list[str] = []  # 结果信息，用于判断战斗是否结束

        # 如果干员无法行动
        while move_op.immobile:
            messages += await self.turn(move_op, -1)  # 结束干员回合
            move_op = self.all_list[0]  # 刷新行动者

        # 敌方持续行动，直到行动者为我方干员为止
        while ((move_op in self.all_enemies_list) or move_op.immobile) and (not await self.is_round_over()):
            print(f"move_op:{move_op.name} speed:{move_op.speed}")
            # 如果干员无法行动
            if move_op.immobile:
                messages += await self.turn(move_op, -1)  # 结束干员回合
                move_op = self.all_list[0]  # 刷新行动者
                continue

            # 如果未被嘲讽则随机选一个目标
            while True:
                if move_op.atk_type_p in [0, 1, 2, 3, 6, 7, 8]:
                    # 随机选一个序号
                    random_num: int = random.randint(0, len(self.all_ops_list) - 1)

                    # 如果自身被嘲讽
                    if move_op.mocked:

                        # 如果嘲讽对象隐匿则嘲讽失效
                        if not move_op.mocking_obj.hidden:
                            obj = move_op.mocking_obj
                        else:
                            obj = self.all_ops_list[random_num]

                    # 如果没被嘲讽的话则随便选一个干员
                    else:
                        obj = self.all_ops_list[random_num] if not move_op.mocked else move_op.mocking_obj

                    if not obj.hidden or await is_all_hidden(self.all_ops_list):  # 如果所有干员都处于隐匿状态则隐匿失效
                        break

                elif move_op.atk_type_p in [4, 5]:
                    random_num: int = random.randint(0, len(self.all_enemies_list) - 1)
                    obj = self.all_enemies_list[random_num]
                    break

                else:
                    obj = None
                    break

            # 条件达成则使用技能
            if len(move_op.skills_list) and random.randint(1, 100) <= 15 + (12 * move_op.stars) and \
                    self.enemy_skill_count >= move_op.skills_list[0].consume and not move_op.silent:

                # 倒序遍历技能列表(一般后面的技能更厉害)
                for i in range(len(move_op.skills_list) - 1, -1, -1):
                    skill = move_op.skills_list[i]  # 获取技能对象

                    #  如果技能点足够且技能不在持续时间内
                    if self.enemy_skill_count >= int(skill.consume) and skill.count == 0:
                        result_message = await self.turn(move_op, i + 1, obj)
                        print(f"skill:{result_message}")
                        messages.append(result_message[0])
                        break
            # 否则进行普攻
            else:
                result_message = await self.turn(move_op, 0, obj)
                print(f"atk:{result_message}")
                messages.append(result_message[0])

            # 判断作战是否结束
            if ("作战失败" in result_message) or ("作战成功" in result_message):
                messages.append(result_message[len(result_message) - 1])
                return messages

            # 刷新行动干员
            move_op = self.all_list[0]

        if await self.is_round_over():
            messages.append("当前轮已结束，进入下一轮！")
            for op in self.all_list:
                op.speed = op.max_speed_p
            self.all_list = await bubble_sort(self.all_list)  # 根据速度做冒泡排序
            messages += (await self.is_enemy_turn())

        return messages

    async def is_round_over(self):
        """
        判断当前轮是否结束

        :return: 当前轮是否结束
        """
        is_round_over: bool = True
        for op in self.all_list:
            if op.speed > 0:
                is_round_over = False
                break
        return is_round_over

    async def turn(self, sub: Operator, operate: int, obj1: Operator = None, obj2: Operator = None) -> list[str]:
        """
        干员的一个回合

        :param sub: 行动者
        :param operate: 操作序号 0普攻 1-3技能 -1不行动
        :param obj1: 目标对象1(可选)
        :param obj2: 目标对象2(可选)
        :return : messages[0]为返回信息，如果战斗结束的话，messages[1]只会为“作战成功”或“作战失败”，否则没有message[1]
        """
        messages = []  # 返回的消息
        if not sub.immobile:
            if sub in self.all_ops_list:  # 我方干员回合
                if operate == 0:
                    messages.append(await sub.attack(obj1))
                    if sub.profession != "先锋-冲锋":
                        self.player_skill_count += int(5)  # 普攻回复5技力点
                    else:
                        self.player_skill_count += int(10)  # 冲锋手普攻回复10技力点
                elif operate in [1, 2, 3]:
                    self.player_skill_count -= int(sub.skills_list[operate - 1].consume)  # 使用技能消耗技力点
                    messages.append(await sub.use_skill(operate - 1, obj1, obj2))
            else:  # 敌方干员回合
                if operate == 0:
                    messages.append(await sub.attack(obj1))
                    self.enemy_skill_count += int(
                        5 * (1 + (0.125 * (4 - len(self.all_enemies_list))) + ((sub.stars - 1) * 0.1)))  # 普攻回复技力点
                elif operate in [1, 2, 3]:
                    self.enemy_skill_count -= int(sub.skills_list[operate - 1].consume)  # 使用技能消耗技力点
                    messages.append(await sub.use_skill(operate - 1, obj1, obj2))
        else:
            messages.append(f"{sub.name}无法行动...")

        # 结束干员回合
        messages[0] += await sub.finish_turn()

        # 如果我方干员列表或敌方干员列表长度为0则结束战斗
        if not len(self.all_enemies_list):
            messages.append("作战成功")  # messages[1]装战斗结果信息
        elif not len(self.all_ops_list):
            messages.append("作战失败")  # messages[1]装战斗结果信息

        # 对所有干员列表按照速度从大到小进行冒泡排序
        self.all_list = await bubble_sort(self.all_list)
        return messages


async def is_all_hidden(op_list: list[Operator]):
    """
    检测列表中的干员是否都处于隐匿状态

    :param op_list: 干员列表
    :return: 列表中的干员是否都处于隐匿状态
    """
    is_all_op_hidden: bool = True
    for op in op_list:
        if not op.hidden:
            is_all_op_hidden = False
            break
    return is_all_op_hidden


async def new_instance(uid: str or int, mid: str) -> PlayingManager:
    pm: PlayingManager = PlayingManager()
    player_ops_list: list[Operator] = await get_operator_list(uid, pm)
    map_enemies_list: list[Operator] = await get_enemies_list(mid, pm)

    pm.all_ops_list = player_ops_list
    pm.all_enemies_list = map_enemies_list

    # 刷新周围干员
    await player_ops_list[0].refresh_op_next_list()
    await map_enemies_list[0].refresh_op_next_list()

    # 排序
    pm.all_list = await bubble_sort(player_ops_list + map_enemies_list)

    return pm


# 冒泡排序函数
async def bubble_sort(arr: list[Operator]):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j].speed < arr[j + 1].speed:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
