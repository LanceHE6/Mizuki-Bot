# -*- coding = utf-8 -*-
# @File:skill.py
# @Author:Hycer_Lance
# @Time:2023/4/27 17:00
# @Software:PyCharm

from .player import user_data


async def new_instance(skill: dict):
    return Skill(skill["type"], skill["level"], skill["is_using"])


class Skill:
    def __init__(self, skill_type: int, level: int, is_using: bool):
        self.name = ""
        self.max_rate = 0
        self.min_rate = 0
        self.skill_type = skill_type
        self.level = level
        self.is_using = is_using
        await self.init_type(skill_type, level)

    async def init_type(self, skill_type: int, level: int):
        if skill_type == 1:
            self.name = "技能1"
            self.min_rate = 10 + 1 * level
            self.max_rate = 20 + 2 * level
        elif skill_type == 2:
            self.name = "技能2"
            self.min_rate = 10 + 1 * level
            self.max_rate = 20 + 2 * level
        elif skill_type == 3:
            self.name = "技能3"
            self.min_rate = 10 + 1 * level
            self.max_rate = 20 + 2 * level

