import json
import os
import subprocess
import sys
from pathlib import Path

STATE_FILE = Path("sent_videos.json")
CHANNEL_URL = "https://www.youtube.com/@saytanar68/videos"
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "@happydayfor").strip()
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
BOOTSTRAP_SEND = os.environ.get("BOOTSTRAP_SEND", "false").lower() == "true"


def load_state():
    if not STATE_FILE.exists():
        return []
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_state(ids):
    # Keep the state small while retaining enough history to prevent duplicates.
    STATE_FILE.write_text(json.dumps(ids[:100], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_latest_videos():
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--flat-playlist",
        "--playlist-end",
        "15",
        "--dump-single-json",
        "--no-warnings",
        "--skip-download",
        CHANNEL_URL,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    videos = []
    for item in data.get("entries", []):
        if not item or not item.get("id"):
            continue
        video_id = item["id"]
        title = item.get("title") or "YouTube video"
        videos.append({"id": video_id, "title": title})
    return videos


def send_telegram(video):
    import requests

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    text = f"🎬 {video['title']}\nhttps://youtu.be/{video['id']}"
    response = requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": False},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(payload)


def main():
    if not TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN GitHub Secret is missing.")

    latest = get_latest_videos()
    if not latest:
        print("No videos found.")
        return

    sent = load_state()
    sent_set = set(sent)

    # First run: establish a baseline so old videos are not sent as if they were new.
    if not sent and not BOOTSTRAP_SEND:
        save_state([v["id"] for v in latest])
        print("Initial baseline created; existing videos were not sent.")
        return

    new_videos = [v for v in reversed(latest) if v["id"] not in sent_set]
    for video in new_videos:
        send_telegram(video)
        sent.insert(0, video["id"])

    if new_videos:
        save_state(sent)
        print(f"Sent {len(new_videos)} new video(s).")
    else:
        print("No new videos.")


if __name__ == "__main__":
    main()
