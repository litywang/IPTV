@echo off
set PATH=C:\tools\ffmpeg\ffmpeg-7.1-essentials_build\bin;%PATH%
set HTTP_PROXY=http://127.0.0.1:3067
set HTTPS_PROXY=http://127.0.0.1:3067
cd /d C:\tools\IPTV
python IPTV-Apex-dzh.py -w 80 -t 5 2>nul
