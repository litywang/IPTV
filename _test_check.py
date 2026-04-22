#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
os.environ['PATH'] = r'C:\tools\ffmpeg\bin;' + os.environ.get('PATH', '')
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:3067'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:3067'

# Load the script's classes
with open('IPTV-Apex-dzh.py', 'r', encoding='utf-8') as f:
    code = f.read()
exec(code.split("if __name__")[0])

# Test StreamChecker
checker = StreamChecker()
lines = []
with open('live_ok.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and ',' in line and not line.endswith('#genre#'):
            lines.append(line)
            if len(lines) >= 5:
                break

for line in lines:
    name = line.split(',')[0][:30]
    url = line.split(',', 1)[1][:60]
    print(f'--- Testing: {name} | {url}...')
    result = checker.check(line, proxy=None)
    if result:
        s = result.get('status', '?')
        lat = result.get('lat', 'N/A')
        q = result.get('quality', 'N/A')
        r = result.get('reason', '')
        print(f'  status={s}, lat={lat}, quality={q}, reason={r}')
    else:
        print(f'  result=None (filtered out)')
