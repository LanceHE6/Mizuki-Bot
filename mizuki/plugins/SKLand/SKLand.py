# -*- coding = utf-8 -*-
# @File:SKLand.py
# @Author:Hycer_Lance
# @Time:2023/9/6 16:41
# @Software:PyCharm

import json

import httpx

from typing import Optional
from nonebot.log import logger

from .api import HyperGryphAPI
from .database import SKLandDB


class SKLand:

    def __init__(self):
        self.qid = Optional[str]
        self.token = Optional[str]  # 鹰角网络token
        self.oauth2 = Optional[str]  # OAuth2授权代码
        self.uid = Optional[str]
        self.userId = Optional[str]
        self.cred = Optional[str]  # 森空岛Cred凭证
        self.binding = Optional[str]  # 绑定的游戏角色列表
        self.arknights_roles = Optional[list]
        self.binding_arknights_role = Optional[dict]  # 当前绑定的方舟角色 为arknights_roles的一个元素

    async def create_by_qid(self, qid: str):
        """
        使用数据库中的数据构建SKLand对象
        :param qid: 用户qq号
        :return: SKLand对象
        """
        if await SKLandDB.is_user_exist(qid):
            sql_sequence = f'select * from SKLand_User where qid={int(qid)};'
            data = await SKLandDB.db_query_column(sql_sequence)
            self.qid = data[0]
            self.token = data[1]
            self.cred = data[2]
            self.binding = eval(data[3])
            self.arknights_roles = eval(data[4])
            self.binding_arknights_role = eval(data[5])
            self.oauth2 = Optional[str]  # OAuth2授权代码
            self.uid = Optional[str]
            self.userId = Optional[str]
            return self
        else:
            return -1

    def login_by_psw(self, phone_number: str, password: str):
        """
        通过手机号和密码登录获取token及cred
        :param phone_number: 手机号
        :param password: 密码
        :return: None
        """
        api = HyperGryphAPI.get_token_by_phone_psw
        data = {
            "phone": phone_number,
            "password": password
        }
        response = httpx.post(url=api, json=data).json()
        if response["status"] == 0:
            self.token = response["data"]["token"]
            print("token:" + self.token)
            if self.__get_oauth2() == 0:
                if self.__get_cred() == 0:
                    print("登录成功")
        else:
            print("获取token失败" + response)
        if self.get_player_binding() == 0:
            self.get_arknights_game_info()

    async def binding_by_token(self, qid: str, token: str):
        """
        使用token绑定账号
        :param qid: 用户qq号
        :param token: 鹰角网络凭证token
        :return: 0 绑定成功/ -1 获取cred失败/ -2 获取oauth2授权码失败/ -3 获取绑定角色列表失败
                绑定成功会自动保存数据进数据库
        """
        self.token = token
        self.qid = qid
        oauth2 = self.__get_oauth2()
        cred = self.__get_cred()
        binding = await self.get_player_binding()
        if oauth2 == 0:
            if cred == 0:
                if binding == 0:
                    logger.info(f"[SKLandBinding]用户{self.qid}绑定成功")
                    await self.save_data()
                    return 0, 0
                else:
                    logger.info(f"[SKLandBinding]用户{self.qid}获取绑定角色列表失败:{binding}")
                    return -3, "获取绑定角色失败"
            else:
                logger.info(f"[SKLandBinding]用户{self.qid}获取cred失败:{cred}")
                return -1, "获取cred凭证失败"
        else:
            logger.info(f"[SKLandBinding]用户{self.qid}获取oauth2授权码失败:{oauth2}")
            return -2, "获取oauth2授权码失败"

    def __get_oauth2(self):
        """
        获取oauth2授权码
        :return: 0 成功 -1 失败
        """
        logger.info("[SKLand]正在获取oauth2授权码")
        api = HyperGryphAPI.get_oauth2_by_token
        data = {
            "token": self.token,
            "appCode": "4ca99fa6b56cc2ba",
            "type": 0}
        response = httpx.post(url=api, json=data).json()
        if response["status"] == 0:
            self.oauth2 = response["data"]["code"]
            self.uid = response["data"]["uid"]
            # print("oauth2:" + self.oauth2)
            # print("uid:" + self.uid)
            return 0
        else:
            logger.warning(f"获取oauth2失败:{response}")
            return -1

    def __get_cred(self):
        """
        获取cred凭证
        :return: 0 成功 -1 失败
        """
        logger.info("[SKLand]正在获取cred凭证")
        api = HyperGryphAPI.get_cred_by_oauth2
        data = {
            "kind": 1,
            "code": self.oauth2
        }
        response = httpx.post(url=api, json=data).json()
        if response["code"] == 0:
            self.cred = response["data"]["cred"]
            self.userId = response["data"]["userId"]
            print("cred:" + self.cred)
            # print("userId:" + self.userId)
            return 0
        else:
            logger.warning(f"[SKLand]cred凭证获取失败:{response}")
            return -1

    async def save_data(self):
        """
        将数据保存进数据库中
        :return: None
        """
        if await SKLandDB.is_user_exist(self.qid):
            sql_sequence = f'Update SKLand_User Set token="{self.token}", cred="{self.cred}", ' \
                           f'binding="{self.binding}", arknights_roles="{self.arknights_roles}", ' \
                           f'binding_arknights_role="{self.binding_arknights_role}" where qid={self.qid};'
            result = await SKLandDB.db_execute(sql_sequence)
            if not result == "ok":
                logger.warning("[SKLand_save_data]" + result)
        else:
            sql_sequence = f'Insert Into SKLand_User(qid, token, cred, binding, arknights_roles,' \
                           f' binding_arknights_role) values ({self.qid}, "{self.token}", "{self.cred}",' \
                           f' "{self.binding}", "{self.arknights_roles}", "{self.binding_arknights_role}");'
            result = await SKLandDB.db_execute(sql_sequence)
            if not result == "ok":
                logger.warning("[SKLand_save_data]" + result)

    async def get_player_binding(self):
        """
        获取用户在鹰角下的所有绑定游戏角色
        并设置明日方舟的默认绑定
        :return: 0 成功 -1 失败
        """
        api = HyperGryphAPI.get_player_binding
        headers = {
            "cred": self.cred
        }
        response = httpx.get(url=api, headers=headers).json()
        if response["code"] == 0:
            self.binding = response["data"]["list"]
            for app in self.binding:
                if app["appCode"] == "arknights":
                    self.arknights_roles = app["bindingList"]
            # print("binding:")
            # print(self.binding)
            self.binding_arknights_role = self.arknights_roles[0]
            return 0
        else:
            # print("获取binding失败")
            # print(response)
            return -1

    async def get_arknights_game_info(self):
        headers = {
            "cred": self.cred
        }
        for role in self.arknights_roles:
            print(role)
            api = HyperGryphAPI.get_game_info + role['uid']
            response = httpx.get(url=api, headers=headers).json()
            if response["code"] == 0:
                game_data = response["data"]
                print("gameinfo:")
                print(game_data)
                with open(f"{role['uid']}_game_data.json", "w", encoding="utf-8") as f:
                    json.dump(game_data, f, indent=4)
                    f.close()
            else:
                print(f"获取uid:{role['uid']}的游戏信息失败\n" + response)

    async def skland_sign(self):
        """
        森空岛签到
        :return: 状态及结果 0为成功 -1 为重复签到 -2 为签到失败 -3 为token过期或无效
        """
        if not self.token_verification():
            return -3,
        api = HyperGryphAPI.skland_sign
        headers = {
            "cred": self.cred
        }

        data = {
            "uid": self.binding_arknights_role["uid"],
            "gameId": self.binding_arknights_role["channelMasterId"]
        }
        response = httpx.post(url=api, headers=headers, json=data).json()
        # print(response)
        if response["code"] == 0:
            logger.info(f"[SKLandSign]用户{self.qid}签到成功")
            return 0, response["data"]["awards"]
        elif response["code"] == 10001:
            logger.info(f"[SKLandSign]用户{self.qid}重复签到")
            return -1, response
        else:
            logger.warning(f"[SKLandSign]用户{self.qid}签到失败")
            logger.warning(str(response))
            return -2, response

    def token_verification(self):
        """
        token有效性校验
        :return: True有效
        """
        api = HyperGryphAPI.token_verification + self.token
        result = httpx.get(url=api).json()
        try:
            if result["status"] == 0:
                return True
            else:
                return False
        except KeyError:
            return False

    def cred_verification(self):
        """
        cred有效性检验
        :return: True有效
        """
        api = HyperGryphAPI.get_cred_by_oauth2
        headers = {
            "cred": self.cred
        }
        result = httpx.post(url=api, headers=headers).json()
        if result["code"] == 0:
            return True
        else:
            return False
