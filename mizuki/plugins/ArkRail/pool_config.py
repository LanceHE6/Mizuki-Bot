# -*- coding = utf-8 -*-
# @File:pool_config.json.py
# @Author:Hycer_Lance
# @Time:2023/5/8 20:08
# @Software:PyCharm

import json
from .DB import get_op_attribute, OPAttribute
from pathlib import Path
from nonebot.permission import SUPERUSER
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

config = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'data' / 'pool_config.json'

change_up_6s_comm = on_command("修改up6星", aliases={"更改up6星", "up6星设置"}, block=True, priority=3, permission=SUPERUSER)
change_up_5s_comm = on_command("修改up5星", aliases={"更改up5星", "up5星设置"}, block=True, priority=3, permission=SUPERUSER)


# change_prob_improvement = on_command("")
class Pool:
    """卡池配置"""

    def __init__(self):
        with open(config, 'r', encoding='utf-8') as file:
            all_config = json.load(file)
            file.close()
        self.stars_values_lmc = all_config["stars_values_lmc"]
        self.up_6s: list = all_config["up_6s"]
        self.up_5s: list = all_config["up_5s"]
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


@change_up_6s_comm.handle()
async def _(args: Message = CommandArg()):
    """修改up6星 管理员发送的参数为up6星oid的列表"""
    try:
        up_list = eval(args.extract_plain_text().replace(' ', ''))  # 获取命令后面跟着的纯文本内容
        if len(up_list) > 2:
            await change_up_6s_comm.finish("超过最大up6星数量")
    except NameError:
        up_list = None
        await change_up_6s_comm.finish("非法指令格式，请在指令后跟up6星oid的列表")
    await PoolConfig.change_up_6s(up_list)
    reply = f"当前up6星已改为"
    for oid in up_list:
        name = await get_op_attribute(oid, OPAttribute.name)
        reply += ' ' + name
    await change_up_6s_comm.finish(reply)


@change_up_5s_comm.handle()
async def _(args: Message = CommandArg()):
    """修改up6星 管理员发送的参数为up5星oid的列表"""
    try:
        up_list = eval(args.extract_plain_text().replace(' ', ''))  # 获取命令后面跟着的纯文本内容
        if len(up_list) > 3:
            await change_up_6s_comm.finish("超过最大up5星数量")
    except NameError:
        up_list = None
        await change_up_5s_comm.finish("非法指令格式，请在指令后跟up5星oid的列表")
    await PoolConfig.change_up_5s(up_list)
    reply = f"当前up5星已改为"
    for oid in up_list:
        name = await get_op_attribute(oid, OPAttribute.name)
        reply += ' ' + name
    await change_up_5s_comm.finish(reply)
