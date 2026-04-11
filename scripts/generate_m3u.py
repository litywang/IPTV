import os

# 分类中文名 → M3U group-title 映射（与 IPTV-Apex-dzh.py 的 CATEGORY_ORDER 一致）
CAT_NAMES = {
    "4K專區": "4K",
    "港澳台頻": "港澳台",
    "影視劇集": "影视剧",
    "央視頻道": "央视",
    "衛視綜藝": "卫视综艺",
    "體育賽事": "体育",
    "少兒動漫": "少儿动漫",
    "新聞資訊": "新闻",
    "音樂頻道": "音乐",
    "其他頻道": "其他",
}

# 反向映射：中文分类名 → group-title
CAT_TO_GROUP = {v: k for k, v in CAT_NAMES.items()}
# 同时保留英文 key 作为 group-title 的友好名称
for k in CAT_NAMES:
    CAT_TO_GROUP[k] = CAT_NAMES[k]

def make_group_tag(cat_prefix):
    """从 cat_prefix 推断 M3U group-title"""
    return CAT_TO_GROUP.get(cat_prefix, cat_prefix)

if os.path.exists('live_ok.txt'):
    with open('live_ok.txt', 'r', encoding='utf-8') as f:
        raw_lines = [l.strip() for l in f if l.strip()]

    with open('live_ok.m3u', 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n\n')
        current_group = None
        for line in raw_lines:
            if '|' not in line:
                continue
            cat_prefix, rest = line.split('|', 1)
            if ',' not in rest:
                continue
            name, url = rest.split(',', 1)
            group = make_group_tag(cat_prefix.strip())
            if group != current_group:
                f.write(f'#EXTGRP:{group}\n')
                current_group = group
            f.write(f'#EXTINF:-1 group-title="{group}",{name}\n')
            f.write(f'{url}\n')

    print(f'M3U done ({len(raw_lines)} channels)')
