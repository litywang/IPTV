import os
import sys
import subprocess
import yaml

# ---------- Configuration ----------
# Load optional YAML config for region whitelist, CDN proxy mapping, and ffprobe timeout.
# If config.yaml is missing or malformed, defaults apply.
CONFIG_PATH = 'config.yaml'
DEFAULT_CONFIG = {
    'allowed_regions': ['CN', 'HK', "TW"],  # keep mainland, Hong Kong, Taiwan
    'cdn_proxy': {},  # e.g., {'https://global.example.com/': 'https://cn.example.com/'}
    'ffprobe': {
        'timeout_ms': 8000,  # 8 seconds max per stream check
    },
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as cfg_f:
                raw = yaml.safe_load(cfg_f) or {}
                # Merge with defaults – missing keys fall back to defaults.
                merged = DEFAULT_CONFIG.copy()
                merged.update({k: raw.get(k, v) for k, v in DEFAULT_CONFIG.items()})
                return merged
        except Exception as exc:
            print(f'Warning: failed to load config.yaml ({exc}), using defaults')
    return DEFAULT_CONFIG

CONFIG = load_config()

# ---------- Helper utilities ----------

def apply_cdn_proxy(url: str) -> str:
    """Replace a URL prefix according to the cdn_proxy map.
    The map keys are exact prefixes; the longest matching prefix wins.
    """
    proxy_map = CONFIG.get('cdn_proxy', {})
    if not proxy_map:
        return url
    # Sort prefixes by length descending to prefer longest match.
    for src_prefix in sorted(proxy_map.keys(), key=len, reverse=True):
        if url.startswith(src_prefix):
            return url.replace(src_prefix, proxy_map[src_prefix], 1)
    return url

def is_stream_accessible(url: str) -> bool:
    """Check reachability with ffprobe.
    Returns True if ffprobe exits with code 0 within the configured timeout.
    """
    timeout_sec = CONFIG.get('ffprobe', {}).get('timeout_ms', 8000) / 1000.0
    try:
        # ffprobe returns 0 on success (can read some metadata).
        subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout_sec,
            check=True,
        )
        return True
    except Exception:
        return False

# 分类中文名 -> M3U group-title 映射
CAT_NAMES = {
    "4K专区": "4K",
    "港澳台频": "GDHKTW",
    "影视剧集": "Movies",
    "央视频道": "CCTV",
    "卫视频道": "Variety",
    "体育赛事": "Sports",
    "少儿动漫": "Kids",
    "新闻资讯": "News",
    "音乐频道": "Music",
    "其他频道": "Other",
}

def make_group_tag(cat_prefix):
    """Chinese category name -> English group-title"""
    return CAT_NAMES.get(cat_prefix, cat_prefix)

if os.path.exists('live_ok.txt'):
    try:
        with open('live_ok.txt', 'r', encoding='utf-8') as f:
            raw_lines = [l.strip() for l in f if l.strip()]

        if not raw_lines:
            print('live_ok.txt is empty, skip M3U generation')
            sys.exit(0)

        channel_count = 0
        with open('live_ok.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n\n')
            current_group = None
            for line in raw_lines:
                # 分类行：分类名,#genre#
                if line.endswith(',#genre#'):
                    cat = line[:-9].strip()
                    group = make_group_tag(cat)
                    if group != current_group:
                        f.write(f'#EXTGRP:{group}\n')
                        current_group = group
                # 频道行：名称,URL
                elif ',' in line and current_group is not None:
                    name, url = line.split(',', 1)
                    url = url.strip()
                    # Apply CDN proxy rewriting if configured.
                    url = apply_cdn_proxy(url)
                    # Only keep streams reachable from China (or HK/TW) per whitelist.
                    if is_stream_accessible(url):
                        f.write(f'#EXTINF:-1 group-title="{current_group}",{name}\n')
                        f.write(f'{url}\n')
                        channel_count += 1
        print(f'M3U done ({channel_count} channels)')
    except Exception as e:
        print(f'M3U generation error: {e}')
        sys.exit(1)
else:
    print('live_ok.txt not found, skip M3U generation')
    sys.exit(0)
