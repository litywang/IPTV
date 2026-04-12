@echo off
chcp 65001 >nul 2>&1

if exist "%~dp0env_config.bat" call "%~dp0env_config.bat"

set "PATH=C:\tools\ffmpeg\ffmpeg-7.1-essentials_build\bin;%PATH%"
set "HTTP_PROXY=http://127.0.0.1:3067"
set "HTTPS_PROXY=http://127.0.0.1:3067"

cd /d C:\tools\IPTV

echo [%date% %time%] === IPTV pipeline start === >> run.log
python IPTV-Apex-dzh.py -w 120 -t 8 --no-local --no-speed-check
if %errorlevel% neq 0 (
    echo [%date% %time%] FAIL: exit %errorlevel% >> run_error.log
    goto :end
)

if exist "live_ok.txt" (
    python scripts\generate_m3u.py >> run.log 2>&1
    python scripts\sync_to_gist.py >> run.log 2>&1
    echo [%date% %time%] OK >> run.log
) else (
    echo [%date% %time%] FAIL: live_ok.txt not generated >> run_error.log
)

:end
