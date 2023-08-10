# -*- coding = utf-8 -*-
# @File:StableDiffusionAPI.py
# @Author:Hycer_Lance
# @Time:2023/8/10 10:39
# @Software:PyCharm

import time
import base64
import requests

from pathlib import Path

from nonebot import get_driver

casual_img_path = Path() / 'mizuki' / 'plugins' / 'StableDiffusion' / 'outputs'


class StableDiffusionAPI:
    __base_url = get_driver().config.sdbaseurl
    __headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    @staticmethod
    async def sd_request(url: str, data=None):
        if data is None:
            response = requests.get(url=url, headers=StableDiffusionAPI.__headers)
            return response.json()
        response = requests.post(url=url, json=data, headers=StableDiffusionAPI.__headers)
        return response.json()

    @staticmethod
    async def txt2img(prompt: str):
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
            "width": 1024,
            "height": 1024,
            "negative_prompt": "logo,text,badhandv4,EasyNegative,ng_deepnegative_v1_75t,rev2-badprompt,"
                               "verybadimagenegative_v1.3,negative_hand-neg,mutated hands and fingers,poorly drawn "
                               "face,extra limb,missing limb,disconnected limbs,malformed hands,ugly",
        }
        api = StableDiffusionAPI.__base_url + "/sdapi/v1/txt2img"
        response = await StableDiffusionAPI.sd_request(api, data)
        try:
            now_time = round(time.time(), 0)
            save_path = casual_img_path / f"{now_time}.png"
            with open(save_path, 'wb') as f:
                f.write(base64.b64decode(response["images"][0]))
                f.close()
            return save_path
        except KeyError:
            return "请求错误，请稍后再试：" + str(response)

    @staticmethod
    async def get_progress():
        api = StableDiffusionAPI.__base_url + "/sdapi/v1/progress?skip_current_image=false"
        response = StableDiffusionAPI.sd_request(api)
        return response["progress"]
