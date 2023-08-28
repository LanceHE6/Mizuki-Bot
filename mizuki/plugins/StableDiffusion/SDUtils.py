# -*- coding = utf-8 -*-
# @File:SDUtils.py
# @Author:Hycer_Lance
# @Time:2023/8/28 9:35
# @Software:PyCharm

import re
import httpx

from typing import Optional
from pathlib import Path
from nonebot import get_driver

from ..Utils.GroupAndGuildUtils import GuildMessageEvent


class SDUtils:
    casual_img_path = Path() / 'mizuki' / 'plugins' / 'StableDiffusion' / 'outputs'
    base_url = get_driver().config.sdbaseurl
    __headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    @staticmethod
    async def sd_async_request(url: str, data: Optional[dict] = None):
        """
        异步请求函数
        :param url: 接口地址
        :param data: 请求体，为None则为get请求
        :return: 返回json格式的请求内容
        """
        async with httpx.AsyncClient(timeout=60) as async_client:
            if data is None:
                response = await async_client.get(url=url, headers=SDUtils.__headers)
                return response.json()
            response = await async_client.post(url=url, json=data, headers=SDUtils.__headers)
            return response.json()

    @staticmethod
    def sd_sync_request(url: str, data: Optional[dict] = None):
        """
        同步请求函数
        :param url: 接口地址
        :param data: 请求体，为None则为get请求
        :return: 返回json格式的请求内容
        """
        with httpx.Client() as sync_client:
            if data is None:
                response = sync_client.get(url=url, headers=SDUtils.__headers)
                return response.json()
            response = sync_client.post(url=url, json=data, headers=SDUtils.__headers)
            return response.json()

    @staticmethod
    async def get_img2img_parameters(event, res: str) -> dict:
        """
        正则匹配用户发送的图生图参数
        :param event: 触发事件
        :param res: 消息字符串
        :return: 匹配结果字典
        """
        result = {}
        prompt_match = re.search(r"(?:prompt|p)[:：]([\w\u4e00-\u9fa5,，]+)", res, re.UNICODE)
        if prompt_match:
            prompt_value = prompt_match.group(1)
            print("Prompt value:", prompt_value)
        else:
            prompt_value = None
        result["prompt"] = prompt_value

        # 匹配 extent 或 e: 后面的值
        extent_match = re.search(r"(?:extent|e)[:：]([\d.]+)", res)
        if extent_match:
            extent_value = extent_match.group(1)
            print("Extent value:", extent_value)
        else:
            extent_value = None
        result["extent"] = extent_value

        if isinstance(event, GuildMessageEvent):
            # 适配频道
            url_match = re.search(r"<attachment:([^,]+)>", res)
            if url_match:
                url_value = url_match.group(1)
                print("URL value:", url_value)
                result["img_url"] = "https://" + url_value
            else:
                result["img_url"] = None
        else:
            # 匹配 url= 后面的值
            url_match = re.search(r"url=([^,]+)", res)
            if url_match:
                url_value = url_match.group(1)
                print("URL value:", url_value)
            else:
                url_value = None
            result["img_url"] = url_value

        return result
