#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一解析器：M3U / M3U8 / TXT → [(name, url), ...]

三处解析逻辑（parser / sync_fetcher / async_crawler）统一到此模块。
调用方只需 parse(content) 即可获得标准化的 (name, url) 列表。
"""

import re
from typing import List, Tuple, Optional


# ---------------------------------------------------------------------------
# 公开接口
# ---------------------------------------------------------------------------

def parse(content: str) -> List[Tuple[str, str]]:
    """
    自动识别格式并解析，返回 [(频道名, URL), ...]。

    支持格式：
      - M3U/M3U8  : #EXTINF:...,name\\nurl
      - TXT       : name,url
      - 旧格式    : category|name,url

    优先级：M3U > TXT > 旧格式
    """
    if not content:
        return []

    # 检测 M3U
    if '#EXTM3U' in content[:1024] or '#EXTINF' in content[:1024]:
        return _parse_m3u(content)

    # 检测旧格式（含 | 分隔符）
    if '|' in content[:512] and ',' in content[:512]:
        return _parse_old_format(content)

    # 默认 TXT
    return _parse_txt(content)


def parse_m3u(content: str) -> List[Tuple[str, str]]:
    """显式解析 M3U/M3U8 格式"""
    return _parse_m3u(content)


def parse_txt(content: str) -> List[Tuple[str, str]]:
    """显式解析 TXT 格式（name,url）"""
    return _parse_txt(content)


# ---------------------------------------------------------------------------
# M3U 解析
# ---------------------------------------------------------------------------

def _parse_m3u(content: str) -> List[Tuple[str, str]]:
    results = []
    lines = content.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            name = _extract_m3u_name(line)
            # 下一行是 URL
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url and not url.startswith('#') and url.startswith(('http://', 'https://')):
                    results.append((name, url))
                i += 2
                continue
        elif line and not line.startswith('#') and ',' in line:
            # TXT 格式的退化处理（M3U 文件中偶尔混有 TXT 行）
            name, url = _split_name_url(line)
            if url:
                results.append((name, url))
        i += 1
    return results


def _extract_m3u_name(extinf_line: str) -> str:
    """从 #EXTINF 行提取频道名"""
    # 优先 tvg-name
    m = re.search(r'tvg-name="([^"]*)"', extinf_line)
    if m:
        return m.group(1).strip()
    # 其次逗号后的 displayName
    if ',' in extinf_line:
        return extinf_line.split(',', 1)[1].strip()
    return '未知频道'


# ---------------------------------------------------------------------------
# TXT 解析
# ---------------------------------------------------------------------------

def _parse_txt(content: str) -> List[Tuple[str, str]]:
    results = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.endswith(',#genre#'):
            continue  # 分类标记行，跳过
        name, url = _split_name_url(line)
        if url:
            results.append((name, url))
    return results


# ---------------------------------------------------------------------------
# 旧格式解析（category|name,url）
# ---------------------------------------------------------------------------

def _parse_old_format(content: str) -> List[Tuple[str, str]]:
    results = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or ',' not in line:
            continue
        if '|' in line:
            _, rest = line.split('|', 1)
            name, url = _split_name_url(rest)
        else:
            name, url = _split_name_url(line)
        if url:
            results.append((name, url))
    return results


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------

def _split_name_url(line: str) -> Tuple[str, str]:
    """将 'name,url' 拆分为 (name, url)，url 必须以 http 开头"""
    if ',' not in line:
        return line.strip(), ''
    parts = line.split(',', 1)
    name = parts[0].strip()
    url = parts[1].strip()
    if not url.startswith(('http://', 'https://')):
        return name, ''
    return name, url
