# -*- coding = utf-8 -*-
# @File:StableDiffusion.py
# @Author:Hycer_Lance
# @Time:2023/8/10 10:39
# @Software:PyCharm

import re
import os

import httpcore
import httpx

from nonebot.log import logger
from .SDUtils import SDUtils
from .Text2Image import SDText2Image
from .Image2Image import SDImage2Image
from ..Utils.GroupAndGuildUtils import GroupAndGuildMessageUtils, GroupAndGuildMessageSegment
from ..Utils.QQ import QQ


class StableDiffusion:
    """
    SD管理类
    """
    # 模型列表
    models_list: list
    # 当前模型title
    current_model_title: str
    # 任务列表
    tasks: list = []

    def __init__(self):
        """
        初始化SD服务获取相关信息
        """
        try:
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
        except TimeoutError:
            logger.warning("[StableDiffusion]连接SD服务超时")
        except httpcore.ConnectTimeout:
            logger.warning("[StableDiffusion]连接SD服务超时")
        except httpx.ConnectTimeout:
            logger.warning("[StableDiffusion]连接SD服务超时")
        if not os.path.exists(SDUtils.casual_img_path):
            os.mkdir(SDUtils.casual_img_path)

    @staticmethod
    async def get_progress():
        """
        获取当前进行任务的执行进度
        :return: 小数进度
        """
        api = SDUtils.base_url + "/sdapi/v1/progress?skip_current_image=false"
        response = await SDUtils.sd_async_request(url=api)
        return response["progress"]

    @staticmethod
    def get_models_list() -> list or str:
        """
        获取模型列表
        :return: 模型列表
        """
        api = SDUtils.base_url + "/sdapi/v1/sd-models"
        response = SDUtils.sd_sync_request(api)
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

    @staticmethod
    def get_current_model_title() -> str:
        """
        获取当前模型title
        :return: 模型title
        """
        api = SDUtils.base_url + "/sdapi/v1/options"
        response = SDUtils.sd_sync_request(api)
        logger.debug(f"get_current_model_title->{response}")
        try:
            return response["sd_model_checkpoint"]
        except KeyError:
            return "请求出错, 请稍后再试：" + str(response)

    @staticmethod
    async def set_model(model_title):
        """
        设置当前套用模型
        :param model_title: 模型title
        :return: 0为设置成功否则返回请求返回内容
        """
        api = SDUtils.base_url + "/sdapi/v1/options"
        data = {
            "sd_model_checkpoint": f"{model_title}"
        }
        response = await SDUtils.sd_async_request(url=api, data=data)
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

        def is_all_english(text):
            """
            判断是否为全英文
            :param text: 目标字符串
            :return: bool
            """
            pattern = r'^[A-Za-z0-9]+$'
            return re.match(pattern, text) is not None

        if not is_all_english(prompt):
            data = {'doctype': 'json', 'type': 'ZH_CN2EN', 'i': f"{prompt}"}
            async with httpx.AsyncClient() as client:
                r = await client.get(url="https://fanyi.youdao.com/translate", params=data)
                result = r.json()
            return result["translateResult"][0][0]["tgt"]
        return prompt

    async def add_txt2img(self, event, bot, prompt: str):
        """
        添加文生图任务
        :param event: 触发事件event
        :param bot: 触发事件bot
        :param prompt: 文生图描述
        :return: None
        """
        prompt = await self.prompt_translate(prompt)
        task = SDText2Image(prompt)
        self.tasks.append((event, bot, task))

    async def add_img2img(self, event, bot, paras: dict):
        """
        添加文生图任务
        :param event: 触发事件event
        :param bot: 触发事件bot
        :param paras: 正则匹配的参数字典
        :return: None
        """
        paras["prompt"] = await self.prompt_translate(paras["prompt"]) \
            if not paras["prompt"] is None else paras["prompt"]
        task = SDImage2Image(paras)
        self.tasks.append((event, bot, task))

    async def run(self):
        """
        sd执行任务
        :return: None
        """
        if len(self.tasks) == 1:
            await self.process_task()

    async def process_task(self):
        """
        处理任务列表中的各个任务
        :return: None
        """
        event, bot, task = self.tasks[0]
        uid = await GroupAndGuildMessageUtils.get_event_user_id(event)
        qq = QQ(uid)
        nick_name = qq.get_nickname()
        message = f"开始执行用户{nick_name}的{task.task_type}任务\nprompt:{task.prompt}"
        if task.task_type == "图生图":
            message += f"\nextent:{task.extent}"
        await bot.send(event, message=message)
        # 执行任务逻辑，生成图片
        img_path = await task.get_img()
        # 发送结果
        message = GroupAndGuildMessageSegment.at(event) + GroupAndGuildMessageSegment.image(event, img_path)
        await bot.send(event, message)
        self.tasks.pop(0)

        if not len(self.tasks) == 0:
            await self.process_task()  # 处理下一个任务
