$env:PATH = 'C:\tools\ffmpeg\ffmpeg-7.1-essentials_build\bin;' + $env:PATH
$env:HTTP_PROXY = 'http://127.0.0.1:3067'
$env:HTTPS_PROXY = 'http://127.0.0.1:3067'
Set-Location 'C:\tools\IPTV'
python IPTV-Apex-dzh.py -w 80 -t 5
