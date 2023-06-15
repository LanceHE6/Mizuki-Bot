# -*- coding = utf-8 -*-
# @File:Session.py
# @Author:Hycer_Lance
# @Time:2023/6/11 15:03
# @Software:PyCharm

import requests

from nonebot.log import logger
from nonebot import get_driver


class Session:

    _headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_driver().config.api_key}"
    }
    _initial_message: list = []

    def __init__(self):
        """
        构造一个会话，用于记录聊天内容
        """
        # 判断是否启用代理
        self._API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
        if get_driver().config.enable_proxy:
            self._API_ENDPOINT = f"{get_driver().config.proxy}/v1/chat/completions"

        self._message: list = [
            {
                "role": "system",
                "content": get_driver().config.personality
            }
        ]
        self._data: dict = {
            "model": "gpt-3.5-turbo",
            "messages": self._message,
            "max_tokens": 3072
        }

    async def get_response(self) -> str:
        """
        利用现有message信息获取回复
        :return:
        """
        if get_driver().config.api_key == "":
            logger.error("[ChatGPT]未配置API-KEY,ChatGPT无法正常提供服务")
            return "未配置API-KEY,ChatGPT无法正常提供服务"
        # 发送POST请求
        response = requests.post(self._API_ENDPOINT, json=self._data, headers=self._headers)

        # 解析响应
        if response.status_code == 200:
            result = response.json()
            # 提取生成的文本
            generated_text = result["choices"][0]["message"]["content"]
            # 将回复消息添加进message中
            self._message.append({"role": "assistant", "content": f"{generated_text}"})

            return generated_text
        else:

            return f"错误信息：{response.text}"

    async def add_user_content(self, content: str):
        """
        添加用户message
        :param content: message
        :return: none
        """
        self._message.append({"role": "user", "content": f"{content}"})

    async def get_message(self) -> list:
        """
        获取message列表
        :return: message
        """
        return self._message

    async def clear_message(self):
        """
        清空message列表
        :return:
        """
        self._message = self._initial_message
