# -*- coding = utf-8 -*-
# @File:update.py 
# @Author:Hycer_Lance
# @Time:2023/7/2 22:33
# @Software:PyCharm

from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.log import logger

from ..Help.PluginInfo import PluginInfo
from .reboot import reboot

import subprocess
import os
from colorama import Fore
from pathlib import Path

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
async def _(event: MessageEvent):
    await update_comm.send("正在从GitHub获取更新...")
    logger.info(Fore.BLUE + "Mizuki更新 开始从Github获取更新")
    # 执行 git pull 命令拉取最新代码
    try:
        output = subprocess.check_output('git pull', shell=True,
                                         stderr=subprocess.STDOUT, encoding='utf-8').replace('\n', '')
        if output == "Already up to date.":
            await update_comm.finish("当前bot已是最新版本")
        if 'timeout' in output or 'unable to access' in output:
            msg = '更新失败，连接git仓库超时。'
            await update_comm.finish(msg)
        elif ' Your local changes' in output:
            msg = f'更新失败，本地修改过文件导致冲突，请解决冲突后再更新。\n{output}'
            await update_comm.finish(msg)
        log_output = subprocess.check_output('git log -3 --pretty=format:"%s (%an)"', shell=True,
                                             stderr=subprocess.STDOUT, encoding='utf-8')
        print(log_output)

        # 执行 git diff 命令检查 requirements.txt 文件是否有改动
        try:
            diff_output = subprocess.check_output('git diff --name-only HEAD@{1} HEAD', shell=True,
                                                  stderr=subprocess.STDOUT, encoding='utf-8')
            # 如果有改动，则执行 pip install 命令安装新增的依赖库
            print(diff_output)
            if "requirements.txt" in diff_output or "requirements.txt" == diff_output.replace('\n', ''):
                logger.info("依赖库存在更新")
                # 检查 requirements.txt 文件是否存在
                if os.path.exists(Path() / 'requirements.txt'):
                    install_output = subprocess.check_output('pip install -r requirements.txt --upgrade', shell=True,
                                                             stderr=subprocess.STDOUT, encoding='utf-8')
                    if install_output:
                        logger.info('依赖库已成功更新！')
                else:
                    logger.info('requirements.txt 文件不存在，无法检查依赖库更新。')
        except subprocess.CalledProcessError as e:
            await update_comm.send(f'更新依赖库时出现错误：{e.output}')
        await update_comm.send('bot已成功更新！\n\n最近更新日志：\n' + log_output)
        await reboot(event)

    except subprocess.CalledProcessError as e:
        if 'timeout' in e.output or 'unable to access' in e.output:
            msg = '更新失败，连接git仓库超时。'
        elif ' Your local changes' in e.output:
            msg = f'更新失败，本地修改过文件导致冲突，请解决冲突后再更新。\n{e.output}'
        else:
            msg = e
        await update_comm.send(msg)
