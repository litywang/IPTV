@echo off
chcp 65001 >nul 2>&1
if exist "%~dp0env_config.bat" call "%~dp0env_config.bat"
set PATH=C:\tools\ffmpeg\ffmpeg-7.1-essentials_build\bin;%PATH%
set HTTP_PROXY=http://127.0.0.1:3067
set HTTPS_PROXY=http://127.0.0.1:3067
cd /d C:\tools\IPTV

:: IPTV 检测（仅拉取 web 源，跳过 paste.txt，直连测活过滤大陆不可直通的源）
python IPTV-Apex-dzh.py -w 120 -t 8 --no-local --no-speed-check
if %errorlevel% neq 0 (
    echo [%date% %time%] IPTV check failed with exit code %errorlevel% >> run_error.log
)

:: 生成 M3U + 同步 GitHub/Gist
if exist "live_ok.txt" (
    python scripts\generate_m3u.py
    python scripts\sync_to_gist.py
    echo [%date% %time%] Run completed successfully >> run.log
) else (
    echo [%date% %time%] WARNING: live_ok.txt not generated >> run_error.log
)
