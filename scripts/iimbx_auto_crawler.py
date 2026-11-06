"""
IIMBx Course Extractor & StudyEngine Ingestor.
Connects to an existing Chrome instance on port 9222, reads enrolled courses,
queries Open edX Course Blocks API, and populates SQLite database.
"""

import sys
import json
import time
import uuid
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Add study-engine to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core import db

TARGET_COURSES = [
    "family business strategy",
    "critical thinking",
    "corporate finance",
    "startup dilemmas",
    "data visualisation"
]

def get_driver():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    return webdriver.Chrome(options=options)

def get_enrolled_courses(driver):
    """
    Tries multiple methods to get enrolled courses:
    1. /api/enrollment/v1/enrollment
    2. Parsing DOM on /dashboard
    """
    script = """
    const done = arguments[arguments.length - 1];
    fetch('/api/enrollment/v1/enrollment')
        .then(r => r.ok ? r.json() : null)
        .then(data => done(data))
        .catch(() => done(null));
    """
    driver.set_script_timeout(10)
    data = None
    try:
        data = driver.execute_async_script(script)
    except Exception as e:
        print("[!] Enrollment API check error:", e)

    courses = []
    if data and isinstance(data, list):
        for item in data:
            cd = item.get("course_details") or {}
            c_id = cd.get("course_id")
            c_name = cd.get("course_name") or cd.get("course_title") or ""
            if c_id and c_name:
                courses.append({"id": c_id, "name": c_name})

    if not courses:
        # Fallback to DOM scan on current page
        links = driver.find_elements("tag name", "a")
        seen_ids = set()
        for l in links:
            href = l.get_attribute("href") or ""
            text = l.text.strip()
            m = re.search(r"(course-v1:[^/]+)", href)
            if m:
                cid = m.group(1)
                if cid not in seen_ids:
                    seen_ids.add(cid)
                    courses.append({"id": cid, "name": text or cid})

    return courses

def fetch_course_blocks(driver, course_id):
    script = """
    const courseId = arguments[0];
    const url = `/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}&all_blocks=true&depth=all&requested_fields=children,student_view_data,type,display_name`;
    const done = arguments[arguments.length - 1];
    fetch(url)
        .then(r => {
            if (!r.ok) throw new Error("HTTP " + r.status + " " + r.statusText);
            return r.json();
        })
        .then(data => done({success: true, data: data}))
        .catch(err => done({success: false, error: err.toString()}));
    """
    driver.set_script_timeout(30)
    return driver.execute_async_script(script, course_id)

def parse_blocks_tree(blocks_data):
    blocks = blocks_data.get("blocks", {})
    root_id = blocks_data.get("root")
    if not root_id or root_id not in blocks:
        return []

    root = blocks[root_id]
    modules = []

    for chapter_id in root.get("children", []):
        chapter = blocks.get(chapter_id)
        if not chapter or chapter.get("type") != "chapter":
            continue

        mod_title = chapter.get("display_name", "Untitled Module").strip()
        videos = []

        def collect_videos(block_id):
            b = blocks.get(block_id)
            if not b:
                return
            if b.get("type") == "video":
                title = b.get("display_name", "Untitled Video").strip()
                svd = b.get("student_view_data") or {}
                yt_url = ""
                vid_id = ""

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

                m = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", yt_url)
                if m:
                    vid_id = m.group(1)
                    if not yt_url.startswith("http"):
                        yt_url = f"https://www.youtube.com/watch?v={vid_id}"

                if yt_url:
                    videos.append({
                        "title": title,
                        "url": yt_url,
                        "video_id": vid_id or str(uuid.uuid4())[:8],
                        "duration": svd.get("duration", 0)
                    })

            for child_id in b.get("children", []):
                collect_videos(child_id)

        collect_videos(chapter_id)
        if videos:
            modules.append({
                "name": mod_title,
                "videos": videos
            })

    return modules

def ingest_course_into_vault(course_name, modules, skip_existing_corporate_finance=True):
    conn = db.get_conn()
    course_name_clean = course_name.strip()
    
    # Check if course exists
    c_row = conn.execute("SELECT id FROM courses WHERE LOWER(name) LIKE ?", (f"%{course_name_clean.lower()}%",)).fetchone()
    if c_row:
        course_id = c_row["id"]
        print(f"[*] Found existing course in DB: '{course_name}' (ID: {course_id})")
    else:
        course_id = str(uuid.uuid4())[:8]
        with conn:
            conn.execute(
                "INSERT INTO courses (id, code, name, description, module_count) VALUES (?, '', ?, 'Extracted from IIMBx', ?)",
                (course_id, course_name_clean, len(modules))
            )
        print(f"[+] Created new course in DB: '{course_name}' (ID: {course_id})")

    existing_modules = {row["number"]: row["id"] for row in conn.execute("SELECT id, number FROM modules WHERE course_id = ?", (course_id,)).fetchall()}
    
    total_added_videos = 0
    
    for idx, mod in enumerate(modules, start=1):
        mod_num = idx
        # Special check for Corporate Finance
        if "corporate finance" in course_name.lower() and skip_existing_corporate_finance and mod_num <= 5:
            print(f"[-] Skipping Corporate Finance Module {mod_num} (already curated by user).")
            continue

        if mod_num in existing_modules:
            mod_id = existing_modules[mod_num]
            # Update module title if needed
            with conn:
                conn.execute("UPDATE modules SET name = ? WHERE id = ?", (mod["name"], mod_id))
        else:
            mod_id = f"{course_id}-m{mod_num}"
            with conn:
                conn.execute(
                    "INSERT INTO modules (id, course_id, number, name) VALUES (?, ?, ?, ?)",
                    (mod_id, course_id, mod_num, mod["name"])
                )
            existing_modules[mod_num] = mod_id

        # Insert topics
        existing_video_ids = {row["video_id"] for row in conn.execute("SELECT video_id FROM topics WHERE module_id = ?", (mod_id,)).fetchall()}
        
        for v in mod["videos"]:
            if v["video_id"] in existing_video_ids:
                continue
            t_id = str(uuid.uuid4())[:8]
            with conn:
                conn.execute(
                    "INSERT INTO topics (id, module_id, title, youtube_url, video_id, duration_seconds, status) VALUES (?, ?, ?, ?, ?, ?, 'pending')",
                    (t_id, mod_id, v["title"], v["url"], v["video_id"], v["duration"])
                )
            existing_video_ids.add(v["video_id"])
            total_added_videos += 1

        print(f"  [✓] Module {mod_num} ('{mod['name']}'): {len(mod['videos'])} videos mapped.")

    return total_added_videos

if __name__ == "__main__":
    driver = get_driver()
    print("[*] Connected to Chrome on port 9222.")
    print("[*] Current URL:", driver.current_url)
    courses = get_enrolled_courses(driver)
    print(f"[*] Found {len(courses)} enrolled courses.")
    for c in courses:
        print(f"  - {c['name']} (ID: {c['id']})")
