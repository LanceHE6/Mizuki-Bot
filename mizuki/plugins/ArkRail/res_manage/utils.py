# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/6/9 15:43
# @Software:PyCharm

import asyncio
import datetime
import json
import shutil
import time
import zipfile
import hashlib

import requests
import os
from tqdm import tqdm
from pathlib import Path

from .playwright import playwright_get_release_page

from nonebot.log import logger
from nonebot import get_driver

img_resources_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res'
res_version_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res_manage' / 'res_version_data.json'

target_hash = "10c63d4c164399ec48b7fb1760668261"

async def check_release():
    """
    检查仓库release，获取asset信息
    :return: 成功则返回包含图片资源下载地址和版本信息的列表，失败
            则返回字符串信息
    """
    try:
        release_page = (await playwright_get_release_page())
    except KeyError:
        logger.warning("[ArkRail]GitHub API请求次数过多，已达限制")
        return
    latest_release = release_page[0]
    version = latest_release['tag_name']
    assets = latest_release['assets']
    download_url = assets[0]['browser_download_url']
    update_log = latest_release['body']
    return [download_url, version, update_log]


async def zip_extract(zip_file: Path, extract_path: Path, reserve_zip: bool = False):
    """
    解压文件
    :param zip_file: 压缩包
    :param extract_path: 解压路劲
    :param reserve_zip: 是否保留压缩包
    :return:
    """

    # 打开 ZIP 文件
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        # 获取 ZIP 文件中的文件列表
        file_list = zip_ref.namelist()
        # 设置进度条
        progress_bar = tqdm(total=len(file_list), unit="file")
        # 遍历 ZIP 文件中的每个文件
        for file_info in zip_ref.infolist():
            # 重新编码防止中文乱码
            file_info.filename = file_info.filename.encode('cp437').decode('gbk')
            # 解压文件到目标路径
            zip_ref.extract(file_info, extract_path)
            progress_bar.update(1)
            await asyncio.sleep(0.01)
        # 关闭进度条
        progress_bar.close()
    if not reserve_zip:
        os.remove(zip_file)
    logger.info(f'[ArkRail]资源解压完成')


async def download(download_url: str, save_path: Path, version: str, update_log: str):
    """
    下载资源
    :param update_log: 更新内容
    :param download_url: 下载地址
    :param save_path: 保存路劲
    :param version: 版本信息，保存于json文件中，用于检查更新
    :return:
    """
    while True:
        if not os.path.exists(save_path):
            os.mkdir(save_path)

        # 5秒超时，采用代理服务器下载
        try:
            response = requests.get(download_url, stream=True, timeout=5)
        except requests.exceptions.SSLError as e:
            logger.warning(f"[ArkRail]{e}")
            response = requests.get(download_url, stream=True, timeout=5, verify=False)
        # 检查响应状态码
        if response.status_code != 200:
            logger.warning('[ArkRail]资源下载超时，更换为代理服务器下载')
            proxy_url = 'https://ghproxy.com/'
            # 请求失败，添加代理服务器地址并重试
            retry_url = proxy_url + download_url
            response = requests.get(retry_url, stream=True)
        if response.status_code == 200:
            # 提取文件名
            filename = download_url.split('/')[-1]
            # 获取文件大小
            file_size = int(response.headers.get('Content-Length', 0))
            # 设置进度条
            progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, colour='blue')
            # 保存文件到本地
            with open(save_path / filename, 'wb') as file:
                for data in response.iter_content(chunk_size=1024):
                    # 更新进度条
                    progress_bar.update(len(data))
                    file.write(data)
                file.close()

            # 关闭进度条
            progress_bar.close()
            with open(res_version_data, 'w', encoding='utf-8') as data_file:
                now_time = datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')
                version_data = {
                    "res_name": filename,
                    "version": version,
                    "download_time": now_time,
                    "update_log": update_log
                }
                json.dump(version_data, data_file, indent=4, ensure_ascii=False)
                data_file.close()

            logger.info(f'[ArkRail]下载完成: {filename}')
            time.sleep(2)
            logger.info(f'[ArkRail]开始解压资源')
            await zip_extract(img_resources_path / filename, img_resources_path)
            logger.info(f'[ArkRail]正在校验文件完整性')
            time.sleep(2)
            file_hash = calculate_total_hash(img_resources_path)
            if target_hash == file_hash:
                logger.info(f'[ArkRail]文件校验通过')
                break
            else:
                logger.info(f'[ArkRail]文件校验未通过,开始重新下载资源')
                continue
        else:
            logger.warning(f'[ArkRail]下载资源文件失败HTTP CODE:{response.status_code} 3s后重试')
            time.sleep(3)
            continue


async def check_image_res():
    """
    检查图片资源
    :return:
    """
    logger.info('[ArkRail]开始检查图片资源')
    if os.path.exists(img_resources_path) \
            and len(os.listdir(img_resources_path)) != 0 \
            and os.path.exists(res_version_data):
        logger.info('[ArkRail]图片资源已存在')
        if not get_driver().config.auto_check_res:
            return
        with open(res_version_data, 'r', encoding='utf-8') as data:
            local_data = json.load(data)
            data.close()
        release_data = await check_release()
        if local_data["version"] != release_data[1]:
            logger.info("[ArkRail]图片资源存在更新，开始更新资源")
            shutil.rmtree(img_resources_path)
            await download(release_data[0], img_resources_path, release_data[1], release_data[2])
            logger.info('[ArkRail]图片资源更新完成')
        else:
            logger.info("[ArkRail]已是最新版资源")

    elif os.path.exists(img_resources_path) and not os.path.exists(res_version_data):
        logger.warning('[ArkRail]未检测到图片资源版本信息，即将开始重新下载资源')
        shutil.rmtree(img_resources_path)
        release_data = await check_release()
        await download(release_data[0], img_resources_path, release_data[1], release_data[2])
    else:
        logger.warning('[ArkRail]未检测到图片资源信息即将开始下载资源')
        release_data = await check_release()
        await download(release_data[0], img_resources_path, release_data[1], release_data[2])


def calculate_file_hash(file_path):
    hash_algo = hashlib.md5()

    with open(file_path, 'rb') as file:
        # 逐块读取文件并更新哈希值
        for chunk in iter(lambda: file.read(4096), b''):
            hash_algo.update(chunk)

    # 返回文件的哈希值
    return hash_algo.hexdigest()


def calculate_total_hash(directory_path):
    # 获取目录下的所有文件（包括子目录中的文件）
    all_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)

    # 对所有文件的哈希值进行计算，并组合成一个总的哈希值
    total_hash_algo = hashlib.md5()
    for file_path in all_files:
        file_hash = calculate_file_hash(file_path)
        total_hash_algo.update(file_hash.encode())

    # 返回总的哈希值
    return total_hash_algo.hexdigest()
