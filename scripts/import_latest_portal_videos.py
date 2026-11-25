#!/usr/bin/env python3
"""
Step 1: Import all latest released modules & videos from IIMBx (via Chrome port 9222)
for Critical Thinking, Data Visualisation for Business Decisions, and Corporate Finance.
Fetches official IIMBx SRT transcripts (with YouTube/Whisper fallback) and updates
study_vault.db + study_data.js cleanly WITHOUT running batch note generation.
"""

import sys
import json
import re
import uuid
import sqlite3
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import db
from core.transcript import fetch_transcript

TARGET_COURSES = [
    {
        "db_id": "d9173426",
        "name": "Critical Thinking",
        "edx_id": "course-v1:IIMBx+MD71x+BBA_DBE_B1",
    },
    {
        "db_id": "deb83564",
        "name": "Data Visualisation for Business Decisions",
        "edx_id": "course-v1:IIMBx+DS71x+BBA_DBE_B1",
    },
    {
        "db_id": "2989cdfe",
        "name": "Corporate Finance",
        "edx_id": "course-v1:IIMBx+FA71x+BBA_DBE_B1",
    },
]

def parse_srt_to_snippets(srt_text: str):
    """Parses SRT/VTT subtitles into timed snippet dicts and clean full text."""
    blocks = re.split(r"\r?\n\r?\n+", srt_text.strip())
    snippets = []
    texts = []
    time_re = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")

    def to_sec(h, m, s, ms):
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

    for blk in blocks:
        lines = [l.strip() for l in blk.splitlines() if l.strip()]
        if not lines:
            continue
        t_match = None
        text_lines = []
        for l in lines:
            m = time_re.search(l)
            if m and not t_match:
                t_match = m
            elif re.fullmatch(r"\d+", l) and not t_match:
                continue
            elif l.upper() == "WEBVTT":
                continue
            else:
                text_lines.append(l)
        if not text_lines:
            continue
        line_text = " ".join(text_lines)
        # Strip HTML/caption tags if any
        line_text = re.sub(r"<[^>]+>", "", line_text).strip()
        if not line_text or (line_text.startswith("[") and line_text.endswith("]")):
            continue
        texts.append(line_text)
        if t_match:
            start = to_sec(*t_match.groups()[:4])
            end = to_sec(*t_match.groups()[4:])
            snippets.append({
                "text": line_text,
                "start": round(start, 3),
                "duration": round(max(0.5, end - start), 3),
                "end": round(end, 3)
            })

    full_text = " ".join(texts)
    duration = snippets[-1]["end"] if snippets else 0.0
    return full_text, snippets, duration

def fetch_text_in_browser(driver, url: str) -> str:
    if not url:
        return ""
    script = """
    const done = arguments[arguments.length - 1];
    fetch(arguments[0], { credentials: 'include' })
        .then(r => r.ok ? r.text() : '')
        .then(t => done(t))
        .catch(() => done(''));
    """
    driver.set_script_timeout(20)
    try:
        return driver.execute_async_script(script, url) or ""
    except Exception:
        return ""

def get_transcript_for_video(driver, cname: str, yt_id: str, t_url: str):
    """Tries IIMBx official transcript first, then falls back to YouTube/Whisper."""
    if t_url:
        raw_srt = fetch_text_in_browser(driver, t_url)
        if raw_srt and len(raw_srt) > 40:
            full_text, snippets, duration = parse_srt_to_snippets(raw_srt)
            if len(full_text) > 40:
                return full_text, snippets, duration, "iimbx_srt"

    if yt_id:
        try:
            snips = fetch_transcript(f"https://www.youtube.com/watch?v={yt_id}", course_name=cname)
            full_text = " ".join([s.text for s in snips])
            snippets = [{"text": s.text, "start": s.start, "duration": s.duration, "end": s.end} for s in snips]
            duration = snips[-1].end if snips else 0.0
            return full_text, snippets, duration, "youtube_or_whisper"
        except Exception as e:
            print(f"      [!] Fallback transcript failed for {yt_id}: {e}")

    return "", [], 0.0, "none"

def main():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    username = "Garv_Gupta"

    conn = db.get_conn()

    summary = {"inserted": [], "updated": [], "failed_transcripts": []}

    for c_cfg in TARGET_COURSES:
        db_cid = c_cfg["db_id"]
        cname = c_cfg["name"]
        edx_id = c_cfg["edx_id"]

        print(f"\n==================================================================")
        print(f"Scanning {cname} ({edx_id})...")
        print(f"==================================================================")

        script = """
        const done = arguments[arguments.length - 1];
        const u = `https://iimbx.edu.in/api/courses/v1/blocks/?course_id=${encodeURIComponent(arguments[0])}&username=${encodeURIComponent(arguments[1])}&depth=all&requested_fields=children,student_view_data,type,display_name,graded&student_view_data=video`;
        fetch(u, { credentials: 'include' })
            .then(r => r.json())
            .then(d => done(d))
            .catch(e => done({ error: e.toString() }));
        """
        driver.set_script_timeout(30)
        data = driver.execute_async_script(script, edx_id, username)
        if "error" in data or "blocks" not in data:
            print(f"[!] Error fetching {cname}: {data}")
            continue

        blocks = data["blocks"]
        root = blocks.get(data.get("root"), {})

        # Get existing videos in this course
        existing_rows = conn.execute("""
            SELECT t.id, t.module_id, t.title, t.video_id, t.transcript_text, m.name as mod_name
            FROM topics t JOIN modules m ON t.module_id = m.id
            WHERE m.course_id = ?
        """, (db_cid,)).fetchall()

        existing_by_yt = {r["video_id"]: dict(r) for r in existing_rows if r["video_id"]}
        existing_mods = {
            r["name"].lower().strip(): dict(r)
            for r in conn.execute("SELECT id, number, name FROM modules WHERE course_id = ?", (db_cid,)).fetchall()
        }

        for ch_idx, ch_id in enumerate(root.get("children", []), start=1):
            ch = blocks.get(ch_id, {})
            ch_name = (ch.get("display_name") or "").strip()
            if not ch_name:
                continue

            # Collect all videos in chapter in exact syllabus order
            chap_videos = []
            def walk(bid, sec_name=""):
                b = blocks.get(bid, {})
                btype = b.get("type")
                if btype == "sequential":
                    sec_name = (b.get("display_name") or sec_name).strip()
                if btype == "video":
                    svd = b.get("student_view_data") or {}
                    yt_id = None
                    enc = svd.get("encoded_videos") or {}
                    if isinstance(enc, dict):
                        for k, v in enc.items():
                            if isinstance(v, dict) and "url" in v:
                                m = re.search(r"(?:v=|/embed/|/watch\?v=|/v/|youtu\.be/|/shorts/)([a-zA-Z0-9_-]{11})", v["url"])
                                if m:
                                    yt_id = m.group(1)
                                    break
                    if not yt_id:
                        for s in svd.get("sources", []):
                            m = re.search(r"(?:v=|/embed/|/watch\?v=|/v/|youtu\.be/|/shorts/)([a-zA-Z0-9_-]{11})", s)
                            if m:
                                yt_id = m.group(1)
                                break
                    tr = svd.get("transcripts") or {}
                    t_url = ""
                    if isinstance(tr, dict):
                        t_url = tr.get("en") or (list(tr.values())[0] if tr else "")
                    title = (b.get("display_name") or "").strip()
                    chap_videos.append({
                        "title": title,
                        "section": sec_name,
                        "yt_id": yt_id,
                        "t_url": t_url
                    })
                for child_id in b.get("children", []):
                    walk(child_id, sec_name)

            walk(ch_id)
            if not chap_videos:
                continue

            # Resolve target module in DB
            ch_key = ch_name.lower().strip()
            mod_row = existing_mods.get(ch_key)
            if not mod_row:
                # Special mappings for existing DB names
                if db_cid == "2989cdfe" and "live session" in ch_key:
                    mod_row = existing_mods.get("live session")
                elif db_cid == "2989cdfe" and ch_key.startswith("module 8"):
                    for k, v in existing_mods.items():
                        if k.startswith("module 8"):
                            mod_row = v
                            break

            if not mod_row:
                # Create missing module
                max_num = conn.execute("SELECT COALESCE(MAX(number), 0) FROM modules WHERE course_id = ?", (db_cid,)).fetchone()[0]
                m_match = re.search(r"module\s*(\d+)", ch_key)
                next_num = int(m_match.group(1)) if m_match else (max_num + 1)
                mod_id = f"{db_cid}-m{next_num}"
                if conn.execute("SELECT id FROM modules WHERE id = ?", (mod_id,)).fetchone():
                    mod_id = f"{db_cid}-m{next_num}-{str(uuid.uuid4())[:4]}"
                with conn:
                    conn.execute(
                        "INSERT INTO modules (id, course_id, number, name) VALUES (?, ?, ?, ?)",
                        (mod_id, db_cid, next_num, ch_name)
                    )
                mod_row = {"id": mod_id, "number": next_num, "name": ch_name}
                existing_mods[ch_key] = mod_row
                print(f"  📁 Created Module [{mod_id}] {ch_name}")

            mod_id = mod_row["id"]
            mod_topics = conn.execute(
                "SELECT id, title, video_id, transcript_text FROM topics WHERE module_id = ? ORDER BY rowid ASC",
                (mod_id,)
            ).fetchall()
            mod_by_title = {r["title"].lower().strip(): dict(r) for r in mod_topics}

            # Count per section to make generic 'Video' titles readable if newly inserted
            sec_counts = {}
            for v in chap_videos:
                yt_id = v["yt_id"]
                raw_title = v["title"]
                sec = v["section"]
                if not yt_id:
                    continue

                if yt_id in existing_by_yt:
                    continue  # Already in DB with exact same YouTube ID

                # Check if same title exists inside THIS module (e.g. CF Mod 7 re-uploads, ignore generic 'Video')
                if raw_title.lower() != "video" and raw_title.lower() in mod_by_title:
                    existing_t = mod_by_title[raw_title.lower()]
                    print(f"  🔄 Updating re-uploaded video in '{ch_name}': {raw_title} ({existing_t['video_id']} -> {yt_id})")
                    full_text, snippets, duration, src = get_transcript_for_video(driver, cname, yt_id, v["t_url"])
                    yt_url = f"https://www.youtube.com/watch?v={yt_id}"
                    with conn:
                        if full_text:
                            conn.execute("""
                                UPDATE topics
                                SET youtube_url = ?, video_id = ?, duration_seconds = ?,
                                    transcript_text = ?, transcript_snippets_json = ?
                                WHERE id = ?
                            """, (yt_url, yt_id, duration, full_text, json.dumps(snippets, ensure_ascii=False), existing_t["id"]))
                        else:
                            conn.execute("UPDATE topics SET youtube_url = ?, video_id = ? WHERE id = ?", (yt_url, yt_id, existing_t["id"]))
                    existing_by_yt[yt_id] = existing_t
                    summary["updated"].append((cname, ch_name, raw_title, yt_id, src, len(full_text)))
                    continue

                # Brand-new video to insert
                display_title = raw_title
                if raw_title.lower() == "video" and sec:
                    sec_counts[sec] = sec_counts.get(sec, 0) + 1
                    display_title = f"{sec} (Part {sec_counts[sec]})"

                print(f"  ➕ Importing NEW video into '{ch_name}': {display_title} [{yt_id}]")
                full_text, snippets, duration, src = get_transcript_for_video(driver, cname, yt_id, v["t_url"])
                if not full_text:
                    summary["failed_transcripts"].append((cname, ch_name, display_title, yt_id))

                topic_id = str(uuid.uuid4())[:8]
                yt_url = f"https://www.youtube.com/watch?v={yt_id}"
                with conn:
                    conn.execute("""
                        INSERT INTO topics (
                            id, module_id, title, youtube_url, video_id, duration_seconds,
                            status, transcript_text, transcript_snippets_json
                        ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
                    """, (
                        topic_id, mod_id, display_title, yt_url, yt_id, duration,
                        full_text, json.dumps(snippets, ensure_ascii=False)
                    ))
                existing_by_yt[yt_id] = {"id": topic_id, "title": display_title, "video_id": yt_id}
                summary["inserted"].append((cname, ch_name, display_title, yt_id, src, len(full_text)))

    print("\nExporting static bundle to study_data.js...")
    db.export_static_data()

    print("\n==================================================================")
    print("IMPORT SUMMARY")
    print("==================================================================")
    print(f"Newly inserted videos: {len(summary['inserted'])}")
    for item in summary["inserted"]:
        print(f"  + {item[0]} | {item[1]} | {item[2]} [{item[3]}] (src={item[4]}, chars={item[5]})")
    print(f"Updated re-uploaded videos: {len(summary['updated'])}")
    for item in summary["updated"]:
        print(f"  ~ {item[0]} | {item[1]} | {item[2]} [{item[3]}] (src={item[4]}, chars={item[5]})")
    print(f"Failed transcripts: {len(summary['failed_transcripts'])}")
    for item in summary["failed_transcripts"]:
        print(f"  ! {item}")

if __name__ == "__main__":
    main()
