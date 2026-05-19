# IPTV Live Source Aggregator

![IPTV](https://img.shields.io/badge/IPTV-Live%20Sources-blue) ![Python](https://img.shields.io/badge/Python-3.12-green) ![License](https://img.shields.io/badge/License-MIT-orange) ![Actions](https://github.com/litywang/IPTV/actions/workflows/iptv.yml/badge.svg)

> Auto-updated IPTV live sources for China mainland viewers. Crawls, checks, and syncs daily via GitHub Actions.

---

## Usage

### TVBox / M3U Player Import

**TXT (TVBox format):**
`
https://raw.githubusercontent.com/litywang/IPTV/master/live_ok_git.txt
`

**M3U format:**
`
https://raw.githubusercontent.com/litywang/IPTV/master/live_ok.m3u
`

Copy the link above into your player's live source management.

---

## Stats

| Metric | Value |
|--------|-------|
| Valid sources | ~1950 |
| Channels | ~1530 |
| Categories | 10 |
| Update frequency | Daily (UTC 02:00) |
| Format | TVBox TXT + M3U |

---

## Channel Categories

| Category | Description |
|----------|-------------|
| 4K Zone | Ultra HD channels |
| CCTV | CCTV 1-17 + Education |
| Satellite TV | Provincial satellite channels |
| News | News / Finance / Weather |
| Sports | Live sports / Esports |
| Kids | Children / Animation |
| Music | Music / MTV |
| Movies | Movies / Drama channels |
| HK/Macau/TW | Hong Kong, Macau, Taiwan |
| Other | Unclassified |

---

## Architecture

`
run_iptv.py          # Entry point
iptv_apex/            # Core package
  checker/            # Stream + direct verification
  core/               # Parser + pipeline
  crawler/            # Sync fetcher + async crawler
  utils/              # Name / stats / URL utilities
scripts/
  generate_m3u.py     # Generate M3U from results
  sync_to_gist.py     # Sync to GitHub + Gist
config.json           # Source list + parameters
`

---

## GitHub Actions

Daily automated pipeline (.github/workflows/iptv.yml):

1. **Crawl** - Fetch sources from subscriptions
2. **Check** - Verify streams are playable (HTTP, no proxy)
3. **Generate** - Create M3U + TVBox TXT
4. **Sync** - Push to GitHub repo + Gist

Secrets required:
- GIST_TOKEN - GitHub PAT for Gist API
- GIST_ID - Target Gist ID
- GH_TOKEN - GitHub token for push

---

## Local Development

`ash
git clone https://github.com/litywang/IPTV.git
cd IPTV
pip install requests httpx beautifulsoup4 tqdm zhconv

# Run with default settings
python run_iptv.py -w 20 -t 10 --no-speed-check

# With speed check (requires ffmpeg)
python run_iptv.py -w 20 -t 10
`

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| -w, --workers | 80 | Concurrent threads |
| -t, --timeout | 8 | Timeout per source (s) |
| --no-speed-check | off | Skip speed test (faster) |
| --no-local | off | Skip local paste.txt |
| --no-web-fetch | off | Skip web crawling |
| --async-crawl | off | Enable async crawler |
| --incremental | off | Incremental mode |

---

## Credits

- [IPTV-Apex](https://github.com/CoiaPrant/IPTV-Apex)
- [Guovin/iptv-api](https://github.com/Guovin/iptv-api)
- [fanmingming/live](https://github.com/fanmingming/live)
- [iptv-org](https://github.com/iptv-org/iptv)

## License

MIT