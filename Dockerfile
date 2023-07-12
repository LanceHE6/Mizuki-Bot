FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install nb-cli

RUN pip install -r requirements.txt

RUN playwright install

RUN pip install nonebot-adapter-onebot

RUN pip install nonebot-adapter-qqguild

RUN pip install nonebot2[fastapi]

RUN pip install nonebot2[httpx]

RUN pip install nonebot2[aiohttp]

CMD ["python", "bot.py"]
