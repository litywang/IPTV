#!/usr/bin/env python3
"""Sync tvbox_cang.json to Gist."""
import os, sys, json, urllib.request

GIST_ID = os.environ.get('GIST_ID', 'dc272a4f2e95ffbd41e7e31d27ef3d76')

def get_token():
    token = os.environ.get('GIST_TOKEN', '')
    if token and token != 'YOUR_GIST_TOKEN_HERE':
        return token
    token = os.environ.get('GH_TOKEN', '')
    if token:
        return token
    return ''

if not os.path.exists('tvbox_cang.json'):
    print("tvbox_cang.json not found")
    sys.exit(1)

with open('tvbox_cang.json', 'r', encoding='utf-8') as f:
    content = f.read()

token = get_token()
if not token:
    print("No token found")
    sys.exit(1)

# Gist API 走代理（github.com 国内不可直连）
_proxy_url = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY') or None
if _proxy_url:
    proxy_handler = urllib.request.ProxyHandler({'http': _proxy_url, 'https': _proxy_url})
else:
    proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

payload = json.dumps({
    'files': {'csk.json': {'content': content}}
}).encode()

req = urllib.request.Request(
    'https://api.github.com/gists/' + GIST_ID,
    data=payload,
    headers={'Authorization': 'token ' + token,
             'Accept': 'application/vnd.github.v3+json',
             'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    print("Gist updated: csk.json -> TVBOX multi-warehouse format")
    print("URL: https://gist.githubusercontent.com/litywang/%s/raw/csk.json" % GIST_ID)
except Exception as e:
    print("Gist error: " + str(e))
    sys.exit(1)
