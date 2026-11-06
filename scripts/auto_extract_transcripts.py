"""
Auto-extracts official transcripts from all 5 IIMBx courses via Chrome DevTools bridge.
Waits for user login, queries Open edX blocks API, downloads all SRT transcripts,
and populates SQLite vault with 0% CPU usage.
"""

import sys
import time
import json
import re
import urllib.request
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core import db

TARGET_COURSE_IDS = [
    ("course-v1:IIMBx+ST71x+BBA_DBE_B1", "Family Business Strategy"),
    ("course-v1:IIMBx+MD71x+BBA_DBE_B1", "Critical Thinking"),
    ("course-v1:IIMBx+FA71x+BBA_DBE_B1", "Corporate Finance"),
    ("course-v1:IIMBx+EP71x+BBA_DBE_B1", "Startup Dilemmas"),
    ("course-v1:IIMBx+DS71x+BBA_DBE_B1", "Data Visualisation")
]

def clean_srt(srt_text: str) -> str:
    lines = srt_text.splitlines()
    cleaned = []
    seen = set()
    for l in lines:
        line = l.strip()
        if not line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if re.match(r"^\d+$", line) or "-->" in line:
            continue
        if line.startswith("[") and line.endswith("]"):
            continue
        clean_line = re.sub(r"<[^>]+>", "", line).strip()
        if clean_line and clean_line not in seen:
            seen.add(clean_line)
            cleaned.append(clean_line)
    return " ".join(cleaned)

def run():
    print("[*] Connecting to Chrome on port 9222...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    
    # Check if user is logged in
    print("[*] Waiting for user to complete login...")
    while True:
        url = driver.current_url.lower()
        if "login" not in url and ("dashboard" in url or "course" in url or "learning" in url or "home" in url):
            print(f"[✓] Login detected! Current URL: {driver.current_url}")
            break
        time.sleep(2)

    # Allow session cookies to settle
    time.sleep(3)

    # Get student username
    script_user = """
    try {
        const m = document.cookie.match(/edx-user-info=([^;]+)/);
        if (m) return JSON.parse(decodeURIComponent(m[1])).username;
    } catch(e) {}
    return 'Garv_Gupta';
    """
    username = driver.execute_script(script_user) or "Garv_Gupta"
    print(f"[*] Authenticated as student: {username}")

    script_blocks = """
    const courseId = arguments[0];
    const username = arguments[1];
    const done = arguments[arguments.length - 1];
    const u = `https://iimbx.edu.in/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}&username=${encodeURIComponent(username)}&depth=all&requested_fields=children,student_view_data,type,display_name&student_view_data=video`;

    fetch(u, { credentials: 'include' })
        .then(r => r.json())
        .then(data => done({ success: true, data: data }))
        .catch(err => done({ success: false, error: err.toString() }));
    """
    driver.set_script_timeout(30)

    transcripts_map = {}
    
    for cid, cname in TARGET_COURSE_IDS:
        print(f"\n[*] Querying course blocks for: {cname} ({cid})...")
        res = driver.execute_async_script(script_blocks, cid, username)
        if not res.get("success"):
            print(f"  [!] Error: {res.get('error')}")
            continue

        blocks = res.get("data", {}).get("blocks", {})
        count = 0
        for bid, b in blocks.items():
            if b.get("type") == "video":
                svd = b.get("student_view_data") or {}
                enc = svd.get("encoded_videos") or {}
                yt_url = ""
                if enc.get("youtube") and enc["youtube"].get("url"):
                    yt_url = enc["youtube"]["url"]
                elif svd.get("youtube_id_1_0"):
                    yt_url = f"https://www.youtube.com/watch?v={svd['youtube_id_1_0']}"
                elif svd.get("sources"):
                    for s in svd["sources"]:
                        if "youtube" in s or "youtu.be" in s:
                            yt_url = s
                            break

                m = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", yt_url)
                vid_id = m.group(1) if m else ""

                t_url = ""
                transcripts = svd.get("transcripts") or {}
                if isinstance(transcripts, dict):
                    t_url = transcripts.get("en") or (list(transcripts.values())[0] if transcripts else "")

                if vid_id and t_url:
                    transcripts_map[vid_id] = t_url
                    count += 1

        print(f"  [✓] {cname}: Found {count} official university transcript download links!")

    print(f"\n[*] Total official transcript links collected: {len(transcripts_map)}")
    
    # Save mapping file
    out_file = BASE_DIR / "data" / "iimbx_transcripts_map.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(transcripts_map, f, indent=2)
    print(f"[+] Saved transcript map to: {out_file}")

    # Now download all transcripts directly into SQLite topics!
    conn = db.get_conn()
    pending_rows = conn.execute("SELECT id, video_id, title, transcript_text FROM topics WHERE status = 'pending'").fetchall()
    print(f"\n[*] Ingesting official transcripts for {len(pending_rows)} pending topics...")

    saved_count = 0
    for idx, r in enumerate(pending_rows, start=1):
        vid = r["video_id"]
        if r["transcript_text"] and len(r["transcript_text"].strip()) > 50:
            continue

        t_url = transcripts_map.get(vid)
        if not t_url:
            continue

        try:
            req = urllib.request.Request(t_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw_srt = resp.read().decode("utf-8", errors="ignore")
                cleaned = clean_srt(raw_srt)
                if len(cleaned) > 50:
                    with conn:
                        conn.execute("UPDATE topics SET transcript_text = ? WHERE id = ?", (cleaned, r["id"]))
                    saved_count += 1
                    if saved_count % 25 == 0:
                        print(f"  [✓] Ingested {saved_count} official transcripts directly into DB (0% CPU)...")
        except Exception:
            continue

    print(f"\n" + "="*60)
    print(f"🎉 COMPLETED! Ingested {saved_count} official transcripts directly into the database!")
    print(f"   Zero CPU was used. No Whisper required. Laptop stays cold.")
    print(f"="*60)
    
    # Close automated browser
    driver.quit()

if __name__ == "__main__":
    run()

