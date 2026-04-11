#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给 IPTV-Apex-dzh.py 注入「直连二验」补丁
在测速步骤之后、写入结果之前，对每个有效源做一次无代理的直连检测
被墙的海外源 / token过期的CDN源 / 直连超时的源 → 标记为失效
"""
import re, sys

TARGET = r"C:\tools\IPTV\IPTV-Apex-dzh.py"
BACKUP = r"C:\tools\IPTV\IPTV-Apex-dzh.py.bak_direct_recheck"

with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

# 检查是否已打过补丁
if "直连二验" in content or "direct_recheck" in content:
    print("补丁已存在，跳过")
    sys.exit(0)

# 备份
with open(BACKUP, "w", encoding="utf-8") as f:
    f.write(content)
print(f"备份已保存: {BACKUP}")

# ===== 找到目标位置 =====
# 在 "# 6. 写入结果文件" 前面插入直连二验步骤
# 注意：代码里这行是 "# 6. 写入结果文件"（中文注释）
insert_marker = '        # 6. 写入结果文件'
if insert_marker not in content:
    print("ERROR: 未找到插入点!")
    sys.exit(1)

patch_code = r'''        # ===== 直连二验（核心修复）=====
        # 背景：测活走代理(绕过GFW)，但用户直连时被墙的源应过滤掉
        # 策略：对所有候选源做一次无代理的轻量级检测（HEAD + 3秒超时）
        # 效果：过滤 海外域名/GFW封禁/token过期 三类无效源
        self.logger.info(f"直连二验: 检查 {sum(len(v) for v in cat_map.values())} 个候选源是否大陆直连...")
        try:
            import requests as _req
            _recheck_removed = 0
            _recheck_tested = 0
            for _cat_key in list(cat_map.keys()):
                _still_valid = []
                for _ch in cat_map[_cat_key]:
                    _url = _ch.get('url', '')
                    if not _url:
                        _still_valid.append(_ch)
                        continue
                    # 跳过多播/UDP源（直连不可测）
                    if _url.startswith(('udp://', 'rtp://', 'srt://')):
                        _still_valid.append(_ch)
                        continue
                    # 跳过国内已知可直连的CDN域名（白名单加速）
                    _KNOWN_DIRECT = {
                        'live.264788', 'goodiptv', '163189', 'jdshipin',
                        'tencentplay', 'bp-resource', 'bestv', 'amucn',
                        'xryo', 'migu', 'dsj', 'ottiptv', 'iill',
                        'aktv', '061833', '888', 'ott.mobai', 'mobai',
                        'cdn8.', 'cdn6.', 'cdn12.', 'cdn.', 'cos.',
                        'tencent.', 'aliyun', 'alicdn', 'ali-cdn',
                        'speedws', 'freetv.fun',  # 这两个可直连
                    }
                    _netloc = _url.split('://', 1)[-1].split('?')[0].split('/')[0].lower()
                    _is_known_direct = any(_k in _netloc for _k in _KNOWN_DIRECT)
                    if _is_known_direct:
                        _still_valid.append(_ch)
                        continue
                    _recheck_tested += 1
                    try:
                        _r = _req.head(_url, timeout=4, verify=False,
                                        allow_redirects=True,
                                        headers={'User-Agent': 'Mozilla/5.0 (compatible; IPTV-Checker/1.0)'})
                        _recheck_tested += 0  # already counted
                        if _r.status_code < 500:
                            _still_valid.append(_ch)
                        else:
                            _recheck_removed += 1
                    except Exception:
                        _recheck_removed += 1
                cat_map[_cat_key] = _still_valid
            # 删除空分类
            for _k in list(cat_map.keys()):
                if not cat_map[_k]:
                    del cat_map[_k]
            self.stats['filtered_by_recheck'] = _recheck_removed
            self.stats['valid'] = sum(len(v) for v in cat_map.values())
            if _recheck_removed > 0:
                self.logger.info(f"直连二验: 过滤 {_recheck_removed} 个不可直连源 (已测 {_recheck_tested} 个)")
            else:
                self.logger.info(f"直连二验: 全部 {_recheck_tested} 个源均可直连")
        except Exception as _e:
            self.logger.warning(f"直连二验异常，跳过: {_e}")

'''

new_content = content.replace(insert_marker, patch_code + insert_marker)

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"补丁已注入，共写入 {len(new_content) - len(content)} 字节")
print("验证语法...")
import py_compile
try:
    py_compile.compile(TARGET, doraise=True)
    print("✅ 语法检查通过")
except py_compile.PyCompileError as e:
    print(f"❌ 语法错误: {e}")
    # 恢复
    with open(BACKUP, "r", encoding="utf-8") as f:
        content2 = f.read()
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(content2)
    print("已恢复备份")
