"""
Fast Transcript Pre-fetcher from IIMBx Open edX.
Fetches all official transcripts directly via HTTP without using CPU or Whisper!
"""

import sys
import json
import re
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core import db

TARGET_COURSE_IDS = [
    "course-v1:IIMBx+ST71x+BBA_DBE_B1", # Family Business Strategy
    "course-v1:IIMBx+MD71x+BBA_DBE_B1", # Critical Thinking
    "course-v1:IIMBx+FA71x+BBA_DBE_B1", # Corporate Finance
    "course-v1:IIMBx+EP71x+BBA_DBE_B1", # Startup Dilemmas
    "course-v1:IIMBx+DS71x+BBA_DBE_B1"  # Data Visualisation
]

def clean_srt(srt_text: str) -> str:
    """Cleans SRT/VTT format into smooth spoken text."""
    lines = srt_text.splitlines()
    cleaned = []
    for l in lines:
        line = l.strip()
        if not line:
            continue
        # Skip numeric counters
        if re.match(r"^\d+$", line):
            continue
        # Skip timestamps 00:00:00,000 --> 00:00:00,000
        if "-->" in line:
            continue
        # Skip music / sound markers like [Music]
        if line.startswith("[") and line.endswith("]"):
            continue
        cleaned.append(line)
    return " ".join(cleaned)

def fetch_course_transcripts_map(course_id, username="Garv_Gupta"):
    url = f"https://iimbx.edu.in/api/courses/v1/blocks/?course_id={urllib.parse.quote(course_id)}&username={username}&depth=all&requested_fields=children,student_view_data,type,display_name&student_view_data=video"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            blocks = data.get("blocks", {})
            vids = {}
            for bid, b in blocks.items():
                if b.get("type") == "video":
                    svd = b.get("student_view_data") or {}
                    enc = svd.get("encoded_videos") or {}
                    yt_url = ""
                    if enc.get("youtube") and enc["youtube"].get("url"):
                        yt_url = enc["youtube"]["url"]
                    elif svd.get("youtube_id_1_0"):
                        yt_url = f"https://www.youtube.com/watch?v={svd['youtube_id_1_0']}"
                    
                    m = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", yt_url)
                    vid_id = m.group(1) if m else ""
                    
                    t_url = ""
                    transcripts = svd.get("transcripts") or {}
                    if isinstance(transcripts, dict):
                        t_url = transcripts.get("en") or (list(transcripts.values())[0] if transcripts else "")
                    
                    if vid_id and t_url:
                        vids[vid_id] = t_url
            return vids
    except Exception as e:
        print(f"Error fetching course blocks for {course_id}: {e}")
        return {}

def run():
    conn = db.get_conn()
    all_transcripts_map = {}
    
    print("[*] Fetching official transcript URLs for all 5 courses...")
    for cid in TARGET_COURSE_IDS:
        m = fetch_course_transcripts_map(cid)
        print(f"  -> {cid}: Found {len(m)} official transcript URLs")
        all_transcripts_map.update(m)
        
    print(f"\n[*] Total video IDs with official transcripts: {len(all_transcripts_map)}")
    
    # Check pending topics in DB
    rows = conn.execute("SELECT id, video_id, title, transcript_text FROM topics WHERE status = 'pending'").fetchall()
    print(f"[*] Checking {len(rows)} pending topics...")
    
    prefetched = 0
    for r in rows:
        vid = r["video_id"]
        if r["transcript_text"] and len(r["transcript_text"].strip()) > 50:
            continue
            
        t_url = all_transcripts_map.get(vid)
        if not t_url:
            continue
            
        try:
            req = urllib.request.Request(t_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                srt_data = resp.read().decode("utf-8", errors="ignore")
                clean_txt = clean_srt(srt_data)
                if len(clean_txt) > 50:
                    with conn:
                        conn.execute("UPDATE topics SET transcript_text = ? WHERE id = ?", (clean_txt, r["id"]))
                    prefetched += 1
        except Exception as e:
            continue

    print(f"[+] Successfully pre-fetched official transcripts for {prefetched} pending lectures with 0% CPU!")

if __name__ == "__main__":
    run()

