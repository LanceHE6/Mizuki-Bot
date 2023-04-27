# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:55
# @Software:PyCharm

from pathlib import Path
import json

user_data = Path() / 'mizuki' / 'plugins' / 'test' / 'user_data.json'


async def new_instance(uid: str | int):
    with open(user_data, 'r', encoding='utf-8') as data:
        user = json.load(data)
        data.close()
    player_level: int = user[uid]["level"]
    player_name: str = user[uid]["name"]
    player_skills: dict = user[uid]["skills"]["1"]
    return Player(player_level, player_name)


class Player:

    def __init__(self, level: int, name: str, skills: dict):
        self.player_name = name
        self.max_health = 100 + 2 * level
        self.health = self.max_health
        self.attack = 40 + 2 * level
        self.defence = 20 + 1 * level
        self.critical_rate = 10 + 1 * level
        self.critical_damage = 50 + 5 * level
        self.player_skills = skills
        pass
