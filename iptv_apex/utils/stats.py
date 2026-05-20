#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计信息管理
支持历史运行数据持久化和健康度评分
"""

import json
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Optional


class StatsManager:
    """统计信息持久化 + 历史可用率追踪"""

    def __init__(self, stats_file: Path):
        self.stats_file = stats_file
        self.data: Dict[str, Any] = {}
        self._load_history()

    def _load_history(self):
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
        except Exception:
            traceback.print_exc()
            self.data = {}

    def update(self, key: str, value: Any):
        self.data[key] = value

    def save(self):
        try:
            self.data['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception:
            traceback.print_exc()

    def print_comparison(self):
        """打印与上次运行的对比"""
        if not self.data:
            return
        print(f"\n{'='*60}")
        print("📊 统计对比")
        for key, value in self.data.items():
            if key == 'last_updated':
                continue
            print(f"  {key}: {value}")

    # ------------------------------------------------------------------
    # 历史可用率追踪
    # ------------------------------------------------------------------

    def record_url_result(self, url: str, success: bool):
        """记录 URL 的可用/不可用结果"""
        history = self.data.setdefault('url_history', {})
        entry = history.get(url, {'success': 0, 'fail': 0, 'last_seen': ''})
        if success:
            entry['success'] += 1
        else:
            entry['fail'] += 1
        entry['last_seen'] = time.strftime('%Y-%m-%d %H:%M:%S')
        history[url] = entry

    def get_url_reliability(self, url: str) -> float:
        """
        获取 URL 的历史可用率 (0.0 ~ 1.0)
        返回 0.0 表示无历史记录
        """
        history = self.data.get('url_history', {})
        entry = history.get(url)
        if not entry:
            return 0.0
        total = entry['success'] + entry['fail']
        if total == 0:
            return 0.0
        return entry['success'] / total

    def cleanup_history(self, max_entries: int = 50000):
        """清理历史记录，只保留最近的 N 条"""
        history = self.data.get('url_history', {})
        if len(history) <= max_entries:
            return
        # 按 last_seen 排序，保留最近的
        sorted_items = sorted(history.items(), key=lambda x: x[1].get('last_seen', ''), reverse=True)
        self.data['url_history'] = dict(sorted_items[:max_entries])
