# -*- coding = utf-8 -*-
# @File:Text2Image.py
# @Author:Hycer_Lance
# @Time:2023/8/28 9:30
# @Software:PyCharm

import time
import base64

from nonebot.log import logger
from pathlib import Path
from .SDUtils import SDUtils


class SDText2Image:

    def __init__(self, prompt: str):
        """
        :param prompt: 图片描述 英文
        """
        self.task_type = "文生图"
        self.prompt = prompt
        self.api = SDUtils.base_url + "/sdapi/v1/txt2img"
        self.data = {
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

    async def get_img(self) -> Path or str:
        """
        文生图函数
        :return: 下载的图片本地地址
        """
        logger.info(f"[StableDiffusion]正在请求SD文生图API prompt:{self.prompt}")
        response = await SDUtils.sd_async_request(url=self.api, data=self.data)
        logger.debug(f"[StableDiffusion]Response:{response}")
        try:
            now_time = round(time.time(), 0)
            save_path = SDUtils.casual_img_path / f"{now_time}.png"
            with open(save_path, 'wb') as f:
                f.write(base64.b64decode(response["images"][0]))
                f.close()
            return save_path
        except KeyError:
            return "请求错误，请稍后再试：" + str(response)
