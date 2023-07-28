<div align="center">
<img src="./icon.png" alt="icon" style="width: 250px;height: 250px">
</div>

<div align="center" style="font-size: 14px">
</div>

# <div align="center">🌙Mizuki-Bot</div>

<div align="center">

![Static Badge](https://img.shields.io/badge/Licence-MIT-blue)
![Static Badge](https://img.shields.io/badge/Python-%3E%3D3.8-orange)
![Static Badge](https://img.shields.io/badge/%E6%A1%86%E6%9E%B6-nonebot2-green)

</div>

------
## 目录

* [简介](#简介)
* [项目结构](#项目结构)
* [功能](#功能)
* [部署](#部署)
    + [下载项目文件](#下载项目文件)
    + [修改bot配置文件](#修改bot配置文件)
    + [安装项目依赖](#安装项目依赖)
    + [下载配置go-cqhttp](#下载配置go-cqhttp)
    + [启动bot](#启动bot)
    + [Docker部署](#Docker部署)
* [更新日志](#更新日志)

## [简介](#简介)

✨Mizuki-Bot 是一款基于Python第三方库Nonebot开发以学习为目的的明日方舟主题的娱乐QQ机器人✨

[Nonebot官网](https://v2.nonebot.dev/)

## [项目结构](#项目结构)

```
├─.env //配置文件
├─.gitignore
├─bot.py //bot启动文件
├─pyproject.toml
├─README.md
├─mizuki
|   ├─plugins
|   | //插件目录
├─database
|    ├─Mizuki_DB.db
|    └// 数据库目录
├─data
|  ├─plugins
|  //插件数据目录
```

## [功能](#功能)
```
√ 聊天
√ AI作图
√ 日常签到
√ 货币系统
  方舟铁道主题玩法
    √ 抽卡
    √ 养成
    √ 战斗
  农场主题玩法
√ 点歌
√ help菜单
√ 发图

......
更多功能开发中
```

## [部署](#部署)

*请确保你的python环境版本>=3.8*

### [下载项目文件](#下载项目文件)

在本地创建你的项目文件夹，并将项目clone到该文件夹

`git clone https://github.com/LanceHE6/Mizuki-Bot`

### [修改bot配置文件](#修改bot配置文件)

编辑.env文件并修改相应配置

```
DRIVER=~fastapi+~httpx+~aiohttp 频道前置驱动器
HOST=127.0.0.1  # 主机地址
PORT=13570 # 监听端口号
FASTAPI_RELOAD=false

SUPERUSERS=["2765543491"]  # 配置 NoneBot 超级用户
NICKNAME=["Mizuki", "水月", "mizuki"]  # 配置机器人的昵称
COMMAND_START=["/"]  # 配置命令起始字符

# 频道机器人相关
QQGUILD_BOTS='
[
  {
    "id": "",
    "token": "",
    "secret": "",
    "intent": {
      "guild_messages": true,
      "at_messages": false
    }
  }
]
'
QQGUILD_IS_SANDBOX=false

#ArkRail相关
AUTO_CHECK_RES=false  # 启动自动检查图片资源

#ChatGPT相关
API_KEY=""  # api key sk-xxxxxx
ENABLE_PROXY=false  # 是否启用代理
PROXY=""  # 代理地址 https://example.com
TIMEOUT=600  # 定时清理用户会话 xx秒
PERSONALITY=""  # ChatGPT 人格描述

```

### [安装项目依赖](#安装项目依赖)

1.在项目文件夹中使用pip安装项目依赖

`pip install -r -requirements.txt`

2.安装playwright依赖

`playwright install`

### [下载配置go-cqhttp](#下载配置go-cqhttp)

*（如使用插件中的go-cqhttp可忽略此项）*

1.在[Releases ](https://github.com/Mrs4s/go-cqhttp/releases)页面下载对应版本并解压

2.选择通信方式0 3生成配置文件

3.编辑config.yml文件

注意修改最后的反向WS设置

	`  - ws-reverse:
	  # 反向WS Universal 地址
	  # 注意 设置了此项地址后下面两项将会被忽略
	  universal: ws://127.0.0.1:13570/onebot/v11/ws/ # 将主机地址和端口号与.env文件中保持一致
	  # 反向WS API 地址
	  api: ws://your_websocket_api.server
	  # 反向WS Event 地址
	  event: ws://your_websocket_event.server
	  # 重连间隔 单位毫秒
	  reconnect-interval: 3000
	  middlewares:
	    <<: *default # 引用默认中间件`

4.保存并重新启动go_cqhttp

### [启动bot](#启动bot)

运行项目文件的bot.py 或者使用脚手架 `nb run`启动

不出意外的话bot就能与go-cqhttp正常连接

## [Docker部署](#Docker部署)

请确保已正确安装Docker并能正常使用

### 构建镜像

克隆项目后，在Dockerfile同级目录下使用构建镜像指令

`docker build -t 镜像名 .`

*注意指令后面的`.`不要漏掉*

或者使用下面的指令拉取已经构建好的镜像

`docker pull registry.cn-hangzhou.aliyuncs.com/hycer-images-hub/mizuki-env`

随后等待镜像构建完成

## 创建启动容器

镜像构建完成后使用`docker run 镜像名`创建并启动容器
注意将整个项目目录挂载出来，以便于数据保存和更新

*暂时未解决端口映射后无法访问go-cqhttp的GUI网页问题*
*所以请将go-cqhttp提前在外配置完成后再运行*

------

## [更新日志](#更新日志)

#### *V1.0.1*

*23/7/24*

refactor.重构了重启函数

#### *V1.0.2*

*23/7/27*

feat.新增能单条执行cmd指令模块

feat.新增ChatGPT Dall.E绘图

update.优化更新模块

#### *V1.0.3*

*23/7/28*
