from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

options = Options()
options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
driver = webdriver.Chrome(options=options)

course_id = 'course-v1:IIMBx+ST71x+BBA_DBE_B1'

script = """
const done = arguments[arguments.length - 1];
const courseId = 'course-v1:IIMBx+ST71x+BBA_DBE_B1';
const url = `https://iimbx.edu.in/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}&all_blocks=true&depth=all&requested_fields=children,student_view_data,type,display_name`;

fetch(url, { credentials: 'include' })
    .then(r => r.json())
    .then(d => done(d))
    .catch(e => done({ error: e.toString() }));
"""
driver.set_script_timeout(15)
res = driver.execute_async_script(script)
print("Root:", res.get("root"))
blocks = res.get("blocks", {})
print("Total blocks in full blocks API:", len(blocks))
types = {}
for bid, b in blocks.items():
    t = b.get("type")
    types[t] = types.get(t, 0) + 1
print("Block types:", types)

# Look for video blocks
videos = []
for bid, b in blocks.items():
    if b.get("type") == "video":
        videos.append((b.get("display_name"), b.get("student_view_data")))

print(f"Total video blocks: {len(videos)}")
if videos:
    print("\nSample video 1:")
    print("Title:", videos[0][0])
    print("SVD:", json.dumps(videos[0][1], indent=2))
