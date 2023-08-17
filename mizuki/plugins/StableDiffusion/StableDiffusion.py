# -*- coding = utf-8 -*-
# @File:StableDiffusion.py
# @Author:Hycer_Lance
# @Time:2023/8/10 10:39
# @Software:PyCharm

import time
import base64
import requests

from pathlib import Path

from nonebot import get_driver
from nonebot.log import logger

casual_img_path = Path() / 'mizuki' / 'plugins' / 'StableDiffusion' / 'outputs'


class StableDiffusion:
    # TODO 完善类注释级各个方法注释

    __base_url = get_driver().config.sdbaseurl
    __headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    models_list: list
    current_model_title: str

    def __init__(self):
        logger.info("[StableDiffusion]开始初始化StableDiffusion服务")

        logger.info("[StableDiffusion]正在获取模型列表...")
        models_list = self.get_models_list()
        if "出错" in models_list:
            logger.warning("[StableDiffusion]模型列表获取失败")
        else:
            self.models_list = models_list

        logger.info("[StableDiffusion]正在获取当前模型...")
        current_model_title = self.get_current_model_title()
        if "出错" in current_model_title:
            logger.warning("[StableDiffusion]当前模型获取失败")
        else:
            self.current_model_title = current_model_title

    def sd_request(self, url: str, data=None):
        if data is None:
            response = requests.get(url=url, headers=self.__headers)
            return response.json()
        response = requests.post(url=url, json=data, headers=self.__headers)
        return response.json()

    async def txt2img(self, prompt: str):
        data = {
            "enable_hr": False,
            "prompt": f"{prompt}",
            "seed": -1,
            "subseed": -1,
            "subseed_strength": 0,
            "seed_resize_from_h": -1,
            "seed_resize_from_w": -1,
            "batch_size": 1,
            "n_iter": 1,
            "steps": 50,
            "cfg_scale": 7,
            "width": 512,
            "height": 512,
            "negative_prompt": "logo,text,badhandv4,EasyNegative,ng_deepnegative_v1_75t,rev2-badprompt,"
                               "verybadimagenegative_v1.3,negative_hand-neg,mutated hands and fingers,poorly drawn "
                               "face,extra limb,missing limb,disconnected limbs,malformed hands,ugly",
        }
        api = self.__base_url + "/sdapi/v1/txt2img"
        logger.info(f"[StableDiffusion]正在请求SDAPI prompt:{prompt}")
        response = self.sd_request(api, data)
        logger.debug(f"[StableDiffusion]Response:{response}")
        try:
            now_time = round(time.time(), 0)
            save_path = casual_img_path / f"{now_time}.png"
            with open(save_path, 'wb') as f:
                f.write(base64.b64decode(response["images"][0]))
                f.close()
            return save_path
        except KeyError:
            return "请求错误，请稍后再试：" + str(response)

    async def get_progress(self):
        api = self.__base_url + "/sdapi/v1/progress?skip_current_image=false"
        response = self.sd_request(api)
        return response["progress"]

    def get_models_list(self):
        api = self.__base_url + "/sdapi/v1/sd-models"
        response = self.sd_request(api)
        logger.debug(f"get_models_list->{response}")
        models_title = []
        try:
            for model in response:
                models_title.append(model["title"])
            return models_title
        except KeyError:
            return "请求出错，请稍后再试：" + str(response)
        except TypeError:
            return "请求出错，请稍后再试：" + str(response)

    def get_current_model_title(self):
        api = self.__base_url + "/sdapi/v1/options"
        response = self.sd_request(api)
        logger.debug(f"get_current_model_title->{response}")
        try:
            return response["sd_model_checkpoint"]
        except KeyError:
            return "请求出错, 请稍后再试：" + str(response)

    async def set_model(self, model_title):
        api = self.__base_url + "/sdapi/v1/options"
        data = {
            "sd_model_checkpoint": f"{model_title}"
        }
        response = self.sd_request(url=api, data=data)
        print(response)
        # TODO 待完善模型设置函数