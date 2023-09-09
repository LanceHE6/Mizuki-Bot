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
                    return -3, binding
            else:
                logger.info(f"[SKLandBinding]用户{self.qid}获取cred失败:{cred}")
                return -1, cred
        else:
            logger.info(f"[SKLandBinding]用户{self.qid}获取oauth2授权码失败:{oauth2}")
            return -2, oauth2

    def __get_oauth2(self):
        api = HyperGryphAPI.get_oauth2_by_token
        data = {
            "token": self.token,
            "appCode": "4ca99fa6b56cc2ba",
            "type": 0}
        response = httpx.post(url=api, json=data).json()
        if response["status"] == 0:
            self.oauth2 = response["data"]["code"]
            self.uid = response["data"]["uid"]
            print("oauth2:" + self.oauth2)
            print("uid:" + self.uid)
            return 0
        else:
            print("获取oauth2失败" + response)
            return -1

    def __get_cred(self):
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
            print("userId:" + self.userId)
            return 0
        else:
            print("获取cred失败" + response)
            return -1

    async def save_data(self):
        if await SKLandDB.is_user_exist(self.qid):
            sql_sequence = f'Update SKLand_User Set token="{self.token}", cred="{self.cred}", binding="{self.binding}", arknights_roles="{self.arknights_roles}", binding_arknights_role="{self.binding_arknights_role}" where qid={self.qid};'
            result = await SKLandDB.db_execute(sql_sequence)
            print(f"cunzai{result}")
            if not result == "ok":
                print(result)
        else:
            sql_sequence = f'Insert Into SKLand_User(qid, token, cred, binding, arknights_roles, binding_arknights_role) values ({self.qid}, "{self.token}", "{self.cred}", "{self.binding}", "{self.arknights_roles}", "{self.binding_arknights_role}");'
            result = await SKLandDB.db_execute(sql_sequence)
            print(result)
            if not result == "ok":
                print(result)

    async def get_player_binding(self):
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
            print("binding:")
            print(self.binding)
            self.binding_arknights_role = self.arknights_roles[0]
            return 0
        else:
            print("获取binding失败" + response)
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
        api = HyperGryphAPI.skland_sign
        headers = {
            "cred": self.cred
        }

        data = {
            "uid": self.binding_arknights_role["uid"],
            "gameId": self.binding_arknights_role["channelMasterId"]
        }
        response = httpx.post(url=api, headers=headers, json=data).json()
        print(response)
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

# if __name__ == '__main__':
#     phone = input("账号:>")
#     psw = input("密码:>")
#     skland = SKLand()
#     skland.login_by_psw(phone_number=phone, password=psw)
#     skland.get_arknights_game_info()
#     skland.skland_sign()
