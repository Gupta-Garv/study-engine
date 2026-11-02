"""
FastAPI Server for StudyEngine.
Provides REST endpoints for course management, batch YouTube URL ingestion,
and on-the-spot AI lecture curation.
"""

import os
import uuid
import asyncio
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, BackgroundTasks
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
    extract_slides: bool = True

class SettingsRequest(BaseModel):
    nvidia_api_key: str

# -------------------------------------------------------------
# Background Curation Task & Queue Worker
# -------------------------------------------------------------
is_worker_running = False

async def queue_worker():
    global is_worker_running
    if is_worker_running:
        return
    is_worker_running = True

    while True:
        try:
            conn = db.get_conn()
            pending_topic = conn.execute(
                "SELECT id FROM topics WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1"
            ).fetchone()

            if pending_topic:
                t_id = pending_topic["id"]
                # Run process in threadpool to keep event loop responsive, with slide capture enabled
                await asyncio.to_thread(process_topic_task, t_id, True)
            else:
                await asyncio.sleep(2)
        except Exception as e:
            await asyncio.sleep(2)

@app.on_event("startup")
async def on_startup():
    # Reset any previously stuck 'processing' topics back to 'pending'
    conn = db.get_conn()
    with conn:
        conn.execute("UPDATE topics SET status = 'pending' WHERE status = 'processing'")
    # Launch persistent queue worker
    asyncio.create_task(queue_worker())

def process_topic_task(topic_id: str, extract_slides_flag: bool = True):
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

        # Step 2: Multi-tier Transcript Extraction (caption api -> yt-dlp -> faster-whisper fallback with domain lexicon)
        snippets = fetch_transcript(topic["youtube_url"], course_name=topic["course_name"])
        full_text = " ".join([s.text for s in snippets])
        duration = snippets[-1].end if snippets else 0

        # Step 3: Fast slides/whiteboard capture & local Tesseract OCR
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
                notes_markdown = ?,
                mcqs_json = ?,
                subjectives_json = ?,
                flashcards_json = ?,
                slides_json = ?
            WHERE id = ?
        """, (
            duration,
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

