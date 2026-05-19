#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPTV-Apex 重构版入口
核心目标：输出频道在中国大陆能播放
代理策略：订阅拉取可用代理，频道测活不用代理
"""

import argparse
import asyncio
import io
import os
import sys

# 修复 Windows 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

from iptv_apex.config import Config
from iptv_apex.core.pipeline import IPTVChecker


def main():
    parser = argparse.ArgumentParser(description="IPTV-Apex v2.0")
    parser.add_argument('-w', '--workers', type=int, default=80, help='并发线程数')
    parser.add_argument('-t', '--timeout', type=int, default=8, help='单源超时秒数')
    parser.add_argument('--no-local', action='store_true', help='跳过本地 paste.txt')
    parser.add_argument('--no-web-fetch', action='store_true', help='跳过网络爬取')
    parser.add_argument('--no-cache', action='store_true', help='禁用缓存')
    parser.add_argument('--no-speed-check', action='store_true', help='关闭速度检测')
    parser.add_argument('--incremental', action='store_true', help='增量模式')
    parser.add_argument('--async-crawl', action='store_true', help='使用异步爬虫')
    args = parser.parse_args()

    # 加载配置
    Config.load_from_file()
    Config.init_compiled_rules()

    # 应用命令行覆盖
    if args.no_web_fetch:
        Config.ENABLE_WEB_FETCH = False
        Config.ENABLE_WEB_CHECK = False
    if args.no_cache:
        Config.ENABLE_CACHE = False
    if args.no_local:
        Config.ENABLE_LOCAL_CHECK = False
    if args.no_speed_check:
        Config.ENABLE_SPEED_CHECK = False

    # 代理策略：env_config.bat 设置代理环境变量
    # - 拉源（sync_fetcher/async_crawler）：显式传 proxy 参数，走代理 ✅
    # - 测活（stream.py）：trust_env=False，不走代理 ✅
    # - 直连二验（direct.py）：trust_env=False，不走代理 ✅
    # - 推送（sync_to_gist.py）：继承环境变量，走代理 ✅
    # 因此不再清空环境变量，避免误杀推送阶段的代理

    checker = IPTVChecker()

    if args.incremental or args.async_crawl:
        asyncio.run(checker.run_async(args))
    else:
        checker.run(args)


if __name__ == '__main__':
    main()
