"""
SQLite Database Storage for StudyEngine.
Stores Courses, Modules, Topics, Synthesized Notes, MCQs, and Flashcards.
"""

import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).parent.parent / "data" / "study_vault.db"

def get_conn():
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS courses (
                id TEXT PRIMARY KEY,
                code TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                module_count INTEGER DEFAULT 8,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS modules (
                id TEXT PRIMARY KEY,
                course_id TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                number INTEGER NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS topics (
                id TEXT PRIMARY KEY,
                module_id TEXT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                youtube_url TEXT NOT NULL,
                video_id TEXT NOT NULL,
                duration_seconds REAL DEFAULT 0,
                status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'error'
                transcript_text TEXT DEFAULT '',
                notes_markdown TEXT DEFAULT '',
                mcqs_json TEXT DEFAULT '[]',
                subjectives_json TEXT DEFAULT '[]',
                flashcards_json TEXT DEFAULT '[]',
                slides_json TEXT DEFAULT '[]',
                error_message TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS topic_chats (
                id TEXT PRIMARY KEY,
                topic_id TEXT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS topic_canvases (
                topic_id TEXT PRIMARY KEY REFERENCES topics(id) ON DELETE CASCADE,
                canvas_json TEXT NOT NULL DEFAULT '{"cards":[],"connections":[]}',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Pre-seed integrated NVIDIA NIM Keys
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES ('nvidia_api_key', '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')"
        )
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES ('copilot_api_key', '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')"
        )

def get_all_courses() -> List[Dict[str, Any]]:
    conn = get_conn()
    courses = []
    c_rows = conn.execute("SELECT * FROM courses ORDER BY created_at ASC").fetchall()
    for c in c_rows:
        course = dict(c)
        m_rows = conn.execute("SELECT * FROM modules WHERE course_id = ? ORDER BY number ASC", (course["id"],)).fetchall()
        modules = []
        for m in m_rows:
            mod = dict(m)
            t_rows = conn.execute("SELECT id, module_id, title, youtube_url, video_id, duration_seconds, status FROM topics WHERE module_id = ? ORDER BY created_at ASC", (mod["id"],)).fetchall()
            mod["topics"] = [dict(t) for t in t_rows]
            modules.append(mod)
        course["modules"] = modules
        courses.append(course)
    return courses

def get_topic_detail(topic_id: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["mcqs"] = json.loads(d.get("mcqs_json") or "[]")
    d["subjective_questions"] = json.loads(d.get("subjectives_json") or "[]")
    d["flashcards"] = json.loads(d.get("flashcards_json") or "[]")
    d["slides"] = json.loads(d.get("slides_json") or "[]")
    return d

def get_module_quiz(module_id: str) -> Dict[str, Any]:
    conn = get_conn()
    t_rows = conn.execute("SELECT mcqs_json, subjectives_json, flashcards_json FROM topics WHERE module_id = ? AND status = 'completed'", (module_id,)).fetchall()
    all_mcqs = []
    all_subj = []
    all_flash = []
    for r in t_rows:
        all_mcqs.extend(json.loads(r["mcqs_json"] or "[]"))
        all_subj.extend(json.loads(r["subjectives_json"] or "[]"))
        all_flash.extend(json.loads(r["flashcards_json"] or "[]"))
    return {
        "mcqs": all_mcqs,
        "subjective_questions": all_subj,
        "flashcards": all_flash
    }

def get_setting(key: str, default: str = "") -> str:
    conn = get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default

def set_setting(key: str, value: str):
    conn = get_conn()
    with conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))

def get_topic_chat(topic_id: str) -> List[Dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, topic_id, role, content, created_at FROM topic_chats WHERE topic_id = ? ORDER BY created_at ASC",
        (topic_id,)
    ).fetchall()
    return [dict(r) for r in rows]

def save_chat_message(topic_id: str, role: str, content: str) -> Dict[str, Any]:
    import uuid
    msg_id = str(uuid.uuid4())[:12]
    conn = get_conn()
    with conn:
        conn.execute(
            "INSERT INTO topic_chats (id, topic_id, role, content) VALUES (?, ?, ?, ?)",
            (msg_id, topic_id, role, content)
        )
    return {"id": msg_id, "topic_id": topic_id, "role": role, "content": content}

def get_topic_canvas(topic_id: str) -> Dict[str, Any]:
    conn = get_conn()
    row = conn.execute("SELECT canvas_json FROM topic_canvases WHERE topic_id = ?", (topic_id,)).fetchone()
    if row and row["canvas_json"]:
        try:
            return json.loads(row["canvas_json"])
        except Exception:
            pass
    return {"cards": [], "connections": [], "drawings": [], "text_notes": []}

def save_topic_canvas(topic_id: str, canvas_data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_conn()
    canvas_str = json.dumps(canvas_data, ensure_ascii=False)
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO topic_canvases (topic_id, canvas_json, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (topic_id, canvas_str)
        )
    return canvas_data

def export_static_data():
    """Exports SQLite vault to static study_data.js for 24/7 GitHub Pages hosting."""
    try:
        courses = get_all_courses()
        conn = get_conn()
        topics = {}
        for row in conn.execute("SELECT * FROM topics").fetchall():
            d = dict(row)
            d["mcqs"] = json.loads(d.get("mcqs_json") or "[]")
            d["subjective_questions"] = json.loads(d.get("subjectives_json") or "[]")
            d["flashcards"] = json.loads(d.get("flashcards_json") or "[]")
            d["slides"] = json.loads(d.get("slides_json") or "[]")
            topics[d["id"]] = d
            
        exams = {}
        for c in courses:
            for m in c["modules"]:
                exams[m["id"]] = get_module_quiz(m["id"])

        chats = {}
        for row in conn.execute("SELECT id, topic_id, role, content, created_at FROM topic_chats ORDER BY created_at ASC").fetchall():
            tid = row["topic_id"]
            if tid not in chats:
                chats[tid] = []
            chats[tid].append(dict(row))

        canvases = {}
        for row in conn.execute("SELECT topic_id, canvas_json FROM topic_canvases").fetchall():
            try:
                canvases[row["topic_id"]] = json.loads(row["canvas_json"])
            except Exception:
                pass
                
        out_path = Path(__file__).parent.parent / "study_data.js"
        bundle = {
            "courses": courses, 
            "topics": topics, 
            "exams": exams, 
            "chats": chats,
            "canvases": canvases
        }
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("window.STUDY_DATA = " + json.dumps(bundle, ensure_ascii=False, indent=2) + ";\n")
    except Exception as e:
        print("Failed to export static data:", e)
