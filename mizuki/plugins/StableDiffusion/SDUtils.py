# -*- coding = utf-8 -*-
# @File:SDUtils.py
# @Author:Hycer_Lance
# @Time:2023/8/28 9:35
# @Software:PyCharm

import httpx

from typing import Optional
from pathlib import Path
from nonebot import get_driver


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
