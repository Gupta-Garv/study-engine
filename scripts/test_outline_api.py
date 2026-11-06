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

const urls = [
    `/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}&all_blocks=true&depth=all&requested_fields=children,student_view_data,type,display_name`,
    `/api/course_home/v1/outline/${encodeURIComponent(courseId)}`,
    `/learning/api/course_home/outline/${encodeURIComponent(courseId)}`
];

async function check() {
    const results = {};
    for (const u of urls) {
        try {
            const r = await fetch(u);
            results[u] = { status: r.status, ok: r.ok };
            if (r.ok) {
                const text = await r.text();
                results[u].sample = text.substring(0, 300);
            }
        } catch(e) {
            results[u] = { error: e.toString() };
        }
    }
    done(results);
}
check();
"""
driver.set_script_timeout(15)
res = driver.execute_async_script(script, course_id)
print(json.dumps(res, indent=2))
