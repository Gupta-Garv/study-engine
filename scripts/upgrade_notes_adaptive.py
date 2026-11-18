#!/usr/bin/env python3
"""
Parallel, resumable, zero-data-loss batch upgrade of `topics.notes_markdown`
to the Adaptive Academic Note Architecture (v2).

- Touches ONLY `topics.notes_markdown` (preserves MCQs, subjectives, flashcards,
  key moments, slides, personal canvases, copilot chats, and exam tests).
- Invalidates stale cached TTS audio for each upgraded topic so Studio Neural Voice
  reads the new crisp notes.
- Exports static data (`study_data.js`) after each course completes.
"""

from __future__ import annotations

import os
import sys
import re
import json
import time
import sqlite3
import logging
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.llm_client import synthesize_adaptive_notes_only
from core.db import export_static_data

DB_PATH = BASE_DIR / "data" / "study_vault.db"
AUDIO_CACHE_DIR = BASE_DIR / "data" / "audio_cache"
CHECKPOINT_PATH = BASE_DIR / "data" / "adaptive_upgrade_checkpoint.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("adaptive_upgrade")

COURSE_PRIORITY = [
    "Family Business Strategy",
    "Corporate Finance",
    "Data Visualisation for Business Decisions",
    "Critical Thinking",
    "Startup Dilemmas: Founding or Joining",
]

MATH_KEYWORDS_RE = re.compile(
    r"\b(npv|irr|wacc|capm|pv|fv|annuity|perpetuity|bond|yield|discount|payback|"
    r"beta|variance|standard deviation|sharpe|gordon|dividend|leverage|ebit|"
    r"ebitda|depreciation|tax shield|rate of return|compounding|present value|"
    r"future value|cost of capital|valuation|formula|equation)\b",
    re.IGNORECASE,
)

db_lock = threading.Lock()
ckpt_lock = threading.Lock()


def load_checkpoint() -> set[str]:
    if CHECKPOINT_PATH.exists():
        try:
            data = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
            return set(data.get("completed_ids", []))
        except Exception:
            pass
    return set()


def save_checkpoint(completed_ids: set[str], stats: dict):
    with ckpt_lock:
        payload = {
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_count": len(completed_ids),
            "completed_ids": sorted(completed_ids),
            "stats": stats,
        }
        CHECKPOINT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def validate_note(md: str) -> tuple[bool, str]:
    if not md or len(md.strip()) < 120:
        return False, "too_short"
    words = len(md.split())
    if words < 45:
        return False, f"word_count_too_low({words})"
    if words > 950:
        return False, f"word_count_too_high({words})"
    lower = md.lower()
    if '"mcqs":' in lower or '"flashcards":' in lower or '"subjective_questions":' in lower:
        return False, "leaked_json"
    if "no mathematical formulas introduced" in lower or "conceptual session:" in lower:
        return False, "boilerplate_no_formula"
    if "core takeaway" not in lower and not md.lstrip().startswith("#"):
        return False, "missing_header_structure"
    return True, "ok"


def invalidate_topic_audio_cache(topic_id: str):
    if not AUDIO_CACHE_DIR.exists():
        return
    for p in AUDIO_CACHE_DIR.glob(f"{topic_id}_*"):
        try:
            p.unlink()
        except Exception:
            pass


def update_topic_notes_in_db(topic_id: str, new_notes: str):
    with db_lock:
        conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
        try:
            conn.execute(
                "UPDATE topics SET notes_markdown = ? WHERE id = ?",
                (new_notes, topic_id),
            )
            conn.commit()
        finally:
            conn.close()
    invalidate_topic_audio_cache(topic_id)


def is_quantitative_lecture(course_name: str, title: str, transcript: str) -> bool:
    if course_name != "Corporate Finance":
        return False
    combined = f"{title} {transcript[:2500]}"
    return bool(MATH_KEYWORDS_RE.search(combined))


def process_one_topic(row: dict, use_high_precision_for_cf: bool) -> dict:
    tid = row["id"]
    course = row["course_name"]
    module = row["module_name"]
    title = row["title"]
    transcript = row["transcript_text"] or ""
    old_notes = row["notes_markdown"] or ""
    old_words = len(old_notes.split())

    prefer_hp = use_high_precision_for_cf and is_quantitative_lecture(course, title, transcript)

    last_err = ""
    for attempt in range(1, 4):
        try:
            t0 = time.time()
            # If retry after primary failed validation, try high-precision secondary model
            hp_flag = prefer_hp or (attempt == 3)
            new_notes = synthesize_adaptive_notes_only(
                course_name=course,
                module_name=module,
                topic_title=title,
                transcript_text=transcript,
                existing_notes_fallback=old_notes,
                prefer_high_precision=hp_flag,
            )
            ok, reason = validate_note(new_notes)
            if not ok:
                last_err = f"validation_failed:{reason}"
                logger.warning(f"[{tid}] {title}: attempt {attempt} failed ({reason}), retrying...")
                continue

            update_topic_notes_in_db(tid, new_notes)
            new_words = len(new_notes.split())
            elapsed = round(time.time() - t0, 2)
            return {
                "id": tid,
                "course": course,
                "title": title,
                "ok": True,
                "old_words": old_words,
                "new_words": new_words,
                "elapsed": elapsed,
                "hp": hp_flag,
            }
        except Exception as e:
            last_err = str(e)
            logger.warning(f"[{tid}] {title}: attempt {attempt} error: {e}")
            time.sleep(2.0 * attempt)

    return {
        "id": tid,
        "course": course,
        "title": title,
        "ok": False,
        "error": last_err,
        "old_words": old_words,
        "new_words": old_words,
        "elapsed": 0.0,
    }


def main():
    use_hp = "--fast-cf" not in sys.argv
    max_workers = 6

    completed_ids = load_checkpoint()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = [
        dict(r)
        for r in conn.execute(
            """
            SELECT t.id, c.name AS course_name, m.name AS module_name, t.title,
                   t.duration_seconds, t.transcript_text, t.notes_markdown
            FROM topics t
            JOIN modules m ON t.module_id = m.id
            JOIN courses c ON m.course_id = c.id
            WHERE t.status = 'completed'
            ORDER BY c.id, m.rowid, t.rowid
            """
        ).fetchall()
    ]
    conn.close()

    # Group by course in priority order
    by_course: dict[str, list[dict]] = {}
    for r in rows:
        by_course.setdefault(r["course_name"], []).append(r)

    ordered_courses = [c for c in COURSE_PRIORITY if c in by_course]
    for c in by_course:
        if c not in ordered_courses:
            ordered_courses.append(c)

    total_all = len(rows)
    remaining_all = sum(1 for r in rows if r["id"] not in completed_ids)
    logger.info(
        f"Starting Adaptive Notes v2 Upgrade: {total_all} total lectures "
        f"({len(completed_ids)} already done, {remaining_all} remaining, workers={max_workers}, hp_cf={use_hp})"
    )

    stats = {"upgraded": 0, "failed": 0, "old_words_sum": 0, "new_words_sum": 0, "failed_ids": []}
    start_all = time.time()

    for course_name in ordered_courses:
        course_rows = [r for r in by_course[course_name] if r["id"] not in completed_ids]
        if not course_rows:
            logger.info(f"Course '{course_name}': already 100% upgraded, skipping.")
            continue

        logger.info(f"=== Course: {course_name} ({len(course_rows)} lectures to upgrade) ===")
        c_done = 0
        c_total = len(course_rows)

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {
                pool.submit(process_one_topic, r, use_hp): r for r in course_rows
            }
            for fut in as_completed(futures):
                res = fut.result()
                c_done += 1
                if res["ok"]:
                    completed_ids.add(res["id"])
                    stats["upgraded"] += 1
                    stats["old_words_sum"] += res["old_words"]
                    stats["new_words_sum"] += res["new_words"]
                    pct = round((1 - res["new_words"] / max(res["old_words"], 1)) * 100)
                    if c_done % 10 == 0 or c_done == c_total:
                        elapsed_min = (time.time() - start_all) / 60.0
                        logger.info(
                            f"[{course_name}] {c_done}/{c_total} | Total done: {len(completed_ids)}/{total_all} "
                            f"({elapsed_min:.1f}m elapsed) | Last: '{res['title'][:38]}' "
                            f"{res['old_words']}w -> {res['new_words']}w ({pct:+d}%)"
                        )
                    if len(completed_ids) % 10 == 0:
                        save_checkpoint(completed_ids, stats)
                else:
                    stats["failed"] += 1
                    stats["failed_ids"].append({"id": res["id"], "title": res["title"], "error": res.get("error")})
                    logger.error(f"FAILED [{res['id']}] {res['title']}: {res.get('error')}")

        save_checkpoint(completed_ids, stats)
        logger.info(f"Finished course '{course_name}'. Syncing static data export...")
        try:
            export_static_data()
            logger.info("Static data exported cleanly.")
        except Exception as e:
            logger.warning(f"Static export warning: {e}")

    total_mins = (time.time() - start_all) / 60.0
    avg_red = (
        round((1 - stats["new_words_sum"] / max(stats["old_words_sum"], 1)) * 100)
        if stats["old_words_sum"] > 0
        else 0
    )
    logger.info(
        f"ALL DONE in {total_mins:.1f}m! Upgraded: {stats['upgraded']} | Failed: {stats['failed']} | "
        f"Words: {stats['old_words_sum']} -> {stats['new_words_sum']} ({avg_red}% overall compression)"
    )


if __name__ == "__main__":
    main()
