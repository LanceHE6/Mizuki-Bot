# -*- coding = utf-8 -*-
# @File:StableDiffusion.py
# @Author:Hycer_Lance
# @Time:2023/8/10 10:39
# @Software:PyCharm

import re
import time
import base64
import httpx

from pathlib import Path

from nonebot import get_driver
from nonebot.log import logger

casual_img_path = Path() / 'mizuki' / 'plugins' / 'StableDiffusion' / 'outputs'


class StableDiffusion:
    """
    SD管理类
    """

    __base_url = get_driver().config.sdbaseurl
    __headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    # 模型列表
    models_list: list
    # 当前模型title
    current_model_title: str

    def __init__(self):
        """
        初始化SD服务获取相关信息
        """
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

    async def sd_async_request(self, url: str, data=None):
        """
        异步请求函数
        :param url: 接口地址
        :param data: 请求体，为None则为get请求
        :return: 返回json格式的请求内容
        """
        async with httpx.AsyncClient(timeout=60) as async_client:
            if data is None:
                response = await async_client.get(url=url, headers=self.__headers)
                return response.json()
            response = await async_client.post(url=url, json=data, headers=self.__headers)
            return response.json()

    def sd_sync_request(self, url: str, data=None):
        """
        同步请求函数
        :param url: 接口地址
        :param data: 请求体，为None则为get请求
        :return: 返回json格式的请求内容
        """
        with httpx.Client() as sync_client:
            if data is None:
                response = sync_client.get(url=url, headers=self.__headers)
                return response.json()
            response = sync_client.post(url=url, json=data, headers=self.__headers)
            return response.json()

    async def txt2img(self, prompt: str) -> Path or str:
        """
        文生图函数
        :param prompt: 图片描述
        :return: 下载的图片本地地址
        """
        prompt = StableDiffusion.prompt_translate(prompt)
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
        response = await self.sd_async_request(api, data)
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
        """
        获取当前进行任务的执行进度
        :return: 小数进度
        """
        api = self.__base_url + "/sdapi/v1/progress?skip_current_image=false"
        response = await self.sd_async_request(api)
        return response["progress"]

    def get_models_list(self) -> list or str:
        """
        获取模型列表
        :return: 模型列表
        """
        api = self.__base_url + "/sdapi/v1/sd-models"
        response = self.sd_sync_request(api)
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

    def get_current_model_title(self) -> str:
        """
        获取当前模型title
        :return: 模型title
        """
        api = self.__base_url + "/sdapi/v1/options"
        response = self.sd_sync_request(api)
        logger.debug(f"get_current_model_title->{response}")
        try:
            return response["sd_model_checkpoint"]
        except KeyError:
            return "请求出错, 请稍后再试：" + str(response)

    async def set_model(self, model_title):
        """
        设置当前套用模型
        :param model_title: 模型title
        :return: 0为设置成功否则返回请求返回内容
        """
        api = self.__base_url + "/sdapi/v1/options"
        data = {
            "sd_model_checkpoint": f"{model_title}"
        }
        response = await self.sd_async_request(url=api, data=data)
        if response is None:
            return 0
        else:
            return response.json()

    @staticmethod
    async def prompt_translate(prompt: str) -> str:
        """
        利用有道翻译api将非全英文prompt翻译为英文
        全英文则直接返回不做处理
        :param prompt: 目标prompt
        :return: 翻译后的英文
        """
        if not StableDiffusion.is_all_english(prompt):
            data = {'doctype': 'json', 'type': 'ZH_CN2EN', 'i': f"{prompt}"}
            with httpx.Client as client:
                r = client.get("https://fanyi.youdao.com/translate", params=data)
                result = r.json()
            return result["translateResult"][0][0]["tgt"]
        return prompt

    @staticmethod
    def is_all_english(text):
        """
        判断是否为全英文
        :param text: 目标字符串
        :return: bool
        """
        pattern = r'^[A-Za-z0-9]+$'
        return re.match(pattern, text) is not None
