FROM python:3.10
EXPOSE 13570
WORKDIR /Mizuki
COPY . /Mizuki
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -r requirements.txt
RUN nb plugin install nonebot-plugin-gocqhttp
RUN playwright install
RUN playwright install-deps # 安装Linux playwright依赖
CMD ["python", "bot.py"]
