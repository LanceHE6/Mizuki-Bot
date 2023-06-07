# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Silence
# @Time:2023/6/6 19:47
# @Software:PyCharm

class Effect:

    def __init__(self, effect_id: str, persistence: int, effect_type: int, effect_degree: float, effect_level: int = 0, max_level: int = 0):
        """
        :param effect_id: 效果id(唯一标识符)
        :param persistence: 效果持续时间(为负数时持续时间无限)
        :param effect_type: 效果种类
        :param effect_degree: 效果强度(可为负数)
        :param effect_level: 效果层数(攻击类型)
        :param max_level: 最大层数

        效果种类:
        数值类
        0: 攻击力百分比加成  1: 防御力百分比加成  2: 最大生命值百分比加成  3: 法抗百分比加成
        4: 攻击力数值加成  5: 防御力数值加成  6: 最大生命值数值加成  7: 法抗数值加成
        8: 暴击率数值加成  9: 暴击伤害数值加成  10: 速度数值加成
        注:百分比加成用"提升/提高"，数值加成用"增加"

        特殊类
        11: 忍耐(每次被攻击到时自身攻击力提升)
        12: 复活(复活后进入第二阶段，第二阶段id存放在effect_level中)
        13: 攻击类型变化(类型存放在effect_level中)
        14: 生命持续恢复
        15: 屏障(防御力提升，每次受到伤害防御力提升幅度减少)
        16: 愤怒(攻击力提升，每次进行攻击时攻击力额外提升)
        """
        self.effect_id = effect_id
        self.persistence = persistence
        self.effect_type = effect_type
        self.effect_degree = effect_degree
        self.effect_level = effect_level
        self.max_level = max_level

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
            self.name = "生命恢复"
        elif e_t == 12:
            self.name = "屏障"
        elif e_t == 13:
            self.name = "愤怒"
