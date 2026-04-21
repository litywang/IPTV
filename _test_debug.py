#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io, os, subprocess, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
os.environ['PATH'] = r'C:\tools\ffmpeg\bin;' + os.environ.get('PATH', '')
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:3067'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:3067'

# Check ffprobe availability
has_ffprobe = shutil.which('ffprobe') is not None
print(f'HAS_FFPROBE = {has_ffprobe}')

if has_ffprobe:
    result = subprocess.run(['ffprobe', '-version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f'ffprobe version OK')
        has_ffprobe = True
    else:
        print(f'ffprobe version check failed')
        has_ffprobe = False

# Load the script's classes
with open('IPTV-Apex-dzh.py', 'r', encoding='utf-8') as f:
    code = f.read()
exec(code.split("if __name__")[0])

# Now check HAS_FFPROBE from the loaded script
print(f'Script HAS_FFPROBE = {HAS_FFPROBE}')

# Test with detailed debugging
checker = StreamChecker()
lines = []
with open('live_ok.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and ',' in line and not line.endswith('#genre#'):
            lines.append(line)
            if len(lines) >= 3:
                break

for line in lines:
    name_part, url_part = line.split(',', 1)
    name = name_part.strip()[:100]
    url = url_part.strip()
    
    print(f'\n=== Testing: {name[:30]} | {url[:80]}...')
    
    # Pre-filter checks
    if not name or not url:
        print(f'  FAIL: empty name or url')
        continue
    if NameProcessor.is_blacklisted(name):
        print(f'  FAIL: blacklisted name')
        continue
    if URLCleaner.filter_private_ip(url):
        print(f'  FAIL: private IP')
        continue
    if URLCleaner.is_vod_domain(url):
        print(f'  FAIL: VOD domain')
        continue
    if not url.startswith(('http://', 'https://')):
        print(f'  FAIL: not http/https')
        continue
    
    print(f'  Pre-filters passed.')
    
    overseas = NameProcessor.is_overseas(name)
    timeout = Config.TIMEOUT_OVERSEAS if overseas else Config.TIMEOUT_CN
    print(f'  overseas={overseas}, timeout={timeout}s')
    
    # Test ffprobe directly
    if HAS_FFPROBE:
        print(f'  Testing ffprobe (direct, no proxy)...')
        result = checker._check_with_ffprobe(url, name, timeout, None, overseas)
        if result:
            print(f'  ffprobe OK: status={result.get("status")}, lat={result.get("lat")}, quality={result.get("quality")}')
        else:
            print(f'  ffprobe FAILED (returned None)')
    else:
        print(f'  ffprobe not available, skipping')
    
    # Test HTTP directly  
    print(f'  Testing HTTP (direct, no proxy)...')
    result = checker._check_with_http(url, name, timeout, None, overseas)
    if result:
        s = result.get('status', '?')
        lat = result.get('lat', 'N/A')
        q = result.get('quality', 'N/A')
        r = result.get('reason', '')
        print(f'  HTTP: status={s}, lat={lat}, quality={q}, reason={r}')
    else:
        print(f'  HTTP returned None')
