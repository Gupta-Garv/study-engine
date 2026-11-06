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
    .then(async r => {
        const text = await r.text();
        done({ status: r.status, text: text.substring(0, 500) });
    })
    .catch(err => done({ error: err.toString() }));
"""
driver.set_script_timeout(20)
res = driver.execute_async_script(script, course_id)
print(json.dumps(res, indent=2))
