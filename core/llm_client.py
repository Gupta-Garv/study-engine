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

def get_client(timeout: float = 85.0) -> OpenAI:
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY, timeout=timeout)

def _invoke_model(model_name: str, messages: List[Dict[str, str]], temperature: float = 0.15, max_tokens: int = 4096, timeout: float = 85.0) -> str:
    client = get_client(timeout=timeout)
    limiter.acquire()
    resp = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    content = resp.choices[0].message.content
    if content and content.strip():
        return content
    reasoning = getattr(resp.choices[0].message, "reasoning_content", None)
    if reasoning and reasoning.strip():
        return reasoning
    raise RuntimeError(f"Model {model_name} returned empty text content.")

def call_llm(messages: List[Dict[str, str]], temperature: float = 0.15, max_tokens: int = 4096, max_retries: int = 3) -> str:
    """
    Executes LLM request using high-speed model with fallback to secondary reasoning model.
    """
    # Attempt 1: Try High-Speed Model
    try:
        logger.info(f"Calling high-speed academic model {PRIMARY_MODEL}...")
        return _invoke_model(PRIMARY_MODEL, messages, temperature=temperature, max_tokens=max_tokens, timeout=85.0)
    except Exception as e:
        logger.warning(f"Model {PRIMARY_MODEL} encountered issue ({e}). Switching to secondary engine {SECONDARY_MODEL}...")

    # Attempt 2: Try Secondary Model
    try:
        logger.info(f"Calling secondary model {SECONDARY_MODEL}...")
        return _invoke_model(SECONDARY_MODEL, messages, temperature=temperature, max_tokens=max_tokens, timeout=90.0)
    except Exception as e:
        logger.warning(f"Secondary model also failed: {e}")

    # Retries on Primary
    for attempt in range(1, max_retries + 1):
        try:
            return _invoke_model(PRIMARY_MODEL, messages, temperature=temperature, max_tokens=max_tokens, timeout=35.0)
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2.0)
            else:
                raise e

def safe_parse_json(raw: str) -> Dict[str, Any]:
    """Robust JSON parser that isolates the final JSON object from reasoning traces and fixes LaTeX backslashes."""
    cleaned = raw.strip()

    # 1. Look for ```json { ... } ``` or ``` { ... } ``` codeblocks first
    codeblock_matches = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if codeblock_matches:
        candidate = codeblock_matches[-1]
        try:
            fixed = re.sub(r'\\(?![\\\"/bfnrtu])', r'\\\\', candidate)
            return json.loads(fixed)
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
                return json.loads(fixed)
            except Exception:
                try:
                    res = json_repair.loads(sub)
                    if isinstance(res, dict) and "notes_markdown" in res:
                        return res
                except Exception:
                    pass

    # 3. Direct parse
    try:
        fixed = re.sub(r'\\(?![\\\"/bfnrtu])', r'\\\\', cleaned)
        return json.loads(fixed)
    except Exception:
        pass

    # 4. Fallback to json_repair across entire string
    try:
        res = json_repair.loads(cleaned)
        if isinstance(res, dict) and "notes_markdown" in res:
            return res
    except Exception:
        pass

    raise RuntimeError("Failed to parse AI response into structured notes and questions.")

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
        "You are an Eminent University Professor and Chief Examiner in Corporate Finance and Advanced Business Academics. "
        "Your mission is to transform university lecture transcripts and visual slide text into exhaustive, textbook-grade revision notes "
        "and rigorous exam assessments for typed online university exams.\n\n"
        "STRICT QUALITY & ACCURACY MANDATES:\n"
        "1. GROUND TRUTH FIDELITY (NO HALLUCINATIONS):\n"
        "   - Anchor all notes strictly in what was actually taught in the transcript and shown on the slides.\n"
        "   - ABSOLUTELY NO SUPERFICIAL SUMMARIES: Never write high-level meta-summaries like 'In this video, the professor introduces...'. "
        "Write the actual theoretical depth, economic principles, formulas, and complete explanations directly.\n"
        "2. CONDITIONAL MATHEMATICAL FORMULATIONS:\n"
        "   - IF THE LECTURE INCLUDES FORMULAS/CALCULATIONS: Transcribe exact KaTeX LaTeX block ($$...$$) and inline ($...$) equations. "
        "Include a comprehensive Variable Definition Table (Variable, Name, Units, Interpretation), economic assumptions, and step-by-step worked numerical examples.\n"
        "   - IF THE LECTURE IS PURELY CONCEPTUAL/QUALITATIVE (e.g. Legal Forms of Business, Corporate Governance, Agency Problems): "
        "DO NOT invent hypothetical math formulas! In Section 2, state explicitly: 'Conceptual Lecture — No mathematical formulas introduced in this session.' "
        "Then provide exhaustive structural comparisons, legal distinctions, advantages/disadvantages, and governance mechanisms in full theoretical depth.\n"
        "3. COMPARATIVE MATRICES & DIAGRAMS:\n"
        "   - Include Markdown comparison tables contrasting conflicting concepts (e.g., Profit Maximization vs Shareholder Wealth Maximization, Sole Proprietorship vs Partnership vs Company).\n"
        "   - Include at least ONE valid Mermaid flowchart (```mermaid flowchart TD ...```) with quoted node labels.\n"
        "4. UNIVERSITY EXAM PITFALLS & TRICKY TRAPS:\n"
        "   - Detail exact traps and subtle distinctions where examiners penalize students on university exams.\n"
        "5. ASSESSMENTS:\n"
        "   - 3-4 challenging timed MCQs with 4 options and thorough step-by-step explanations for the correct answer AND distractors.\n"
        "   - 2 typed subjective questions (5-mark and 10-mark) with complete model answers and grading rubrics.\n"
        "   - 4-5 high-yield flashcards with front/back."
    )

    slide_block = f"\n\nVisual Slides & Whiteboard Text (OCR):\n\"\"\"\n{slide_text[:4000]}\n\"\"\"" if slide_text.strip() else ""

    user_prompt = f"""Course: {course_name}
Module: {module_name}
Lecture Topic: {topic_title}

Spoken Lecture Transcript:
\"\"\"
{transcript_text[:14000]}
\"\"\"{slide_block}

TASK MANDATE:
Write the complete, exhaustive academic revision package. Fill every section with thorough textbook prose, real lecture facts, exact formulas or clear qualitative frameworks, and detailed explanations. Do NOT abbreviate, do NOT write ellipses (...), and do NOT leave placeholder text.

Output valid JSON matching this schema:
{{
  "notes_markdown": "# {topic_title}\\n\\n## 1. Executive Theoretical Exposition\\n[Comprehensive explanation of the lecture's core foundations, principles, and real-world mechanisms]\\n\\n## 2. Mathematical Formulations & Exact Equations\\n[Explicit KaTeX LaTeX block formulas ($$...$$) and inline variables ($...$), with full variable tables and constraints. If qualitative lecture, write 'Conceptual Lecture — No mathematical formulas introduced in this session' followed by structural frameworks]\\n\\n## 3. Worked Numerical Demonstration / Case Analysis\\n[Step 1, Step 2, Step 3 calculations with real lecture numbers OR detailed case breakdown of the lecture's core scenario]\\n\\n## 4. Analytical Comparative Matrix\\n| Dimension | Concept A | Concept B |\\n|---|---|---|\\n...\\n\\n## 5. Architectural Flow & Decision Logic\\n```mermaid\\nflowchart TD\\n  A[\\\"Start Condition\\\"] --> B[\\\"Evaluation Rule\\\"]\\n```\\n\\n## 6. University Exam Pitfalls & Tricky Traps\\n* [Trap 1: Common misconception examiners test]\\n* [Trap 2: Tricky edge case]\\n\\n## 7. High-Yield Revision Flashpoints\\n* [Point 1]\\n* [Point 2]",
  "mcqs": [
    {{
      "id": 1,
      "question": "Rigorous conceptual or numerical exam problem",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_index": 0,
      "difficulty": "Tricky",
      "explanation": "Step-by-step mathematical or conceptual proof for why A is correct and why B, C, D are specific traps.",
      "key_concept": "Concept name"
    }}
  ],
  "subjective_questions": [
    {{
      "id": 1,
      "question": "Comprehensive 5-mark or 10-mark exam question",
      "marks": 10,
      "suggested_time_minutes": 15,
      "model_answer": "Complete, structured typed model answer with headings, LaTeX equations (if applicable), and analytical discussion.",
      "rubric": [
        {{"criterion": "Core theoretical definition and principles", "marks": 4}},
        {{"criterion": "Analytical comparison and real-world application", "marks": 4}},
        {{"criterion": "Edge cases, limitations, and governance mechanisms", "marks": 2}}
      ]
    }}
  ],
  "flashcards": [
    {{
      "front": "Key term, formula name, or exam scenario",
      "back": "Exact definition, LaTeX formula, or distinction rule"
    }}
  ]
}}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    raw = call_llm(messages, temperature=0.15, max_tokens=4096)
    return safe_parse_json(raw)
