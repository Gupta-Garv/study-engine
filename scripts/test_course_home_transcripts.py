from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import json

BASE_DIR = Path('/Users/apple/.gemini/study-engine')
options = Options()
options.add_argument(f'--user-data-dir={BASE_DIR}/chrome_profile')
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=options)
cid = 'course-v1:IIMBx+ST71x+BBA_DBE_B1'
# Navigate to the actual course home first so cookies for iimbx.edu.in are active
driver.get(f'https://apps.iimbx.edu.in/learning/course/{cid}/home')
print('Current URL:', driver.current_url)

script = """
const done = arguments[arguments.length - 1];
const courseId = arguments[0];
const u = `https://iimbx.edu.in/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}&username=Garv_Gupta&depth=all&requested_fields=children,student_view_data,type,display_name&student_view_data=video`;

fetch(u, { credentials: 'include' })
    .then(r => r.json())
    .then(data => done({ success: true, data: data }))
    .catch(err => done({ success: false, error: err.toString() }));
"""
driver.set_script_timeout(20)
res = driver.execute_async_script(script, cid)
driver.quit()

print("Success:", res.get("success"))
blocks = res.get("data", {}).get("blocks", {})
print("Blocks count:", len(blocks))
for bid, b in blocks.items():
    if b.get("type") == "video":
        svd = b.get("student_view_data") or {}
        transcripts = svd.get("transcripts") or {}
        print("Sample video:", b.get("display_name"))
        print("Transcripts:", transcripts)
        break

