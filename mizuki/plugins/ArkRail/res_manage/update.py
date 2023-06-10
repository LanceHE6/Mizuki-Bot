# -*- coding = utf-8 -*-
# @File:update.py
# @Author:Hycer_Lance
# @Time:2023/6/9 15:41
# @Software:PyCharm
import shutil

from nonebot import on_command
from nonebot.permission import SUPERUSER

from ...Utils.PluginInfo import PluginInfo
from .utils import *

update_res_comm = on_command("update_res", aliases={'更新资源'}, block=True, priority=1, permission=SUPERUSER)

__plugin_info__ = PluginInfo(
    plugin_name="ArkRail_res_manage",
    name="图片资源更新",
    description="图片资源更新",
    usage=(
        "更新资源"
    ),
    extra={
        "author": "Hycer_Lance",
        "version": "0.2.0",
        "priority": 1,
        "permission": "SUPERUSER"
    }
)

@update_res_comm.handle()
async def update_res():
    release_data = await check_release()
    with open(res_version_data, 'r', encoding='utf-8') as data:
        local_data = json.load(data)
        data.close()
    if local_data["version"] != release_data[1]:
        await update_res_comm.send("图片资源存在更新，开始更新资源")
        shutil.rmtree(img_resources_path)  # os.remove只能删除一个文件，删除目录时会报错
        await download(release_data[0], img_resources_path, release_data[1], release_data[2])
        await update_res_comm.finish(f'图片资源更新完成\nVersion:{release_data[1]}\nLog:{release_data[2]}')
    else:
        await update_res_comm.finish("当前已是最新版资源")
