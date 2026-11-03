"""
NVIDIA NIM LLM Client with Rate Limiting & High-Fidelity Academic Note Synthesizer.
Engineered for university-grade exam preparation: exact LaTeX formulas, variable legends,
worked numerical examples, comparative matrices, timed MCQs, and typed subjective rubrics.
"""

from __future__ import annotations

import os
import time
import json
import re
import threading
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
import json_repair
from dotenv import load_dotenv
from .db import get_setting

load_dotenv()
logger = logging.getLogger("study_engine.llm")

# Integrated NVIDIA NIM Key via Environment or Database Settings
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY") or get_setting("nvidia_api_key") or "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"

# Lightning-fast primary engine + Deep reasoning fallback model (both verified active on user NIM key)
PRIMARY_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"
SECONDARY_MODEL = "mistralai/mistral-large-4-1t-a52b"

class RateLimiter:
    def __init__(self, max_per_minute: int = 35):
        # Strict cap of 35 requests/minute to safely stay below the 40 req/min limit
        self.max_per_minute = max_per_minute
        self.timestamps: List[float] = []
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            now = time.time()
            self.timestamps = [t for t in self.timestamps if now - t < 60.0]
            if len(self.timestamps) >= self.max_per_minute:
                wait_time = 60.0 - (now - self.timestamps[0]) + 0.15
                if wait_time > 0:
                    logger.info(f"Rate limiter pacing: sleeping {wait_time:.2f}s to respect 40 req/min cap...")
                    time.sleep(wait_time)
                now = time.time()
                self.timestamps = [t for t in self.timestamps if now - t < 60.0]
            self.timestamps.append(time.time())

limiter = RateLimiter(max_per_minute=35)

def get_api_key() -> str:
    return NVIDIA_API_KEY

def get_client(timeout: float = 75.0) -> OpenAI:
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY, timeout=timeout)

def _invoke_model(model_name: str, messages: List[Dict[str, str]], temperature: float = 0.15, max_tokens: int = 3000, timeout: float = 75.0) -> str:
    client = get_client(timeout=timeout)
    limiter.acquire()
    
    # Strictly disable hidden reasoning loops to ensure fast generation and prevent token budget exhaustion
    resp = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body={"chat_template_kwargs": {"thinking": False}}
    )

    content = resp.choices[0].message.content
    if content and content.strip():
        return content
    reasoning = getattr(resp.choices[0].message, "reasoning_content", None)
    if reasoning and reasoning.strip():
        return reasoning
    raise RuntimeError(f"Model {model_name} returned empty text content.")

def call_llm(messages: List[Dict[str, str]], temperature: float = 0.15, max_tokens: int = 3000) -> str:
    """
    Executes LLM request using high-speed model with fallback to secondary engine.
    """
    # Attempt 1: Try High-Speed Model
    try:
        logger.info(f"Calling high-speed academic model {PRIMARY_MODEL}...")
        return _invoke_model(PRIMARY_MODEL, messages, temperature=temperature, max_tokens=max_tokens, timeout=75.0)
    except Exception as e:
        logger.warning(f"Model {PRIMARY_MODEL} encountered issue ({e}). Switching to secondary engine {SECONDARY_MODEL}...")

    # Attempt 2: Try Secondary Model
    try:
        logger.info(f"Calling secondary model {SECONDARY_MODEL}...")
        return _invoke_model(SECONDARY_MODEL, messages, temperature=temperature, max_tokens=max_tokens, timeout=80.0)
    except Exception as e:
        logger.warning(f"Secondary model also failed: {e}")
        raise e

def safe_parse_json(raw: str, fallback_title: str = "Lecture Notes") -> Dict[str, Any]:
    """Robust JSON parser that isolates the JSON object and gracefully salvages content if JSON fails."""
    cleaned = raw.strip()

    # 1. Look for ```json { ... } ``` or ``` { ... } ``` codeblocks first
    codeblock_matches = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    for candidate in reversed(codeblock_matches):
        try:
            fixed = re.sub(r'\\(?![\\\"/bfnrtu])', r'\\\\', candidate)
            parsed = json.loads(fixed)
            if isinstance(parsed, dict) and "notes_markdown" in parsed:
                return parsed
        except Exception:
            try:
                res = json_repair.loads(candidate)
                if isinstance(res, dict) and "notes_markdown" in res:
                    return res
            except Exception:
                pass

    # 2. Check if the block containing "notes_markdown" can be isolated
    idx = cleaned.rfind('"notes_markdown"')
    if idx != -1:
        open_brace = cleaned.rfind("{", 0, idx)
        close_brace = cleaned.rfind("}")
        if open_brace != -1 and close_brace > open_brace:
            sub = cleaned[open_brace : close_brace + 1]
            try:
                fixed = re.sub(r'\\(?![\\\"/bfnrtu])', r'\\\\', sub)
                parsed = json.loads(fixed)
                if isinstance(parsed, dict) and "notes_markdown" in parsed:
                    return parsed
            except Exception:
                try:
                    res = json_repair.loads(sub)
                    if isinstance(res, dict) and "notes_markdown" in res:
                        return res
                except Exception:
                    pass

    # 3. Direct parse with json / json_repair
    try:
        fixed = re.sub(r'\\(?![\\\"/bfnrtu])', r'\\\\', cleaned)
        parsed = json.loads(fixed)
        if isinstance(parsed, dict) and "notes_markdown" in parsed:
            return parsed
    except Exception:
        pass

    try:
        res = json_repair.loads(cleaned)
        if isinstance(res, dict) and "notes_markdown" in res:
            return res
    except Exception:
        pass

    # 4. Bulletproof Fallback: Never raise RuntimeError!
    # If the AI generated direct Markdown or corrupted JSON, preserve the entire notes content!
    logger.warning("Could not parse strict JSON. Applying intelligent markdown extraction fallback.")
    
    # Check if there is a raw notes_markdown field we can extract via regex
    notes_match = re.search(r'"notes_markdown"\s*:\s*"(.*?)(?:"\s*,\s*"(?:mcqs|subjective_questions|flashcards)"|\Z)', cleaned, re.DOTALL)
    if notes_match:
        notes_content = notes_match.group(1).replace('\\"', '"').replace('\\n', '\n')
    else:
        # Strip markdown codeblock markers if present
        notes_content = re.sub(r"^```(?:markdown)?\s*", "", cleaned).strip()
        notes_content = re.sub(r"\s*```$", "", notes_content).strip()

    # Extract any MCQs embedded in text or provide high-yield defaults
    mcqs = []
    mcq_block = re.search(r'"mcqs"\s*:\s*(\[.*?\])', cleaned, re.DOTALL)
    if mcq_block:
        try:
            salvaged_mcqs = json_repair.loads(mcq_block.group(1))
            if isinstance(salvaged_mcqs, list):
                mcqs = salvaged_mcqs
        except Exception:
            pass

    return {
        "notes_markdown": notes_content if len(notes_content) > 50 else f"# {fallback_title}\n\n{notes_content}",
        "mcqs": mcqs,
        "subjective_questions": [],
        "flashcards": []
    }

def generate_notes_and_questions(
    course_name: str, 
    module_name: str, 
    topic_title: str, 
    transcript_text: str,
    slide_text: str = ""
) -> Dict[str, Any]:
    """
    Synthesizes academic, textbook-grade lecture notes anchored strictly to the lecture's
    spoken transcript and slide OCR text.
    """
    system_prompt = (
        "You are an expert academic note synthesizer for university students. "
        "Your mission is to produce clear, structured, high-yield lecture notes based STRICTLY AND ONLY on what is taught in the provided video transcript.\n\n"
        "STRICT QUALITY & CONCISENESS RULES:\n"
        "1. GROUND TRUTH FIDELITY (NO OUTSIDE FILLER):\n"
        "   - Anchor notes strictly in what the professor explains in this specific video. Do NOT import unrelated encyclopedia theories or excessive fluff.\n"
        "2. REQUIRED NOTE STRUCTURE:\n"
        "   - Section 1: Executive Summary & Core Explanation (A clear, intuitive summary explaining what happens in this video and the underlying logic).\n"
        "   - Section 2: Concise Point-Wise Key Takeaways (Bullet-pointed key concepts and core principles taught in this session. Crisp and easy to review).\n"
        "   - Section 3: Key Formulas & Worked Examples (IF formulas are discussed in this video: show exact KaTeX LaTeX formulas ($$...$$ and $...$), variable definition table explaining each symbol/constant, and step-by-step example from the lecture. IF the video is purely qualitative/conceptual: state 'Conceptual session — no mathematical formulas introduced in this video' and summarize the conceptual framework).\n"
        "   - Section 4: University Exam Pitfalls & Tricky Traps (2-3 common misconceptions or exam traps examiners test on this specific lecture).\n"
        "3. ASSESSMENTS:\n"
        "   - 2-3 focused MCQs with options, correct answer, and clear explanation.\n"
        "   - 1 subjective exam question (5-mark or 10-mark) with model answer and grading rubric.\n"
        "   - 3-4 concise high-yield revision flashcards."
    )

    slide_block = f"\n\nVisual Slides & Whiteboard Text (OCR):\n\"\"\"\n{slide_text[:3000]}\n\"\"\"" if slide_text.strip() else ""

    user_prompt = f"""Course: {course_name}
Module: {module_name}
Lecture Topic: {topic_title}

Spoken Lecture Transcript:
\"\"\"
{transcript_text[:14000]}
\"\"\"{slide_block}

TASK INSTRUCTIONS:
Synthesize concise, high-yield university lecture notes strictly grounded in this video's transcript.
Do NOT pad with outside textbook trivia. Follow the required structure cleanly.

Output a single valid JSON object with the following exact keys:
{{
  "notes_markdown": "# {topic_title}\\n\\n## 1. Executive Summary & Core Explanation\\n(Direct, clear explanation of what is taught in this video...)\\n\\n## 2. Concise Point-Wise Key Takeaways\\n* **Key Concept 1**: Concise explanation\\n* **Key Concept 2**: Concise explanation\\n\\n## 3. Key Formulas & Worked Examples\\n(Formulas with variable definition tables, or state that this is a conceptual session)\\n\\n## 4. University Exam Pitfalls & Tricky Traps\\n* **Common Trap**: Distinction to remember",
  "mcqs": [
    {{
      "id": 1,
      "question": "Exam question based strictly on this video",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_index": 0,
      "difficulty": "Tricky",
      "explanation": "Clear explanation of correct answer and traps",
      "key_concept": "Concept name"
    }}
  ],
  "subjective_questions": [
    {{
      "id": 1,
      "question": "Exam question based on this video",
      "marks": 10,
      "suggested_time_minutes": 15,
      "model_answer": "Complete structured model answer",
      "rubric": [{{"criterion": "Core principles", "marks": 5}}, {{"criterion": "Analysis and application", "marks": 5}}]
    }}
  ],
  "flashcards": [
    {{
      "front": "Key Term / Concept from this lecture",
      "back": "Clear definition and takeaway"
    }}
  ]
}}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    raw = call_llm(messages, temperature=0.15, max_tokens=3000)
    return safe_parse_json(raw, fallback_title=topic_title)
