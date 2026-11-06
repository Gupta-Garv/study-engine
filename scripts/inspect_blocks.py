from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

options = Options()
options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
driver = webdriver.Chrome(options=options)

course_id = 'course-v1:IIMBx+ST71x+BBA_DBE_B1'

script = """
const courseId = arguments[0];
const done = arguments[arguments.length - 1];
const url = `/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}&all_blocks=true&depth=all&requested_fields=children,student_view_data,type,display_name`;

fetch(url)
    .then(r => r.json())
    .then(data => done(data))
    .catch(err => done({error: err.toString()}));
"""
driver.set_script_timeout(20)
res = driver.execute_async_script(script, course_id)
print("Root:", res.get("root"))
blocks = res.get("blocks", {})
print("Total blocks:", len(blocks))
types = {}
for bid, b in blocks.items():
    t = b.get("type")
    types[t] = types.get(t, 0) + 1
print("Block types:", types)

# Let's inspect a video block!
for bid, b in blocks.items():
    if b.get("type") == "video":
        print("\n--- SAMPLE VIDEO BLOCK ---")
        print("ID:", bid)
        print("Display name:", b.get("display_name"))
        print("Student view data:", json.dumps(b.get("student_view_data"), indent=2))
        break
