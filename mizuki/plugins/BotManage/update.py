# -*- coding = utf-8 -*-
# @File:update.py 
# @Author:Hycer_Lance
# @Time:2023/7/2 22:33
# @Software:PyCharm

from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageEvent

from ..Help.PluginInfo import PluginInfo
from .reboot import reboot

import subprocess

update_comm = on_command("update", aliases={"更新bot", "更新"}, block=True, priority=1, permission=SUPERUSER)

__plugin_info__ = PluginInfo(
    plugin_name="Update_bot",
    name="Update_bot",
    description="更新bot",
    usage="update ——更新bot",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 1,
        "permission": "SUPERUSER"
    }
)


@update_comm.handle()
async def update(event: MessageEvent):
    await update_comm.send("正在从GitHub获取更新...")
    # 执行 git pull 命令拉取最新代码
    try:
        output = subprocess.check_output('git pull', shell=True,
                                         stderr=subprocess.STDOUT, encoding='utf-8').replace('\n', '')
        if output == "Already up to date.":
            await update_comm.finish("当前bot已是最新版本")
        log_output = subprocess.check_output('git log -3 --pretty=format:"%s (%an)"', shell=True,
                                             stderr=subprocess.STDOUT, encoding='utf-8')
        print(log_output)
        await update_comm.send('bot已成功更新！\n\n更新日志：\n' + log_output)
    except subprocess.CalledProcessError as e:
        await update_comm.send(f'项目更新失败：{e.output}')
    await reboot(event)
