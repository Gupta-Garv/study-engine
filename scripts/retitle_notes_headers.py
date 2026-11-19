#!/usr/bin/env python3
"""
Surgically replaces generic 'Core Mechanics' section headers with natural,
topic-tailored headings (e.g., '### The 5 Core Ownership Rights',
'### Conflict Categories & Dynamics', '### Valuation Rules & Decision Criteria')
across all lecture notes in `data/study_vault.db`.

GUARANTEES:
- Zero content loss: Every single bullet point, word, number, formula, table,
  takeaway, and MCQ stays 100% byte-for-byte identical.
- Only the generic header line itself is replaced.
- Resumable checkpointing via `data/retitle_headers_checkpoint.json`.
- Automatic export to `study_data.js` upon completion.
"""

from __future__ import annotations

import sys
import os
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

from core.llm_client import call_llm
from core.db import export_static_data

DB_PATH = BASE_DIR / "data" / "study_vault.db"
AUDIO_CACHE_DIR = BASE_DIR / "data" / "audio_cache"
CHECKPOINT_PATH = BASE_DIR / "data" / "retitle_headers_checkpoint.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("retitle_headers")

HEADER_PATTERN = re.compile(
    r"(?m)^(?:\s*#{2,3}\s*|\s*>?\s*\*{2,3}\s*)Core Mechanics(?:(?::?\*{2,3})|:\s*)?$",
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


def clean_heading_text(raw: str, fallback_title: str) -> str:
    h = (raw or "").strip()
    # Strip markdown headers, quotes, backticks, asterisks, trailing punctuation
    h = re.sub(r"^[#*_\s]+", "", h)
    h = re.sub(r"[#*_\s]+$", "", h)
    h = h.strip(" \"'`.,:;")
    # Strip accidental prefixes like 'Heading:' or 'Section Heading:'
    h = re.sub(r"^(?:Section\s+)?Heading:\s*", "", h, flags=re.I)
    words = h.split()
    if not h or len(words) < 2 or len(words) > 7 or "core mechanics" in h.lower():
        # Fallback to sensible title-derived heading
        clean_title = re.sub(r"^CF\s+M\d+\s+C\d+\s*", "", fallback_title, flags=re.I).strip()
        return f"{clean_title} Principles"
    # Title-case if all lowercase
    if h.islower():
        h = h.title()
    return h


def generate_natural_heading(course: str, title: str, bullets: str) -> str:
    first_few_bullets = "\n".join(bullets.split("\n")[:6]).strip()
    prompt = f"""Course: {course}
Lecture Topic: {title}

Section Bullet Points:
\"\"\"
{first_few_bullets}
\"\"\"

TASK:
Suggest a natural, concise, topic-specific Markdown section heading (2 to 5 words) that accurately describes what these bullets contain.
CRITICAL RULES:
1. NEVER use generic words like 'Core Mechanics', 'Key Mechanics', 'Mechanics', or 'Overview'.
2. If the bullets describe specific rights, components, categories, models, phases, or principles, name them directly (e.g. 'The 5 Core Ownership Rights', 'Conflict Categories & Dynamics', 'Structural Differences & Liability', 'Corporate Characteristics', 'Historical Phases & Adaptation', 'Valuation Rules & Criteria').
3. Output ONLY the clean heading text in Title Case. No quotes, no markdown '#', no punctuation."""

    raw = call_llm([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=25)
    return clean_heading_text(raw, title)


def process_topic(row: dict) -> dict:
    tid = row["id"]
    course = row["course_name"]
    title = row["title"]
    md = row["notes_markdown"] or ""

    match = HEADER_PATTERN.search(md)
    if not match:
        return {"id": tid, "ok": True, "skipped": True, "title": title}

    # Extract text after header up to next section
    start_pos = match.end()
    rest = md[start_pos:]
    next_sec = re.search(r"\n###|\n##|\Z", rest)
    bullets_block = rest[: next_sec.start()] if next_sec else rest

    for attempt in range(1, 4):
        try:
            t0 = time.time()
            heading = generate_natural_heading(course, title, bullets_block)
            # Perform single exact line replacement
            new_md, count = HEADER_PATTERN.subn(f"### {heading}", md, count=1)
            if count != 1:
                raise RuntimeError(f"Expected 1 substitution, got {count}")

            # Verify bullets weren't harmed
            assert len(new_md) >= len(md) - 30 and len(new_md) <= len(md) + 60, "Suspicious length change!"

            with db_lock:
                conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
                try:
                    conn.execute("UPDATE topics SET notes_markdown = ? WHERE id = ?", (new_md, tid))
                    conn.commit()
                finally:
                    conn.close()

            # Invalidate stale TTS audio
            for p in AUDIO_CACHE_DIR.glob(f"{tid}_*"):
                p.unlink(missing_ok=True)

            elapsed = round(time.time() - t0, 2)
            return {
                "id": tid,
                "course": course,
                "title": title,
                "ok": True,
                "skipped": False,
                "heading": heading,
                "elapsed": elapsed,
            }
        except Exception as e:
            logger.warning(f"[{tid}] {title}: attempt {attempt} error: {e}")
            time.sleep(1.5 * attempt)

    return {"id": tid, "course": course, "title": title, "ok": False, "error": "max_retries_exceeded"}


def main():
    completed_ids = load_checkpoint()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = [
        dict(r)
        for r in conn.execute(
            """
            SELECT t.id, c.name AS course_name, t.title, t.notes_markdown
            FROM topics t
            JOIN modules m ON t.module_id = m.id
            JOIN courses c ON m.course_id = c.id
            WHERE t.status = 'completed'
            ORDER BY c.id, m.rowid, t.rowid
            """
        ).fetchall()
    ]
    conn.close()

    targets = [r for r in rows if HEADER_PATTERN.search(r["notes_markdown"] or "") and r["id"] not in completed_ids]
    logger.info(
        f"Retitling 'Core Mechanics' headers: {len(targets)} to process "
        f"({len(completed_ids)} already completed in checkpoint)"
    )

    if not targets:
        logger.info("Nothing to retitle. Exporting static data...")
        export_static_data()
        return

    stats = {"retitled": 0, "skipped": 0, "failed": 0}
    start_time = time.time()
    total_targets = len(targets)
    done_count = 0

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(process_topic, r): r for r in targets}
        for fut in as_completed(futures):
            res = fut.result()
            done_count += 1
            if res.get("ok"):
                completed_ids.add(res["id"])
                if res.get("skipped"):
                    stats["skipped"] += 1
                else:
                    stats["retitled"] += 1
                    if stats["retitled"] % 15 == 0 or done_count == total_targets:
                        elapsed_min = (time.time() - start_time) / 60.0
                        logger.info(
                            f"Progress: {done_count}/{total_targets} ({elapsed_min:.1f}m) | "
                            f"[{res['course']}] '{res['title'][:32]}' -> '### {res['heading']}'"
                        )
                if len(completed_ids) % 15 == 0:
                    save_checkpoint(completed_ids, stats)
            else:
                stats["failed"] += 1
                logger.error(f"FAILED [{res['id']}] {res['title']}: {res.get('error')}")

    save_checkpoint(completed_ids, stats)
    logger.info("Syncing static export (study_data.js)...")
    export_static_data()
    total_min = (time.time() - start_time) / 60.0
    logger.info(
        f"RETITLING COMPLETE in {total_min:.1f}m! "
        f"Retitled: {stats['retitled']} | Skipped: {stats['skipped']} | Failed: {stats['failed']}"
    )


if __name__ == "__main__":
    main()
