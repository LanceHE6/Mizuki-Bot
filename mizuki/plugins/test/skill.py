# -*- coding = utf-8 -*-
# @File:skill.py
# @Author:Hycer_Lance
# @Time:2023/4/27 17:00
# @Software:PyCharm

from .player import user_data
import json


async def new_instance_list(uid: str | int):
    with open(user_data, 'r', encoding='utf-8') as data:
        user = json.load(data)
        data.close()
        try:
            skills = user[f"{uid}"]["skills"]
        except KeyError:
            player_skills: dict = {
                "1": {
                    "type": 1,
                    "level": 1,
                    "is_using": 1
                }
            }
            user[f"{uid}"]["skills"] = player_skills
            skill_list = []
        for i in range(len(player_skills)):
            s = skills[f"{i}"]
            skill_list.append(new_instance(s))

    return Skill(skills["type"], skills["level"], skills["is_using"])


async def new_instance(skill: dict):
    return Skill(skill["type"], skill["level"], skill["is_using"])


class Skill:
    def __init__(self, skill_type: int, level: int, is_using: bool):
        self.skill_info = "暂无介绍"
        self.skill_name = "无"
        self.max_rate = 0
        self.min_rate = 0
        self.skill_type = skill_type
        self.skill_level = level
        self.is_using = is_using
        await self.init_type(skill_type, level)

    async def init_type(self, skill_type: int, level: int):
        if skill_type == 1:
            self.skill_name = "强力击"
            self.min_rate = 200 + 5 * level
            self.max_rate = 220 + 6 * level
            self.skill_info = f"对对手造成相当于自身攻击力{self.min_rate}%~{self.max_rate}%的伤害"
        elif skill_type == 2:
            self.skill_name = "防御力增强"
            self.min_rate = self.max_rate = 80 + 4 * level
            self.skill_info = f"使自身防御力提高{self.min_rate}%"
        elif skill_type == 3:
            self.skill_name = "急救"
            self.min_rate = 100 + 5 * level
            self.max_rate = 120 + 6 * level
            self.skill_info = f"立即回复相当于自身攻击力{self.min_rate}%~{self.max_rate}%的生命值"

    async def get_info(self) -> dict:
        skill_info = {
            "name": self.skill_name,
            "level": self.skill_level,
            "skill_info": self.skill_info,
        }
        return skill_info

