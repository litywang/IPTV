# IPTV-Apex-dzh 聚合优化版

基于 [IPTV-Apex-Lity.py](https://github.com/litywang/IPTV)，融合多项优化建议的 IPTV 直播源检测工具。

## 功能特性

| 优化项 | 说明 |
|--------|------|
| M3U8 解析增强 | 支持 m3u8 库，频道名解析准确率提升 10-20% |
| 轻量级缓存 | URL 去重缓存（TTL 24小时），避免重复检测 |
| ffprobe 优化 | probesize 5M / analyzeduration 10M，降低误判率 |
| 分辨率过滤 | 自动过滤低于 640x480 的低质量源 |
| 爬虫质量控制 | 域名白名单/黑名单评分机制 |
| 统计持久化 | JSON 文件记录历史运行数据 |
| 点播域名扩展 | 覆盖百度/抖音/快手/淘宝等短视频 CDN |
| 进度条优化 | 简洁实时显示有效率 |

## 快速开始

### 本地运行

```bash
# 安装依赖
pip install requests httpx zhconv tqdm

# 建议安装（可选）
pip install m3u8

# 运行检测
python IPTV-Apex-dzh.py
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `-i, --input` | 输入文件路径（默认: paste.txt） |
| `-o, --output` | 输出文件路径（默认: live_ok.txt） |
| `-w, --workers` | 并发检测线程数（默认: 80） |
| `-t, --timeout` | 境内源超时时间秒（默认: 15） |
| `--proxy` | 代理地址（如: http://127.0.0.1:7890） |
| `--no-speed-check` | 关闭下载速度检测 |
| `--no-cache` | 禁用 URL 去重缓存 |
| `--async-crawl` | 启用异步爬虫扫描新源 |

### 示例

```bash
# 基本使用
python IPTV-Apex-dzh.py

# 自定义输入输出
python IPTV-Apex-dzh.py -i mysources.txt -o result.txt

# 使用代理、80并发
python IPTV-Apex-dzh.py --proxy http://127.0.0.1:7890 -w 80

# 关闭速度检测（更快）
python IPTV-Apex-dzh.py --no-speed-check

# 启用爬虫扫描新源
python IPTV-Apex-dzh.py --async-crawl
```

## 配置文件

运行后会生成 `config.json`，可手动调整：

```json
{
  "ENABLE_WEB_CHECK": true,
  "ENABLE_SPEED_CHECK": true,
  "ENABLE_CACHE": true,
  "MAX_WORKERS": 80,
  "TIMEOUT_CN": 15,
  "MIN_QUALITY_SCORE": 15,
  "MIN_SPEED_MBPS": 0.005,
  "WEB_SOURCES": []
}
```

## 频道分类

自动按以下分类整理输出：

- **4K 專區** - 2160P/8K 超高清源
- **央衛頻道** - CCTV 系列（含 CCTV1-17）
- **衛視綜藝** - 各省卫视综合频道
- **新聞資訊** - 新闻/财经/气象
- **體育賽事** - 体育/足球/篮球/电竞
- **少兒動漫** - 少儿/卡通/动画
- **音樂頻道** - 音乐/MTV/演唱会
- **影視劇集** - 影视/电影/剧集点播
- **港澳台頻** - 港台海外频道
- **其他頻道** - 未分类频道

## GitHub Actions 自动运行

启用 Actions 后，脚本将自动定期检测直播源并更新 `live_ok.txt`。

> ⚠️ **注意**: Actions 运行在 Linux 环境，需要自行安装 FFmpeg：
> ```yaml
> - name: Install FFmpeg
>   run: sudo apt-get update && sudo apt-get install -y ffmpeg
> ```

## 依赖说明

| 依赖 | 必需 | 说明 |
|------|------|------|
| requests | ✅ | HTTP 请求 |
| httpx | ✅ | 异步 HTTP |
| zhconv | ✅ | 繁简转换 |
| tqdm | ✅ | 进度条 |
| m3u8 | ❌ | M3U8 解析（推荐安装） |
| ffprobe | ❌ | 流检测（推荐安装） |

## 致谢

- 基于 [IPTV-Apex-Lity](https://github.com/litywang/IPTV) 开发
- 参考 [IPTV-Apex](https://github.com/CoiaPrant/IPTV-Apex)
- 参考 [Guovin/iptv-api](https://github.com/Guovin/iptv-api)

## License

MIT License
