# -*- coding = utf-8 -*-
# @File:Replicate.py
# @Author:Hycer_Lance
# @Time:2023/8/8 14:13
# @Software:PyCharm

import requests
import json
import asyncio
import time
import tqdm
import re

from pathlib import Path

from nonebot.log import logger
from nonebot import get_driver

casual_path = Path() / 'mizuki' / 'plugins' / 'Replicate'


class Replicate:
    """
    replicate请求类
    """

    __base_url = "https://api.replicate.com/v1/predictions"
    __headers = {
        "Authorization": f"Token {get_driver().config.replicate_api_token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
        "Content-Type": "application/json"
    }
    __prediction_id: str = ""

    def __init__(self):
        if get_driver().config.replicate_enable_proxy:
            if get_driver().config.replicate_proxy == "":
                logger.warning("[replicate]代理地址未配置,replicate无法正常提供服务")
            self.__base_url = get_driver().config.replicate_proxy + "/v1/predictions"

    async def get_img_url(self, prompt: str):
        """
        获取绘制的图片地址
        :param prompt: 绘画描述
        :return: str 网络图片地址或错误提示
        """
        prompt = await Replicate.prompt_translate(str(prompt))
        logger.info(f"[replicate]prompt:{prompt}")
        data = {
            "version": "2b017d9b67edd2ee1401238df49d75da53c523f36e363881e057f5dc3ed3c5b2",
            "input": {
                "prompt": f"{prompt}"
            }
        }
        response = requests.post(url=self.__base_url, headers=self.__headers, data=json.dumps(data)).content
        try:
            response_data = json.loads(response)
        except json.JSONDecodeError:
            logger.warning("[replicate]请求出错 " + str(response))
            return "请求出错"
        prediction_id = response_data["id"]
        query_url = self.__base_url + "/" + prediction_id

        # 4次查询机会，间隔5秒 timeout 20s
        attempts = 1
        while attempts <= 4:
            await asyncio.sleep(5)
            resp = json.loads(requests.get(url=query_url, headers=self.__headers).content)
            logger.info(f'status:{resp["status"]}')
            if resp["status"] == "succeeded":
                if get_driver().config.replicate_enable_proxy:
                    return str(resp["output"][0]).replace("https://replicate.delivery",
                                                          get_driver().config.replicate_delivery_proxy)
            attempts += 1

        return "请求超时"

    async def get_img_path(self, prompt: str):
        """
        将图片下载到本地并返回图片地址
        :param prompt: 图片描述
        :return: Path类或错误提示
        """
        result = await self.get_img_url(prompt)
        if "请求" in result:
            return result
        logger.info("[replicate]开始下载AI绘制图片")
        logger.info(f"[replicate]图片地址{result}")
        img_data = requests.get(result, stream=True)
        now_time = round(time.time())
        img_path = casual_path / f"{now_time}.png"
        with open(img_path, "wb") as img:
            total_size = int(img_data.headers.get('content-length', 0))
            block_size = 1024  # 1KB
            progress_bar = tqdm.tqdm(total=total_size, unit='B', unit_scale=True)

            for data in img_data.iter_content(block_size):
                img.write(data)
                progress_bar.update(len(data))

            progress_bar.close()
        return img_path

    @staticmethod
    async def prompt_translate(prompt: str) -> str:
        """
        利用有道翻译api将非全英文prompt翻译为英文
        全英文则直接返回不做处理
        :param prompt: 目标prompt
        :return: 翻译后的英文
        """
        if not Replicate.is_all_english(prompt):
            data = {'doctype': 'json', 'type': 'ZH_CN2EN', 'i': f"{prompt}"}
            r = requests.get("https://fanyi.youdao.com/translate", params=data)
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
