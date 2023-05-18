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
        self.player_ops_list: list[Operator] = player_ops_list  # 玩家干员列表
        self.map_enemies_list: list[Operator] = map_enemies_list  # 敌方干员列表
        # 所有干员列表，用于计算干员出手顺序，初始化时顺便做一下冒泡排序
        self.all_ops_list: list[Operator] = bubble_sort(player_ops_list + map_enemies_list)
        self.player_skill_count = 20  # 我方初始技力点
        self.enemy_skill_count = 10  # 敌方初始技力点

    async def is_enemy_turn(self) -> list[str]:
        """
        判断是否为敌人回合，如果是则敌人行动，直到玩家回合为止
        :return 返回战斗消息
        """
        move_op = self.all_ops_list[0]  # 当前行动者
        messages: list[str] = []
        while move_op in self.map_enemies_list and not await self.is_round_over():
            while True:  # 如果未被嘲讽则随机选一个目标
                random_num: int = random.randint(0, len(self.player_ops_list) - 1)
                obj: Operator = self.player_ops_list[random_num] if not move_op.mocked else move_op.mocking_obj
                if not obj.hidden:  # 如果所有干员都处于隐匿状态就糟咯awa
                    break

            if len(move_op.skills_list) and random.randint(1, 100) <= 20 + (5 * move_op.stars) and \
                    self.enemy_skill_count >= move_op.skills_list[0].consume:  # 条件达成则使用技能

                for i in range(len(move_op.skills_list) - 1, -1, -1):
                    if self.enemy_skill_count >= move_op.skills_list[i].consume:
                        messages.append(await self.turn(move_op, i + 1, obj))
                        break

            else:  # 否则进行普攻
                messages.append(await self.turn(move_op, 0, obj))
            move_op = self.all_ops_list[0]
        if await self.is_round_over():
            messages.append("当前轮已结束，进入下一轮！")
            for op in self.all_ops_list:
                op.speed_p = op.speed
            self.all_ops_list = bubble_sort(self.all_ops_list)  # 根据速度做冒泡排序
        messages.append("玩家的回合！")
        return messages

    async def is_round_over(self):
        """
        判断当前轮是否结束

        :return: 当前轮是否结束
        """
        is_round_over: bool = True
        for op in self.all_ops_list:
            if op.speed_p != 0:
                is_round_over = False
                break
        return is_round_over

    async def turn(self, sub: Operator, operate: int, obj1: Operator, obj2: Operator = None) -> str:
        """
        干员的一个回合

        :param sub: 行动者
        :param operate: 操作序号 0普攻 1-3技能
        :param obj1: 目标对象1
        :param obj2: 目标对象2(可选)
        """
        message = ""  # 返回的消息
        if sub in self.player_ops_list:  # 我方干员回合
            if operate == 0:
                message = await self.attack(sub, obj1)
                self.player_skill_count += 5  # 普攻回复5技力点
            elif operate in [1, 2, 3]:
                message = await self.use_skill(sub, operate - 1, obj1, obj2)
                self.player_skill_count -= sub.skills_list[operate - 1].consume  # 使用技能消耗技力点
        else:  # 敌方干员回合
            if operate == 0:
                message = await self.attack(sub, obj1)
                self.enemy_skill_count += 10  # 普攻回复10技力点
            elif operate in [1, 2, 3]:
                message = await self.use_skill(sub, operate - 1, obj1, obj2)
                self.enemy_skill_count -= sub.skills_list[operate - 1].consume  # 使用技能消耗技力点
        await self.finish_turn(sub)
        self.all_ops_list = bubble_sort(self.all_ops_list)
        return message

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
        if sub.atk_type_p == 0:  # 单体物理
            damage: int = (sub.atk_p - obj.defence_p) \
                if (sub.atk_p - obj.defence_p > sub.atk_p * 0.05) \
                else (sub.atk_p * 0.05)  # 5%攻击力的保底伤害
            damage += damage * is_crit * sub.crit_d_p
            message = f"{sub.name}对{obj.name}发动了普通攻击，{is_crit_str}对其造成了{damage}点物理伤害！"  # 返回的字符串
            if sub.profession == "重装-中坚" and random.randint(1, 100) < 50:  # 中坚重装普攻有概率嘲讽敌方单位
                message += f"\n{sub.name}嘲讽了{obj.name}！"
                obj.mocked = 1
                obj.mocking_obj = sub
            if not obj.invincible:
                obj.health -= damage
                if await obj.is_die():
                    message += f"\n{obj.name}被{sub.name}击倒了！"
                    if obj in self.map_enemies_list:
                        self.map_enemies_list.remove(obj)
                    else:
                        self.player_ops_list.remove(obj)
                    self.all_ops_list.remove(obj)
        elif sub.atk_type_p == 1:  # 单体法术
            damage: int = int(sub.atk_p * ((100 - obj.res_p) / 100))  # 法抗90封顶
            damage += damage * is_crit * sub.crit_d_p
            message = f"{sub.name}对{obj.name}发动了普通攻击，{is_crit_str}对其造成了{damage}点法术伤害！"  # 返回的字符串

            if not obj.invincible:
                obj.health -= damage
                if await obj.is_die():
                    message += f"\n{obj.name}被{sub.name}击倒了！"
                    if obj in self.map_enemies_list:
                        self.map_enemies_list.remove(obj)
                    else:
                        self.player_ops_list.remove(obj)
                    self.all_ops_list.remove(obj)
        elif sub.atk_type_p == 2:  # 群体物理
            message = f"{sub.name}对"  # 返回的字符串
            objs_name: str = ""  # 所有目标名字
            objs_damage: str = ""  # 各个目标受到的伤害
            die_objs: str = ""  # 被击倒的目标名字
            for op in obj.next_operators:
                objs_name += f" {op.name}"
                damage: int = (sub.atk_p - op.defence_p) \
                    if (sub.atk_p - op.defence_p > sub.atk_p * 0.05) \
                    else (sub.atk_p * 0.05)
                damage += damage * is_crit * sub.crit_d_p
                objs_damage += f" {damage}"
                if not op.invincible:
                    op.health -= damage
                    if await op.is_die():
                        die_objs += f" {op.name}"
                        if op in self.map_enemies_list:
                            self.map_enemies_list.remove(op)
                        else:
                            self.player_ops_list.remove(op)
                        self.all_ops_list.remove(op)
            message += f"{objs_name} 发动了普通攻击，{is_crit_str}分别对他们造成了{objs_damage} 点物理伤害！\n{die_objs} 被击倒了！"
        elif sub.atk_type_p == 3:  # 群体法术
            message = f"{sub.name}对"  # 返回的字符串
            objs_name: str = ""  # 所有目标名字
            objs_damage: str = ""  # 各个目标受到的伤害
            die_objs: str = ""  # 被击倒的目标名字
            for op in obj.next_operators:
                objs_name += f" {op.name}"
                damage: int = int(sub.atk_p * ((100 - op.res_p) / 100))
                damage += damage * is_crit * sub.crit_d_p
                objs_damage += f" {damage}"
                if not op.invincible:
                    op.health -= damage
                    if await op.is_die():
                        die_objs += f" {op.name}"
                        if op in self.map_enemies_list:
                            self.map_enemies_list.remove(op)
                        else:
                            self.player_ops_list.remove(op)
                        self.all_ops_list.remove(op)
            message += f"{objs_name} 发动了普通攻击，{is_crit_str}分别对他们造成了{objs_damage} 点法术伤害！\n{die_objs} 被击倒了！"
        elif sub.atk_type_p == 4:  # 单体治疗
            health_amount = sub.atk_p
            obj.health += health_amount
            if obj.health > obj.max_health_p:
                obj.health = obj.max_health_p
                health_amount = sub.atk_p + (obj.max_health_p - obj.health - sub.atk_p)

            message = f"{sub.name}治疗了{obj.name}，恢复其{health_amount}生命值！"  # 返回的字符串
        elif sub.atk_type_p == 5:  # 群体治疗
            message = f"{sub.name}治疗了"  # 返回的字符串
            objs_name: str = ""  # 所有目标名字
            objs_health: str = ""  # 各个目标恢复的生命值
            health_amount = sub.atk_p
            for op in obj.next_operators:
                objs_name += f" {op.name}"
                op.health += health_amount
                if op.health > op.max_health_p:
                    op.health = op.max_health_p
                    health_amount = sub.atk_p + (op.max_health_p - op.health - sub.atk_p)
                objs_health += f"{health_amount} "
            message += f"{objs_name}，分别恢复他们{objs_health} 的生命值！"
        elif sub.atk_type_p == 6:  # 单体真实
            damage: int = sub.atk_p
            damage += damage * is_crit * sub.crit_d_p
            message = f"{sub.name}对{obj.name}发动了普通攻击，{is_crit_str}对其造成了{damage}点真实伤害！"  # 返回的字符串
            if not obj.invincible:
                obj.health -= damage
                if await obj.is_die():
                    message += f"\n{obj.name}被{sub.name}击倒了！"
                    if obj in self.map_enemies_list:
                        self.map_enemies_list.remove(obj)
                    else:
                        self.player_ops_list.remove(obj)
                    self.all_ops_list.remove(obj)
        elif sub.atk_type_p == 7:  # 不攻击
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
        enemies_obj: list[Operator] = []  # 受影响的敌人
        objs_name: str = ""
        objs_damage: str = ""
        message: str = f"{sub.name}使用了{skill.name}！"  # 返回的信息
        sid = skill.sid  # 技能id
        if sid < 0:  # 小于0的为敌人技能
            if sid == -1:
                for op in obj1.next_operators:
                    damage = sub.atk_p * skill.rate1 * (1 - op.res_p)
                    op.health -= damage
                    enemies_obj.append(op)
                    objs_name += f" {op.name}"
                    objs_damage += f" {damage}"
                message += f"\n对{objs_name}\n分别造成了{objs_damage} 点法术伤害！"
        else:
            if sid <= 50:  # 1~50
                if sid <= 25:  # 1~25
                    if sid == 1:
                        self.player_skill_count += int(skill.rate1)
                        message += f"\n回复了{int(skill.rate1)}技力点！"
                    elif sid == 2:
                        skill.count += 1
                        sub.atk_type_p = skill.rate1
                        sub.atk_add_f += skill.rate2
                        message += f"\n攻击力提高{round(skill.rate2 * 100, 1)}%并变为法术伤害！"
                    elif sid == 3:
                        message += f"\n恢复{round(skill.rate1 * 100, 1)}%最大生命值！"
                        sub.health += sub.max_health_p * skill.rate1
                        if sub.health > sub.max_health_p:
                            sub.health = sub.max_health_p
                    elif sid == 4:
                        rate = random.uniform(skill.rate1, skill.rate2)
                        if sub.atk_type_p == 1:
                            atk_type_str = "法术"
                            damage = int(sub.atk_p * rate * (1 - obj1.res_p))
                        else:
                            atk_type_str = "物理"
                            damage = int(sub.atk_p * rate - obj1.defence_p) if \
                                sub.atk_p * rate - obj1.defence_p > sub.atk_p * rate * 0.05 else \
                                int(sub.atk_p * rate * 0.05)
                        obj1.health -= damage
                        enemies_obj.append(obj1)
                        message += f"\n对{obj1.name}造成了{damage}点{atk_type_str}伤害！"
                    elif sid == 5:
                        skill.count += 1
                        sub.atk_add_f += skill.rate1
                        message += f"\n攻击力提高{round(skill.rate1 * 100, 1)}%！"
                    elif sid == 6:
                        skill.count += 1
                        sub.def_add_f += skill.rate1
                        message += f"\n防御力提高{round(skill.rate1 * 100, 1)}%！"
                    elif sid == 7:
                        damage_str: str = ""
                        for i in range(int(skill.rate1)):
                            rate = random.uniform(skill.rate2, skill.rate3)

                            damage = int(sub.atk_p * rate - obj1.defence_p) if \
                                sub.atk_p * rate - obj1.defence_p > sub.atk_p * rate * 0.05 else \
                                int(sub.atk_p * rate * 0.05)
                            obj1.health -= damage
                            damage_str += f"{damage}+"
                        damage_str = damage_str.rstrip("+")  # 去掉末尾的+号
                        enemies_obj.append(obj1)
                        message += f"\n对{obj1.name}造成了{damage_str}点物理伤害！"
                    elif sid == 8:
                        treat = int(sub.atk_p * skill.rate1)
                        obj1.health += treat
                        obj2.health += treat
                        if obj1.health > obj1.max_health_p:
                            obj1.health = obj1.max_health_p
                        if obj2.health > obj2.max_health_p:
                            obj2.health = obj2.max_health_p
                        message += f"\n分别为{obj1.name}和{obj2.name}恢复了{treat}点生命值！"
                    elif sid == 9:
                        skill.count += 1
                        sub.atk_add_f += skill.rate2
                        message += f"\n每回合回复{int(skill.rate1)}技力点，攻击力提高{round(skill.rate2 * 100, 1)}%！"
                    elif sid == 10:
                        skill.count += 1
                        sub.crit_r_add_d += skill.rate1
                        sub.crit_d_add_d += skill.rate2
                        message += f"\n暴击率增加{round(skill.rate1 * 100, 1)}%，暴击伤害增加{round(skill.rate2 * 100, 1)}%！\n"
                        await sub.upgrade_effect()
                        message += await self.attack(sub, obj1)
                        enemies_obj.append(obj1)
                else:  # 26~50
                    pass
            else:
                if sid <= 75:  # 51~75
                    pass
                else:  # 76~100
                    pass

        skill.count = skill.persistence

        for op in enemies_obj:
            if await op.is_die():
                message += f"\n{op.name}被击倒了！"
                if op in self.map_enemies_list:
                    self.map_enemies_list.remove(op)
                else:
                    self.player_ops_list.remove(op)
                self.all_ops_list.remove(op)
        return message

    async def finish_turn(self, sub: Operator):
        """


        :param sub: 结束回合的对象
        """
        finish_skill: list[Skill] = []
        for skill in sub.skills_list:
            if skill.count > 1:
                skill.count -= 1
                if skill.count == 0:
                    finish_skill.append(skill)
                sid = skill.sid
                if sid == 9:
                    self.player_skill_count += int(skill.rate1)

        for f_s in finish_skill:
            sid = f_s.sid
            if sid == 2:
                sub.atk_type_p = sub.atk_type
                sub.atk_add_f -= f_s.rate2
            elif sid == 5:
                sub.atk_add_f -= f_s.rate1
            elif sid == 6:
                sub.def_add_f -= f_s.rate1
            elif sid == 9:
                sub.atk_add_f -= f_s.rate2
        await sub.finish_turn()
        sub.speed_p = 0


async def new_instance(uid: str or int, mid: str) -> PlayingManager:
    player_ops_list: list[Operator] = await get_operator_list(uid)
    map_enemies_list: list[Operator] = await get_enemies_list(mid)
    return PlayingManager(player_ops_list, map_enemies_list)


# 冒泡排序函数
def bubble_sort(arr: list[Operator]):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j].speed_p < arr[j + 1].speed_p:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
