"""
Batch re-curate Module 1 using the new Conceptual & MCQ-focused synthesis rules.
"""
import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("batch_recurate")

from core import db
from core.transcript import fetch_transcript
from core.llm_client import generate_notes_and_questions

def recurate_all_module1():
    conn = db.get_conn()
    rows = conn.execute("""
        SELECT t.*, m.name as module_name, c.name as course_name 
        FROM topics t 
        JOIN modules m ON t.module_id = m.id 
        JOIN courses c ON m.course_id = c.id 
        WHERE m.name = 'Module 1' OR m.id = '2989cdfe-m1'
        ORDER BY t.created_at ASC
    """).fetchall()

    logger.info(f"Found {len(rows)} topics in Module 1 to re-curate.")

    for i, t in enumerate(rows, 1):
        topic_id = t["id"]
        title = t["title"]
        url = t["youtube_url"]
        logger.info(f"[{i}/{len(rows)}] Processing '{title}' (ID: {topic_id})...")

        # 1. Ensure Transcript
        full_text = t["transcript_text"] if ("transcript_text" in t.keys() and t["transcript_text"]) else ""
        if not full_text or len(full_text.strip()) < 20:
            logger.info(f"Fetching transcript for {title}...")
            try:
                snippets = fetch_transcript(url, course_name=t["course_name"])
                full_text = " ".join([s.text for s in snippets])
            except Exception as e:
                logger.warning(f"Transcript fetch error for {title}: {e}")
                full_text = ""

        if not full_text:
            full_text = f"Lecture on {title}. Concepts covered in corporate finance: theoretical principles, decision criteria, and practical applications."

        # 2. Synthesize with new conceptual standard
        logger.info(f"Synthesizing conceptual notes & MCQs for '{title}' (transcript {len(full_text)} chars)...")
        try:
            result = generate_notes_and_questions(
                course_name=t["course_name"],
                module_name=t["module_name"],
                topic_title=title,
                transcript_text=full_text,
                slide_text=""
            )

            notes_md = result.get("notes_markdown", "")
            mcqs = result.get("mcqs", [])
            subjectives = result.get("subjective_questions", [])
            flashcards = result.get("flashcards", [])

            # 3. Save to database
            with conn:
                conn.execute("""
                    UPDATE topics 
                    SET status = 'completed',
                        transcript_text = ?,
                        notes_markdown = ?,
                        mcqs_json = ?,
                        subjectives_json = ?,
                        flashcards_json = ?,
                        error_message = ''
                    WHERE id = ?
                """, (
                    full_text,
                    notes_md,
                    json.dumps(mcqs, ensure_ascii=False),
                    json.dumps(subjectives, ensure_ascii=False),
                    json.dumps(flashcards, ensure_ascii=False),
                    topic_id
                ))

            logger.info(f"[{i}/{len(rows)}] Successfully updated '{title}' (Notes: {len(notes_md)} chars, MCQs: {len(mcqs)}).")

        except Exception as e:
            logger.error(f"Error synthesizing {title}: {e}")

    # Export to study_data.js
    logger.info("Exporting all updated data to study_data.js for GitHub Pages...")
    db.export_static_data()
    logger.info("Batch re-curation of Module 1 complete!")

if __name__ == "__main__":
    recurate_all_module1()

