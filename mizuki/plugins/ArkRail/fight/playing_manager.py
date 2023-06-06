# -*- coding = utf-8 -*-
# @File:playing_manager.py
# @Author:Silence
# @Time:2023/5/11 11:32
# @Software:PyCharm
import random

from ..operator import Operator, get_operator_list, get_enemies_list
from ..skill import Skill


class PlayingManager:

    def __init__(self, player_ops_list: list[Operator], map_enemies_list: list[Operator]):
        self.all_ops_list: list[Operator] = player_ops_list  # 玩家干员列表
        self.all_enemies_list: list[Operator] = map_enemies_list  # 敌方干员列表
        # 所有干员列表，用于计算干员出手顺序，初始化时顺便做一下冒泡排序
        self.all_list: list[Operator] = bubble_sort(player_ops_list + map_enemies_list)
        self.player_skill_count = 20  # 我方初始技力点
        self.enemy_skill_count = 10  # 敌方初始技力点

        for i in range(len(self.all_ops_list)):
            self.all_ops_list[i].next_operators.clear()
            if i - 1 >= 0:  # 左边的干员
                self.all_ops_list[i].next_operators.append(self.all_ops_list[i - 1])
            else:
                self.all_ops_list[i].next_operators.append(0)
            self.all_ops_list[i].next_operators.append(self.all_ops_list[i])  # 自身
            if i + 1 < len(self.all_ops_list):  # 右边的干员
                self.all_ops_list[i].next_operators.append(self.all_ops_list[i + 1])
            else:
                self.all_ops_list[i].next_operators.append(0)

        for i in range(len(self.all_enemies_list)):
            self.all_enemies_list[i].next_operators.clear()
            if i - 1 >= 0:  # 左边的干员
                self.all_enemies_list[i].next_operators.append(self.all_enemies_list[i - 1])
            else:
                self.all_enemies_list[i].next_operators.append(0)
            self.all_enemies_list[i].next_operators.append(self.all_enemies_list[i])  # 自身
            if i + 1 < len(self.all_enemies_list):  # 右边的干员
                self.all_enemies_list[i].next_operators.append(self.all_enemies_list[i + 1])
            else:
                self.all_enemies_list[i].next_operators.append(0)

    async def is_enemy_turn(self) -> list[str]:
        """
        判断是否为敌人回合，如果是则敌人行动，直到玩家回合为止
        :return 返回战斗消息
        """
        move_op = self.all_list[0]  # 当前行动者
        messages: list[str] = []  # 返回的战斗信息
        result_message: list[str] = []  # 结果信息，用于判断战斗是否结束
        while move_op in self.all_enemies_list and not await self.is_round_over():
            while True:  # 如果未被嘲讽则随机选一个目标
                random_num: int = random.randint(0, len(self.all_ops_list) - 1)
                obj: Operator = self.all_ops_list[random_num] if not move_op.mocked else move_op.mocking_obj
                if not obj.hidden:  # 如果所有干员都处于隐匿状态就糟咯awa
                    break

            if len(move_op.skills_list) and random.randint(1, 100) <= 25 + (5 * move_op.stars) and \
                    self.enemy_skill_count >= move_op.skills_list[0].consume and not move_op.silent:  # 条件达成则使用技能

                for i in range(len(move_op.skills_list) - 1, -1, -1):
                    if self.enemy_skill_count >= move_op.skills_list[i].consume:
                        result_message = await self.turn(move_op, i + 1, obj)
                        messages.append(result_message[0])
                        break

            else:  # 否则进行普攻
                result_message = await self.turn(move_op, 0, obj)
                messages.append(result_message[0])
            if result_message[len(result_message) - 1] in ["作战失败", "作战成功"]:
                messages.append(result_message[len(result_message) - 1])
                return messages
            move_op = self.all_list[0]
        while move_op.immobile:
            messages += await self.turn(move_op, -1)
            move_op = self.all_list[0]
        if await self.is_round_over():
            messages.append("当前轮已结束，进入下一轮！")
            for op in self.all_list:
                op.speed_p = op.speed
            self.all_list = bubble_sort(self.all_list)  # 根据速度做冒泡排序
            messages += (await self.is_enemy_turn())
            messages.pop()  # 去掉一个"玩家的回合！"

        messages.append("玩家的回合！")
        return messages

    async def is_round_over(self):
        """
        判断当前轮是否结束

        :return: 当前轮是否结束
        """
        is_round_over: bool = True
        for op in self.all_list:
            if op.speed_p != 0:
                is_round_over = False
                break
        return is_round_over

    async def turn(self, sub: Operator, operate: int, obj1: Operator = None, obj2: Operator = None) -> list[str]:
        """
        干员的一个回合

        :param sub: 行动者
        :param operate: 操作序号 0普攻 1-3技能
        :param obj1: 目标对象1
        :param obj2: 目标对象2(可选)
        """
        messages = []  # 返回的消息
        if not sub.immobile:
            if sub in self.all_ops_list:  # 我方干员回合
                if operate == 0:
                    messages.append(await self.attack(sub, obj1))
                    self.player_skill_count += 5  # 普攻回复5技力点
                elif operate in [1, 2, 3]:
                    messages.append(await self.use_skill(sub, operate - 1, obj1, obj2))
                    self.player_skill_count -= sub.skills_list[operate - 1].consume  # 使用技能消耗技力点
            else:  # 敌方干员回合
                if operate == 0:
                    messages.append(await self.attack(sub, obj1))
                    self.enemy_skill_count += 5  # 普攻回复5技力点
                elif operate in [1, 2, 3]:
                    messages.append(await self.use_skill(sub, operate - 1, obj1, obj2))
                    self.enemy_skill_count -= sub.skills_list[operate - 1].consume  # 使用技能消耗技力点
        else:
            messages.append(f"{sub.name}无法行动...")
        messages[0] += await self.finish_turn(sub)
        if not len(self.all_enemies_list):
            messages.append("作战成功")  # messages[1]装战斗结果信息
        elif not len(self.all_ops_list):
            messages.append("作战失败")
        self.all_list = bubble_sort(self.all_list)
        return messages

    async def attack(self, sub: Operator, obj: Operator) -> str:
        """
        干员进行普攻的函数，会根据atk_type来进行不同的操作

        :param sub: 对象
        :param obj: 目标
        :return: 信息字符串
        """
        message: str = ""
        is_crit: bool = random.randint(1, 10000) <= sub.crit_r_p * 10000  # 是否暴击
        is_crit_str: str = "暴击并" if is_crit else ""
        damage = int(sub.atk_p + (sub.atk_p * is_crit * sub.crit_d_p))  # 初始伤害

        if sub.atk_type_p in [0, 1, 6, 8]:  # 单体物理(嘲讽)
            atk_type = sub.atk_type_p
            atk_type_str = ""
            if atk_type in [0, 8]:
                atk_type_str = "物理"
            elif atk_type == 1:
                atk_type_str = "法术"
            elif atk_type == 6:
                atk_type_str = "真实"
            damage = await obj.hurt(atk_type, damage)
            message = f"{sub.name}对{obj.name}发动了普通攻击，{is_crit_str}对其造成了{damage}点{atk_type_str}伤害！"  # 返回的字符串
            if sub.atk_type_p == 8 and random.randint(1, 100) < 50:  # 重装普攻有概率嘲讽敌方单位
                message += f"\n{sub.name}嘲讽了{obj.name}！\n持续1回合！"
                obj.mocked = 1
                obj.mocking_obj = sub
            if await obj.is_die():
                message += f"\n{obj.name}被{sub.name}击倒了！"
                await self.op_die(obj)

        elif sub.atk_type_p in [2, 3, 7]:  # 群体真实
            atk_type = sub.atk_type_p  # 攻击类型
            atk_type_str = ""
            if atk_type == 2:
                atk_type_str = "物理"
            elif atk_type == 3:
                atk_type_str = "法术"
            elif atk_type == 7:
                atk_type_str = "真实"
            message = f"{sub.name}对"  # 返回的字符串
            objs_name: str = ""  # 所有目标名字
            objs_damage: str = ""  # 各个目标受到的伤害
            die_objs: str = ""  # 被击倒的目标名字
            for op in obj.next_operators:
                if not isinstance(op, Operator):
                    continue
                objs_name += f" {op.name}"
                damage = await op.hurt(atk_type, damage)
                objs_damage += f" {damage}"
                if await op.is_die():
                    die_objs += f" {op.name}"
                    await self.op_die(op)
            message += f"{objs_name} 发动了普通攻击，{is_crit_str}分别对他们造成了{objs_damage} 点{atk_type_str}伤害！"
            if die_objs != "":
                message += f"\n{die_objs} 被击倒了！"

        elif sub.atk_type_p == 4:  # 单体治疗
            health_amount = await obj.hurt(4, sub.atk_p)
            message = f"{sub.name}治疗了{obj.name}，恢复其{health_amount}生命值！"  # 返回的字符串

        elif sub.atk_type_p == 5:  # 群体治疗
            message = f"{sub.name}治疗了"  # 返回的字符串
            objs_name: str = ""  # 所有目标名字
            objs_health: str = ""  # 各个目标恢复的生命值
            for op in obj.next_operators:
                if not isinstance(op, Operator):
                    continue
                objs_name += f" {op.name}"
                health_amount = await op.hurt(4, sub.atk_p)
                objs_health += f"{health_amount} "
            message += f"{objs_name}，分别恢复他们{objs_health} 的生命值！"

        elif sub.atk_type_p == 9:  # 不攻击
            message = f"{sub.name}无动于衷..."
            pass
        return message

    async def use_skill(self, sub: Operator, skill_num: int, obj1: Operator, obj2: Operator = None) -> str:
        """
        使用技能

        :param sub: 使用者
        :param skill_num: 使用的技能序号
        :param obj1: 目标对象1
        :param obj2: 目标对象2(可选)
        """
        skill: Skill = sub.skills_list[skill_num]  # 使用的技能
        objs_list: list[Operator] = []  # 受影响的敌人
        objs_name: str = ""
        objs_damage: str = ""
        message: str = f"{sub.name}使用了{skill.name}！"  # 返回的信息
        sid = skill.sid  # 技能id
        persistence: int = 0  # 是否为持续性技能
        if sid < 0:  # 小于0的为敌人技能
            if sid == -1:
                for op in obj1.next_operators:
                    if not isinstance(op, Operator):
                        continue
                    damage = await op.hurt(3, int(sub.atk_p * skill.rate1))

                    objs_list.append(op)
                    objs_name += f" {op.name}"
                    objs_damage += f" {damage}"
                message += f"\n对{objs_name}\n分别造成了{objs_damage} 点法术伤害！"
            elif sid == -2:
                for op in obj1.next_operators:
                    if not isinstance(op, Operator):
                        continue
                    damage = await op.hurt(2, int(sub.atk_p * skill.rate1))

                    objs_list.append(op)
                    objs_name += f" {op.name}"
                    objs_damage += f" {damage}"
                message += f"\n对{objs_name}\n分别造成了{objs_damage} 点物理伤害！"
            elif sid == -3:
                for op in obj1.next_operators:
                    if not isinstance(op, Operator):
                        continue
                    damage = await op.hurt(2, int(sub.atk_p * skill.rate1), skill.rate2)

                    objs_list.append(op)
                    objs_name += f" {op.name}"
                    objs_damage += f" {damage}"
                message += f"\n对{objs_name}\n分别造成了{objs_damage} 点物理伤害！"
        else:
            if sid == 1:
                self.player_skill_count += int(skill.rate1)
                message += f"\n回复{int(skill.rate1)}技力点！"
            elif sid == 2:
                persistence = 1
                sub.atk_type_p = skill.rate1
                sub.atk_add_f += skill.rate2
                message += f"\n攻击力提高{round(skill.rate2 * 100, 1)}%并变为法术伤害！"
            elif sid == 3:
                health_amount = await sub.hurt(4, int(skill.rate1 * sub.max_health_p))
                message += f"\n恢复{health_amount}%最大生命值！"
            elif sid in [4, 13, 16]:
                rate = random.uniform(skill.rate1, skill.rate2)
                is_crit: bool = random.randint(1, 10000) <= sub.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(sub.atk_p * rate + (sub.atk_p * is_crit * sub.crit_d_p))
                total_damage = 0
                atk_type = sub.atk_type_p
                atk_type_str = ""
                if atk_type in [0, 2, 8]:
                    atk_type_str = "物理"
                elif atk_type in [1, 3]:
                    atk_type_str = "法术"
                elif atk_type in [6, 7]:
                    atk_type_str = "真实"
                if atk_type in [0, 1, 6, 8]:
                    objs_list.append(obj1)
                    damage = total_damage = await obj1.hurt(atk_type, damage)
                    message += f"\n{is_crit_str}对{obj1.name}造成了{damage}点{atk_type_str}伤害！"
                elif atk_type in [2, 3, 7]:
                    for op in obj1.next_operators:
                        if not isinstance(op, Operator):
                            continue
                        damage = await op.hurt(atk_type, damage)
                        total_damage += damage
                        objs_list.append(op)
                        objs_name += f" {op.name}"
                        objs_damage += f" {damage}"
                    message += f"\n{is_crit_str}对{objs_name}\n分别造成了{objs_damage} 点{atk_type_str}伤害！"
                if sid == 13:
                    health_amount = await sub.hurt(4, int(total_damage * skill.rate3))
                    message += f"\n并恢复了{health_amount}点生命值！"
                elif sid == 16:
                    obj1.speed_p -= skill.rate3
                    message += f"\n并使其速度减少{skill.rate3}！"
            elif sid == 5:
                persistence = 1
                sub.atk_add_f += skill.rate1
                message += f"\n攻击力提高{round(skill.rate1 * 100, 1)}%！"
            elif sid == 6:
                persistence = 1
                sub.def_add_f += skill.rate1
                message += f"\n防御力提高{round(skill.rate1 * 100, 1)}%！"
            elif sid in [7, 14, 28]:
                atk_type = sub.atk_type_p
                atk_type_str = ""
                damage_str: str = ""
                if atk_type in [0, 2, 8]:
                    atk_type_str = "物理"
                elif atk_type in [1, 3]:
                    atk_type_str = "法术"
                elif atk_type in [6, 7]:
                    atk_type_str = "真实"
                if atk_type in [0, 1, 6, 8]:
                    for i in range(int(skill.rate1)):
                        is_crit: bool = random.randint(1, 10000) <= sub.crit_r_p * 10000  # 是否暴击
                        is_crit_sym: str = "★" if is_crit else ""
                        rate = random.uniform(skill.rate2, skill.rate3)
                        damage = int(sub.atk_p * rate + (sub.atk_p * is_crit * sub.crit_d_p))
                        damage = await obj1.hurt(atk_type, damage)
                        damage_str += f"{damage}{is_crit_sym}+"
                    damage_str = damage_str.rstrip("+")  # 去掉末尾的+号
                    objs_list.append(obj1)
                    message += f"\n对{obj1.name}造成了{damage_str}点物理伤害！"
                elif atk_type in [2, 3, 7]:
                    for op in obj1.next_operators:
                        if not isinstance(op, Operator):
                            continue
                        for i in range(int(skill.rate1)):
                            is_crit: bool = random.randint(1, 10000) <= sub.crit_r_p * 10000  # 是否暴击
                            is_crit_sym: str = "★" if is_crit else ""
                            rate = random.uniform(skill.rate2, skill.rate3)
                            damage = int(sub.atk_p * rate + (sub.atk_p * is_crit * sub.crit_d_p))
                            damage = await op.hurt(atk_type, damage)
                            damage_str += f"{damage}{is_crit_sym}+"
                        damage_str = damage_str.rstrip("+")  # 去掉末尾的+号
                        objs_list.append(op)
                        objs_name += f" {op.name}"
                        objs_damage += f" \n{damage_str}"
                    message += f"\n对{objs_name}\n分别造成了{objs_damage} 点{atk_type_str}伤害！"
            elif sid == 8:
                treat1 = treat2 = int(sub.atk_p * skill.rate1)
                treat1 = await obj1.hurt(4, treat1)
                treat2 = await obj2.hurt(4, treat2)
                message += f"\n为{obj1.name}和{obj2.name}分别恢复了 {treat1} {treat2} 点生命值！"
            elif sid == 9:
                persistence = 1
                sub.atk_add_f += skill.rate1
                message += f"\n每回合回复{int(skill.rate2)}技力点，攻击力提高{round(skill.rate1 * 100, 1)}%！"
            elif sid == 10:
                sub.crit_d_add_d += skill.rate1
                message += f"\n下次普攻必定暴击且暴击伤害增加{round(skill.rate1 * 100, 1)}%！\n"
                await sub.upgrade_effect()
                damage = int(sub.atk_p + (sub.atk_p * sub.crit_d_p))
                damage = await obj1.hurt(0, damage)
                message = f"\n{sub.name}对{obj1.name}发动了普通攻击，暴击并对其造成了{damage}点物理伤害！"  # 返回的字符串
                sub.crit_d_add_d -= skill.rate1
                objs_list.append(obj1)
            elif sid == 11:
                persistence = 1
                sub.immobile = skill.persistence + 1
                message += f"\n进入无法行动状态，每回合回复{int(skill.rate1)}技力点！"
            elif sid == 12:
                persistence = 1
                sub.immobile = skill.persistence + 1
                message += f"\n进入无法行动状态，每回合回复{int(skill.rate1)}技力点并为所有干员恢复生命值！"
            elif sid in [15, 20, 22, 30, 39, 45, 49]:
                rate = random.uniform(skill.rate1, skill.rate2)
                is_crit: bool = random.randint(1, 10000) <= sub.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(sub.atk_p * rate + (sub.atk_p * is_crit * sub.crit_d_p))
                atk_type = 0
                atk_type_str = ""
                if sid in [15, 30, 45]:
                    atk_type_str = "物理"
                    atk_type = 0
                elif sid in [22, 39]:
                    atk_type_str = "法术"
                    atk_type = 1
                elif sid in [49]:
                    atk_type_str = "真实"
                    atk_type = 6
                elif sid in [20]:
                    atk_type_str = "治疗"
                    atk_type = 4

                if sid == 22:
                    self.player_skill_count += int(skill.rate3)
                    message += f"\n回复{int(skill.rate3)}技力点！"
                elif sid == 45:
                    self.player_skill_count += int(skill.rate3) * len(self.all_enemies_list)
                    message += f"\n回复{int(skill.rate3)} * {len(self.all_enemies_list)}技力点！"

                for op in self.all_enemies_list:
                    damage_amount = await op.hurt(atk_type, damage)
                    objs_list.append(op)
                    objs_name += f" {op.name}"
                    objs_damage += f" {damage_amount}"
                if sid in [15, 22, 30, 39, 45, 49]:
                    message += f"\n{is_crit_str}对{objs_name}\n分别造成了{objs_damage} 点{atk_type_str}伤害！"
                else:
                    message += f"\n分别为{objs_name}\n恢复了{objs_damage} 点生命值！"
            elif sid == 17:
                health_amount = await obj1.hurt(4, int(sub.atk_p * skill.rate1))
                message += f"恢复{obj1.name}{health_amount}点生命值！"
            elif sid == 18:
                sub.atk_type_p = skill.rate1
                sub.atk_add_f += skill.rate2
                message += f"\n攻击方式变为单体治疗，攻击力提高{round(skill.rate2 * 100, 1)}%！"
            elif sid == 19:
                persistence = 1
                sub.immobile = skill.persistence + 1
                mock_ops = ""
                for op in self.all_enemies_list:
                    if random.randint(1, 10000) < skill.rate1 * 10000:
                        op.mocked = skill.persistence
                        op.mocking_obj = sub
                        mock_ops += f"{op.name} "

                sub.def_add_f += skill.rate2
                message += f"\n防御力提高{round(skill.rate2 * 100, 1)}%并尝试嘲讽所有敌人！"
                message += f"\n{mock_ops} 被嘲讽了！"
            elif sid == 21:
                persistence = 1
                damage = await sub.hurt(6, int(sub.health * skill.rate1))
                sub.atk_add_f += skill.rate2
                sub.speed_add_d += skill.rate3
                message += f"\n流失{damage}点生命值，攻击力提高{round(skill.rate2 * 100, 1)}%，速度提升{skill.rate3}点！"
            elif sid == 23:
                is_crit: bool = random.randint(1, 10000) <= sub.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(sub.atk_p * skill.rate1 + (sub.atk_p * is_crit * sub.crit_d_p))
                atk_type = sub.atk_type_p
                atk_type_str = ""
                if atk_type == 0:
                    atk_type_str = "物理"
                elif atk_type == 3:
                    atk_type_str = "法术"
                if atk_type == 0:
                    damage = await obj1.hurt(atk_type, damage)
                    objs_list.append(obj1)
                    obj1.silent = skill.rate2
                    message += f"\n{is_crit_str}对{obj1.name}造成了{damage}点{atk_type_str}伤害！\n{obj1.name}被沉默了！"
                else:
                    for op in obj1.next_operators:
                        if not isinstance(op, Operator):
                            continue
                        damage = await op.hurt(atk_type, damage)
                        objs_list.append(op)
                        op.silent = skill.rate2
                        objs_name += f" {op.name}"
                        objs_damage += f" {damage}"
                    message += f"\n{is_crit_str}对{objs_name}\n分别造成了{objs_damage} 点{atk_type_str}伤害！\n{objs_name} 被沉默了！"
                    pass
            elif sid == 24:
                persistence = 1
                sub.atk_type_p = skill.rate1
                sub.atk_add_f += skill.rate2
                message += f"\n攻击类型变为群体法术，攻击力提高{round(skill.rate2 * 100, 1)}%！"
            elif sid == 25:
                persistence = 1
                sub.atk_add_f += skill.rate1
                sub.def_add_f += skill.rate2
                message += f"\n攻击力提高{round(skill.rate1 * 100, 1)}%，防御力提高{round(skill.rate2 * 100, 1)}%！"
            elif sid == 26:
                persistence = 1
                sub.atk_add_f += skill.rate1
                sub.deathless = skill.persistence + 1
                message += f"\n攻击力提高{round(skill.rate1 * 100, 1)}%，进入不死状态！"
            elif sid == 27:
                persistence = 1
                sub.def_add_f -= skill.rate1
                sub.atk_add_f += skill.rate2
                message += f"\n防御力降低{round(skill.rate1 * 100, 1)}%，攻击力提高{round(skill.rate2 * 100, 1)}%！"
            elif sid == 29:
                is_crit: bool = random.randint(1, 10000) <= sub.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(sub.atk_p * skill.rate1 + (sub.atk_p * is_crit * sub.crit_d_p))
                obj_health = obj1.health
                await obj1.hurt(0, damage)
                objs_list.append(obj1)
                obj1.speed_p -= skill.rate3
                if obj1.health < obj1.max_health_p * skill.rate2:
                    obj1.health = int(obj1.max_health_p * skill.rate2)
                message += f"\n{is_crit_str}对{obj1.name}造成了{obj_health - obj1.health}点物理伤害并使其速度减少{skill.rate3}！"
            elif sid == 31:
                rate = random.uniform(skill.rate1, skill.rate2)
                is_crit: bool = random.randint(1, 10000) <= sub.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(sub.atk_p * rate + (sub.atk_p * is_crit * sub.crit_d_p))
                for op in obj1.next_operators:
                    if not isinstance(op, Operator):
                        continue
                    damage = await op.hurt(2, damage, skill.rate3)

                    objs_list.append(op)
                    objs_name += f" {op.name}"
                    objs_damage += f" {damage}"
                message += f"\n{is_crit_str}对{objs_name}\n分别造成了{objs_damage} 点物理伤害！"

        skill.count = skill.persistence + persistence

        for op in objs_list:
            if await op.is_die():
                message += f"\n{op.name}被击倒了！"
                await self.op_die(op)
        return message

    async def op_die(self, op: Operator):
        """
        干员被击倒时调用的方法

        :param op: 被击倒的干员
        """
        if op in self.all_enemies_list:
            self.all_enemies_list.remove(op)
            await refresh_op_next_list(self.all_enemies_list)
            for o in self.all_ops_list:  # 解除嘲讽效果
                if o.mocking_obj == op:
                    o.mocked = 0
                    o.mocking_obj = None
        else:
            self.all_ops_list.remove(op)
            await refresh_op_next_list(self.all_ops_list)
            for o in self.all_enemies_list:  # 解除嘲讽效果
                if o.mocking_obj == op:
                    o.mocked = 0
                    o.mocking_obj = None
        self.all_list.remove(op)

    async def finish_turn(self, sub: Operator) -> str:
        """
        干员回合结束时调用的函数

        :param sub: 结束回合的对象
        :return: 回合结束信息
        """
        message: str = ""  # 返回的信息
        finish_skill: list[Skill] = []
        for skill in sub.skills_list:
            if skill.count > 1:
                skill.count -= 1
                sid = skill.sid
                if sid == 9:  # 冲锋号令_进攻
                    self.player_skill_count += int(skill.rate2)
                    message += f"\n{skill.name}生效！回复{int(skill.rate2)}点技力点"
                elif sid == 11:  # 支援号令
                    self.player_skill_count += int(skill.rate1)
                    message += f"\n{skill.name}生效！回复{int(skill.rate1)}点技力点"
                elif sid == 12:  # 支援号令_治疗
                    self.player_skill_count += int(skill.rate1)
                    message += f"\n{skill.name}生效！回复{int(skill.rate1)}点技力点"
                    ops_name = ""
                    health_amount_str = ""
                    for op in self.all_ops_list:
                        health_amount = await op.hurt(4, int(sub.atk_p * skill.rate2))
                        ops_name += f"{op.name} "
                        health_amount_str += f"{health_amount} "
                    message += f"\n同时为{ops_name} 分别恢复了\n{health_amount_str} 生命值！"

                if skill.count == 0:  # 如果技能结束则将其添加进结束技能列表
                    finish_skill.append(skill)

        for f_s in finish_skill:  # 遍历结束技能列表内的技能
            message += f"\n{sub.name}的技能{f_s.name}结束了！"
            sid = f_s.sid
            if sid == 2:  # 法术附魔
                sub.atk_type_p = sub.atk_type
                sub.atk_add_f -= f_s.rate2
            elif sid == 5:  # 攻击力增强
                sub.atk_add_f -= f_s.rate1
            elif sid == 6:  # 防御力增强
                sub.def_add_f -= f_s.rate1
            elif sid == 9:  # 冲锋号令_进攻
                sub.atk_add_f -= f_s.rate2
            elif sid == 18:  # 急救模式
                sub.atk_add_f -= f_s.rate2
            elif sid == 19:  # 壳状防御
                sub.def_add_f -= f_s.rate2
            elif sid == 21:  # 赤色之瞳
                sub.atk_add_f -= f_s.rate2
                sub.speed_add_d -= f_s.rate3
            elif sid == 24:  # 狼魂
                sub.atk_type_p = sub.atk_type
                sub.atk_add_f -= f_s.rate2
            elif sid == 25:  # 星座守护
                sub.atk_add_f -= f_s.rate1
                sub.def_add_f -= f_s.rate2
            elif sid == 26:  # 肉斩骨断
                sub.atk_add_f -= f_s.rate1
                sub.immobile = 2
                message += f"\n{sub.name}眩晕了！"
            elif sid == 27:  # 亮剑
                sub.def_add_f += f_s.rate1
                sub.atk_add_f -= f_s.rate2

        await sub.finish_turn()
        sub.speed_p = 0  # 速度设为0
        return message


async def new_instance(uid: str or int, mid: str) -> PlayingManager:
    player_ops_list: list[Operator] = await get_operator_list(uid)
    map_enemies_list: list[Operator] = await get_enemies_list(mid)
    return PlayingManager(player_ops_list, map_enemies_list)


async def refresh_op_next_list(op_list: list[Operator]):
    """
    刷新干员身边的干员列表

    :param op_list:
    """
    for i in range(len(op_list)):
        op_list[i].next_operators.clear()
        if i - 1 >= 0:  # 左边的干员
            op_list[i].next_operators.append(op_list[i - 1])
        else:
            op_list[i].next_operators.append(0)
        op_list[i].next_operators.append(op_list[i])  # 自身
        if i + 1 < len(op_list):  # 右边的干员
            op_list[i].next_operators.append(op_list[i + 1])
        else:
            op_list[i].next_operators.append(0)


# 冒泡排序函数
def bubble_sort(arr: list[Operator]):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j].speed_p < arr[j + 1].speed_p:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
