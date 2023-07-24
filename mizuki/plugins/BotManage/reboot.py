# -*- coding = utf-8 -*-
# @File:reboot.py
# @Author:Hycer_Lance
# @Time:2023/7/2 22:12
# @Software:PyCharm

from pathlib import Path
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, Bot
from nonebot import get_app, get_driver

import sys
import json
import os
import time
import contextlib

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
        "version": "2.0.0",
        "priority": 1,
        "permission": "SUPERUSER"
    }
)


async def restart_bot():
    """
    重启进程
    :return: None
    """
    with contextlib.suppress(Exception):
        await get_app().router.shutdown()
    reboot_arg = (
        [sys.executable] + sys.argv
        if sys.argv[0].endswith('.py')
        else [sys.executable, 'bot.py']
    )
    os.execv(sys.executable, reboot_arg)


def write_boot_data():
    """
    每次启动bot写入启动数据
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


write_boot_data()

driver = get_driver()


@driver.on_bot_connect
async def check_boot_data(bot: Bot):
    """
    在bot连接上后检查启动数据
    :param bot: Bot对象
    :return: None
    """
    with open(boot_data_path / 'boot_data.json', 'r', encoding='utf-8') as data:
        boot_data = json.load(data)
        data.close()
    if boot_data["replied"] == 0:
        if boot_data["gid"] == '':
            await bot.send_private_msg(message="重启完成", user_id=boot_data["uid"])
        else:
            await bot.send_group_msg(message="重启完成", group_id=boot_data["gid"])
    boot_data["replied"] = 1
    with open(boot_data_path / 'boot_data.json', 'w', encoding='utf-8') as data:
        json.dump(boot_data, data, indent=4)
        data.close()

@reboot_comm.handle()
async def reboot(event: MessageEvent):
    # 写入启动数据中
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    else:
        gid = ''
    uid = event.get_user_id()
    with open(boot_data_path / 'boot_data.json', 'r', encoding='utf-8') as data:
        boot_data = json.load(data)
        data.close()
    boot_data["replied"] = 0  # 打上回复状态标签
    boot_data["gid"] = gid
    boot_data["uid"] = uid
    with open(boot_data_path / 'boot_data.json', 'w', encoding='utf-8') as data:
        json.dump(boot_data, data, indent=4)

    await reboot_comm.send("正在重启...")
    await restart_bot()
