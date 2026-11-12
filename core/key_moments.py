"""
Smart Academic Key Moments & Speedrun Synthesizer.
Extracts high-yield lecture segments and cuts fluff using cross-lecture syllabus context.
Anchors directly to second-by-second timestamps to power interactive timeline pills
and automated fluff-skipping Speedrun playback.
"""

from __future__ import annotations

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import json_repair

from .transcript import Snippet
from .llm_client import call_llm

logger = logging.getLogger("study_engine.key_moments")


def get_adjacent_topics_context(conn, topic_id: str) -> Tuple[Optional[Dict[str, str]], Optional[Dict[str, str]]]:
    """
    Retrieves the previous and next topic in the course sequence, along with their core conceptual summary,
    so the synthesizer knows what was ALREADY taught (to filter out recaps) and what will be taught NEXT (to filter teasers).
    """
    try:
        # Get current topic's course and module order
        cur = conn.execute("""
            SELECT t.id, t.title, m.id as module_id, m.course_id, m.number as module_number
            FROM topics t
            JOIN modules m ON t.module_id = m.id
            WHERE t.id = ?
        """, (topic_id,)).fetchone()

        if not cur:
            return None, None

        course_id = cur["course_id"]

        # Fetch all topics in this course ordered by module number and topic title
        rows = conn.execute("""
            SELECT t.id, t.title, t.notes_markdown, m.name as module_name, m.number as module_number
            FROM topics t
            JOIN modules m ON t.module_id = m.id
            WHERE m.course_id = ?
            ORDER BY m.number ASC, t.title ASC
        """, (course_id,)).fetchall()

        all_topics = [dict(r) for r in rows]
        curr_idx = next((i for i, item in enumerate(all_topics) if item["id"] == topic_id), -1)

        if curr_idx == -1:
            return None, None

        prev_topic = None
        if curr_idx > 0:
            p = all_topics[curr_idx - 1]
            prev_topic = {
                "title": p["title"],
                "summary": (p.get("notes_markdown") or "")[:400].strip()
            }

        next_topic = None
        if curr_idx < len(all_topics) - 1:
            n = all_topics[curr_idx + 1]
            next_topic = {
                "title": n["title"],
                "summary": (n.get("notes_markdown") or "")[:400].strip()
            }

        return prev_topic, next_topic
    except Exception as e:
        logger.warning(f"Failed to fetch adjacent topics context for {topic_id}: {e}")
        return None, None


def format_snippets_into_timestamp_blocks(snippets: List[Snippet], max_block_duration: float = 18.0) -> str:
    """
    Groups granular transcript snippets into readable 15-20 second windows with clean timestamps (mm:ss - mm:ss).
    Keeps token budget compact while preserving exact temporal granularity.
    """
    if not snippets:
        return ""

    blocks = []
    curr_text = []
    block_start = snippets[0].start

    for s in snippets:
        text = s.text.strip()
        if not text or text.lower() == "[music]":
            continue
        curr_text.append(text)
        if s.end - block_start >= max_block_duration:
            start_m, start_s = int(block_start // 60), int(block_start % 60)
            end_m, end_s = int(s.end // 60), int(s.end % 60)
            blocks.append(f"[{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}] " + " ".join(curr_text))
            block_start = s.end
            curr_text = []

    if curr_text:
        last_end = snippets[-1].end
        start_m, start_s = int(block_start // 60), int(block_start % 60)
        end_m, end_s = int(last_end // 60), int(last_end % 60)
        blocks.append(f"[{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}] " + " ".join(curr_text))

    return "\n".join(blocks)


def synthesize_key_moments(
    course_name: str,
    module_name: str,
    topic_title: str,
    snippets: List[Snippet],
    total_duration_seconds: float = 0,
    prev_topic: Optional[Dict[str, str]] = None,
    next_topic: Optional[Dict[str, str]] = None,
    transcript_text: str = ""
) -> Dict[str, Any]:
    """
    Synthesizes academic, high-yield smart chapters and fluff-free speedrun segments
    using cross-lecture syllabus context.
    """
    timestamp_blocks = ""
    if snippets:
        if total_duration_seconds <= 0:
            total_duration_seconds = snippets[-1].end
        timestamp_blocks = format_snippets_into_timestamp_blocks(snippets)

    if not timestamp_blocks.strip() and transcript_text.strip():
        words = transcript_text.split()
        total_words = len(words)
        dur = total_duration_seconds if total_duration_seconds > 0 else max(total_words * 0.35, 120.0)
        total_duration_seconds = dur
        sec_per_word = dur / max(total_words, 1)
        block_size = 40
        blocks = []
        for i in range(0, total_words, block_size):
            chunk = words[i:i+block_size]
            s_sec = i * sec_per_word
            e_sec = min((i + len(chunk)) * sec_per_word, dur)
            sm, ss = int(s_sec // 60), int(s_sec % 60)
            em, es = int(e_sec // 60), int(e_sec % 60)
            blocks.append(f"[{sm:02d}:{ss:02d} - {em:02d}:{es:02d}] " + " ".join(chunk))
        timestamp_blocks = "\n".join(blocks)

    if not timestamp_blocks.strip():
        return _generate_fallback_key_moments(topic_title, total_duration_seconds)

    system_prompt = (
        "You are an expert academic curriculum analyst and lecture video optimizer.\n"
        "Your mission is to eliminate academic fluff, introductory banter, repetitive recaps of already-taught concepts, "
        "and forward teasers, leaving ONLY the high-yield, high-density conceptual breakthroughs that an undergraduate student MUST watch.\n\n"
        "CROSS-LECTURE SYLLABUS INTELLIGENCE RULES:\n"
        "1. PREVIOUS LECTURE RECAP FILTER: If the professor spends time recapping what was already taught in the previous lecture, mark that recap as FLUFF and EXCLUDE it.\n"
        "2. NEXT LECTURE TEASER FILTER: If the professor spends time teasing, promoting, or foreshadowing the next lecture, mark that as FLUFF and EXCLUDE it.\n"
        "3. HIGH-YIELD ESSENCE: Extract ONLY the 2 to 4 essential moments where NEW conceptual frameworks, mathematical definitions, counter-intuitive arguments, or practical decision models are taught.\n"
        "4. SAFE SPEECH BUFFERS: Always add 2 to 3 seconds of lead-in and lead-out padding to start_seconds and end_seconds so sentences and thoughts are never cut mid-breath.\n"
        "5. COMPRESSION RATIO: The total high-yield duration must be roughly 30% to 45% of the total lecture runtime (saving 55% to 70% of time).\n"
        "6. NO EM DASHES: Absolutely never use em dashes (—) anywhere in titles or text.\n\n"
        "OUTPUT FORMAT: Return STRICTLY valid JSON with no conversational text or markdown code fences outside the JSON object:\n"
        "{\n"
        "  \"total_video_duration_seconds\": <number>,\n"
        "  \"high_yield_duration_seconds\": <number>,\n"
        "  \"fluff_saved_percentage\": <number 50-75>,\n"
        "  \"key_moments\": [\n"
        "    {\n"
        "      \"start_seconds\": <float>,\n"
        "      \"end_seconds\": <float>,\n"
        "      \"timestamp_display\": \"<mm:ss - mm:ss>\",\n"
        "      \"title\": \"<Sharp 4-8 word concept title>\",\n"
        "      \"yield_score\": <integer 1-10>,\n"
        "      \"why_essential\": \"<1 concise sentence explaining the conceptual breakthrough>\",\n"
        "      \"key_takeaway\": \"<1 concise takeaway sentence>\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )

    prev_context_block = ""
    if prev_topic and prev_topic.get("title"):
        prev_context_block = f"\nPREVIOUS LECTURE IN SEQUENCE (Already known to student - exclude recaps of this):\nTitle: {prev_topic['title']}\nSummary: {prev_topic.get('summary', '')[:250]}\n"

    next_context_block = ""
    if next_topic and next_topic.get("title"):
        next_context_block = f"\nNEXT LECTURE IN SEQUENCE (Will be taught next - exclude teasers of this):\nTitle: {next_topic['title']}\nSummary: {next_topic.get('summary', '')[:250]}\n"

    user_prompt = f"""COURSE: {course_name}
MODULE: {module_name}
CURRENT LECTURE: {topic_title}
TOTAL DURATION: {int(total_duration_seconds // 60)}m {int(total_duration_seconds % 60)}s ({int(total_duration_seconds)} seconds)
{prev_context_block}{next_context_block}
SECOND-BY-SECOND TRANSCRIPT BLOCKS:
\"\"\"
{timestamp_blocks[:14000]}
\"\"\"

Carefully evaluate the spoken words. Filter out recaps of prior lessons, intros, banter, and forward promos.
Output the structured JSON of high-yield moments:"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        raw_res = call_llm(messages, temperature=0.1, max_tokens=1500)
        parsed = json_repair.loads(raw_res)

        if isinstance(parsed, dict) and "key_moments" in parsed and isinstance(parsed["key_moments"], list):
            valid_moments = []
            total_hy = 0.0

            for m in parsed["key_moments"]:
                start = float(m.get("start_seconds", 0))
                end = float(m.get("end_seconds", 0))

                # Bounds check
                start = max(0.0, min(start, total_duration_seconds))
                end = max(start + 5.0, min(end, total_duration_seconds))
                dur = end - start
                total_hy += dur

                start_m, start_s = int(start // 60), int(start % 60)
                end_m, end_s = int(end // 60), int(end % 60)

                valid_moments.append({
                    "start_seconds": round(start, 1),
                    "end_seconds": round(end, 1),
                    "timestamp_display": f"{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}",
                    "title": str(m.get("title", "Core Concept")).replace("—", "-").strip(),
                    "yield_score": int(m.get("yield_score", 9)),
                    "why_essential": str(m.get("why_essential", "")).replace("—", "-").strip(),
                    "key_takeaway": str(m.get("key_takeaway", "")).replace("—", "-").strip()
                })

            if valid_moments:
                saved_pct = round((1.0 - (total_hy / max(total_duration_seconds, 1.0))) * 100)
                saved_pct = max(30, min(80, saved_pct))
                return {
                    "total_video_duration_seconds": round(total_duration_seconds, 1),
                    "high_yield_duration_seconds": round(total_hy, 1),
                    "fluff_saved_percentage": saved_pct,
                    "key_moments": valid_moments
                }

    except Exception as e:
        logger.error(f"Failed to synthesize key moments for '{topic_title}': {e}")

    return _generate_fallback_key_moments(topic_title, total_duration_seconds)


def _generate_fallback_key_moments(topic_title: str, total_duration: float) -> Dict[str, Any]:
    """Generates clean structured key moments if transcription is unavailable."""
    dur = max(total_duration, 120.0)
    s1 = round(dur * 0.15, 1)
    e1 = round(dur * 0.45, 1)
    s2 = round(dur * 0.55, 1)
    e2 = round(dur * 0.85, 1)

    m1_s, m1_e = f"{int(s1//60):02d}:{int(s1%60):02d}", f"{int(e1//60):02d}:{int(e1%60):02d}"
    m2_s, m2_e = f"{int(s2//60):02d}:{int(s2%60):02d}", f"{int(e2//60):02d}:{int(e2%60):02d}"

    return {
        "total_video_duration_seconds": round(dur, 1),
        "high_yield_duration_seconds": round((e1 - s1) + (e2 - s2), 1),
        "fluff_saved_percentage": 40,
        "key_moments": [
            {
                "start_seconds": s1,
                "end_seconds": e1,
                "timestamp_display": f"{m1_s} - {m1_e}",
                "title": f"{topic_title}: Foundational Principles",
                "yield_score": 9,
                "why_essential": "Core conceptual definitions and theoretical mechanics.",
                "key_takeaway": "Essential framework required for exam mastery."
            },
            {
                "start_seconds": s2,
                "end_seconds": e2,
                "timestamp_display": f"{m2_s} - {m2_e}",
                "title": f"{topic_title}: Analytical Application & Nuance",
                "yield_score": 10,
                "why_essential": "Critical parameter sensitivity, trade-offs, and failure modes.",
                "key_takeaway": "Key application patterns tested in high-order assessments."
            }
        ]
    }

