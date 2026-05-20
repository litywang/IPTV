#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
频道数据模型
用 dataclass 替代裸 Dict，提升类型安全和代码可读性
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Channel:
    """直播频道"""
    name: str
    url: str
    quality: int = 0
    speed: float = 0.0          # MB/s
    delay: float = 0.0          # 响应延迟秒
    overseas: bool = False      # 是否境外频道
    direct_ok: bool = True      # 直连二验是否通过
    category: str = ""          # 分类（由 NameProcessor.classify 填充）

    @property
    def is_valid(self) -> bool:
        return self.quality > 0 and self.direct_ok

    def __repr__(self):
        return f"Channel({self.name!r}, q={self.quality}, s={self.speed:.2f}MB/s)"
