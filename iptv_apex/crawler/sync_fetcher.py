#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步网络源拉取器
使用 core.parser 统一解析 M3U/TXT 格式
"""

import random
from typing import List, Optional

import requests

from ..config import Config
from ..core.parser import parse as parse_playlist


class WebSourceFetcher:
    """同步拉取网络源"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(Config.UA_POOL)
        })
        self.session.trust_env = False

    def fetch(self, url: str, proxy: Optional[str] = None, timeout: int = 15) -> List[str]:
        """拉取并解析源列表，返回 ['name,url', ...]"""
        try:
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            resp = self.session.get(
                url, proxies=proxies, timeout=timeout, verify=False,
                headers={'Accept': '*/*', 'User-Agent': random.choice(Config.UA_POOL)}
            )
            resp.raise_for_status()

            # 强制使用 UTF-8 解码
            if resp.encoding and resp.encoding.lower() != 'utf-8':
                content = resp.content.decode('utf-8', errors='replace')
            else:
                content = resp.text

            # 统一解析
            channels = parse_playlist(content)
            return [f"{name},{url}" for name, url in channels]

        except Exception:
            return []
