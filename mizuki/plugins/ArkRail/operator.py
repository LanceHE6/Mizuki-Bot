# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:55
# @Software:PyCharm
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
                 atk_type: int, skills_list: list[Skill], effect_list: list[Effect], is_enemy: bool):
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
                    if (damage * ((100 - res) / 100) > damage * 0.2) \
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
                stage_2 = await new_instance(int(e.effect_degree), self.level, [0, 0, 0], self.is_enemy)
                await self.obj_cpy(stage_2)  # 更新干员属性
                return False
        return True

    async def finish_turn(self):
        """
        干员结束当前回合时需要执行的函数
        """
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

        # 将技能移出列表
        for f_e in finish_effect_list:
            self.effect_list.remove(f_e)

        await self.upgrade_effect()

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
                if self.effect_list[i].effect_type == 18:  # 嘲讽效果值同时存在一个
                    self.effect_list[i] = e
                    return

        elif e.effect_type == 26:
            for i in range(len(self.effect_list)):
                if self.effect_list[i].effect_type == 24:  # 冻结效果延长持续时间
                    self.effect_list[i].persistence += 1
                    return
                elif self.effect_list[i].effect_type == 26:  # 寒冷效果叠加变为冻结
                    await self.append_effect(Effect(e.effect_id, 24, 1, 0, 0, 0, 0))
                    self.effect_list.remove(self.effect_list[i])
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


async def new_instance(oid: int, level: int, skills_level: list[int], is_enemy: bool = False) -> Operator:
    """
    通过传入的干员id、干员等级以及干员技能等级列表生成一个干员实例

    :param oid: 干员id，详情见operators_data.json文件
    :param level: 干员等级
    :param skills_level: 干员技能等级列表
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
                    skills_list, effect_list, is_enemy)


async def get_operator_list(uid: str or int) -> list[Operator]:
    """
    通过传入的用户id，返回该用户当前出战干员的列表

    :param uid: 用户id
    :return: 返回用户当前出战干员的列表
    """
    playing_ops_dict = await get_user_playing_ops(uid)
    playing_ops_list: list[Operator] = []

    for op in playing_ops_dict:
        oid = playing_ops_dict[op]["oid"]
        level = playing_ops_dict[op]["level"]
        skills_level = playing_ops_dict[op]["skills_level"]  # [0,1,1]
        op_instance = await new_instance(oid, level, skills_level)
        playing_ops_list.append(op_instance)

    return playing_ops_list


async def get_enemies_list(mid: str) -> list[Operator]:
    """
    通过传入的地图id，返回地图敌人列表

    :param mid: 地图id
    :return: 返回地图中的敌人列表
    """
    map_enemies_data_list = await get_map_attribute(mid, MapAttribute.enemies)
    map_enemies_list: list[Operator] = []

    for i in range(len(map_enemies_data_list[0])):
        op_instance = await new_instance(map_enemies_data_list[0][i], map_enemies_data_list[1][i], [0, 0, 0], True)
        map_enemies_list.append(op_instance)

    return map_enemies_list
