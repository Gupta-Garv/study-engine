from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

options = Options()
options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
driver = webdriver.Chrome(options=options)

script = """
const done = arguments[arguments.length - 1];
const courseId = 'course-v1:IIMBx+ST71x+BBA_DBE_B1';
const seqId = 'block-v1:IIMBx+ST71x+BBA_DBE_B1+type@sequential+block@030d538b3f6b4d82b5d6a9fa093e9ce6';

const tests = [
    `/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}`,
    `/api/courses/v1/blocks/${encodeURIComponent(courseId)}`,
    `/api/courses/v1/blocks/${encodeURIComponent(seqId)}`,
    `/api/courses/v1/blocks/?block_id=${encodeURIComponent(seqId)}`,
    `/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}&username=Garv_Gupta`,
    `/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}&depth=all`,
    `/api/courses/v1/blocks/?course_id=${encodeURIComponent(courseId)}&all_blocks=true`
];

async function run() {
    const out = {};
    for (const u of tests) {
        try {
            const r = await fetch('https://iimbx.edu.in' + u, { credentials: 'include' });
            out[u] = { status: r.status };
            if (r.ok) {
                const text = await r.text();
                out[u].len = text.length;
                out[u].preview = text.substring(0, 150);
            }
        } catch(e) {
            out[u] = { error: e.toString() };
        }
    }
    done(out);
}
run();
"""
driver.set_script_timeout(20)
res = driver.execute_async_script(script)
print(json.dumps(res, indent=2))
