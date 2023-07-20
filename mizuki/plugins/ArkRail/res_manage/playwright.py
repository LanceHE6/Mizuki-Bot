# -*- coding = utf-8 -*-
# @File:playwright.py
# @Author:Hycer_Lance
# @Time:2023/6/9 15:27
# @Software:PyCharm

import json
import re

from nonebot.log import logger

from playwright.async_api import async_playwright


async def playwright_get_release_page():
    """
    使用playWright访问github仓库release
    :return: json格式的release内容
    """
    logger.info("[ArkRail]正在访问仓库Release")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)

    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://api.github.com/repos/LanceHE6/Mizuki-Bot/releases")

    page_content = await page.content()
    await page.close()
    await context.close()
    await browser.close()
    await playwright.stop()  # 手动关闭playWright，否则会报警告ValueError: I/O operation on closed pipe
    release = re.findall(r'<pre style="word-wrap: break-word; white-space: pre-wrap;">(.*?)</pre>',
                         page_content, re.DOTALL)

    return json.loads(release[0])
