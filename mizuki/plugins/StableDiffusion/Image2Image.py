# -*- coding = utf-8 -*-
# @File:Image2Image.py
# @Author:Hycer_Lance
# @Time:2023/8/28 18:20
# @Software:PyCharm

import httpx
import base64
import time

from pathlib import Path
from nonebot.log import logger

from .SDUtils import SDUtils


class SDImage2Image:

    def __init__(self, params: dict):
        """
        :param params: 正则匹配的参数字典
        """
        self.task_type = "图生图"
        self.prompt = '' if params["prompt"] is None else params["prompt"]
        self.extent = 0.75 if params["extent"] is None else params["extent"]
        self.img_url = params["img_url"]
        self.api = SDUtils.base_url + "/sdapi/v1/img2img"
        init_image = self.image_to_base64()
        self.data = {
            "init_images": [f"{init_image}"],
            "denoising_strength": self.extent,
            "prompt": self.prompt
        }
        print(f"data:{self.data}")

    def image_to_base64(self):
        response = httpx.get(self.img_url)
        if response.status_code == 200:
            image_data = response.content
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return base64_data
        else:
            print("Error:", response)
            return None

    async def get_img(self) -> Path or str:
        """
        图生图函数
        :return: 下载的图片本地地址
        """
        logger.info(f"[StableDiffusion]正在请求SD图生图API 原图:{self.img_url}")
        response = await SDUtils.sd_async_request(url=self.api, data=self.data)
        # logger.debug(f"[StableDiffusion]Response:{response}")
        try:
            now_time = round(time.time(), 0)
            save_path = SDUtils.casual_img_path / f"{now_time}.png"
            with open(save_path, 'wb') as f:
                f.write(base64.b64decode(response["images"][0]))
                f.close()
            return save_path
        except KeyError:
            return "请求错误，请稍后再试：" + str(response)
