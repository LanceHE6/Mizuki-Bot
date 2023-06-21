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
  * [简介](#span-idjump1-简介-span)
  * [项目结构](#span-idjump2-项目结构-span)
  * [功能](#span-idjump3-功能-span)
  * [部署](#span-idjump4-部署-span)
    + [下载项目文件](#span-idjump4-1-下载项目文件)
    + [修改bot配置文件](#span-idjump4-2-修改bot配置文件)
    + [安装项目依赖](#span-idjump4-3-安装项目依赖)
    + [下载配置go-cqhttp](#span-idjump4-4-下载配置go-cqhttp)
    + [启动bot](#span-idjump4-5-启动bot)
  * [更新日志](#span-idjump5-更新日志-span)



## <span id="jump1">简介</span>

✨Mizuki-Bot 是一款基于Python第三方库Nonebot开发以学习为目的的明日方舟主题的娱乐QQ机器人✨

[Nonebot官网](https://v2.nonebot.dev/)



## <span id="jump2">项目结构</span>

```
├─.env //配置文件
├─.gitignore
├─bot.py //bot启动文件
├─docker-compose.yml
├─Dockerfile
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

## <span id="jump3">功能</span>
```
√ 聊天
√ 日常签到
√ 货币系统
  方舟铁道主题玩法
    √ 抽卡
    √ 养成
      战斗
  农场主题玩法
√ help菜单

......
更多功能开发中
```
## <span id="jump4">部署</span>

*请确保你的python环境版本>=3.8*

### <span id="jump4-1">下载项目文件

在本地创建你的项目文件夹，并将项目clone到该文件夹

`git clone https://github.com/LanceHE6/Mizuki-Bot`

### <span id="jump4-2">修改bot配置文件

编辑.env文件并修改相应配置
```
HOST=127.0.0.1  # 主机地址
PORT=13570 # 监听端口号
FASTAPI_RELOAD=false

SUPERUSERS=["2765543491"]  # 配置 NoneBot 超级用户
NICKNAME=["Mizuki", "水月", "mizuki"]  # 配置机器人的昵称
COMMAND_START=["/"]  # 配置命令起始字符

#ArkRail相关
AUTO_CHECK_RES=false  # 启动自动检查图片资源

#ChatGPT相关
API_KEY=""  # api key sk-xxxxxx
ENABLE_PROXY=false  # 是否启用代理
PROXY=""  # 代理地址 https://example.com
TIMEOUT=600  # 定时清理用户会话 xx秒
PERSONALITY=""  # ChatGPT 人格描述
```

### <span id="jump4-3">安装项目依赖

在项目文件夹中使用pip安装项目依赖

`pip install -r -requirements.txt`

### <span id="jump4-4">下载配置go-cqhttp（如使用插件中的go-cqhttp可忽略此项）

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

### <span id="jump4-5">启动bot

运行项目文件的bot.py

不出意外的话bot就能与go-cqhttp正常连接

------

## <span id="jump5">更新日志</span>

暂未发布第一版
