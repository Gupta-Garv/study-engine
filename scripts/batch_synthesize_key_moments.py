"""
Batch Synthesizer for High-Yield Key Moments & Speedrun Segments.
Processes topics with cross-lecture syllabus context (previous + next topics),
caching timestamped snippets and generated key moments into SQLite and static data.
"""

from __future__ import annotations

import sys
import os
import json
import time
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import db
from core.transcript import fetch_transcript, Snippet
from core.key_moments import get_adjacent_topics_context, synthesize_key_moments

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("batch_key_moments")


def process_course_key_moments(course_id: str = "a846c0e5"):
    conn = db.get_conn()
    conn.row_factory = db.sqlite3.Row

    # Fetch topics for course
    rows = conn.execute("""
        SELECT t.id, t.title, t.video_id, t.youtube_url, t.duration_seconds,
               t.transcript_text, t.transcript_snippets_json, t.key_moments_json,
               m.name as module_name, m.number as module_number, c.name as course_name
        FROM topics t
        JOIN modules m ON t.module_id = m.id
        JOIN courses c ON m.course_id = c.id
        WHERE c.id = ?
        ORDER BY m.number ASC, t.title ASC
    """, (course_id,)).fetchall()

    logger.info(f"Found {len(rows)} topics for course '{course_id}'. Starting key moments synthesis...")

    processed = 0
    skipped = 0

    for idx, r in enumerate(rows, 1):
        topic_id = r["id"]
        title = r["title"]
        existing_km = r["key_moments_json"]

        if existing_km and existing_km != "[]" and existing_km != '""':
            try:
                parsed = json.loads(existing_km)
                if isinstance(parsed, dict) and parsed.get("key_moments"):
                    logger.info(f"[{idx}/{len(rows)}] '{title}' already has {len(parsed['key_moments'])} key moments. Skipping.")
                    skipped += 1
                    continue
            except Exception:
                pass

        logger.info(f"[{idx}/{len(rows)}] Synthesizing high-yield moments for: '{title}'...")

        # 1. Get snippets
        snippets = []
        cached_snips = r["transcript_snippets_json"]
        if cached_snips and cached_snips != "[]":
            try:
                raw_list = json.loads(cached_snips)
                snippets = [Snippet(text=item["text"], start=float(item["start"]), duration=float(item.get("duration", 0))) for item in raw_list]
            except Exception:
                snippets = []

        if not snippets:
            try:
                snippets = fetch_transcript(r["youtube_url"], course_name=r["course_name"])
            except Exception as e:
                logger.warning(f"Could not fetch fresh transcript snippets for '{title}': {e}")
                snippets = []

        duration = snippets[-1].end if snippets else (r["duration_seconds"] or 0)
        snippets_json_str = json.dumps([{"text": s.text, "start": s.start, "duration": s.duration, "end": s.end} for s in snippets], ensure_ascii=False)

        # 2. Get adjacent topics context
        prev_t, next_t = get_adjacent_topics_context(conn, topic_id)

        # 3. Synthesize
        km_result = synthesize_key_moments(
            course_name=r["course_name"],
            module_name=r["module_name"],
            topic_title=title,
            snippets=snippets,
            total_duration_seconds=duration,
            prev_topic=prev_t,
            next_topic=next_t
        )

        km_json_str = json.dumps(km_result, ensure_ascii=False)

        conn.execute("""
            UPDATE topics
            SET duration_seconds = ?,
                transcript_snippets_json = ?,
                key_moments_json = ?
            WHERE id = ?
        """, (duration, snippets_json_str, km_json_str, topic_id))
        conn.commit()

        num_moments = len(km_result.get("key_moments", []))
        saved_pct = km_result.get("fluff_saved_percentage", 0)
        logger.info(f"[{idx}/{len(rows)}] Successfully synthesized {num_moments} key moments for '{title}' ({saved_pct}% fluff saved).")
        processed += 1
        time.sleep(0.5)

    db.export_static_data()
    logger.info(f"Batch completed! Processed: {processed}, Skipped: {skipped}, Total: {len(rows)}")


if __name__ == "__main__":
    cid = sys.argv[1] if len(sys.argv) > 1 else "a846c0e5"
    process_course_key_moments(cid)
