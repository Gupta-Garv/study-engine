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
blocks = res.get("course_blocks", {}).get("blocks", {})
types = {}
for bid, b in blocks.items():
    t = b.get("type")
    types[t] = types.get(t, 0) + 1
print("Block types in outline:", types)

sample_items = list(blocks.items())[:10]
for bid, b in sample_items:
    print(f"[{b.get('type')}] id={bid} | name={b.get('display_name')} | children={len(b.get('children', []))}")
