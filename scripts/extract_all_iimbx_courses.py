"""
Master Course Extractor for IIMBx Open edX LMS.
Extracts all modules and videos for the 5 target courses and saves them to StudyEngine SQLite DB.
"""

import sys
import json
import uuid
import re
import urllib.parse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core import db

TARGET_COURSES = [
    {
        "key": "family_business_strategy",
        "name": "Family Business Strategy",
        "course_id": "course-v1:IIMBx+ST71x+BBA_DBE_B1",
        "skip_modules": []
    },
    {
        "key": "critical_thinking",
        "name": "Critical Thinking",
        "course_id": "course-v1:IIMBx+MD71x+BBA_DBE_B1",
        "skip_modules": []
    },
    {
        "key": "corporate_finance",
        "name": "Corporate Finance",
        "course_id": "course-v1:IIMBx+FA71x+BBA_DBE_B1",
        "skip_modules": [1, 2, 3, 4, 5]  # User already curated first 5 modules
    },
    {
        "key": "startup_dilemmas",
        "name": "Startup Dilemmas: Founding or Joining",
        "course_id": "course-v1:IIMBx+EP71x+BBA_DBE_B1",
        "skip_modules": []
    },
    {
        "key": "data_visualisation",
        "name": "Data Visualisation for Business Decisions",
        "course_id": "course-v1:IIMBx+DS71x+BBA_DBE_B1",
        "skip_modules": []
    }
]

def get_driver():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    return webdriver.Chrome(options=options)

def get_username(driver):
    script = """
    try {
        const match = document.cookie.match(/edx-user-info=([^;]+)/);
        if (match) {
            const info = JSON.parse(decodeURIComponent(match[1]));
            return info.username || 'Garv_Gupta';
        }
    } catch(e) {}
    return 'Garv_Gupta';
    """
    return driver.execute_script(script) or "Garv_Gupta"

def fetch_blocks(driver, course_id, username):
    script = """
    const done = arguments[arguments.length - 1];
    const courseId = arguments[0];
    const username = arguments[1];
    const u = `https://iimbx.edu.in/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}&username=${encodeURIComponent(username)}&depth=all&requested_fields=children,student_view_data,type,display_name&student_view_data=video`;

    fetch(u, { credentials: 'include' })
        .then(r => {
            if (!r.ok) throw new Error("HTTP " + r.status + " " + r.statusText);
            return r.json();
        })
        .then(d => done({ success: true, data: d }))
        .catch(e => done({ success: false, error: e.toString() }));
    """
    driver.set_script_timeout(30)
    return driver.execute_async_script(script, course_id, username)

def extract_course_tree(blocks_data):
    blocks = blocks_data.get("blocks", {})
    root_id = blocks_data.get("root")
    if not root_id or root_id not in blocks:
        return []

    root = blocks[root_id]
    chapters = []

    for chapter_id in root.get("children", []):
        chap = blocks.get(chapter_id)
        if not chap or chap.get("type") != "chapter":
            continue

        chap_name = chap.get("display_name", "").strip()
        videos = []

        def collect_videos(block_id):
            b = blocks.get(block_id)
            if not b:
                return
            if b.get("type") == "video":
                title = b.get("display_name", "").strip()
                svd = b.get("student_view_data") or {}
                yt_url = ""
                enc = svd.get("encoded_videos") or {}
                if enc.get("youtube") and enc["youtube"].get("url"):
                    yt_url = enc["youtube"]["url"]
                elif svd.get("sources"):
                    for s in svd["sources"]:
                        if "youtube" in s or "youtu.be" in s:
                            yt_url = s
                            break
                    if not yt_url and len(svd["sources"]) > 0:
                        yt_url = svd["sources"][0]
                elif svd.get("youtube_id_1_0"):
                    yt_url = f"https://www.youtube.com/watch?v={svd['youtube_id_1_0']}"

                transcript_url = ""
                transcripts = svd.get("transcripts") or {}
                if isinstance(transcripts, dict):
                    transcript_url = transcripts.get("en") or (list(transcripts.values())[0] if transcripts else "")

                m = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", yt_url)
                vid_id = m.group(1) if m else str(uuid.uuid4())[:8]
                if vid_id and not yt_url.startswith("http"):
                    yt_url = f"https://www.youtube.com/watch?v={vid_id}"

                if yt_url:
                    videos.append({
                        "title": title or "Untitled Lecture",
                        "url": yt_url,
                        "video_id": vid_id,
                        "duration": svd.get("duration", 0),
                        "transcript_url": transcript_url
                    })

            for child_id in b.get("children", []):
                collect_videos(child_id)

        collect_videos(chapter_id)
        if videos:
            chapters.append({
                "name": chap_name,
                "videos": videos
            })

    return chapters

def save_to_db(course_meta, chapters):
    conn = db.get_conn()
    course_name = course_meta["name"].strip()
    skip_mods = course_meta.get("skip_modules", [])

    # Check or create course
    c_row = conn.execute("SELECT id FROM courses WHERE LOWER(name) = ?", (course_name.lower(),)).fetchone()
    if c_row:
        course_id = c_row["id"]
        with conn:
            conn.execute("UPDATE courses SET module_count = ? WHERE id = ?", (len(chapters), course_id))
    else:
        course_id = str(uuid.uuid4())[:8]
        with conn:
            conn.execute(
                "INSERT INTO courses (id, code, name, description, module_count) VALUES (?, '', ?, 'IIMBx Course', ?)",
                (course_id, course_name, len(chapters))
            )

    print(f"\n=======================================================")
    print(f"📘 COURSE: {course_name} (ID: {course_id})")
    print(f"   Total Modules: {len(chapters)}")
    print(f"=======================================================")

    # Existing modules mapping: number -> id
    existing_mods = {r["number"]: r["id"] for r in conn.execute("SELECT id, number FROM modules WHERE course_id = ?", (course_id,)).fetchall()}

    total_added = 0
    total_skipped = 0

    for idx, chap in enumerate(chapters, start=1):
        mod_num = idx
        mod_name = chap["name"]

        if mod_num in skip_mods:
            print(f"  ⏭️  Module {mod_num}: '{mod_name}' - SKIPPED ({len(chap['videos'])} videos preserved as per request)")
            total_skipped += len(chap["videos"])
            continue

        if mod_num in existing_mods:
            mod_id = existing_mods[mod_num]
            with conn:
                conn.execute("UPDATE modules SET name = ? WHERE id = ?", (mod_name, mod_id))
        else:
            mod_id = f"{course_id}-m{mod_num}"
            with conn:
                conn.execute(
                    "INSERT INTO modules (id, course_id, number, name) VALUES (?, ?, ?, ?)",
                    (mod_id, course_id, mod_num, mod_name)
                )
            existing_mods[mod_num] = mod_id

        # Insert topics
        existing_vids = {r["video_id"] for r in conn.execute("SELECT video_id FROM topics WHERE module_id = ?", (mod_id,)).fetchall()}
        mod_added = 0

        for v in chap["videos"]:
            if v["video_id"] in existing_vids:
                continue
            t_id = str(uuid.uuid4())[:8]
            with conn:
                conn.execute(
                    "INSERT INTO topics (id, module_id, title, youtube_url, video_id, duration_seconds, status) VALUES (?, ?, ?, ?, ?, ?, 'pending')",
                    (t_id, mod_id, v["title"], v["url"], v["video_id"], v["duration"])
                )
            existing_vids.add(v["video_id"])
            mod_added += 1
            total_added += 1

        print(f"  ✅ Module {mod_num}: '{mod_name}' -> {len(chap['videos'])} videos (added: {mod_added})")

    return total_added, total_skipped

def run():
    print("[*] Connecting to Chrome on port 9222...")
    driver = get_driver()
    username = get_username(driver)
    print(f"[*] Authenticated as student: {username}")

    grand_total_added = 0
    grand_total_skipped = 0

    for target in TARGET_COURSES:
        print(f"\n[*] Fetching course blocks for '{target['name']}' ({target['course_id']})...")
        res = fetch_blocks(driver, target["course_id"], username)
        if not res.get("success"):
            print(f"[!] ERROR fetching {target['name']}: {res.get('error')}")
            continue

        chapters = extract_course_tree(res["data"])
        added, skipped = save_to_db(target, chapters)
        grand_total_added += added
        grand_total_skipped += skipped

    print("\n" + "="*60)
    print("🎉 EXTRACTION COMPLETE!")
    print(f"   Total New Topics Ingested: {grand_total_added}")
    print(f"   Total Existing Topics Preserved: {grand_total_skipped}")
    print("="*60)

if __name__ == "__main__":
    run()

