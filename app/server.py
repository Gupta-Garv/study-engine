"""
FastAPI Server for StudyEngine.
Provides REST endpoints for course management, batch YouTube URL ingestion,
and on-the-spot AI lecture curation.
"""

import os
import re
import uuid
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger("study_engine.server")
logging.basicConfig(level=logging.INFO)
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from core import db
from core.transcript import (
    fetch_transcript, 
    fetch_video_title, 
    extract_video_id, 
    extract_playlist_videos, 
    format_timestamp
)
from core.llm_client import generate_notes_and_questions, get_api_key
from core.copilot import answer_lecture_doubt
from core.slide_capture import capture_slides, capture_slides_and_ocr

BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
SLIDES_DIR = STATIC_DIR / "slides"
SLIDES_DIR.mkdir(parents=True, exist_ok=True)

db.init_db()

app = FastAPI(title="StudyEngine API")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# -------------------------------------------------------------
# Request Models
# -------------------------------------------------------------
class CreateCourseRequest(BaseModel):
    name: str
    code: Optional[str] = ""
    description: Optional[str] = ""
    module_count: int = 8

class IngestVideosRequest(BaseModel):
    urls_text: str
    extract_slides: bool = False

class SettingsRequest(BaseModel):
    nvidia_api_key: str

class ChatMessageRequest(BaseModel):
    message: str

# -------------------------------------------------------------
# Background Curation Task & Queue Worker (2 Concurrent Workers)
# -------------------------------------------------------------
is_worker_running = False

async def worker_loop(worker_id: int):
    while True:
        t_id = None
        try:
            conn = db.get_conn()
            with conn:
                row = conn.execute(
                    "SELECT id FROM topics WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1"
                ).fetchone()
                if row:
                    t_id = row["id"]
                    conn.execute("UPDATE topics SET status = 'processing', error_message = '' WHERE id = ?", (t_id,))
            
            if t_id:
                logger.info(f"[Worker {worker_id}] Starting topic {t_id}...")
                await asyncio.to_thread(process_topic_task, t_id, False)
                logger.info(f"[Worker {worker_id}] Finished topic {t_id}.")
                await asyncio.sleep(1)  # Thermal breathing room
            else:
                await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"[Worker {worker_id}] Error in curation queue: {e}")
            await asyncio.sleep(2)

async def queue_worker():
    global is_worker_running
    if is_worker_running:
        return
    is_worker_running = True
    logger.info("Launching dual-worker parallel curation queue (2 concurrent workers)...")
    await asyncio.gather(
        worker_loop(1),
        worker_loop(2)
    )

@app.on_event("startup")
async def on_startup():
    # Reset any previously stuck 'processing' or 'error' topics back to 'pending'
    conn = db.get_conn()
    with conn:
        conn.execute("UPDATE topics SET status = 'pending' WHERE status IN ('processing', 'error')")
    # Launch persistent queue worker
    asyncio.create_task(queue_worker())

def process_topic_task(topic_id: str, extract_slides_flag: bool = False):
    conn = db.get_conn()
    topic = conn.execute(
        "SELECT t.*, m.name as module_name, c.name as course_name FROM topics t JOIN modules m ON t.module_id = m.id JOIN courses c ON m.course_id = c.id WHERE t.id = ?",
        (topic_id,)
    ).fetchone()

    if not topic:
        return

    conn.execute("UPDATE topics SET status = 'processing', error_message = '' WHERE id = ?", (topic_id,))
    conn.commit()

    try:
        # Step 1: Ensure real lecture title (e.g., 'CF M01 C12 Shareholder Wealth Maximisation')
        current_title = topic["title"]
        if current_title.startswith("Lecture ") and len(current_title) <= 22:
            real_title = fetch_video_title(topic["youtube_url"])
            if real_title and real_title != current_title:
                current_title = real_title
                conn.execute("UPDATE topics SET title = ? WHERE id = ?", (real_title, topic_id))
                conn.commit()

        # Step 2: Multi-tier Transcript Extraction (or use cached transcript)
        cached_transcript = topic["transcript_text"] if "transcript_text" in topic.keys() else ""
        if cached_transcript and cached_transcript.strip():
            logger.info(f"Using cached transcript for {topic_id} ({len(cached_transcript)} chars)...")
            full_text = cached_transcript
            duration = topic["duration_seconds"] or 0
        else:
            snippets = fetch_transcript(topic["youtube_url"], course_name=topic["course_name"])
            full_text = " ".join([s.text for s in snippets])
            duration = snippets[-1].end if snippets else 0

        # Step 3: Fast slides/whiteboard capture & local Tesseract OCR (skipped if false)
        slides_data = []
        slide_ocr_text = ""
        if extract_slides_flag:
            target_slide_dir = str(SLIDES_DIR / topic["video_id"])
            slide_result = capture_slides_and_ocr(topic["youtube_url"], target_slide_dir, topic["video_id"])
            slides_data = slide_result.get("slides", [])
            slide_ocr_text = slide_result.get("combined_text", "")

        # Step 4: Rigorous Academic Synthesis anchored to spoken words and slide content
        result = generate_notes_and_questions(
            course_name=topic["course_name"],
            module_name=topic["module_name"],
            topic_title=current_title,
            transcript_text=full_text,
            slide_text=slide_ocr_text
        )

        import json
        conn.execute("""
            UPDATE topics 
            SET status = 'completed',
                duration_seconds = ?,
                transcript_text = ?,
                notes_markdown = ?,
                mcqs_json = ?,
                subjectives_json = ?,
                flashcards_json = ?,
                slides_json = ?
            WHERE id = ?
        """, (
            duration,
            full_text,
            result.get("notes_markdown", ""),
            json.dumps(result.get("mcqs", []), ensure_ascii=False),
            json.dumps(result.get("subjective_questions", []), ensure_ascii=False),
            json.dumps(result.get("flashcards", []), ensure_ascii=False),
            json.dumps(slides_data, ensure_ascii=False),
            topic_id
        ))
        conn.commit()
        db.export_static_data()
    except Exception as e:
        conn.execute("UPDATE topics SET status = 'error', error_message = ? WHERE id = ?", (str(e), topic_id))
        conn.commit()

# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------
@app.get("/")
def serve_index():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/study_data.js")
def serve_study_data():
    return FileResponse(BASE_DIR / "study_data.js")

@app.get("/api/search")
def search_vault(q: str = Query(..., min_length=1), limit: int = 50):
    conn = db.get_conn()
    query = q.strip().lower()
    if not query:
        return []

    rows = conn.execute("""
        SELECT t.id, t.title, t.notes_markdown,
               m.id as module_id, m.name as module_name, m.number as module_number,
               c.id as course_id, c.name as course_name
        FROM topics t
        JOIN modules m ON t.module_id = m.id
        JOIN courses c ON m.course_id = c.id
        WHERE t.status = 'completed' AND (lower(t.title) LIKE ? OR lower(t.notes_markdown) LIKE ? OR lower(t.transcript_text) LIKE ?)
    """, (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()

    results = []
    for r in rows:
        title = r["title"]
        notes = r["notes_markdown"] or ""
        title_lower = title.lower()
        notes_lower = notes.lower()

        occurrences = notes_lower.count(query)
        if query in title_lower:
            occurrences += 1

        # 1. Title match if query is in title
        if query in title_lower:
            results.append({
                "topic_id": r["id"],
                "title": title,
                "module_id": r["module_id"],
                "module_name": r["module_name"],
                "module_number": r["module_number"],
                "course_id": r["course_id"],
                "course_name": r["course_name"],
                "heading": "Lecture Title",
                "snippet": title,
                "match_count": occurrences,
                "score": 300 if query == title_lower else 200
            })

        # 2. Section matches
        sections = re.split(r'\n(?=#{1,4}\s+)', notes)
        sec_idx = 0
        for sec in sections:
            sec_lower = sec.lower()
            if query in sec_lower:
                hdg_match = re.match(r'^#{1,4}\s+([^\n]+)', sec)
                heading = hdg_match.group(1).strip() if hdg_match else "Overview"
                # Avoid duplicate if heading is identical to title match
                if heading.lower() == title_lower and query in title_lower:
                    continue

                pos = sec_lower.find(query)
                start = max(0, pos - 45)
                end = min(len(sec), pos + len(query) + 55)
                snip = sec[start:end].replace('\n', ' ').strip()
                if start > 0:
                    snip = '...' + snip
                if end < len(sec):
                    snip = snip + '...'

                results.append({
                    "topic_id": r["id"],
                    "title": title,
                    "module_id": r["module_id"],
                    "module_name": r["module_name"],
                    "module_number": r["module_number"],
                    "course_id": r["course_id"],
                    "course_name": r["course_name"],
                    "heading": heading,
                    "snippet": snip,
                    "match_count": occurrences,
                    "score": 100 - min(sec_idx, 30)
                })
                sec_idx += 1

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]

@app.get("/api/courses")
def list_courses():
    return db.get_all_courses()

@app.post("/api/courses")
def create_course(req: CreateCourseRequest):
    conn = db.get_conn()
    course_id = str(uuid.uuid4())[:8]
    course_code = (req.code or "").strip().upper()
    with conn:
        conn.execute(
            "INSERT INTO courses (id, code, name, description, module_count) VALUES (?, ?, ?, ?, ?)",
            (course_id, course_code, req.name.strip(), (req.description or "").strip(), req.module_count)
        )
        for i in range(1, req.module_count + 1):
            mod_id = f"{course_id}-m{i}"
            conn.execute(
                "INSERT INTO modules (id, course_id, number, name) VALUES (?, ?, ?, ?)",
                (mod_id, course_id, i, f"Module {i}")
            )
    return {"id": course_id, "message": "Course created successfully with modules."}

@app.delete("/api/courses/{course_id}")
def delete_course(course_id: str):
    conn = db.get_conn()
    with conn:
        conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    return {"message": "Course deleted"}

@app.post("/api/modules/{module_id}/ingest")
def ingest_videos(module_id: str, req: IngestVideosRequest):
    conn = db.get_conn()
    mod = conn.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    if not mod:
        raise HTTPException(404, "Module not found")

    lines = [line.strip() for line in req.urls_text.splitlines() if line.strip()]
    added_topics = []

    for line in lines:
        if "playlist?list=" in line or "&list=" in line:
            videos = extract_playlist_videos(line)
            for v in videos:
                t_id = str(uuid.uuid4())[:8]
                with conn:
                    conn.execute(
                        "INSERT INTO topics (id, module_id, title, youtube_url, video_id, status) VALUES (?, ?, ?, ?, ?, 'pending')",
                        (t_id, module_id, v["title"], v["url"], v["id"])
                    )
                added_topics.append(t_id)
        else:
            try:
                v_id = extract_video_id(line)
                t_id = str(uuid.uuid4())[:8]
                title = fetch_video_title(line)
                with conn:
                    conn.execute(
                        "INSERT INTO topics (id, module_id, title, youtube_url, video_id, status) VALUES (?, ?, ?, ?, ?, 'pending')",
                        (t_id, module_id, title, line, v_id)
                    )
                added_topics.append(t_id)
            except Exception:
                continue

    return {"added_count": len(added_topics), "topic_ids": added_topics}

@app.post("/api/topics/{topic_id}/retry")
def retry_topic(topic_id: str):
    conn = db.get_conn()
    with conn:
        conn.execute("UPDATE topics SET status = 'pending', error_message = '' WHERE id = ?", (topic_id,))
    return {"message": "Curation queued for processing."}

@app.post("/api/modules/{module_id}/recurate")
def recurate_module(module_id: str):
    conn = db.get_conn()
    with conn:
        conn.execute("UPDATE topics SET status = 'pending', error_message = '' WHERE module_id = ?", (module_id,))
    return {"message": "All lectures in module queued for re-curation."}

@app.get("/api/topics/{topic_id}")
def get_topic(topic_id: str):
    t = db.get_topic_detail(topic_id)
    if not t:
        raise HTTPException(404, "Topic not found")
    return t

@app.get("/api/modules/{module_id}/exam")
def get_module_exam(module_id: str):
    return db.get_module_quiz(module_id)

@app.get("/api/settings")
def get_settings():
    return {
        "has_api_key": bool(get_api_key()),
        "recommended_model": "mistralai/mistral-large-4-1t-a52b",
        "vision_model": "meta/llama-3.2-90b-vision-instruct"
    }

@app.post("/api/settings")
def save_settings(req: SettingsRequest):
    db.set_setting("nvidia_api_key", req.nvidia_api_key.strip())
    return {"message": "NVIDIA NIM API key saved successfully."}

class CanvasDataRequest(BaseModel):
    cards: List[dict] = []
    connections: List[dict] = []

@app.get("/api/topics/{topic_id}/canvas")
def get_topic_canvas_endpoint(topic_id: str):
    return db.get_topic_canvas(topic_id)

@app.post("/api/topics/{topic_id}/canvas")
def save_topic_canvas_endpoint(topic_id: str, req: CanvasDataRequest):
    data = {"cards": req.cards, "connections": req.connections}
    saved = db.save_topic_canvas(topic_id, data)
    db.export_static_data()
    return saved

@app.get("/api/topics/{topic_id}/chat")
def get_topic_chat_history(topic_id: str):
    return db.get_topic_chat(topic_id)

@app.post("/api/topics/{topic_id}/chat")
def post_topic_chat_message(topic_id: str, req: ChatMessageRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(400, "Message cannot be empty")
    reply = answer_lecture_doubt(topic_id, req.message.strip())
    db.export_static_data()
    return {"reply": reply}

