# -*- coding = utf-8 -*-
# @File:pool_config.json.py
# @Author:Hycer_Lance
# @Time:2023/5/8 20:08
# @Software:PyCharm

import json
from pathlib import Path

config = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'data' / 'pool_config.json'
class Pool:
    """卡池配置"""
    def __init__(self):
        with open(config, 'r', encoding='utf-8') as file:
          all_config = json.load(file)
          file.close()
        self.stars_values_lmc = all_config["stars_values_lmc"]
        self.up_6s = all_config["up_6s"]
        self.up_5s = all_config["up_5s"]
        self.prob_improvement = all_config["prob_improvement"]

    async def change_up_6s(self, new_up: list):
        """更改6星up"""
        self.up_6s = new_up
        with open(config, 'r', encoding='utf-8') as file:
          all_config = json.load(file)
          file.close()
        all_config["up_6s"] = self.up_6s
        with open(config, 'w', encoding='utf-8') as file:
          json.dump(all_config, file)


    async def change_up_5s(self, new_up: list):
        """更改5星up"""
        self.up_5s = new_up
        with open(config, 'r', encoding='utf-8') as file:
          all_config = json.load(file)
          file.close()
        all_config["up_5s"] = self.up_5s
        with open(config, 'w', encoding='utf-8') as file:
          json.dump(all_config, file)


    async def change_prob_improvement(self, new_times: int):
        """概率提升的抽数"""
        self.prob_improvement = new_times
        with open(config, 'r', encoding='utf-8') as file:
          all_config = json.load(file)
          file.close()
        all_config["prob_improvement"] = self.prob_improvement
        with open(config, 'w', encoding='utf-8') as file:
          json.dump(all_config, file)

PoolConfig = Pool()