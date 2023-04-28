# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:55
# @Software:PyCharm

from pathlib import Path
import json

user_data = Path() / 'mizuki' / 'plugins' / 'test' / 'user_data.json'


async def new_instance(uid: str or int):
    with open(user_data, 'r', encoding='utf-8') as data:
        user = json.load(data)
        data.close()
    try:
        player_level: int = user[f"{uid}"]["level"]
        player_name: str = user[f"{uid}"]["name"]
        player_skills: dict = user[f"{uid}"]["skills"]
    except KeyError:
        player_level: int = 0
        player_name: str = ''
        player_skills: dict = {
            "1": {
                "type": 1,
                "level": 1,
                "is_using": 1
            }
        }
        user[f"{uid}"] = {
            "name": player_name,
            "level": player_level,
            "skills": player_skills
        }
        with open(user_data, 'w', encoding='utf-8') as data:
            json.dump(user, data)
            data.close()

    return Player(player_level, player_name, player_skills)


class Player:

    def __init__(self, level: int, name: str, skills: dict):
        self.player_name = name
        self.player_level = level
        self.max_health = 2000 + 30 * level
        self.health = self.max_health
        self.attack = 200 + 4 * level
        self.defence = 150 + 3 * level
        self.critical_rate = 10 + int(level / 10)
        self.critical_damage = 50 + level
        self.player_skills = skills

    async def get_info(self) -> dict:
        player_info = {
            "name": self.player_name,
            "level": self.player_level,
            "max_health": self.max_health,
            "attack": self.attack,
            "defence": self.defence,
            "crit_rate": self.critical_rate,
            "crit_damage": self.critical_damage
        }
        return player_info
