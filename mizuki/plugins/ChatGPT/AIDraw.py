# -*- coding = utf-8 -*-
# @File:AIDraw.py
# @Author:Hycer_Lance
# @Time:2023/7/27 13:51
# @Software:PyCharm

import requests
import time
import tqdm

from pathlib import Path

from nonebot.log import logger
from nonebot import get_driver

casual_path = Path() / 'mizuki' / 'plugins' / 'ChatGPT'


class AIDraw:
    """
    ChatGPT Dall.E ai绘图类
    """

    _headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_driver().config.chatgpt_api_key}"
    }

    def __init__(self, prompt: str):
        """
        以prompt构建对象
        :param prompt: 绘图描述
        """
        # 判断是否启用代理
        self._API_ENDPOINT = "https://api.openai.com/v1/images/generations"
        if get_driver().config.chatgpt_enable_proxy:
            self._API_ENDPOINT = f"{get_driver().config.chatgpt_proxy}/v1/images/generations"
        self._data: dict = {
            "prompt": f"{prompt}",
            "n": 1,
            "size": "512x512"
        }

    async def get_image(self):
        if get_driver().config.chatgpt_api_key == "":
            logger.error("[ChatGPT]未配置API-KEY,ChatGPT无法正常提供服务")
            return "未配置API-KEY,ChatGPT无法正常提供服务"
        response = requests.post(self._API_ENDPOINT, json=self._data, headers=self._headers)
        if response.status_code == 200:
            result = response.json()
            # 提取图片url
            img_url = result["data"][0]["url"]
            logger.info("[ChatGPT]开始下载AI绘制图片")
            img_data = requests.get(img_url, stream=True)
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
        else:
            if "content_policy_violation" in response.text:
                return "描述中包含敏感词汇"
            return f"错误信息：{response.text}"
