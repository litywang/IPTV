#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直播流检测模块
核心：频道测活时不能用代理
优化：
  1. 测活+测速合并为一次 HTTP 请求
  2. 5xx/连接错误自动重试（默认 1 次）
  3. 及时释放连接，避免 fd 泄漏
"""

import random
import time
import warnings
from typing import Dict, Optional

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用 HTTPS 证书验证警告（直播源大量使用自签名证书）
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

from ..config import Config
from ..core.models import Channel


class StreamChecker:
    """直播流检测器：测活+测速一次完成，无代理"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18'
        })
        # 禁用系统代理检测（Windows 注册表可能配置了代理）
        self.session.trust_env = False

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    def check(self, line: str) -> Optional[Dict]:
        """
        检测单条直播源，返回结果字典或 None。
        一次 HTTP 请求同时完成：
          - 可用性判断（状态码 + 媒体特征）
          - 速度测量（下载 SPEED_CHECK_BYTES 字节计时）
          - 质量评分（Content-Length + 速度 + 媒体类型）
        """
        try:
            name, url = line.split(',', 1)
            name = name.strip()
            url = url.strip()
        except ValueError:
            return None

        if not url.startswith(('http://', 'https://', 'udp://', 'rtp://', 'srt://')):
            return None

        is_overseas = self._is_overseas_name(name)
        timeout = Config.TIMEOUT_OVERSEAS if is_overseas else Config.TIMEOUT_CN

        result = self._check_with_http(url, timeout)
        if not result:
            return None

        return Channel(
            name=name, url=url, overseas=is_overseas,
            quality=result['quality'], speed=result['speed'], delay=result['delay']
        )

    # ------------------------------------------------------------------
    # 内部：HTTP 测活 + 测速（一次请求）
    # ------------------------------------------------------------------

    def _check_with_http(self, url: str, timeout: int) -> Optional[Dict]:
        """
        HTTP 流检测，支持 IPv6 和重定向。
        下载最多 SPEED_CHECK_BYTES 字节，同时完成可用性判断和速度测量。
        对 5xx 和连接错误自动重试。
        """
        max_retries = max(Config.RETRY_COUNT, 1)
        last_err = None

        for attempt in range(max_retries):
            try:
                headers = {
                    'User-Agent': random.choice(Config.UA_POOL),
                    'Range': f'bytes=0-{Config.SPEED_CHECK_BYTES - 1}',
                    'Accept': '*/*',
                    'Connection': 'keep-alive',
                }

                resp = self.session.get(
                    url, headers=headers, timeout=timeout,
                    stream=True, verify=False, allow_redirects=True
                )

                # 非 200/206 → 重试
                if resp.status_code not in (200, 206):
                    resp.close()
                    if resp.status_code >= 500:
                        last_err = f'status={resp.status_code}'
                        continue
                    return None

                # 读取内容（最多 SPEED_CHECK_BYTES），同时计时
                content = b''
                start = time.time()
                for chunk in resp.iter_content(chunk_size=8192):
                    content += chunk
                    if len(content) >= Config.SPEED_CHECK_BYTES:
                        break
                elapsed = time.time() - start
                resp.close()

                # 内容太少 → 无效
                if len(content) < 512:
                    last_err = 'content_too_short'
                    continue

                # Content-Type 是 HTML 且不是 M3U → 无效
                content_type = resp.headers.get('Content-Type', '').lower()
                if 'html' in content_type and not content.startswith(b'#EXTM3U'):
                    return None

                # 验证媒体特征
                if not self._is_media_content(content):
                    return None

                # 计算速度 (MB/s)
                speed_mbps = (
                    (len(content) / 1024 / 1024) / elapsed
                    if elapsed > 0 else 0.0
                )

                # 质量评分
                quality = self._estimate_quality(content, resp.headers, speed_mbps)

                return {
                    'quality': quality,
                    'speed': speed_mbps,
                    'delay': elapsed,
                }

            except (requests.ConnectionError, requests.Timeout) as e:
                last_err = str(e)
                continue
            except Exception:
                return None

        return None

    # ------------------------------------------------------------------
    # 媒体类型判断
    # ------------------------------------------------------------------

    @staticmethod
    def _is_media_content(content: bytes) -> bool:
        """判断内容是否为媒体流"""
        if len(content) < 16:
            return False
        if content.startswith(b'#EXTM3U'):
            return True
        if content[:1] == b'\x47' or content.find(b'\x47') < 188:
            return True
        if content[:3] == b'FLV':
            return True
        if len(content) >= 8 and content[4:8] == b'ftyp':
            return True
        return False

    # ------------------------------------------------------------------
    # 质量评分（综合 Content-Length + 速度 + 媒体类型）
    # ------------------------------------------------------------------

    @staticmethod
    def _estimate_quality(content: bytes, headers, speed_mbps: float) -> int:
        """
        综合质量评分 (0-100)：
          - 基础分 50
          - Content-Length 加分（>1MB +20, >500KB +10）
          - 下载速度加分（>5MB/s +20, >1MB/s +10）
          - M3U 索引文件 +5
          - CDN 类型加分（知名 CDN +5）
        """
        quality = 50

        # Content-Length 加分
        content_length = headers.get('Content-Length')
        if content_length:
            try:
                size = int(content_length)
                if size > 1_000_000:
                    quality += 20
                elif size > 500_000:
                    quality += 10
            except ValueError:
                pass

        # 下载速度加分
        if speed_mbps > 5.0:
            quality += 20
        elif speed_mbps > 1.0:
            quality += 10

        # M3U 索引文件额外加分
        if content.startswith(b'#EXTM3U'):
            quality += 5

        # CDN 类型加分
        cdn_headers = ('X-Cache', 'X-Cache-Hits', 'CF-Cache-Status',
                       'X-Served-By', 'X-Timer', 'Age')
        if any(h in headers for h in cdn_headers):
            quality += 5

        return min(quality, 100)

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _is_overseas_name(name: str) -> bool:
        name_upper = name.upper()
        return any(kw.upper() in name_upper for kw in Config.OVERSEAS_KEYWORDS)
