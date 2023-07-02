# -*- coding = utf-8 -*-
# @File:reboot.py
# @Author:Hycer_Lance
# @Time:2023/7/2 22:12
# @Software:PyCharm

from nonebot import on_command
from nonebot.permission import SUPERUSER

import sys
import subprocess

from ..Help.PluginInfo import PluginInfo

reboot_comm = on_command("reboot", aliases={"重启bot", "重启"}, block=True, priority=1, permission=SUPERUSER)

__plugin_info__ = PluginInfo(
    plugin_name="Reboot",
    name="Reboot",
    description="重启bot",
    usage="reboot ——重启bot",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 1,
        "permission": "SUPERUSER"
    }
)


def restart_program():
    # 关闭当前的Python进程
    python = sys.executable
    subprocess.call([python] + sys.argv)


@reboot_comm.handle()
async def reboot():
    await reboot_comm.send("正在重启...")
    restart_program()
    await reboot_comm.send("重启成功")
