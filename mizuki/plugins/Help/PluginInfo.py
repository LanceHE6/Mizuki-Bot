# -*- coding = utf-8 -*-
# @File:PluginInfo.py
# @Author:Hycer_Lance
# @Time:2023/5/15 8:08
# @Software:PyCharm

from pathlib import Path
import json
import os

data_path = Path() / 'data'
plugin_info_path = data_path / 'plugins'

class PluginInfo:

    def __init__(self, plugin_name: str, name: str, description: str, usage: str or tuple, extra: dict):
        """
        单个插件信息保存类，将插件信息json保存到指定目录中
        :param plugin_name: 插件模块名
        :param name: 插件名
        :param description: 插件描述
        :param usage: 指令使用说明,一条指令为str字符串,多条为字符串元组
        :param extra: 插件其他信息,包括但不限于 auther, version, priority
        """

        plugin_info = {
            "plugin_name": plugin_name,
            "name": name,
            "description": description,
            "usage": usage,
            "extra": extra
        }

        if not os.path.exists(data_path):
            os.mkdir(data_path)
            if not os.path.exists(plugin_info_path):
                os.mkdir(plugin_info_path)
        with open(plugin_info_path/f"{plugin_name}.json", "w", encoding='utf-8') as plugin_meta_info:
            json.dump(plugin_info, plugin_meta_info, ensure_ascii=False, indent=4)
            plugin_meta_info.close()


class PluginMetaInfo:

    def __init__(self, plugin_json_info: dict):
        """
        单个插件信息类，从给定的字典读取插件信息

        :param plugin_json_info:
        """

        self.plugin_name: str = plugin_json_info["plugin_name"]
        self.name: str = plugin_json_info["name"]
        self.description: str = plugin_json_info["description"]
        self.usage: str or tuple = plugin_json_info["usage"]
        self.extra: dict = plugin_json_info["extra"]


class PluginsInfoList:

    def __init__(self, path: Path or str = plugin_info_path):
        """
        插件信息列表类，构造传入存放插件信息的地址，遍历每个插件信息文件并将它放进列表中
        列表中的元素为PluginMetaInfo类

        :param path: 存放插件信息的地址
        """
        self.plugins_list: list = []
        plugins_list = os.listdir(path)
        for plugin in plugins_list:
            with open(plugin_info_path/f"{plugin}", 'r', encoding='utf-8') as plugin_info_file:
                plugin_info = json.load(plugin_info_file)
                plugin_info_file.close()
            plugin_meta_info = PluginMetaInfo(plugin_info)
            self.plugins_list.append(plugin_meta_info)
