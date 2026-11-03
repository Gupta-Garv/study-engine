"""
In-Context AI Lecture Copilot for Study Hall.
Powered by user's dedicated key and model: z-ai/glm-5.3-flash with fast fallback to nemotron-lightning.
Answers student doubts strictly grounded in the currently active video transcript and notes.
"""

from __future__ import annotations

import os
import time
import logging
from typing import List, Dict, Any
from openai import OpenAI
from core.db import get_conn, get_topic_chat, save_chat_message, get_setting

logger = logging.getLogger("study_engine.copilot")

COPILOT_API_KEY = os.getenv("COPILOT_API_KEY") or get_setting("copilot_api_key") or "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"
PRIMARY_COPILOT_MODEL = "z-ai/glm-5.3-flash"
FAST_FALLBACK_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"

def get_copilot_client(timeout: float = 20.0) -> OpenAI:
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=COPILOT_API_KEY, timeout=timeout)

def answer_lecture_doubt(topic_id: str, user_question: str) -> str:
    """Answers a student question in the context of the active video lecture."""
    conn = get_conn()
    topic = conn.execute(
        "SELECT t.*, m.name as module_name, c.name as course_name FROM topics t JOIN modules m ON t.module_id = m.id JOIN courses c ON m.course_id = c.id WHERE t.id = ?",
        (topic_id,)
    ).fetchone()

    if not topic:
        return "Sorry, could not find the context for this lecture."

    topic = dict(topic)
    transcript = topic.get("transcript_text", "")
    notes = topic.get("notes_markdown", "")

    # Retrieve existing chat history for this topic
    history_rows = get_topic_chat(topic_id)
    chat_history = []
    for h in history_rows[-8:]:  # Keep recent context window
        chat_history.append({"role": h["role"], "content": h["content"]})

    # Save user message to DB
    save_chat_message(topic_id, "user", user_question)

    system_prompt = (
        f"You are the dedicated personal university study tutor for the course '{topic.get('course_name')}' ({topic.get('module_name')}).\n"
        f"The student is currently watching and reading notes for the lecture: '{topic.get('title')}'.\n\n"
        f"=== LECTURE SPOKEN TRANSCRIPT (GROUND TRUTH) ===\n"
        f"{transcript[:10000] if transcript else 'No spoken transcript available.'}\n\n"
        f"=== LECTURE REVISION NOTES ===\n"
        f"{notes[:8000] if notes else 'No notes available yet.'}\n\n"
        "MANDATES FOR YOUR RESPONSES:\n"
        "1. GROUND TRUTH: Base your explanation primarily on what the professor taught in this specific lecture.\n"
        "2. CLARITY & BREVITY: Give direct, crystal-clear explanations. Do not write unnecessary generic fluff. Use bullet points and bold terms.\n"
        "3. FORMULAS & MATH: If explaining a calculation, use KaTeX LaTeX notation ($...$ inline or $$...$$ block) and clearly explain every variable.\n"
        "4. EXAM TIPS: Highlight tricky distinctions or traps students frequently make on exams if relevant to their doubt."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_question})

    client = get_copilot_client(timeout=18.0)

    # Attempt 1: Try GLM 5.3 Flash as requested
    try:
        logger.info(f"Calling copilot model {PRIMARY_COPILOT_MODEL} for topic {topic_id}...")
        resp = client.chat.completions.create(
            model=PRIMARY_COPILOT_MODEL,
            messages=messages,
            temperature=0.5,
            top_p=1.0,
            max_tokens=1024
        )
        reply = resp.choices[0].message.content
        if reply and reply.strip():
            save_chat_message(topic_id, "assistant", reply.strip())
            return reply.strip()
    except Exception as e:
        logger.warning(f"Primary copilot model {PRIMARY_COPILOT_MODEL} timed out or failed ({e}). Switching to ultra-fast fallback {FAST_FALLBACK_MODEL}...")

    # Attempt 2: Instant fallback to Nemotron Lightning (responds in ~1.1s)
    try:
        fallback_client = get_copilot_client(timeout=30.0)
        resp = fallback_client.chat.completions.create(
            model=FAST_FALLBACK_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
            extra_body={"chat_template_kwargs": {"thinking": False}}
        )
        reply = resp.choices[0].message.content
        if reply and reply.strip():
            save_chat_message(topic_id, "assistant", reply.strip())
            return reply.strip()
    except Exception as e2:
        logger.error(f"Fallback copilot model also failed: {e2}")
        fallback_msg = f"I encountered a temporary connection delay with the AI service. Here is what this lecture focuses on: {topic.get('title')}. Please try your question again in a moment."
        save_chat_message(topic_id, "assistant", fallback_msg)
        return fallback_msg

    return "No response generated."

