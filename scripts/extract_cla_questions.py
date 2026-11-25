#!/usr/bin/env python3
"""
Extract all CLA and Mid-Term assessment questions, options, correct answers,
explanations, and embedded images from the IIMBx portal via Chrome (port 9222).
"""

import base64
import json
import os
import re
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "data" / "cla_questions"

COURSES = [
    {
        "slug": "corporate_finance",
        "name": "Corporate Finance",
        "edx_id": "course-v1:IIMBx+FA71x+BBA_DBE_B1",
        "assessments": [
            ("Module 1", "CLA 1", "block-v1:IIMBx+FA71x+BBA_DBE_B1+type@sequential+block@7c65e258636f46f0ade4a75a5d5ea42f"),
            ("Module 2", "CLA 2", "block-v1:IIMBx+FA71x+BBA_DBE_B1+type@sequential+block@1bbf3d707b9c424db5976d7ae3c368b0"),
            ("Module 3", "CLA 3", "block-v1:IIMBx+FA71x+BBA_DBE_B1+type@sequential+block@cb49356bf91b44c2b00504e2de4c895f"),
            ("Module 4", "CLA 4", "block-v1:IIMBx+FA71x+BBA_DBE_B1+type@sequential+block@a98656c677ce468f875fbaff9c5e3638"),
            ("Module 5", "CLA 5", "block-v1:IIMBx+FA71x+BBA_DBE_B1+type@sequential+block@3f6909fe4d2c4966bc859077f38c37f7"),
            ("Module 6", "CLA 6", "block-v1:IIMBx+FA71x+BBA_DBE_B1+type@sequential+block@1349df727ff3401f94c09d21c34cda06"),
            ("Module 7", "CLA 7", "block-v1:IIMBx+FA71x+BBA_DBE_B1+type@sequential+block@2dc735796a6f4fbd8a964b31be2bad65"),
            ("Module 8", "CLA 8", "block-v1:IIMBx+FA71x+BBA_DBE_B1+type@sequential+block@cbf28fad7272451896101b48452bda4e"),
        ],
    },
    {
        "slug": "critical_thinking",
        "name": "Critical Thinking",
        "edx_id": "course-v1:IIMBx+MD71x+BBA_DBE_B1",
        "assessments": [
            ("Module 1", "CLA 1", "block-v1:IIMBx+MD71x+BBA_DBE_B1+type@sequential+block@b5cad90c71f14e5cabd9441bdcc6d62d"),
            ("Module 2", "CLA 2", "block-v1:IIMBx+MD71x+BBA_DBE_B1+type@sequential+block@54bbfc0de0fd4dc08f928681e2a57256"),
            ("Module 3", "CLA 3", "block-v1:IIMBx+MD71x+BBA_DBE_B1+type@sequential+block@b17d699fe12b43fc9a61478ad03a8c16"),
            ("Module 4", "CLA 4", "block-v1:IIMBx+MD71x+BBA_DBE_B1+type@sequential+block@6796b28a7b004cb393d809487a38cfe9"),
            ("Module 5", "CLA 5", "block-v1:IIMBx+MD71x+BBA_DBE_B1+type@sequential+block@c9c827811a2a4d9aae9dbdadb2cbdf91"),
            ("Module 6", "CLA 6", "block-v1:IIMBx+MD71x+BBA_DBE_B1+type@sequential+block@70b55c49f3b74bc4aa2fcebd09cb8cc0"),
            ("Module 7", "CLA 7", "block-v1:IIMBx+MD71x+BBA_DBE_B1+type@sequential+block@1ad943ffbfd04de6aba12601c6d3bab8"),
        ],
    },
    {
        "slug": "family_business",
        "name": "Family Business Strategy",
        "edx_id": "course-v1:IIMBx+ST71x+BBA_DBE_B1",
        "assessments": [
            ("Module 1", "CLA 1", "block-v1:IIMBx+ST71x+BBA_DBE_B1+type@sequential+block@bb659c4417c64963aeae2f37e82c20e6"),
            ("Module 2", "CLA 2", "block-v1:IIMBx+ST71x+BBA_DBE_B1+type@sequential+block@4c709730c5254d24a7e3ddcaa9e2f13e"),
            ("Module 3", "CLA 3", "block-v1:IIMBx+ST71x+BBA_DBE_B1+type@sequential+block@14a1b1f044454ab39df29f45471f127c"),
            ("Module 4", "CLA 4", "block-v1:IIMBx+ST71x+BBA_DBE_B1+type@sequential+block@aec5e1ab771d4ea6b020cb251304fd61"),
            ("Module 5", "CLA 5", "block-v1:IIMBx+ST71x+BBA_DBE_B1+type@sequential+block@58e22e49de064c0aaca1750b40e2a40c"),
            ("Module 6", "CLA 6", "block-v1:IIMBx+ST71x+BBA_DBE_B1+type@sequential+block@57f1f0fd94a4491c8c887f95ef93fe1d"),
            ("Module 7", "CLA 7", "block-v1:IIMBx+ST71x+BBA_DBE_B1+type@sequential+block@3b56a7e3d92e4089a4d46a02d06eebb6"),
            ("Module 8", "CLA 8", "block-v1:IIMBx+ST71x+BBA_DBE_B1+type@sequential+block@6c2658fd54be4f9ebedfaf71a8c9a4f9"),
        ],
    },
    {
        "slug": "data_visualisation",
        "name": "Data Visualisation for Business Decisions",
        "edx_id": "course-v1:IIMBx+DS71x+BBA_DBE_B1",
        "assessments": [
            ("Mid-Term 1", "Mid-Term 1 Quiz", "block-v1:IIMBx+DS71x+BBA_DBE_B1+type@sequential+block@ea9e0d28a86f4a9196b7e553d9c963a9"),
            ("Mid-Term 2", "Mid-Term 2 Quiz", "block-v1:IIMBx+DS71x+BBA_DBE_B1+type@sequential+block@a88d97b04b634b54900a0d8ddfcfb633"),
        ],
    },
]

UNAVAILABLE_MARKERS = [
    "due date has passed",
    "timed out",
    "assessment not available",
    "not available",
    "past due",
    "time has expired",
    "this exam is closed",
    "no longer available",
    "you have not started",
    "exam has ended",
]


def wait_for_unit_iframe(driver, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        driver.switch_to.default_content()
        iframes = driver.find_elements(By.ID, "unit-iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
            probs = driver.find_elements(By.CSS_SELECTOR, ".problems-wrapper")
            body_txt = (driver.execute_script("return document.body ? document.body.innerText : '';") or "").strip()
            if probs or len(body_txt) > 50:
                return True
        else:
            body_txt = (driver.execute_script("return document.body ? document.body.innerText : '';") or "").lower()
            if any(m in body_txt for m in UNAVAILABLE_MARKERS):
                return False
        time.sleep(0.5)
    return False


def download_image_in_browser(driver, img_el, dest_path: Path) -> bool:
    src = img_el.get_attribute("src") or ""
    if src.startswith("data:image"):
        try:
            header, b64 = src.split(",", 1)
            dest_path.write_bytes(base64.b64decode(b64))
            return True
        except Exception:
            pass

    if src:
        script = """
        const done = arguments[arguments.length - 1];
        fetch(arguments[0], { credentials: 'include' })
            .then(r => {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.blob();
            })
            .then(blob => {
                const reader = new FileReader();
                reader.onloadend = () => done({ ok: true, dataUrl: reader.result });
                reader.readAsDataURL(blob);
            })
            .catch(e => done({ ok: false, err: e.toString() }));
        """
        try:
            driver.set_script_timeout(15)
            res = driver.execute_async_script(script, src)
            if res and res.get("ok") and res.get("dataUrl"):
                _, b64 = res["dataUrl"].split(",", 1)
                dest_path.write_bytes(base64.b64decode(b64))
                return True
        except Exception:
            pass

    # Fallback: element screenshot
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", img_el)
        time.sleep(0.2)
        img_el.screenshot(str(dest_path))
        return True
    except Exception:
        return False


def extract_assessment(driver, course_slug: str, edx_id: str, module_label: str, assess_label: str, seq_id: str, img_dir: Path):
    url = f"https://apps.iimbx.edu.in/learning/course/{edx_id}/{seq_id}"
    driver.switch_to.default_content()
    driver.get(url)
    time.sleep(3)

    # Check outer page for unavailable/timed-out before iframe
    outer_text = (driver.execute_script("return document.body ? document.body.innerText : '';") or "").strip()
    outer_lower = outer_text.lower()

    has_iframe = wait_for_unit_iframe(driver, timeout=15)
    if not has_iframe:
        reason = "No unit-iframe or timed out / unavailable"
        for m in UNAVAILABLE_MARKERS:
            if m in outer_lower:
                reason = f"Unavailable ({m})"
                break
        return {
            "module": module_label,
            "assessment": assess_label,
            "seq_id": seq_id,
            "status": "unavailable",
            "reason": reason,
            "questions": [],
        }

    # Inside unit-iframe
    iframe_text = (driver.execute_script("return document.body ? document.body.innerText : '';") or "").strip()
    iframe_lower = iframe_text.lower()
    probs = driver.find_elements(By.CSS_SELECTOR, ".problems-wrapper")

    if not probs:
        reason = "No problems found"
        for m in UNAVAILABLE_MARKERS:
            if m in iframe_lower or m in outer_lower:
                reason = f"Unavailable ({m})"
                break
        return {
            "module": module_label,
            "assessment": assess_label,
            "seq_id": seq_id,
            "status": "unavailable",
            "reason": reason,
            "raw_snippet": iframe_text[:400],
            "questions": [],
        }

    # Click all enabled "Show answer" buttons so correct answers & solutions appear
    show_btns = driver.find_elements(By.CSS_SELECTOR, "button.show")
    clicked = 0
    for btn in show_btns:
        try:
            if btn.is_displayed() and btn.is_enabled():
                driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", btn)
                clicked += 1
        except Exception:
            pass
    if clicked:
        time.sleep(2.5)

    # Extract each problem
    slug_prefix = re.sub(r"[^a-z0-9]+", "_", f"{module_label}_{assess_label}".lower()).strip("_")
    questions = []
    probs = driver.find_elements(By.CSS_SELECTOR, ".problems-wrapper")

    for idx, prob in enumerate(probs, start=1):
        # Extract structured fields via JS
        q_data = driver.execute_script("""
        const prob = arguments[0];
        const titleEl = prob.querySelector('h3.problem-header');
        const progressEl = prob.querySelector('.problem-progress');
        const problemBody = prob.querySelector('.problem');

        // Clone problem body to extract clean stem without options/actions/solutions
        let stemText = '';
        let stemHtml = '';
        if (problemBody) {
            const clone = problemBody.cloneNode(true);
            clone.querySelectorAll('.choicegroup, .capa_inputtype, .status, .action, .solution-span, .notification, script, style').forEach(el => el.remove());
            stemText = clone.innerText.trim();
            stemHtml = clone.innerHTML.trim();
        }

        // Options (radio or checkbox)
        const options = [];
        let qType = 'unknown';
        const radios = prob.querySelectorAll('input[type="radio"]');
        const checkboxes = prob.querySelectorAll('input[type="checkbox"]');
        const textInputs = prob.querySelectorAll('input[type="text"], input[type="number"]');

        if (radios.length > 0) qType = 'single_choice';
        else if (checkboxes.length > 0) qType = 'multi_select';
        else if (textInputs.length > 0) qType = 'numerical_or_text';

        const fields = prob.querySelectorAll('.choicegroup .field');
        fields.forEach((f, i) => {
            const inp = f.querySelector('input');
            const lbl = f.querySelector('label');
            const lblText = lbl ? lbl.innerText.trim() : '';
            const cls = lbl ? (lbl.className || '') : '';
            const isCorrect = cls.includes('choicegroup_correct') || cls.includes('correct') || !!f.querySelector('.correct');
            const wasSelected = inp ? inp.checked : false;
            options.push({
                index: i,
                text: lblText,
                is_correct: isCorrect,
                was_selected: wasSelected
            });
        });

        // Text/numerical answers if any
        const textAnswers = [];
        prob.querySelectorAll('.textline .answer, .capa_inputtype .answer').forEach(a => {
            const t = a.innerText.trim();
            if (t) textAnswers.push(t);
        });

        // Solution / explanation if revealed
        let solutionText = '';
        const sol = prob.querySelector('.solution-span, .detailed-solution');
        if (sol) solutionText = sol.innerText.trim();

        // Status message (correct / incorrect / unanswered)
        const statusEl = prob.querySelector('.status');
        const statusText = statusEl ? statusEl.innerText.trim() : '';

        return {
            title: titleEl ? titleEl.innerText.trim() : '',
            score: prob.getAttribute('data-problem-score') || '',
            total_possible: prob.getAttribute('data-problem-total-possible') || '',
            progress: progressEl ? progressEl.innerText.trim() : '',
            type: qType,
            stem: stemText,
            stem_html: stemHtml,
            options: options,
            text_answers: textAnswers,
            solution: solutionText,
            status_text: statusText
        };
        """, prob)

        # Find all images inside this problem
        imgs = prob.find_elements(By.TAG_NAME, "img")
        saved_imgs = []
        for j, img_el in enumerate(imgs, start=1):
            src = img_el.get_attribute("src") or ""
            # Skip tiny UI icons if any (like 16x16 checkmarks)
            try:
                w = int(img_el.get_attribute("naturalWidth") or 0)
                h = int(img_el.get_attribute("naturalHeight") or 0)
                if w > 0 and h > 0 and w < 30 and h < 30:
                    continue
            except Exception:
                pass
            ext = "png"
            m = re.search(r"\.(png|jpg|jpeg|gif|webp|svg)(?:\?|$)", src.lower())
            if m:
                ext = m.group(1)
            fname = f"{slug_prefix}_q{idx}_img{j}.{ext}"
            dest = img_dir / fname
            ok = download_image_in_browser(driver, img_el, dest)
            if ok:
                saved_imgs.append(f"images/{fname}")

        q_data["question_number"] = idx
        q_data["images"] = saved_imgs
        q_data["correct_indices"] = [o["index"] for o in q_data["options"] if o["is_correct"]]
        questions.append(q_data)

    return {
        "module": module_label,
        "assessment": assess_label,
        "seq_id": seq_id,
        "status": "extracted",
        "question_count": len(questions),
        "image_count": sum(len(q["images"]) for q in questions),
        "questions": questions,
    }


def main():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)

    summary = {}
    for c in COURSES:
        slug = c["slug"]
        cname = c["name"]
        edx_id = c["edx_id"]
        c_dir = OUT_DIR / slug
        img_dir = c_dir / "images"
        img_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n================ {cname} ================")
        results = []
        total_q = 0
        total_img = 0
        unavail = []

        for mod_label, assess_label, seq_id in c["assessments"]:
            res = extract_assessment(driver, slug, edx_id, mod_label, assess_label, seq_id, img_dir)
            results.append(res)
            if res["status"] == "extracted":
                qc = res["question_count"]
                ic = res["image_count"]
                total_q += qc
                total_img += ic
                print(f"  [OK] {mod_label} ({assess_label}): {qc} questions, {ic} images")
            else:
                unavail.append(f"{mod_label} ({assess_label}): {res['reason']}")
                print(f"  [SKIP] {mod_label} ({assess_label}): {res['reason']}")

        out_file = c_dir / "cla_questions.json"
        out_file.write_text(json.dumps({
            "course": cname,
            "slug": slug,
            "edx_id": edx_id,
            "total_questions": total_q,
            "total_images": total_img,
            "assessments": results,
        }, indent=2, ensure_ascii=False))

        summary[slug] = {
            "course": cname,
            "total_questions": total_q,
            "total_images": total_img,
            "extracted_modules": [f"{r['module']} ({r['question_count']}Q, {r['image_count']}img)" for r in results if r["status"] == "extracted"],
            "unavailable_modules": unavail,
            "file": str(out_file),
        }

    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print("\n=== EXTRACTION COMPLETE ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
