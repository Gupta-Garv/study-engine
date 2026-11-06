from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
driver = webdriver.Chrome(options=options)

url = 'https://apps.iimbx.edu.in/learning/course/course-v1:IIMBx+ST71x+BBA_DBE_B1/home'
driver.get(url)
time.sleep(4)
print("Loaded URL:", driver.current_url)
print("Title:", driver.title)

# Let's inspect what APIs or course structure is loaded in window or DOM
script = """
return {
    title: document.title,
    h1: Array.from(document.querySelectorAll('h1, h2, h3')).map(h => h.innerText.trim()).slice(0, 15),
    sections: Array.from(document.querySelectorAll('button, a')).filter(a => a.innerText.toLowerCase().includes('module') || a.innerText.toLowerCase().includes('week') || a.innerText.toLowerCase().includes('chapter')).map(a => a.innerText.trim()).slice(0, 15)
};
"""
res = driver.execute_script(script)
import json
print(json.dumps(res, indent=2))

