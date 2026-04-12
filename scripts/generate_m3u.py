import os

# 分类中文名 → M3U group-title 映射
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

CAT_TO_GROUP = {v: k for k, v in CAT_NAMES.items()}
for k in CAT_NAMES:
    CAT_TO_GROUP[k] = CAT_NAMES[k]

def make_group_tag(cat_prefix):
    return CAT_TO_GROUP.get(cat_prefix, cat_prefix)

if os.path.exists('live_ok.txt'):
    with open('live_ok.txt', 'r', encoding='utf-8') as f:
        raw_lines = [l.strip() for l in f if l.strip()]

    channel_count = 0
    with open('live_ok.m3u', 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n\n')
        current_group = None
        for line in raw_lines:
            # 新格式：分类行  分类名,#genre#
            if line.endswith(',#genre#'):
                cat = line[:-9].strip()
                group = make_group_tag(cat)
                if group != current_group:
                    f.write(f'#EXTGRP:{group}\n')
                    current_group = group
            # 新格式：频道行  名称,URL  （current_group 已由上方设置）
            elif ',' in line and current_group is not None:
                parts = line.split(',', 1)
                if len(parts) == 2:
                    name, url = parts
                    f.write(f'#EXTINF:-1 group-title="{current_group}",{name}\n')
                    f.write(f'{url}\n')
                    channel_count += 1
            # 旧格式兜底：  分类|名称,URL
            elif '|' in line:
                cat_part, rest = line.split('|', 1)
                if ',' in rest:
                    name, url = rest.split(',', 1)
                    group = make_group_tag(cat_part.strip())
                    if group != current_group:
                        f.write(f'#EXTGRP:{group}\n')
                        current_group = group
                    f.write(f'#EXTINF:-1 group-title="{group}",{name}\n')
                    f.write(f'{url}\n')
                    channel_count += 1

    print(f'M3U done ({channel_count} channels)')
