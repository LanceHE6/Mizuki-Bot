# -*- coding = utf-8 -*-
# @File:__init__.py
# @Author:Hycer_Lance
# @Time:2023/6/4 10:36
# @Software:PyCharm

from .update import *
from .utils import check_image_res

asyncio.run(check_image_res())
