# -*- coding = utf-8 -*-
# @File:api.py
# @Author:Hycer_Lance
# @Time:2023/9/6 16:18
# @Software:PyCharm

class HyperGryphAPI:
    """
    鹰角网络相关api
    """
    # ---鹰角网络凭证获取---

    get_token_by_phone_psw = "https://as.hypergryph.com/user/auth/v1/token_by_phone_password"
    """
    -手机密码登录-
    /POST https://as.hypergryph.com/user/auth/v1/token_by_phone_password
    
    {"phone": "手机号","password": "密码"}
    
    返回 {"status":0,"type":"A","msg":"OK","data":{"token":"xxx"}}
    """

    send_phone_code = "https://as.hypergryph.com/general/v1/send_phone_code"
    """
    -验证码登录-
    发送验证码
    /POST https://as.hypergryph.com/general/v1/send_phone_code
    
    {"phone":"199********","type":2}
    
    返回 {"status":0,"type":"A","msg":"OK"}  
    """

    get_token_by_phone_code = "https://as.hypergryph.com/user/auth/v2/token_by_phone_code"
    """
    验证验证码
    /POST https://as.hypergryph.com/user/auth/v2/token_by_phone_code
    
    {"phone":"199********","code":"******"}
    
    返回 {"status":0,"type":"A","msg":"OK","data":{"token":"FQyXK4vy**********GkI7Rr"}}
    """

    # ---森空岛凭证获取（需先获取鹰角网络凭证）---

    get_oauth2_by_token = "https://as.hypergryph.com/user/oauth2/v2/grant"
    """
    获取OAuth2授权代码
    /POST https://as.hypergryph.com/user/oauth2/v2/grant
    
    {"token":"鹰角网络凭证","appCode":"4ca99fa6b56cc2ba","type":0}
    
    返回 {"status":0,"type":"A","msg":"OK","data":{"code":"****","uid":"12**********1"}}
    """

    get_cred_by_oauth2 = "https://zonai.skland.com/api/v1/user/auth/generate_cred_by_code"
    """
    获取Cred凭证
    /POST https://zonai.skland.com/api/v1/user/auth/generate_cred_by_code
    
    {"kind":1,"code":"****"}
    
    返回 {"code":0,"message":"OK","data":{"cred":"32位凭证","userId":"8****3"}}

    ---森空岛凭证校验(存活/有效性)---
    /POST https://zonai.skland.com/api/v1/user/auth/generate_cred_by_code
    
    header['cred'] = 32位cred
    
    返回 {"code":0,"message":"OK","data":{"policyList":[],"isNewUser":false}}
    """

    get_player_binding = "https://zonai.skland.com/api/v1/game/player/binding"
    """
    ---森空岛APP--- 获取玩家绑定角色列表 /GET https://zonai.skland.com/api/v1/game/player/binding 
    
    header = {"cred": ""} 
    
    返回 {
    "code":0,"message":"OK","data":{"list":[{"appCode":"arknights","appName":"明日方舟","bindingList":[{"uid":"68463675",
    "isOfficial":true,"isDefault":true,"channelMasterId":"1","channelName":"官服","nickName":"探姬#9315",
    "isDelete":false}],"defaultUid":""}]}}
    """

    get_game_info = "https://zonai.skland.com/api/v1/game/player/info?uid="
    """
    ---游戏内数据---
     /GET https://zonai.skland.com/api/v1/game/player/info?uid=?
     
     header['cred'] = 32位cred
     
     返回 {"code":0,"message":"OK","data":{很大很大的数据}}
    """

    skland_sign = "https://zonai.skland.com/api/v1/game/attendance"
    """---森空岛签到--- 
    /POST https://zonai.skland.com/api/v1/game/attendance 
    
    header['cred'] = 32位cred 
    
    {"uid": "uid","gameId": "channelMasterId"}
    
    返回 {"code": 0,"message": "OK","data": {"ts": "1693823939","awards": [{"resource": {
    "id": "4003,"type": "DIAMOND_SHD","name": "合成玉","rarity": 4},"count": 500,"type": "first"},{"resource": {"id": 
    "2002","type": "CARD_EXP","name": "初级作战记录","rarity": 2},"count": 3,"type": "daily"}]}}
    """
