# -*- coding = utf-8 -*-
# @File:reboot.py
# @Author:Hycer_Lance
# @Time:2023/7/2 22:12
# @Software:PyCharm

from pathlib import Path
from nonebot import on_command, get_bot
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent

import sys
import asyncio
import json
import os
import time

from ..Help.PluginInfo import PluginInfo

boot_data_path = Path() / 'mizuki' / 'plugins' / 'BotManage' / 'boot_data'

reboot_comm = on_command("reboot", aliases={"重启bot", "重启"}, block=True, priority=1, permission=SUPERUSER)

__plugin_info__ = PluginInfo(
    plugin_name="Reboot",
    name="Reboot",
    description="重启bot",
    usage="reboot ——重启bot",
    extra={
        "author": "Hycer_Lance",
        "version": "1.0.0",
        "priority": 1,
        "permission": "SUPERUSER"
    }
)


def restart_bot():
    os.system(f"{sys.executable} {os.getcwd()}\\mizuki\\plugins\\BotManage\\boot_script.py")


def write_boot_data():
    """
    写入启动数据
    :return: None
    """
    if not os.path.exists(boot_data_path):
        os.mkdir(boot_data_path)
    with open(boot_data_path / 'boot_data.json', 'r', encoding='utf-8') as data:
        boot_data = json.load(data)
        data.close()
    cwd = os.getcwd()
    boot_data["cwd"] = cwd
    boot_data["boot_time"] = int(time.time())
    with open(boot_data_path / 'boot_data.json', 'w', encoding='utf-8') as data:
        json.dump(boot_data, data, indent=4)


async def check_boot_data():
    await asyncio.sleep(10)
    with open(boot_data_path / 'boot_data.json', 'r', encoding='utf-8') as data:
        boot_data = json.load(data)
        data.close()
    if not boot_data["reply"]:
        bot = get_bot()
        if boot_data["gid"] == '':
            await bot.send_private_msg(message="重启完成", user_id=boot_data["uid"])
        else:
            await bot.send_group_msg(message="重启完成", user_id=boot_data["uid"], group_id=boot_data["gid"])


write_boot_data()


@reboot_comm.handle()
async def reboot(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    else:
        gid = ''
    uid = event.get_user_id()
    with open(boot_data_path / 'boot_data.json', 'r', encoding='utf-8') as data:
        boot_data = json.load(data)
        data.close()
    boot_data["gid"] = gid
    boot_data["uid"] = uid
    with open(boot_data_path / 'boot_data.json', 'w', encoding='utf-8') as data:
        json.dump(boot_data, data, indent=4)

    await reboot_comm.send("正在重启...")
    restart_bot()
    await reboot_comm.send("重启成功")
