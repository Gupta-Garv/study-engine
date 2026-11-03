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
        """)
        # Pre-seed integrated NVIDIA NIM Key
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES ('nvidia_api_key', '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')"
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
                
        out_path = Path(__file__).parent.parent / "study_data.js"
        bundle = {"courses": courses, "topics": topics, "exams": exams}
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("window.STUDY_DATA = " + json.dumps(bundle, ensure_ascii=False, indent=2) + ";\n")
    except Exception as e:
        print("Failed to export static data:", e)
