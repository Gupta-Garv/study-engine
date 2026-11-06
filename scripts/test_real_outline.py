from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

options = Options()
options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
driver = webdriver.Chrome(options=options)

course_id = 'course-v1:IIMBx+ST71x+BBA_DBE_B1'

script = """
const done = arguments[arguments.length - 1];
const url = 'https://iimbx.edu.in/api/course_home/outline/course-v1:IIMBx+ST71x+BBA_DBE_B1';

fetch(url, { credentials: 'include' })
    .then(r => r.json())
    .then(d => done(d))
    .catch(e => done({ error: e.toString() }));
"""
driver.set_script_timeout(15)
res = driver.execute_async_script(script)
print("Keys in outline response:", list(res.keys()) if isinstance(res, dict) else type(res))
if isinstance(res, dict):
    print("Course blocks keys:", list(res.get("course_blocks", {}).keys()))
    blocks = res.get("course_blocks", {}).get("blocks", {})
    print("Total blocks in outline:", len(blocks))
    # print sample
    sample_blocks = list(blocks.items())[:5]
    for bid, b in sample_blocks:
        print(f"[{b.get('type')}] {b.get('display_name')}")
