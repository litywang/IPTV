import os, requests, subprocess, datetime, sys
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ========== 1. GitHub Push ==========
print("=== GitHub Push ===")
try:
    result = subprocess.run(
        ["git", "add", "live_ok.txt", "live_ok.m3u", ".iptv_cache.json", ".iptv_stats.json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    result2 = subprocess.run(
        ["git", "diff", "--staged", "--stat"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result2.stdout.strip():
        print("Changes:", result2.stdout.strip())
        commit_msg = f"chore: auto-update {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "config", "--local", "user.email", "anftlity@email.com"], check=False)
        subprocess.run(["git", "config", "--local", "user.name", "anftlity"], check=False)
        subprocess.run(["git", "commit", "-m", commit_msg], check=False)
        push = subprocess.run(
            ["git", "push", "origin", "master"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        )
        if push.returncode == 0:
            print("✅ GitHub push 成功")
        else:
            print("⚠️ GitHub push:", push.stderr.strip() or push.stdout.strip())
    else:
        print("无变更，跳过 commit")
except Exception as e:
    print(f"⚠️ GitHub push 出错: {e}")

# ========== 2. Gist Sync ==========
print("\n=== Gist Sync ===")
if not os.path.exists("live_ok.txt"):
    print("live_ok.txt 不存在，跳过 Gist")
else:
    with open("live_ok.txt", "r", encoding="utf-8") as f:
        content = f.read()
    cnt = len([l for l in content.splitlines() if l.strip()])

    # 优先用 GIST_TOKEN，否则用 git config 的 token
    token = os.environ.get("GIST_TOKEN", "")
    if not token or token == "YOUR_GIST_TOKEN_HERE":
        try:
            token_result = subprocess.run(
                ["git", "config", "--global", "credential.helper"],
                capture_output=True, text=True, encoding="utf-8"
            )
            if "cache" in token_result.stdout:
                token_result2 = subprocess.run(
                    ["git", "config", "--global", "--list"],
                    capture_output=True, text=True, encoding="utf-8"
                )
                for line in token_result2.stdout.splitlines():
                    if "token" in line.lower() or "oauth" in line.lower():
                        parts = line.split("=", 1)
                        if len(parts) == 2 and parts[1].strip().startswith("ghp_"):
                            token = parts[1].strip()
                            break
        except:
            pass

    if not token or token == "YOUR_GIST_TOKEN_HERE":
        print("⚠️ 未找到 GIST_TOKEN，跳过 Gist 同步")
    else:
        gist_id = "dc272a4f2e95ffbd41e7e31d27ef3d76"
        r = requests.patch(
            f"https://api.github.com/gists/{gist_id}",
            headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
            json={"description": f"IPTV | {cnt} sources | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                  "files": {"IPTV.txt": {"content": content}}}
        )
        if r.status_code == 200:
            print(f"✅ Gist 同步成功: {cnt} 条")
        else:
            print(f"❌ Gist 失败: {r.status_code} {r.text}")
