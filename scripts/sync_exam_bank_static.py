#!/usr/bin/env python3
"""
Syncs generated exam banks and extracted CLA baselines (including images) into static/exam_bank/
so the frontend Exam Arena can load them cleanly in both local FastAPI and static hosting.
"""

import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXAM_BANK_DIR = BASE_DIR / "data" / "exam_bank"
CLA_DIR = BASE_DIR / "data" / "cla_questions"
STATIC_OUT = BASE_DIR / "static" / "exam_bank"

SUBJECTS = [
    {
        "slug": "family_business",
        "course_id": "db945ff9",
        "name": "Family Business Strategy",
        "exam_date": "05 Dec 2026 • 12:00–02:00 PM",
        "duration_mins": 120,
        "total_marks": 75,
        "calculator": False,
        "negative_marking": False,
        "pattern_summary": "Sec A: 30 MCQs (1m) + Sec B: 9 Short Answers (5m, ≤100w)",
    },
    {
        "slug": "data_visualisation",
        "course_id": "deb83564",
        "name": "Data Visualisation for Business Decisions",
        "exam_date": "05 Dec 2026 • 09:00–10:00 AM",
        "duration_mins": 60,
        "total_marks": 30,
        "calculator": False,
        "negative_marking": True,
        "pattern_summary": "Sec A: 14 MCQs (1m) + Sec B: 8 MSQs (2m, partial/negative floored at 0)",
    },
    {
        "slug": "critical_thinking",
        "course_id": "d9173426",
        "name": "Critical Thinking",
        "exam_date": "06 Dec 2026 • 09:00–11:00 AM",
        "duration_mins": 120,
        "total_marks": 50,
        "calculator": False,
        "negative_marking": False,
        "pattern_summary": "Sec A: 14 MCQs (1m) + Sec B: 6 Short (2m, 20–30w) + Sec C: 3 Cases (24m, 40–50w)",
    },
    {
        "slug": "corporate_finance",
        "course_id": "2989cdfe",
        "name": "Corporate Finance",
        "exam_date": "06 Dec 2026 • 01:00–03:00 PM",
        "duration_mins": 120,
        "total_marks": 75,
        "calculator": True,
        "negative_marking": False,
        "pattern_summary": "Sec A: 50 MCQs (1.5m) • Scientific Calc + Formula Sheet allowed",
    },
]


def main():
    STATIC_OUT.mkdir(parents=True, exist_ok=True)
    index = {"subjects": []}

    for s in SUBJECTS:
        slug = s["slug"]
        s_out = STATIC_OUT / slug
        s_out.mkdir(parents=True, exist_ok=True)

        pred_src = EXAM_BANK_DIR / f"{slug}_exam_bank.json"
        cla_src = CLA_DIR / slug / "cla_questions.json"
        img_src = CLA_DIR / slug / "images"

        has_pred = pred_src.exists()
        has_cla = cla_src.exists()

        pred_counts = {"subjective": 0, "mcq": 0, "msq": 0, "case": 0}
        if has_pred:
            shutil.copy2(pred_src, s_out / "exam_bank.json")
            pd = json.loads(pred_src.read_text())
            pred_counts["subjective"] = len(pd.get("subjective_questions", []))
            pred_counts["mcq"] = len(pd.get("mcq_questions", []))
            pred_counts["msq"] = len(pd.get("msq_questions", []))
            pred_counts["case"] = len(pd.get("case_questions", []))

        cla_count = 0
        if has_cla:
            shutil.copy2(cla_src, s_out / "cla_questions.json")
            cd = json.loads(cla_src.read_text())
            cla_count = cd.get("total_questions", 0)

        if img_src.exists() and any(img_src.iterdir()):
            img_dest = s_out / "images"
            img_dest.mkdir(parents=True, exist_ok=True)
            for f in img_src.iterdir():
                if f.is_file():
                    shutil.copy2(f, img_dest / f.name)

        index["subjects"].append({
            **s,
            "has_predicted": has_pred,
            "has_cla": has_cla,
            "predicted_counts": pred_counts,
            "cla_count": cla_count,
        })

    (STATIC_OUT / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False))
    print(f"Synced exam_bank static assets to {STATIC_OUT}")
    for subj in index["subjects"]:
        print(f"  - {subj['name']}: predicted={subj['predicted_counts']}, cla={subj['cla_count']}")


if __name__ == "__main__":
    main()
