# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:55
# @Software:PyCharm
import copy
import random

from pathlib import Path
from .DB import get_user_playing_ops, get_op_attribute, OPAttribute, get_map_attribute, MapAttribute
from .skill import get_skills_list
from .skill import Skill
from .effect import Effect, new_effect_instance

user_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'user_data.json'

"""
数据库玩家表示例
uid:str         level:int           operators_all                               operators_playing
  123               10           {2:{level:10,skills:{1,2,3}},...}             {2:{level:10,skills:{1,2,3}},...} 
"""


class Operator:

    def __init__(self, oid: int, name: str, level: int, stars: int, profession: str, health: int, atk: int,
                 defence: int, res: float, crit_r: float, crit_d: float, speed: float,
                 atk_type: int, skills_list: list[Skill], effect_list: list[Effect], pm, is_enemy: bool):
        """
        :param oid: 干员id
        :param name: 干员名称
        :param level: 干员等级
        :param stars: 干员星级 / 敌人类型
        :param profession: 干员职业 / 敌人种类
        :param health: 干员初始生命值(初始赋值给干员的最大生命值max_health和当前生命值health)
        :param atk: 干员初始攻击力
        :param defence: 干员初始防御力
        :param res: 干员初始法抗
        :param crit_r: 干员初始暴击率
        :param crit_d: 干员初始暴击伤害倍率
        :param speed: 干员初始速度
        :param atk_type: 干员攻击方式
        :param skills_list: 干员的技能列表
        :param effect_list: 效果列表(开局就拥有的效果)
        :param is_enemy: 是否为敌人
        :param pm: 战斗数据

        后面有_p的变量表示干员战斗时该变量的实际值(xxx_p = xxx * (1 + xxx_add_f) + xxx_add_d)

        攻击类型列表
        0:物理单体  1:法术单体  2:物理群体  3:法术群体  4:治疗单体  5:治疗群体  6:真实单体  7:真实群体  8:物理单体嘲讽  9:不进行普攻

        敌人类型列表
        1:普通  2:高级  3:精英  4:高级精英  5:领袖  6:强大领袖(双阶段)
        """
        self.oid = oid
        self.name = name
        self.stars = stars
        self.profession = profession
        self.level = level
        self.max_health = self.health = self.max_health_p = health
        self.atk = self.atk_p = atk
        self.defence = self.defence_p = defence
        self.res = self.res_p = res
        self.crit_r = self.crit_r_p = crit_r
        self.crit_d = self.crit_d_p = crit_d
        self.max_speed = self.speed = self.max_speed_p = speed
        self.atk_type_p = self.atk_type = atk_type
        self.atk_type_str = "-"
        self.skills_list = skills_list
        self.pm = pm
        self.is_enemy = is_enemy

        if atk_type == 0:
            self.atk_type_str = "物理单体"
        elif atk_type == 1:
            self.atk_type_str = "法术单体"
        elif atk_type == 2:
            self.atk_type_str = "物理群体"
        elif atk_type == 3:
            self.atk_type_str = "法术群体"
        elif atk_type == 4:
            self.atk_type_str = "单体治疗"
        elif atk_type == 5:
            self.atk_type_str = "群体治疗"
        elif atk_type == 6:
            self.atk_type_str = "真实单体"
        elif atk_type == 7:
            self.atk_type_str = "真实群体"
        elif atk_type == 8:
            self.atk_type_str = "物理单体嘲讽"
        elif atk_type == 9:
            self.atk_type_str = "不进行普攻"

        """
        以下是干员战斗时特有的属性:
        
        health_add_f: 最大生命值百分比加成
        atk_add_f: 攻击力百分比加成
        def_add_f: 防御力百分比加成
        res_add_f: 法抗百分比加成
        crit_r_add_f: 暴击率百分比加成
        crit_d_add_f: 暴击伤害百分比加成
        
        health_add_d: 最大生命值数值加成
        atk_add_d: 攻击力数值加成
        def_add_d: 防御力数值加成
        res_add_d: 法抗数值加成
        speed_f: 速度数值加成
        
        特殊状态(数值表示持续回合，大于0时生效，效果生效时每回合减1)
        immobile: 无法行动(无法普攻和使用技能，跳过该干员回合)
        silent: 沉默(无法使用技能)
        hidden: 隐匿(无法被敌方指向性技能选中)
        deathless: 不死(血量最多降为1)
        invincible: 无敌(无法受到任何伤害)
        mocked: 被嘲讽(攻击时只能攻击指定单位)
        mocking_obj: 嘲讽者(被嘲讽时只能攻击的单位)
        
        effect_list: 增益(削弱)效果列表
        next_operators: 身边的干员(包括自己)
        damage_list: 受到的伤害(包括治疗量)
        """

        self.health_add_f: float = 0.0
        self.atk_add_f: float = 0.0
        self.def_add_f: float = 0.0
        self.res_add_f: float = 0.0

        self.health_add_d: int = 0
        self.atk_add_d: int = 0
        self.def_add_d: int = 0
        self.res_add_d: float = 0
        self.crit_r_add_d: float = 0
        self.crit_d_add_d: float = 0
        self.speed_add_d: float = 0

        self.immobile: int = 0
        self.silent: int = 0
        self.hidden: int = 0
        self.deathless: int = 0
        self.invincible: int = 0
        self.mocked: int = 0
        self.mocking_obj = None

        self.effect_list: list[Effect] = effect_list
        self.next_operators: list = []
        self.damage_list = []

        self.init_effect()

    async def hurt(self, sub, atk_type: int, damage: int, ignore_def: float = 0, ignore_res: float = 0) -> int:
        """
        干员受到伤害时调用的方法

        :param sub: 攻击者
        :param atk_type: 攻击类型。0:物理  1:法术  6:真实
        :param damage: 伤害量
        :param ignore_def: 无视防御比例
        :param ignore_res: 无视法抗比例
        :return: 返回受到的伤害/治疗量
        """
        result = 0  # 返回的伤害或治疗量
        if not self.invincible:  # 自身处于无敌状态则不会扣血
            if atk_type in [0, 2, 8, 9]:  # 物理伤害
                defence = self.defence_p * (1 - ignore_def)
                result = int(damage * (damage / (damage + 2 * defence)))
            elif atk_type in [1, 3]:  # 法术伤害
                res = self.res_p * (1 - ignore_res)
                result = damage * ((100 - res) / 100) \
                    if (damage * ((100 - res) / 100) > damage * 0.1) \
                    else int(damage * 0.1)  # 10%攻击力的保底伤害
            elif atk_type in [6, 7]:  # 真实伤害
                result = damage

        # 无敌状态可以受到治疗
        if atk_type in [4, 5]:
            result = int(damage)

        result = int(result)
        if atk_type in [0, 1, 2, 3, 6, 7, 8, 9]:
            self.health -= result
            self.damage_list.append(int(-1 * result))  # 将伤害值存进伤害表里(负数)

            # 受到伤害后会改变的属性
            for e in self.effect_list:
                if e.effect_type == 11 and e.effect_level < e.max_level:
                    e.effect_level += 1
                elif e.effect_type == 15:
                    e.effect_level -= 1
                    if e.effect_level <= 0:
                        self.effect_list.remove(e)
                    self.def_add_f -= e.effect_degree
                    self.defence_p = self.defence * (1 + self.def_add_f) + self.def_add_d
                    self.defence_p = 0 if self.defence_p < 0 else self.defence_p

        elif atk_type in [4, 5]:
            self.health += result
            if self.health > self.max_health_p:
                temp = self.health
                self.health = self.max_health_p
                result = result - (temp - self.max_health_p)
            self.damage_list.append(int(result))  # 将治疗量存进伤害表里(正数)

        if sub is not None:
            for e in sub.effect_list:
                if e.effect_type == 16 and e.effect_level < e.max_level:
                    e.effect_level += 1

        return int(result)

    async def is_die(self) -> bool:
        """
        判断干员是否被击倒的函数

        :return: 干员是否被击倒(如果干员处于不死状态则不会被击倒)
        """
        if self.health > 0:  # 血量大于0直接返回False
            return False

        if self.deathless:  # 如果干员处于不死状态，则将其血量恢复为1
            self.health = 1
            return False

        for e in self.effect_list:

            if e.effect_type == 12:
                stage_2 = await new_instance(int(e.effect_degree), self.level, [0, 0, 0], self.pm, self.is_enemy)
                await self.obj_cpy(stage_2)  # 更新干员属性
                return False
        return True

    async def finish_turn(self) -> str:
        """
        干员结束当前回合时需要执行的函数
        """
        message: str = ""  # 返回的信息
        finish_skill: list[Skill] = []  # 持续时间结束的技能列表

        # 回合结束后生效的技能效果在这里实现
        # 这里也进行技能持续时间是否结束的判断
        for skill in self.skills_list:
            # 如果技能持续时间大于等于1回合(对于持续时间无限的技能，skill.count为-1)
            if skill.count >= 1:
                skill.count -= 1  # 技能持续时间减少1回合

                # 技能效果生效逻辑在这里
                sid = skill.sid
                if sid in [9, 11, 12]:  # 冲锋号令_进攻 支援号令 支援号令_治疗
                    self.pm.player_skill_count += int(skill.rate1)
                    message += f"\n{skill.name}生效！回复{int(skill.rate1)}点技力点"

                # 如果技能结束则将其添加进结束技能列表
                if skill.count == 0:
                    finish_skill.append(skill)

        # 遍历结束技能列表内的技能
        for f_s in finish_skill:
            message += f"\n{self.name}的技能{f_s.name}结束了！"
            f_sid = f_s.sid

            # 技能结束后效果生效逻辑在这里
            if f_sid == 26:  # 肉斩骨断
                await self.append_effect(Effect("26-3", 23, 2, 0, 0, 0, 0))
                message += f"\n{self.name}眩晕了！"

        finish_effect_list: list[Effect] = []
        for e in self.effect_list:
            if e.effect_type == 14:
                await self.hurt(None, 4, int(self.max_health_p * e.effect_degree))
            elif e.effect_type == 17:
                await self.hurt(None, 6, int(self.health * (-1 * e.effect_degree)))

            e.persistence -= 1

            if e.persistence == 0:  # 持续时间结束
                if e.effect_type == 25:  # 死战效果结束干员直接倒地
                    self.health = -10000

                finish_effect_list.append(e)  # 将技能放入待移除列表(直接在这里移除的话该循环会出现遍历异常)

        # 如果干员被击倒(这通常是因为流血buff导致的，当然也有可能是死战buff)
        if await self.is_die():
            message += f"\n{self.name}被击倒了！"
            await self.op_die()  # 调用干员倒地函数
            return message

        # 将技能移出列表
        for f_e in finish_effect_list:
            self.effect_list.remove(f_e)

        await self.upgrade_effect()

        # 干员速度设为0(我以后可能会改成跟星铁那样的行动条)
        self.speed = 0
        return message

    async def upgrade_effect(self):
        """
        更新干员各项属性的方法
        """
        self.health_add_f = 0.0
        self.atk_add_f = 0.0
        self.def_add_f = 0.0
        self.res_add_f = 0.0
        self.health_add_d = 0
        self.atk_add_d = 0
        self.def_add_d = 0
        self.res_add_d = 0
        self.crit_r_add_d = 0
        self.crit_d_add_d = 0
        self.speed_add_d = 0
        self.atk_type_p = self.atk_type

        self.mocked = 0
        self.hidden = 0
        self.deathless = 0
        self.invincible = 0
        self.silent = 0
        self.immobile = 0

        for e in self.effect_list:
            # 根据效果种类给予属性加成
            e_t = e.effect_type
            e_d = e.effect_degree
            if e_t == 0:
                self.atk_add_f += e_d
            elif e_t == 1:
                self.def_add_f += e_d
            elif e_t == 2:
                self.health_add_f += e_d
            elif e_t == 3:
                self.res_add_f += e_d
            elif e_t == 4:
                self.atk_add_d += e_d
            elif e_t == 5:
                self.def_add_d += e_d
            elif e_t == 6:
                self.health_add_d += e_d
            elif e_t == 7:
                self.res_add_d += e_d
            elif e_t == 8:
                self.crit_r_add_d += e_d
            elif e_t == 9:
                self.crit_d_add_d += e_d
            elif e_t in [10, 26]:
                self.speed_add_d += e_d
            elif e_t == 11:
                self.atk_add_f += (e_d * e.effect_level)
            elif e_t == 13:
                self.atk_type_p = int(e.effect_degree)
            elif e_t == 15:
                self.def_add_f += (e_d * e.effect_level)
            elif e_t == 16:
                self.atk_add_f += (e_d * e.effect_level)
            elif e_t == 18:
                self.mocked = 1
            elif e_t == 19:
                self.hidden = 1
            elif e_t == 20:
                self.deathless = 1
            elif e_t == 21:
                self.invincible = 1
            elif e_t == 22:
                self.silent = 1
            elif e_t in [23, 24]:
                self.immobile = 1

        if self.mocked == 0:
            self.mocking_obj = None

        self.max_health_p = self.max_health * (1 + self.health_add_f) + self.health_add_d
        self.max_health_p = 0 if self.max_health_p < 0 else self.max_health_p
        self.atk_p = self.atk * (1 + self.atk_add_f) + self.atk_add_d
        self.atk_p = 0 if self.atk_p < 0 else self.atk_p
        self.defence_p = self.defence * (1 + self.def_add_f) + self.def_add_d
        self.defence_p = 0 if self.defence_p < 0 else self.defence_p
        self.res_p = self.res * (1 + self.res_add_f) + self.res_add_d
        self.res_p = 0 if self.res_p < 0 else self.res_p
        self.crit_r_p = self.crit_r + self.crit_r_add_d
        self.crit_r_p = 0 if self.crit_r_p < 0 else self.crit_r_p
        self.crit_d_p = self.crit_d + self.crit_d_add_d
        self.crit_d_p = 0 if self.crit_d_p < 0 else self.crit_d_p
        self.max_speed_p = self.max_speed + self.speed_add_d
        self.max_speed_p = 10 if self.max_speed_p < 10 else self.max_speed_p  # 保底速度
        if self.speed > self.max_speed_p:
            self.speed = self.max_speed_p

    def init_effect(self):
        """
        更新干员各项属性的方法
        """

        for e in self.effect_list:
            # 根据效果种类给予属性加成
            e_t = e.effect_type
            e_d = e.effect_degree
            if e_t == 0:
                self.atk_add_f += e_d
            elif e_t == 1:
                self.def_add_f += e_d
            elif e_t == 2:
                self.health_add_f += e_d
            elif e_t == 3:
                self.res_add_f += e_d
            elif e_t == 4:
                self.atk_add_d += e_d
            elif e_t == 5:
                self.def_add_d += e_d
            elif e_t == 6:
                self.health_add_d += e_d
            elif e_t == 7:
                self.res_add_d += e_d
            elif e_t == 8:
                self.crit_r_add_d += e_d
            elif e_t == 9:
                self.crit_d_add_d += e_d
            elif e_t in [10, 26]:
                self.speed_add_d += e_d
            elif e_t == 11:
                self.atk_add_f += (e_d * e.effect_level)
            elif e_t == 13:
                self.atk_type_p = int(e.effect_degree)
            elif e_t == 15:
                self.def_add_f += (e_d * e.effect_level)
            elif e_t == 16:
                self.atk_add_f += (e_d * e.effect_level)
            elif e_t == 18:
                self.mocked = 1
            elif e_t == 19:
                self.hidden = 1
            elif e_t == 20:
                self.deathless = 1
            elif e_t == 21:
                self.invincible = 1
            elif e_t == 22:
                self.silent = 1
            elif e_t in [23, 24]:
                self.immobile = 1

        if self.mocked == 0:
            self.mocking_obj = None

        self.max_health_p = self.max_health * (1 + self.health_add_f) + self.health_add_d
        self.max_health_p = 1 if self.max_health_p < 1 else self.max_health_p
        if self.health > self.max_health_p:
            self.health = self.max_health_p
        self.atk_p = self.atk * (1 + self.atk_add_f) + self.atk_add_d
        self.atk_p = 1 if self.atk_p < 1 else self.atk_p
        self.defence_p = self.defence * (1 + self.def_add_f) + self.def_add_d
        self.defence_p = 0 if self.defence_p < 0 else self.defence_p
        self.res_p = self.res * (1 + self.res_add_f) + self.res_add_d
        self.res_p = 0 if self.res_p < 0 else self.res_p
        self.crit_r_p = self.crit_r + self.crit_r_add_d
        self.crit_r_p = 0 if self.crit_r_p < 0 else self.crit_r_p
        self.crit_d_p = self.crit_d + self.crit_d_add_d
        self.crit_d_p = 0 if self.crit_d_p < 0 else self.crit_d_p
        self.max_speed_p = self.max_speed + self.speed_add_d
        self.max_speed_p = 10 if self.max_speed_p < 10 else self.max_speed_p

    async def append_effect_list(self, effect_list: list[Effect]):
        """
        给干员添加效果的方法(请不要直接将Effect列表直接用"+"或者"+="添加进effect_list中)

        :param effect_list: 要添加的效果列表
        """
        for e in effect_list:
            await self.append_effect(e)

    async def append_effect(self, e: Effect):
        """
        给干员添加效果的方法(请不要直接用list.append()函数将效果添加进effect_list中)

        :param e: 要添加的效果
        """
        # 只可同时存在一个的效果
        if e.effect_type == 18:
            for i in range(len(self.effect_list)):
                if self.effect_list[i].effect_type == 18:  # 嘲讽效果只同时存在一个
                    self.effect_list[i] = e
                    return

        elif e.effect_type == 26:
            for i in range(len(self.effect_list)):
                if self.effect_list[i].effect_type == 24:  # 冻结效果延长持续时间
                    self.effect_list[i].persistence += 1
                    return
                elif self.effect_list[i].effect_type == 26:  # 寒冷效果叠加变为冻结
                    self.effect_list[i].effect_type = 24
                    self.effect_list[i].persistence = 1
                    self.effect_list[i].effect_degree = 0
                    return

        # 其他效果
        else:
            for i in range(len(self.effect_list)):
                if self.effect_list[i].effect_id == e.effect_id:  # 同id效果只需要刷新持续时间
                    self.effect_list[i].persistence = e.persistence
                    return

        self.effect_list.append(e)  # 添加效果

        if e.effect_type in [2, 6]:  # 最大生命值加成类效果附带回血效果
            if e.effect_type == 6 and e.effect_degree > 0:
                health_amount = e.effect_degree
            else:  # e.effect_type == 2 and e.effect_degree > 0:
                health_amount = self.max_health_p * e.effect_degree
            await self.upgrade_effect()
            await self.hurt(self, 4, int(health_amount))

    async def obj_cpy(self, des):
        self.oid = des.oid
        self.name = des.name
        self.stars = des.stars
        self.profession = des.profession
        self.level = des.level
        self.max_health = self.health = self.max_health_p = des.health
        self.atk = self.atk_p = des.atk
        self.defence = self.defence_p = des.defence
        self.res = self.res_p = des.res
        self.crit_r = self.crit_r_p = des.crit_r
        self.crit_d = self.crit_d_p = des.crit_d
        self.max_speed = self.speed = self.max_speed_p = des.speed
        self.atk_type_p = self.atk_type = des.atk_type
        self.atk_type_str = "-"
        self.skills_list = des.skills_list
        self.is_enemy = des.is_enemy

        atk_type = des.atk_type

        if atk_type == 0:
            self.atk_type_str = "物理单体"
        elif atk_type == 1:
            self.atk_type_str = "法术单体"
        elif atk_type == 2:
            self.atk_type_str = "物理群体"
        elif atk_type == 3:
            self.atk_type_str = "法术群体"
        elif atk_type == 4:
            self.atk_type_str = "单体治疗"
        elif atk_type == 5:
            self.atk_type_str = "群体治疗"
        elif atk_type == 6:
            self.atk_type_str = "真实单体"
        elif atk_type == 7:
            self.atk_type_str = "真实群体"
        elif atk_type == 8:
            self.atk_type_str = "物理单体嘲讽"
        elif atk_type == 9:
            self.atk_type_str = "不进行普攻"

        self.effect_list: list[Effect] = des.effect_list
        self.damage_list = []

        self.init_effect()

    async def attack(self, obj) -> str:
        """
        干员进行普攻的函数，会根据atk_type来进行不同的操作

        :param obj: 目标
        :return: 信息字符串
        """
        message: str = ""
        is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
        is_crit_str: str = "暴击并" if is_crit else ""
        damage = int(self.atk_p + (self.atk_p * is_crit * self.crit_d_p))  # 初始伤害
        atk_type = self.atk_type_p

        if atk_type in [0, 1, 6, 8]:  # 单体物理(嘲讽)
            atk_type = atk_type
            atk_type_str = ""
            if atk_type in [0, 8]:
                atk_type_str = "物理"
            elif atk_type == 1:
                atk_type_str = "法术"
            elif atk_type == 6:
                atk_type_str = "真实"
            damage = await obj.hurt(self, atk_type, damage)
            message = f"{self.name}对{obj.name}发动了普通攻击，{is_crit_str}对其造成了{damage}点{atk_type_str}伤害！"  # 返回的字符串
            if atk_type == 8 and random.randint(1, 100) < 80:  # 重装普攻大概率嘲讽敌方单位
                message += f"\n{self.name}嘲讽了{obj.name}！\n持续2回合！"
                obj.mocking_obj = self
                await obj.append_effect(Effect("0-1", 18, 2, 0, 0, 0, 0))
                await obj.upgrade_effect()
            if await obj.is_die():
                message += f"\n{obj.name}被{self.name}击倒了！"
                await obj.op_die()

        elif atk_type in [2, 3, 7]:  # 群体真实
            atk_type = atk_type  # 攻击类型
            atk_type_str = ""
            if atk_type == 2:
                atk_type_str = "物理"
            elif atk_type == 3:
                atk_type_str = "法术"
            elif atk_type == 7:
                atk_type_str = "真实"
            message = f"{self.name}对"  # 返回的字符串
            objs_name: str = ""  # 所有目标名字
            objs_damage: str = ""  # 各个目标受到的伤害
            die_objs: str = ""  # 被击倒的目标名字
            for op in obj.next_operators:
                if not isinstance(op, Operator):
                    continue
                objs_name += f" {op.name}"
                damage_amount = await op.hurt(self, atk_type, damage)
                objs_damage += f" {damage_amount}"
                if await op.is_die():
                    die_objs += f" {op.name}"
                    await op.op_die()
            message += f"{objs_name} 发动了普通攻击，{is_crit_str}分别对他们造成了{objs_damage} 点{atk_type_str}伤害！"
            if die_objs != "":
                message += f"\n{die_objs} 被击倒了！"

        elif atk_type == 4:  # 单体治疗
            health_amount = await obj.hurt(self, atk_type, self.atk_p)
            message = f"{self.name}治疗了{obj.name}，恢复其{health_amount}生命值！"  # 返回的字符串

        elif atk_type == 5:  # 群体治疗
            message = f"{self.name}治疗了"  # 返回的字符串
            objs_name: str = ""  # 所有目标名字
            objs_health: str = ""  # 各个目标恢复的生命值
            for op in obj.next_operators:
                if not isinstance(op, Operator):
                    continue
                objs_name += f" {op.name}"
                health_amount = await op.hurt(self, atk_type, self.atk_p)
                objs_health += f" {health_amount}"
            message += f"{objs_name}，分别恢复他们{objs_health} 的生命值！"

        elif atk_type == 9:  # 不攻击
            message = f"{self.name}无动于衷..."

        return message

    async def op_die(self):
        """
        干员被击倒时调用的方法

        """
        if self in self.pm.all_enemies_list:
            sub_list = self.pm.all_enemies_list
            obj_list = self.pm.all_ops_list
        else:
            sub_list = self.pm.all_ops_list
            obj_list = self.pm.all_enemies_list

        sub_list.remove(self)
        await self.refresh_op_next_list()  # 刷新周围干员
        for op in obj_list:  # 解除嘲讽效果
            if op.mocking_obj == self:
                for e in op.effect_list:
                    if e.effect_type == 18:
                        op.effect_list.remove(e)
                        break
                op.mocked = 0
                op.mocking_obj = None
        self.pm.all_list.remove(self)

    async def refresh_op_next_list(self):
        """
        刷新干员身边的干员列表
        """
        if self in self.pm.all_enemies_list:
            op_list = self.pm.all_enemies_list
        else:
            op_list = self.pm.all_ops_list

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

    async def use_skill(self, skill_num: int, obj1=None, obj2=None) -> str:
        """
        使用技能

        :param skill_num: 使用的技能序号
        :param obj1: 目标对象1(可选)
        :param obj2: 目标对象2(可选)
        """
        skill: Skill = self.skills_list[skill_num]  # 使用的技能
        objs_list: list[Operator] = []  # 受影响的敌人
        objs_name: str = ""
        objs_damage: str = ""
        message: str = f"{self.name}使用了{skill.name}！"  # 返回的信息
        sid = skill.sid  # 技能id
        persistence: int = 0  # 是否为持续性技能
        if sid < 0:  # 小于0的为敌人技能
            if sid in [-1, -2, -3, -5, -14, -18, -22, -24]:
                atk_type = 0
                atk_type_str = ""
                if sid in [-2, -3, -5, -18]:
                    atk_type = 2
                    atk_type_str = "物理"
                elif sid in [-3, -14, -22, -24]:
                    atk_type = 3
                    atk_type_str = "法术"
                for op in obj1.next_operators:
                    if not isinstance(op, Operator):
                        continue
                    damage = int(self.atk_p * skill.rate1)
                    if sid == -13:
                        for e in obj1.effect_list:  # 对被冰冻目标伤害提高50%
                            if e.effect_type == 24:
                                damage = int(damage * 1.5)
                                break
                    damage_amount = await op.hurt(self, atk_type, damage, skill.rate2)

                    objs_list.append(op)
                    objs_name += f" {op.name}"
                    objs_damage += f" {damage_amount}"
                message += f"\n对{objs_name}\n分别造成了{objs_damage} 点{atk_type_str}伤害！"
            elif sid == -4:
                atk_type_str = ""
                if self.atk_type_p in [0, 2, 8]:
                    atk_type_str = "物理"
                elif self.atk_type_p in [1, 3]:
                    atk_type_str = "法术"
                elif self.atk_type_p in [6, 7]:
                    atk_type_str = "真实"
                damage = int((self.atk_p * (1 + self.crit_d_p)) * skill.rate1)
                damage = await obj1.hurt(self, self.atk_type_p, damage)
                objs_list.append(obj1)
                message += f"\n暴击并对{obj1.name}造成了{damage}点{atk_type_str}伤害！"
            elif sid in [-6, -8, -10]:
                atk_type_str = ""
                if self.atk_type_p in [0, 2, 8]:
                    atk_type_str = "物理"
                elif self.atk_type_p in [1, 3]:
                    atk_type_str = "法术"
                elif self.atk_type_p in [6, 7]:
                    atk_type_str = "真实"
                damage = int(self.atk_p * skill.rate1)
                damage = await obj1.hurt(self, self.atk_type_p, damage)
                obj1.immobile = 1
                objs_list.append(obj1)
                message += f"\n对{obj1.name}造成了{damage}点{atk_type_str}伤害！并使其无法行动{skill.rate2}回合！"
            elif sid == -7:
                damage = int(self.atk_p * skill.rate1)
                for op in self.pm.all_ops_list:
                    if not isinstance(op, Operator):
                        continue
                    damage_amount = await op.hurt(self, 1, damage)

                    objs_list.append(op)
                    objs_name += f" {op.name}"
                    objs_damage += f" {damage_amount}"
                message += f"\n对{objs_name}\n分别造成了{objs_damage} 点法术伤害并使其寒冷，持续1回合！"
            elif sid == -9:
                persistence = 1
                message += f"\n每回合恢复{round(skill.rate1 * 100, 2)}%最大生命值，持续{skill.persistence}回合！"
            elif sid == -11:
                persistence = 1
                self.hidden = skill.persistence + 1
                message += f"\n进入隐匿状态，持续{skill.persistence}回合！"
            elif sid in [-12, -13]:
                atk_type_str = ""
                if self.atk_type_p in [0, 2, 8]:
                    atk_type_str = "物理"
                elif self.atk_type_p in [1, 3]:
                    atk_type_str = "法术"
                elif self.atk_type_p in [6, 7]:
                    atk_type_str = "真实"
                damage = int(self.atk_p * skill.rate1)
                if sid == -13:
                    for e in obj1.effect_list:  # 对被冰冻目标伤害提高50%
                        if e.effect_type == 24:
                            damage = int(damage * 1.5)
                            break
                damage = await obj1.hurt(self, self.atk_type_p, damage)
                objs_list.append(obj1)
                message += f"\n对{obj1.name}造成了{damage}点{atk_type_str}伤害！"
            elif sid == -15:
                for op in self.pm.all_enemies_list:
                    objs_list.append(op)
                message += f"\n使所有敌人攻击力和防御力提升！"
            elif sid == -16:
                objs_list.append(self)
                message += f"\n使自身伤害类型变为单体法术！"
            elif sid == -17:
                mock_ops = ""
                for op in self.pm.all_ops_list:
                    if random.randint(1, 10000) < skill.rate1 * 10000:
                        op.mocking_obj = self
                        await op.append_effect(Effect("-17-2", 18, int(skill.rate2), 0, 0, 0, 0))
                        await op.upgrade_effect()
                        mock_ops += f"{op.name} "

                message += f"\n{mock_ops}被嘲讽了！"
            elif sid == -19:
                persistence = 1
                message += f"\n自身攻击力提升{round(skill.rate1 * 100, 2)}%！"
            elif sid == -20:
                for op in self.pm.all_ops_list:
                    objs_list.append(op)
                message += f"\n使所有敌人每回合流失{round(skill.rate1 * 100, 2)}%当前生命值！"
            elif sid == -21:
                damage = int(self.atk_p * skill.rate1)
                damage = await obj1.hurt(self, 1, damage)
                health_amount = await self.hurt(self, 4, int(damage * skill.rate2))
                objs_list.append(obj1)
                message += f"\n对{obj1.name}造成了{damage}点法术伤害并为自己恢复了{health_amount}生命值！"
            elif sid == -23:
                damage = int(self.atk_p * skill.rate1)
                damage = await obj1.hurt(self, 1, damage)
                objs_list.append(obj1)
                message += f"\n对{obj1.name}造成了{damage}点法术伤害并使其每回合流失{round(skill.rate2 * 100, 2)}%最大生命值！"
            elif sid == -25:
                for op in self.pm.all_ops_list:
                    objs_list.append(op)
                message += f"\n使所有敌人攻击力，防御力，法抗降低{round(skill.rate1 * 100, 2)}%！"

        else:
            if sid == 1:
                self.pm.player_skill_count += int(skill.rate1)
                message += f"\n回复{int(skill.rate1)}技力点！"
            elif sid == 2:
                persistence = 1
                message += f"\n攻击力提高{round(skill.rate2 * 100, 1)}%并变为法术伤害！"
            elif sid == 3:
                health_amount = await self.hurt(self, 4, int(skill.rate1 * self.max_health_p))
                message += f"\n恢复{health_amount}生命值！"
            elif sid in [4, 13, 16, 58]:
                rate = random.uniform(skill.rate1, skill.rate2)
                is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(self.atk_p * rate + (self.atk_p * is_crit * self.crit_d_p))
                total_damage = 0
                atk_type = self.atk_type_p
                atk_type_str = ""
                if atk_type in [0, 2, 8]:
                    atk_type_str = "物理"
                elif atk_type in [1, 3]:
                    atk_type_str = "法术"
                elif atk_type in [6, 7]:
                    atk_type_str = "真实"
                if atk_type in [0, 1, 6, 8]:
                    objs_list.append(obj1)
                    if sid == 58 and obj1.health <= 0.5 * obj1.max_health_p:
                        damage = int(damage * (1 + skill.rate3))
                    damage_amount = total_damage = await obj1.hurt(self, atk_type, damage)
                    message += f"\n{is_crit_str}对{obj1.name}造成了{damage_amount}点{atk_type_str}伤害！"
                elif atk_type in [2, 3, 7]:
                    for op in obj1.next_operators:
                        if not isinstance(op, Operator):
                            continue
                        d = damage
                        if sid == 58 and op.health <= 0.5 * op.max_health_p:
                            d = int(d * (1 + skill.rate3))
                        damage_amount = await op.hurt(self, atk_type, d)
                        total_damage += damage_amount
                        objs_list.append(op)
                        objs_name += f" {op.name}"
                        objs_damage += f" {damage_amount}"
                    message += f"\n{is_crit_str}对{objs_name}\n分别造成了{objs_damage} 点{atk_type_str}伤害！"
                if sid == 13:
                    health_amount = await self.hurt(self, 4, int(total_damage * skill.rate3))
                    message += f"\n并恢复了{health_amount}点生命值！"
                elif sid == 16:
                    message += f"\n并使其速度减少{round(skill.rate3, 2)}，持续1回合！"
            elif sid == 5:
                persistence = 1
                message += f"\n攻击力提高{round(skill.rate1 * 100, 1)}%！"
            elif sid == 6:
                persistence = 1
                message += f"\n防御力提高{round(skill.rate1 * 100, 1)}%！"
            elif sid in [7, 14, 28]:
                atk_type = self.atk_type_p
                atk_type_str = ""
                damage_str: str = ""
                if atk_type in [0, 2, 8, 9]:
                    atk_type_str = "物理"
                elif atk_type in [1, 3]:
                    atk_type_str = "法术"
                elif atk_type in [6, 7]:
                    atk_type_str = "真实"

                if atk_type in [0, 1, 6, 8, 9]:
                    for i in range(int(skill.rate1)):
                        is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                        is_crit_sym: str = "★" if is_crit else ""
                        rate = random.uniform(skill.rate2, skill.rate3)
                        damage = int(self.atk_p * rate + (self.atk_p * is_crit * self.crit_d_p))
                        damage = await obj1.hurt(self, atk_type, damage)
                        damage_str += f"{damage}{is_crit_sym}+"
                    damage_str = damage_str.rstrip("+")  # 去掉末尾的+号
                    objs_list.append(obj1)
                    message += f"\n对{obj1.name}造成了{damage_str}点物理伤害！"

                elif atk_type in [2, 3, 7]:
                    for op in obj1.next_operators:
                        if not isinstance(op, Operator):
                            continue
                        damage_str = ""
                        for i in range(int(skill.rate1)):
                            is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                            is_crit_sym: str = "★" if is_crit else ""
                            rate = random.uniform(skill.rate2, skill.rate3)
                            damage = int(self.atk_p * rate + (self.atk_p * is_crit * self.crit_d_p))
                            damage_amount = await op.hurt(self, atk_type, damage)
                            damage_str += f"{damage_amount}{is_crit_sym}+"
                        damage_str = damage_str.rstrip("+")  # 去掉末尾的+号
                        objs_list.append(op)
                        objs_name += f" {op.name}"
                        objs_damage += f" \n{damage_str}"
                    message += f"\n对{objs_name}\n分别造成了{objs_damage} 点{atk_type_str}伤害！"
            elif sid == 8:
                treat1 = treat2 = int(self.atk_p * skill.rate1)
                treat1 = await obj1.hurt(self, 4, treat1)
                treat2 = await obj2.hurt(self, 4, treat2)
                message += f"\n为{obj1.name}和{obj2.name}分别恢复了 {treat1} {treat2} 点生命值！"
            elif sid == 9:
                persistence = 1
                message += f"\n每回合回复{int(skill.rate1)}技力点，攻击力提高{round(skill.rate2 * 100, 1)}%！"
            elif sid == 10:
                message += f"\n下次普攻必定暴击且暴击伤害增加{round(skill.rate1 * 100, 1)}%！"
                damage = int(self.atk_p + (self.atk_p * (self.crit_d_p + skill.rate1)))
                damage = await obj1.hurt(self, 0, damage)
                message = f"\n{self.name}对{obj1.name}发动了普通攻击，暴击并对其造成了{damage}点物理伤害！"  # 返回的字符串
                objs_list.append(obj1)
            elif sid == 11:
                persistence = 1
                self.immobile = skill.persistence + 1
                message += f"\n进入无法行动状态，每回合回复{int(skill.rate1)}技力点！"
            elif sid == 12:
                persistence = 1
                self.immobile = skill.persistence + 1
                for op in self.pm.all_ops_list:
                    objs_list.append(op)
                message += f"\n进入无法行动状态，每回合回复{int(skill.rate1)}技力点并使我方所有干员每回合恢复生命值！"
            elif sid in [15, 20, 22, 30, 39, 45, 50]:
                rate = random.uniform(skill.rate1, skill.rate2)
                is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(self.atk_p * rate + (self.atk_p * is_crit * self.crit_d_p))
                atk_type = 0
                atk_type_str = ""
                if sid in [15, 30, 45]:
                    atk_type_str = "物理"
                    atk_type = 0
                elif sid in [22, 39]:
                    atk_type_str = "法术"
                    atk_type = 1
                elif sid in [50]:
                    atk_type_str = "真实"
                    atk_type = 6
                elif sid in [20]:
                    atk_type_str = "治疗"
                    atk_type = 4

                if sid == 22:
                    self.pm.player_skill_count += int(skill.rate3)
                    message += f"\n回复{int(skill.rate3)}技力点！"
                elif sid == 45:
                    self.pm.player_skill_count += int(skill.rate3) * len(self.pm.all_enemies_list)
                    message += f"\n回复{int(skill.rate3)} * {len(self.pm.all_enemies_list)}技力点！"

                obj_list = self.pm.all_enemies_list if sid in [15, 22, 30, 39, 45, 50] else self.pm.all_ops_list
                for op in obj_list:
                    damage_amount = await op.hurt(self, atk_type, damage)
                    objs_list.append(op)
                    objs_name += f" {op.name}"
                    objs_damage += f" {damage_amount}"
                if sid in [15, 22, 30, 39, 45, 50]:
                    message += f"\n{is_crit_str}对{objs_name}\n分别造成了{objs_damage} 点{atk_type_str}伤害！"
                else:
                    message += f"\n分别为{objs_name}\n恢复了{objs_damage} 点生命值！"
            elif sid == 17:
                health_amount = await obj1.hurt(self, 4, int(self.atk_p * skill.rate1))
                message += f"\n恢复{obj1.name}{health_amount}点生命值！"
            elif sid == 18:
                persistence = 1
                message += f"\n攻击方式变为单体治疗，攻击力提高{round(skill.rate2 * 100, 1)}%！"
            elif sid == 19:
                persistence = 1
                self.immobile = skill.persistence + 1
                mock_ops = ""
                for op in self.pm.all_enemies_list:
                    if random.randint(1, 10000) < skill.rate1 * 10000:
                        op.mocking_obj = self
                        await op.append_effect(Effect("19-2", 18, skill.persistence, 0, 0, 0, 0))
                        await op.upgrade_effect()
                        mock_ops += f"{op.name} "

                message += f"\n防御力提高{round(skill.rate2 * 100, 1)}%并尝试嘲讽所有敌人！"
                message += f"\n{mock_ops} 被嘲讽了！"
            elif sid == 21:
                persistence = 1
                damage = await self.hurt(None, 6, int(self.health * skill.rate1))
                message += f"\n流失{damage}点生命值，攻击力提高{round(skill.rate2 * 100, 1)}%，速度提升{round(skill.rate3, 2)}点！"
            elif sid == 23:
                is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(self.atk_p * skill.rate1 + (self.atk_p * is_crit * self.crit_d_p))
                atk_type = self.atk_type_p
                atk_type_str = ""
                if atk_type == 0:
                    atk_type_str = "物理"
                elif atk_type == 3:
                    atk_type_str = "法术"
                if atk_type == 0:
                    damage = await obj1.hurt(self, atk_type, damage)
                    objs_list.append(obj1)
                    await obj1.upgrade_effect()
                    message += f"\n{is_crit_str}对{obj1.name}造成了{damage}点{atk_type_str}伤害！\n{obj1.name}被沉默了！"
                else:
                    for op in obj1.next_operators:
                        if not isinstance(op, Operator):
                            continue
                        damage_amount = await op.hurt(self, atk_type, damage)
                        objs_list.append(op)
                        await op.upgrade_effect()
                        objs_name += f" {op.name}"
                        objs_damage += f" {damage_amount}"
                    message += f"\n{is_crit_str}对{objs_name}\n分别造成了{objs_damage} 点{atk_type_str}伤害！\n{objs_name} 被沉默了！"
            elif sid == 24:
                persistence = 1
                message += f"\n攻击类型变为群体法术，攻击力提高{round(skill.rate2 * 100, 1)}%！"
            elif sid == 25:
                persistence = 1
                message += f"\n攻击类型变为群体法术，攻击力提高{round(skill.rate1 * 100, 1)}%，防御力提高{round(skill.rate2 * 100, 1)}%！"
            elif sid == 26:
                persistence = 1
                self.deathless = skill.persistence + 1
                message += f"\n攻击力提高{round(skill.rate1 * 100, 1)}%，进入不死状态！"
            elif sid == 27:
                persistence = 1
                message += f"\n防御力降低{int(skill.rate1)}，攻击力提高{round(skill.rate2 * 100, 1)}%！"
            elif sid == 29:
                is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(self.atk_p * skill.rate1 + (self.atk_p * is_crit * self.crit_d_p))
                obj_health = obj1.health
                await obj1.hurt(self, 0, damage)
                objs_list.append(obj1)
                obj1.speed -= skill.rate3
                if obj1.health < obj1.max_health_p * skill.rate2:
                    obj1.health = int(obj1.max_health_p * skill.rate2)
                message += f"\n{is_crit_str}对{obj1.name}造成了{obj_health - obj1.health}点物理伤害并使其速度减少{round(skill.rate3, 2)}！"
            elif sid in [31, 53]:
                rate = random.uniform(skill.rate1, skill.rate2)
                is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(self.atk_p * rate + (self.atk_p * is_crit * self.crit_d_p))
                atk_type = 0
                atk_type_str = ""
                if sid == 31:
                    atk_type = 2
                    atk_type_str = "物理"
                elif sid == 53:
                    atk_type = 3
                    atk_type_str = "法术"

                for op in obj1.next_operators:
                    if not isinstance(op, Operator):
                        continue
                    damage_amount = await op.hurt(self, atk_type, damage, skill.rate3, skill.rate3)

                    objs_list.append(op)
                    objs_name += f" {op.name}"
                    objs_damage += f" {damage_amount}"
                message += f"\n{is_crit_str}对{objs_name}\n分别造成了{objs_damage} 点{atk_type_str}伤害！"
            elif sid == 32:
                persistence = 1
                message += f"\n攻击类型变为群体法术，攻击力提高{round(skill.rate1 * 100, 1)}%但速度减少{round(skill.rate2, 2)}"
            elif sid == 33:
                health_amount = await obj1.hurt(self, 4,
                                                int((self.atk_p * skill.rate1) + (obj1.max_health_p * skill.rate2)))
                message += f"\n恢复{obj1.name}{health_amount}点生命值！"
            elif sid == 34:
                persistence = 1
                objs_list.append(self)
                objs_list.append(obj1)
                message += f"\n使自己和{obj1.name}攻击力提高{round(skill.rate2, 2) * 100}%但每回合流失{round(skill.rate1, 3) * 100}%当前生命值！"
            elif sid == 35:
                persistence = 1
                message += f"\n自身速度增加{round(skill.rate1, 2)}！"
            elif sid in [36, 38]:  # 减速类
                if sid == 36:
                    atk_type = 1
                    atk_type_str = "法术"
                else:
                    atk_type = 6
                    atk_type_str = "真实"
                is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(self.atk_p * skill.rate1 + (self.atk_p * is_crit * self.crit_d_p))
                damage = await obj1.hurt(self, atk_type, damage)
                objs_list.append(obj1)
                message += f"\n{is_crit_str}对{obj1.name}造成了{damage}点{atk_type_str}伤害！并使其速度减少{round(skill.rate2, 2)}，持续{int(skill.rate3)}回合！"
            elif sid == 37:
                is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(self.atk_p * skill.rate1 + (self.atk_p * is_crit * self.crit_d_p))
                damage = await obj1.hurt(self, 1, damage)
                health_amount = int(self.atk_p * skill.rate2)
                health_amount = await obj2.hurt(obj2, 4, health_amount)
                objs_list.append(obj1)
                message += f"\n{is_crit_str}对{obj1.name}造成了{damage}点法术伤害！并为{obj2.name}恢复{health_amount}点生命值！"
            elif sid == 40:
                if self.atk_type_p == 1:
                    atk_type_str = "法术"
                else:
                    atk_type_str = "真实"
                random_obj_list = random.choices(self.pm.all_enemies_list, k=int(skill.rate1))
                for op in random_obj_list:
                    is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                    is_crit_str: str = "★" if is_crit else ""
                    damage = int(self.atk_p * skill.rate2 + (self.atk_p * is_crit * self.crit_d_p))
                    damage_amount = await op.hurt(self, self.atk_type_p, damage)
                    objs_list.append(op)
                    message += f"\n对{op.name}造成{is_crit_str}{damage_amount}"
                message += f"\n点{atk_type_str}伤害！"
            elif sid == 41:
                persistence = 1
                self.skills_list[2] = await new_skill_instance(57, skill.level, False)
                message += f"\n攻击类型变为单体真实，生命值上限提高{round(skill.rate1 * 100, 1)}%，攻击力提高{round(skill.rate2 * 100, 1)}%"
            elif sid == 42:
                damage = int((self.atk_p * skill.rate1) + ((obj1.max_health_p - obj1.health) * skill.rate2))
                damage = await obj1.hurt(self, 6, damage)
                objs_list.append(obj1)
                message += f"\n对{obj1.name}造成了{damage}点真实伤害！"
            elif sid == 43:
                is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                is_crit_str: str = "暴击并" if is_crit else ""
                damage = int(self.atk_p * skill.rate1 + (self.atk_p * is_crit * self.crit_d_p))
                damage = await obj1.hurt(self, 1, damage)
                objs_list.append(obj1)
                self.pm.player_skill_count += int(skill.rate2)
                message += f"\n{is_crit_str}对{obj1.name}造成了{damage}点法术伤害！使其每回合流失{round(skill.rate3, 3) * 100}%当前生命值并回复{int(skill.rate2)}技力点！"
            elif sid == 44:
                persistence = 1
                self.hidden = skill.persistence + 1
                message += f"\n攻击力提高{round(skill.rate1 * 100, 1)}%，进入隐匿状态！"
            elif sid == 46:
                persistence = 1
                message += f"\n攻击力和防御力提高{round(skill.rate1 * 100, 1)}%，暴击率增加{round(skill.rate2 * 100, 2)}%！"
                await self.upgrade_effect()
                damage_str = ""
                for i in range(3):
                    is_crit: bool = random.randint(1, 10000) <= (self.crit_r_p + skill.rate2) * 10000  # 是否暴击
                    is_crit_sym: str = "★" if is_crit else ""
                    damage = int((self.atk * (1 + self.atk_add_f + skill.rate1) + self.atk_add_d) + (
                            self.atk_p * is_crit * self.crit_d_p))
                    damage = await obj1.hurt(self, 1, damage)
                    damage_str += f"{damage}{is_crit_sym}+"
                damage_str = damage_str.rstrip("+")  # 去掉末尾的+号
                objs_list.append(obj1)
                message += f"\n并对{obj1.name}造成了{damage_str}点物理伤害！"
            elif sid == 47:
                persistence = 1
                mock_ops = ""
                for op in self.pm.all_enemies_list:
                    if random.randint(1, 10000) < skill.rate1 * 10000:
                        op.mocking_obj = self
                        await op.append_effect(Effect("47-3", 18, skill.persistence, 0, 0, 0, 0))
                        await op.upgrade_effect()
                        mock_ops += f"{op.name} "

                message += f"\n进入忍耐状态，防御力提高{round(skill.rate2 * 100, 1)}%并尝试嘲讽所有敌人！"
                message += f"\n{mock_ops} 被嘲讽了！"
            elif sid == 48:
                damage1 = int(self.atk_p * skill.rate1)  # 物理伤害
                damage2 = int(self.atk_p * skill.rate2)  # 真实伤害
                for op in self.pm.all_enemies_list:
                    damage_amount1 = await op.hurt(self, 2, damage1)
                    damage_amount2 = await op.hurt(self, 7, damage2)
                    objs_list.append(op)
                    objs_name += f" {op.name}"
                    objs_damage += f" {damage_amount1}+{damage_amount2}"
                message += f"\n对{objs_name}\n分别造成了{objs_damage} 点伤害！"
            elif sid == 49:
                persistence = 0
                message += f"\n攻击力提高{round(skill.rate1 * 100, 1)}%，速度增加{round(skill.rate2, 2)}！"
            elif sid == 51:
                persistence = 1
                message += f"\n伤害类型变为真实单体，攻击力提高{round(skill.rate1 * 100, 1)}%，防御力提高{round(skill.rate2 * 100, 1)}%！"
            elif sid == 52:
                persistence = 1
                message += f"\n攻击力提高{round(skill.rate1 * 100, 1)}%，防御力降低{round(skill.rate2 * 100, 1)}%，每回合恢复{round(skill.rate3 * 100, 2)}%最大生命值！"
            elif sid == 54:
                persistence = 0
                health_amount = int(self.max_health_p - self.health)
                await self.hurt(self, 4, health_amount)
                message += f"\n攻击力提高{round(skill.rate1 * 100, 1)}%，生命上限提高{round(skill.rate2 * 100, 1)}%，每回合流失{round(skill.rate3 * 100, 2)}%最大生命值！"
            elif sid == 55:
                persistence = 1
                message += f"\n防御力提高{round(skill.rate1 * 100, 1)}%，速度减少{round(skill.rate3, 2)}点，每回合恢复{round(skill.rate2 * 100, 2)}%最大生命值！"
            elif sid == 56:
                persistence = 1
                message += f"\n伤害类型变为群体物理，攻击力提高{round(skill.rate2 * 100, 1)}%，防御力降低{round(skill.rate1 * 100, 1)}%！"
            elif sid == 57:
                persistence = 0
                self.effect_list.clear()  # 清空效果列表
                await self.upgrade_effect()  # 更新干员属性
                for i in range(int(skill.rate1)):
                    atk_obj = self.pm.all_enemies_list[0]
                    for op in self.pm.all_enemies_list:
                        if atk_obj.health <= 0:  # 寻找血量大于0且血量最少的敌人
                            atk_obj = op
                            continue
                        if atk_obj.health > op.health > 0:  # 寻找血量大于0且血量最少的敌人
                            atk_obj = op
                    is_crit: bool = random.randint(1, 10000) <= self.crit_r_p * 10000  # 是否暴击
                    is_crit_str: str = "★" if is_crit else ""
                    damage = int(self.atk_p * skill.rate2 + (self.atk_p * is_crit * self.crit_d_p))
                    damage = await atk_obj.hurt(self, 1, damage)
                    objs_list.append(atk_obj)
                    message += f"\n对{atk_obj.name}造成{is_crit_str}{damage}"
                message += f"\n点法术伤害！"

        skill.count = int(skill.persistence) + persistence
        sub_effect_list: list[Effect] = []
        obj_effect_list: list[Effect] = []
        for e in skill.effect_list:
            if e.obj_type == 0:
                sub_effect_list.append(e)
            else:
                obj_effect_list.append(e)

        # 要用deepcopy来创建新的Effect类对象，不然效果之间会互相影响
        # 给行动者加buff
        await self.append_effect_list(copy.deepcopy(sub_effect_list))
        objs_list = list(set(objs_list))  # 除去列表里的相同元素

        # 给目标加buff(顺便判断目标是否被击倒)
        for op in objs_list:
            if await op.is_die():  # 如果目标被击倒
                message += f"\n{op.name}被击倒了！"
                await op.op_die()
            else:
                # 要用deepcopy来创建新的Effect类对象，不然效果之间会互相影响
                await op.append_effect_list(copy.deepcopy(obj_effect_list))
                await op.upgrade_effect()
        return message


async def new_instance(oid: int, level: int, skills_level: list[int], pm=None, is_enemy: bool = False) -> Operator:
    """
    通过传入的干员id、干员等级以及干员技能等级列表生成一个干员实例

    :param oid: 干员id，详情见operators_data.json文件
    :param level: 干员等级
    :param skills_level: 干员技能等级列表
    :param pm: 战斗数据
    :param is_enemy: 是否是敌人，默认为False
    :return: 返回一个干员实例
    """
    name = await get_op_attribute(oid, OPAttribute.name, is_enemy)
    stars = await get_op_attribute(oid, OPAttribute.stars, is_enemy)
    profession = await get_op_attribute(oid, OPAttribute.profession, is_enemy)
    health = int(await get_op_attribute(oid, OPAttribute.health, is_enemy) +
                 await get_op_attribute(oid, OPAttribute.health_plus, is_enemy) * (level - 1))
    atk = int(await get_op_attribute(oid, OPAttribute.atk, is_enemy) +
              await get_op_attribute(oid, OPAttribute.atk_plus, is_enemy) * (level - 1))
    defence = int(await get_op_attribute(oid, OPAttribute.defence, is_enemy) +
                  await get_op_attribute(oid, OPAttribute.defence_plus, is_enemy) * (level - 1))
    res = (await get_op_attribute(oid, OPAttribute.res, is_enemy) +
           await get_op_attribute(oid, OPAttribute.res_plus, is_enemy) * (level - 1))
    crit_r = (await get_op_attribute(oid, OPAttribute.crit_r, is_enemy) +
              await get_op_attribute(oid, OPAttribute.crit_r_plus, is_enemy) * (level - 1))
    crit_d = (await get_op_attribute(oid, OPAttribute.crit_d, is_enemy) +
              await get_op_attribute(oid, OPAttribute.crit_d_plus, is_enemy) * (level - 1))
    speed = (await get_op_attribute(oid, OPAttribute.speed, is_enemy) +
             await get_op_attribute(oid, OPAttribute.speed_plus, is_enemy) * (level - 1))
    atk_type = await get_op_attribute(oid, OPAttribute.atk_type, is_enemy)
    sid_list = await get_op_attribute(oid, OPAttribute.skills, is_enemy)
    skills_list: list[Skill] = await get_skills_list(sid_list, skills_level, is_enemy)
    effect_dict_list = await get_op_attribute(oid, OPAttribute.effect_list, is_enemy)
    effect_list: list[Effect] = []
    for e_dict in effect_dict_list:
        effect_list.append(await new_effect_instance(e_dict))

    return Operator(oid, name, level, stars, profession, health, atk, defence, res, crit_r, crit_d, speed, atk_type,
                    skills_list, effect_list, pm, is_enemy)


async def get_operator_list(uid: str or int, pm=None) -> list[Operator]:
    """
    通过传入的用户id，返回该用户当前出战干员的列表

    :param uid: 用户id
    :param pm: 战斗数据
    :return: 返回用户当前出战干员的列表
    """
    playing_ops_dict = await get_user_playing_ops(uid)
    playing_ops_list: list[Operator] = []

    for op in playing_ops_dict:
        oid = playing_ops_dict[op]["oid"]
        level = playing_ops_dict[op]["level"]
        skills_level = playing_ops_dict[op]["skills_level"]  # [0,1,1]
        op_instance = await new_instance(oid, level, skills_level, pm)
        playing_ops_list.append(op_instance)

    return playing_ops_list


async def get_enemies_list(mid: str, pm=None) -> list[Operator]:
    """
    通过传入的地图id，返回地图敌人列表

    :param mid: 地图id
    :param pm: 战斗数据
    :return: 返回地图中的敌人列表
    """
    map_enemies_data_list = await get_map_attribute(mid, MapAttribute.enemies)
    map_enemies_list: list[Operator] = []

    for i in range(len(map_enemies_data_list[0])):
        op_instance = await new_instance(map_enemies_data_list[0][i], map_enemies_data_list[1][i], [0, 0, 0], pm, True)
        map_enemies_list.append(op_instance)

    return map_enemies_list
