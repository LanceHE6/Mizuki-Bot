# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Silence
# @Time:2023/6/6 19:47
# @Software:PyCharm

class Effect:

    def __init__(self, effect_id: str, effect_type: int, persistence: int, effect_degree: float, effect_level: int,
                 max_level: int, obj_type: int):
        """
        :param effect_id: 效果id(唯一标识符)
        :param effect_type: 效果种类
        :param persistence: 效果持续时间(为负数时持续时间无限)
        :param effect_degree: 效果强度(可为负数)
        :param effect_level: 效果层数(攻击类型)
        :param max_level: 最大层数
        :param obj_type: 目标类型(0为我方, 1为敌方)

        效果种类:
        数值类
        0: 攻击力百分比加成  1: 防御力百分比加成  2: 最大生命值百分比加成  3: 法抗百分比加成
        4: 攻击力数值加成  5: 防御力数值加成  6: 最大生命值数值加成  7: 法抗数值加成
        8: 暴击率数值加成  9: 暴击伤害数值加成  10: 速度数值加成
        注:百分比加成用"提升/提高"，数值加成用"增加"

        特殊数值类
        11: 忍耐(每次被攻击到时自身攻击力提升)
        12: 复活(复活后进入第二阶段，第二阶段id存放在effect_degree中)
        13: 攻击类型变化(类型存放在effect_degree中)
        14: 恢复(每回合恢复最大生命值)(可为负数，负数时流血)
        15: 屏障(防御力提升，每次受到伤害防御力提升幅度减少)
        16: 愤怒(攻击力提升，每次进行攻击时攻击力额外提升)
        17: 流血(每回合流失当前生命值)

        特殊类
        18: 嘲讽(嘲讽对象必须为选中目标)
        19: 隐匿(无法被选中)
        20: 不死(血量不会小于1)
        21: 无敌(免疫所有伤害)
        22: 沉默(无法使用技能)
        23: 眩晕(无法行动)
        24: 冻结(无法行动)
        25: 死战(持续时间结束后血量清空)
        """
        self.effect_id = effect_id
        self.effect_type = effect_type
        self.persistence = persistence
        self.effect_degree = effect_degree
        self.effect_level = effect_level
        self.max_level = max_level
        self.obj_type = obj_type

        e_t = self.effect_type
        self.name = ""
        if e_t == 0:
            self.name = "攻击力加成"
        elif e_t == 1:
            self.name = "防御力加成"
        elif e_t == 2:
            self.name = "最大生命值加成"
        elif e_t == 3:
            self.name = "法抗加成"
        elif e_t == 4:
            self.name = "攻击力增加"
        elif e_t == 5:
            self.name = "防御力增加"
        elif e_t == 6:
            self.name = "最大生命值增加"
        elif e_t == 7:
            self.name = "法抗增加"
        elif e_t == 8:
            self.name = "暴击率增加"
        elif e_t == 9:
            self.name = "暴击伤害增加"
        elif e_t == 10:
            self.name = "速度增加"
        elif e_t == 11:
            self.name = "忍耐"
        elif e_t == 12:
            self.name = "复活"
        elif e_t == 13:
            self.name = "攻击类型改变"
        elif e_t == 14:
            self.name = "恢复"
        elif e_t == 15:
            self.name = "屏障"
        elif e_t == 16:
            self.name = "愤怒"
        elif e_t == 17:
            self.name = "流血"
        elif e_t == 18:
            self.name = "嘲讽"
        elif e_t == 19:
            self.name = "隐匿"
        elif e_t == 20:
            self.name = "不死"
        elif e_t == 21:
            self.name = "无敌"
        elif e_t == 22:
            self.name = "沉默"
        elif e_t == 23:
            self.name = "眩晕"
        elif e_t == 24:
            self.name = "冻结"
        elif e_t == 25:
            self.name = "死战"


async def new_effect_instance(effect_dict: dict):
    return Effect(effect_dict["e_id"], int(effect_dict["e_t"]), eval(effect_dict["e_p"]), float(effect_dict["e_d"]),
                  int(effect_dict["e_l"]), int(effect_dict["e_ml"]), int(effect_dict["obj_type"]))
