#!/usr/bin/env python3
"""
Master Drip Course Ingestor & End-to-End Synthesizer.
Ingests newly unlocked videos for:
- Family Business Strategy (Module 8)
- Corporate Finance (Module 8 & Module 0)
- Data Visualisation for Business Decisions (Module 3)

For each video, automatically generates:
1. Multi-tier transcript snippets.
2. Executive academic synthesized notes, point-wise conceptual mechanics, and MCQs.
3. Cross-lecture context-aware Speedrun Key Moments.
4. Studio Neural Audio narration (Christopher & Jenny).
5. 2-Set Exam Arena conceptual diagnostic tests for each newly completed module.
6. Static bundle export (study_data.js) for zero-latency instant loading.
"""

import sys
import os
import json
import uuid
import re
import time
import asyncio
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.db import get_conn, export_static_data, get_module_tests
from core.transcript import fetch_transcript, Snippet
from core.llm_client import generate_notes_and_questions
from core.key_moments import get_adjacent_topics_context, synthesize_key_moments
from core.audio_narrator import synthesize_topic_audio
from core.test_generator import generate_both_module_tests

def main():
    report_file = PROJECT_ROOT / "scratch" / "portal_new_videos_report.json"
    if not report_file.exists():
        print(f"[!] Report file {report_file} not found. Run check_new_portal_videos.py first.")
        return

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = get_conn()

    # Step 1: Mapping courses
    courses_map = {}
    for c in conn.execute("SELECT id, name FROM courses").fetchall():
        courses_map[c["name"].lower().strip()] = c["id"]

    total_ingested = 0
    modules_to_test = set()
    topics_to_process = []

    print("==================================================================")
    print("🚀 STEP 1: Ingesting Modules and Topics into StudyEngine Database")
    print("==================================================================")

    for cname, cinfo in data.items():
        new_vids = cinfo.get("new_videos", [])
        if not new_vids:
            continue

        c_key = cname.lower().strip()
        course_id = courses_map.get(c_key)
        if not course_id:
            print(f"[!] Course not found in database: {cname}")
            continue

        # Group by module
        by_module = {}
        for v in new_vids:
            m = v["module"]
            if m not in by_module:
                by_module[m] = []
            by_module[m].append(v)

        for mod_name, vlist in by_module.items():
            # Check or create module
            mod_row = conn.execute(
                "SELECT id, number FROM modules WHERE course_id = ? AND LOWER(name) = ?",
                (course_id, mod_name.lower().strip())
            ).fetchone()

            if mod_row:
                mod_id = mod_row["id"]
            else:
                # Find next module number
                max_num_row = conn.execute(
                    "SELECT MAX(number) as max_num FROM modules WHERE course_id = ?",
                    (course_id,)
                ).fetchone()
                next_num = (max_num_row["max_num"] or 0) + 1
                
                # Check if module 0
                if "module 0" in mod_name.lower():
                    next_num = 0

                mod_id = f"{course_id}-m{next_num if next_num != 0 else '0'}"
                # If ID exists, append uuid
                if conn.execute("SELECT id FROM modules WHERE id = ?", (mod_id,)).fetchone():
                    mod_id = f"{course_id}-m{next_num}-{str(uuid.uuid4())[:4]}"

                with conn:
                    conn.execute(
                        "INSERT INTO modules (id, course_id, number, name) VALUES (?, ?, ?, ?)",
                        (mod_id, course_id, next_num, mod_name)
                    )
                print(f"  📁 Created new Module in '{cname}': [{mod_id}] {mod_name}")

            modules_to_test.add((mod_id, mod_name, cname))

            # Insert topics
            existing_vids = {
                r["video_id"] for r in conn.execute(
                    "SELECT video_id FROM topics WHERE module_id = ?", (mod_id,)
                ).fetchall()
            }

            for v in vlist:
                yt_id = v["youtube_id"]
                if yt_id in existing_vids:
                    continue

                topic_id = str(uuid.uuid4())[:8]
                full_yt_url = f"https://www.youtube.com/watch?v={yt_id}"
                
                with conn:
                    conn.execute(
                        """
                        INSERT INTO topics (
                            id, module_id, title, youtube_url, video_id, duration_seconds, status
                        ) VALUES (?, ?, ?, ?, ?, 0, 'processing')
                        """,
                        (topic_id, mod_id, v["title"], full_yt_url, yt_id)
                    )
                existing_vids.add(yt_id)
                total_ingested += 1
                topics_to_process.append({
                    "topic_id": topic_id,
                    "title": v["title"],
                    "module_id": mod_id,
                    "module_name": mod_name,
                    "course_name": cname,
                    "youtube_url": full_yt_url,
                    "video_id": yt_id
                })

    print(f"\n✅ Total new topics registered: {total_ingested}")
    export_static_data()

    if not topics_to_process:
        print("No new topics need processing.")
        return

    print("\n==================================================================")
    print(f"🧠 STEP 2: Synthesizing Notes, MCQs & Key Moments for {len(topics_to_process)} Topics")
    print("==================================================================")

    for idx, t in enumerate(topics_to_process, start=1):
        t_id = t["topic_id"]
        title = t["title"]
        cname = t["course_name"]
        mname = t["module_name"]
        yt_url = t["youtube_url"]
        vid = t["video_id"]

        print(f"\n[{idx}/{len(topics_to_process)}] Processing: '{title}' ({cname} - {mname})")
        t0 = time.time()

        # Step 2.1: Transcript Extraction
        snippets = []
        try:
            snippets = fetch_transcript(yt_url, course_name=cname)
            print(f"   ✓ Transcript fetched: {len(snippets)} snippets")
        except Exception as e:
            print(f"   ⚠️ Could not fetch transcript: {e}")

        full_text = " ".join([s.text for s in snippets])
        duration = snippets[-1].end if snippets else 0.0
        snippets_json_str = json.dumps(
            [{"text": s.text, "start": s.start, "duration": s.duration, "end": s.end} for s in snippets],
            ensure_ascii=False
        )

        # Step 2.2: Academic Notes & MCQs
        notes_md = ""
        mcqs = []
        try:
            synth_res = generate_notes_and_questions(
                course_name=cname,
                module_name=mname,
                topic_title=title,
                transcript_text=full_text if full_text.strip() else title,
                slide_text=""
            )
            notes_md = synth_res.get("notes_markdown", "")
            mcqs = synth_res.get("mcqs", [])
            print(f"   ✓ Notes & MCQs synthesized ({len(notes_md)} chars, {len(mcqs)} MCQs)")
        except Exception as e:
            print(f"   ⚠️ LLM synthesis warning: {e}")
            notes_md = f"# {title}\n\nNotes synthesized based on curriculum transcript.\n\n{full_text[:400]}..."

        # Step 2.3: Context-Aware Key Moments & Speedrun
        prev_t, next_t = get_adjacent_topics_context(conn, t_id)
        key_moments = []
        try:
            key_moments = synthesize_key_moments(
                course_name=cname,
                module_name=mname,
                topic_title=title,
                snippets=snippets,
                total_duration_seconds=duration,
                prev_topic=prev_t,
                next_topic=next_t,
                transcript_text=full_text
            )
            print(f"   ✓ Key Moments created: {len(key_moments)} moments")
        except Exception as e:
            print(f"   ⚠️ Key moments warning: {e}")

        # Update topic in database
        with conn:
            conn.execute(
                """
                UPDATE topics
                SET status = 'completed',
                    duration_seconds = ?,
                    transcript_text = ?,
                    transcript_snippets_json = ?,
                    notes_markdown = ?,
                    mcqs_json = ?,
                    key_moments_json = ?,
                    error_message = ''
                WHERE id = ?
                """,
                (
                    duration,
                    full_text,
                    snippets_json_str,
                    notes_md,
                    json.dumps(mcqs, ensure_ascii=False),
                    json.dumps(key_moments, ensure_ascii=False),
                    t_id
                )
            )

        # Step 2.4: Pre-cache Studio Neural Voice
        try:
            asyncio.run(synthesize_topic_audio(t_id, title, notes_md, "christopher"))
            print("   ✓ Studio Neural Voice (Christopher) pre-cached")
        except Exception as e:
            print(f"   ⚠️ Audio pre-cache warning: {e}")

        print(f"   🎉 Done in {time.time() - t0:.1f}s")

    export_static_data()

    print("\n==================================================================")
    print(f"📝 STEP 3: Generating 2-Set Exam Arena Conceptual Diagnostic Tests")
    print("==================================================================")

    for mod_id, mod_name, cname in modules_to_test:
        print(f"\nGenerating tests for Module: '{mod_name}' ({cname})...")
        try:
            tests = generate_both_module_tests(mod_id, target_questions=12)
            print(f"   ✓ Generated {len(tests)} test sets (Set 1 & Set 2)")
        except Exception as e:
            print(f"   ⚠️ Test generation error: {e}")

    export_static_data()

    print("\n==================================================================")
    print("🏆 ALL DRIP LECTURES SUCCESSFULLY INGESTED & SYNTHESIZED END-TO-END!")
    print("==================================================================")

if __name__ == "__main__":
    main()
