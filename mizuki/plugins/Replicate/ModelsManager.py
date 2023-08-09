# -*- coding = utf-8 -*-
# @File:ModelsManager.py
# @Author:Hycer_Lance
# @Time:2023/8/8 18:00
# @Software:PyCharm

import json

from pathlib import Path

models_config_path = Path() / 'mizuki' / 'plugins' / 'Replicate' / 'models_config.json'


class ModelsManager:
    current_model_name: str
    current_model_version: str
    models_list: dict

    def __init__(self):
        with open(models_config_path, "r", encoding="utf-8") as file:
            config = dict(json.load(file))
            file.close()
        current_model = config["current_model"]
        self.current_model_name = next(iter(current_model))
        self.current_model_version = current_model.get(self.current_model_name)
        self.models_list = config["models_list"]

    def get_current_model_name(self) -> str:
        return self.current_model_name

    def get_current_model_version(self) -> str:
        return self.current_model_version

    def get_models_list(self) -> dict:
        return self.models_list

    def set_current_model_by_name(self, model_name: str):
        self.current_model_name = model_name
        self.current_model_version = self.models_list[model_name]
        self.save_config()

    def add_model(self, model_name: str, model_version: str):
        self.models_list[model_name] = model_version
        self.save_config()

    def remove_model_by_name(self, model_name: str) -> bool:
        """
        根据模型名称删除模型
        :param model_name: 目标模型名称
        :return: 删除状态 True为成功，False为不存在该模型
        """
        if model_name in self.models_list.keys():
            self.models_list.pop(model_name)
            self.save_config()
            return True
        return False

    def save_config(self):
        with open(models_config_path, "r", encoding="utf-8") as file:
            config = dict(json.load(file))
            file.close()
        config["current_model"] = {
            self.current_model_name: self.current_model_version
        }
        config["models_list"] = self.models_list
        with open(models_config_path, "w", encoding="utf-8") as file:
            json.dump(config, file)
            file.close()
