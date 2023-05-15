# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/5/15 7:56
# @Software:PyCharm

from ..Utils.PluginInfo import PluginsInfoList
from nonebot import on_command

test = on_command("help")

@test.handle()
async def _():
    reply = ""
    plugins_meta_info_list = PluginsInfoList().plugins_list
    for plugin_meta_info in plugins_meta_info_list:
        reply+= str(plugin_meta_info.usage)+"\n"
    await test.finish(reply)