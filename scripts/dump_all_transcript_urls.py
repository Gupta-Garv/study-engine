"""
Dump all IIMBx video IDs and transcript download URLs using Chrome session.
"""

import sys
import json
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

TARGET_COURSE_IDS = [
    "course-v1:IIMBx+ST71x+BBA_DBE_B1", # Family Business Strategy
    "course-v1:IIMBx+MD71x+BBA_DBE_B1", # Critical Thinking
    "course-v1:IIMBx+FA71x+BBA_DBE_B1", # Corporate Finance
    "course-v1:IIMBx+EP71x+BBA_DBE_B1", # Startup Dilemmas
    "course-v1:IIMBx+DS71x+BBA_DBE_B1"  # Data Visualisation
]

def run():
    print("[*] Launching headless Chrome with user profile to dump transcript URLs...")
    options = Options()
    options.add_argument(f"--user-data-dir={BASE_DIR}/chrome_profile")
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=options)
    
    # Navigate to iimbx to ensure cookies are active
    driver.get("https://apps.iimbx.edu.in/dashboard")
    
    script = """
    const courseId = arguments[0];
    const done = arguments[arguments.length - 1];
    const u = `https://iimbx.edu.in/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}&username=Garv_Gupta&depth=all&requested_fields=children,student_view_data,type,display_name&student_view_data=video`;

    fetch(u, { credentials: 'include' })
        .then(r => r.json())
        .then(data => done({ success: true, data: data }))
        .catch(err => done({ success: false, error: err.toString() }));
    """
    driver.set_script_timeout(30)
    
    all_transcripts = {}
    
    for cid in TARGET_COURSE_IDS:
        print(f"[*] Fetching block transcripts for: {cid}...")
        res = driver.execute_async_script(script, cid)
        if not res.get("success"):
            print(f"  [!] Failed: {res.get('error')}")
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
                    all_transcripts[vid_id] = t_url
                    count += 1
                    
        print(f"  [✓] Found {count} official transcripts for {cid}")

    driver.quit()
    
    out_file = BASE_DIR / "data" / "iimbx_transcripts_map.json"
    with open(out_file, "w") as f:
        json.dump(all_transcripts, f, indent=2)
        
    print(f"\n[+] Total {len(all_transcripts)} transcript URLs saved to {out_file}")

if __name__ == "__main__":
    run()

