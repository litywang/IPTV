#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gist 同步模块
只负责将 live_ok.txt 同步到 Gist，不做 git commit/push
"""
import os, datetime, sys, json, shutil
from urllib.parse import urlparse, parse_qs, urlencode

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ========== URL 清理（GitHub Push Protection 合规） ==========
SENSITIVE_PARAMS = {
    'userid','sign','auth_token','token','key','secret','password','passwd',
    'tk','auth','verify','access_token','refresh_token','expires_in','nonce',
    'authkey','encrypt','client_secret','migutoken','msisdn','txsecret','txtime',
    'signkey','api_key','apikey','private_key','pwd','authcode','sid','spid',
    'clientid','client_id','deviceid','device_id','session','sessionid',
    'signstr','sign_type','resign','authkey2','auth_token_v2',
    'sign_token','secure_token','access_key','accesskey','access_secret',
    'authsign','checksum','hash','md5','sha',
}

def clean_url(url):
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        clean_qs = {k: v for k, v in qs.items() if k.lower() not in SENSITIVE_PARAMS}
        return parsed._replace(query=urlencode(clean_qs, doseq=True)).geturl()
    except Exception:
        return url

def sanitize_file(src, dst):
    with open(src, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    new_lines = []
    for line in lines:
        if ',#genre#' in line:
            new_lines.append(line)
        elif ',' in line:
            name, url = line.split(',', 1)
            new_lines.append('%s,%s' % (name, clean_url(url)))
        else:
            new_lines.append(line)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')
    return len([l for l in new_lines if l.strip() and ',#genre#' not in l])

def get_token():
    """从环境变量获取 Gist Token"""
    token = os.environ.get('GIST_TOKEN', '')
    if token and token != 'YOUR_GIST_TOKEN_HERE':
        return token
    token = os.environ.get('GH_TOKEN', '')
    if token:
        return token
    return ''

# ========== Gist Sync ==========
print("=== Gist Sync ===")
if not os.path.exists('live_ok.txt'):
    print("live_ok.txt not found, skip")
    sys.exit(0)

with open('live_ok.txt', 'r', encoding='utf-8') as f:
    content = f.read()
lines = [l for l in content.splitlines() if l.strip() and ',#genre#' not in l]
cnt = len(lines)
ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

# 生成 sanitized 版本
chan_count = sanitize_file('live_ok.txt', 'live_ok_git.txt')
print("Sanitized: %d channels -> live_ok_git.txt" % chan_count)

token = get_token()
if not token:
    print("No GIST_TOKEN found, skip")
    sys.exit(0)

gist_id = os.environ.get('GIST_ID', '')
if not gist_id:
    print("No GIST_ID found, skip")
    sys.exit(0)

import urllib.request
# Gist API 走代理（github.com 国内不可直连）
_proxy_url = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY') or None
if _proxy_url:
    proxy_handler = urllib.request.ProxyHandler({'http': _proxy_url, 'https': _proxy_url})
else:
    proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

gist_files = {'IPTV.txt': {'content': content}}
payload = json.dumps({
    'description': 'IPTV | %d channels | %s' % (cnt, ts),
    'files': gist_files
}).encode()

req = urllib.request.Request(
    'https://api.github.com/gists/' + gist_id,
    data=payload,
    headers={'Authorization': 'token ' + token,
             'Accept': 'application/vnd.github.v3+json',
             'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    print("Gist OK: %d channels" % cnt)
except Exception as e:
    print("Gist error: " + str(e))
    sys.exit(1)
