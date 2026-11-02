"""
NVIDIA NIM LLM Client with Rate Limiting & Academic Note Synthesizer.
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
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY") or get_setting("nvidia_api_key") or ""

# Fast, high-capacity model
DEFAULT_TEXT_MODEL = "nvidia/nemotron-3.5-bolt-e4b"

class RateLimiter:
    def __init__(self, max_per_minute: int = 35):
        # Strict cap of 35 requests/minute to safely stay below the 40 req/min limit
        self.max_per_minute = max_per_minute
        self.timestamps = []
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

def get_client() -> OpenAI:
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY, timeout=90.0)

def call_llm(messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 4096, max_retries: int = 5) -> str:
    client = get_client()

    for attempt in range(1, max_retries + 1):
        limiter.acquire()
        try:
            resp = client.chat.completions.create(
                model=DEFAULT_TEXT_MODEL,
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
            raise RuntimeError("Received empty response from NIM model.")
        except Exception as e:
            err_str = str(e).lower()
            is_rate_limit = "429" in err_str or "rate limit" in err_str or "quota" in err_str
            if is_rate_limit and attempt < max_retries:
                sleep_s = attempt * 4.0
                logger.warning(f"Hit 429 rate limit. Backing off for {sleep_s}s (attempt {attempt}/{max_retries})...")
                time.sleep(sleep_s)
            elif attempt < max_retries:
                time.sleep(2.5)
            else:
                raise e

def safe_parse_json(raw: str) -> Dict[str, Any]:
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # 1. Direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 2. Fix unescaped backslashes commonly produced by LaTeX ($$ \frac, \beta, \sum $$)
    try:
        fixed = re.sub(r'\\(?![\\\"/bfnrtu])', r'\\\\', cleaned)
        return json.loads(fixed)
    except Exception:
        pass

    # 3. Robust json_repair parser
    try:
        result = json_repair.loads(cleaned)
        if isinstance(result, dict) and "notes_markdown" in result:
            return result
    except Exception:
        pass

    # 4. Regex substring search
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        block = match.group(0)
        try:
            fixed = re.sub(r'\\(?![\\\"/bfnrtu])', r'\\\\', block)
            return json.loads(fixed)
        except Exception:
            return json_repair.loads(block)

    raise RuntimeError("Failed to parse AI response into structured notes and questions.")

def generate_notes_and_questions(course_name: str, module_name: str, topic_title: str, transcript_text: str) -> Dict[str, Any]:
    """
    Synthesizes academic, textbook-grade lecture notes, exact LaTeX formulas,
    worked numeric examples, comparative tables, timed MCQs, and typed subjective rubrics.
    """
    system_prompt = (
        "You are an Eminent University Professor and Chief Examiner in Corporate Finance and Advanced Business Academics. "
        "Your mission is to transform university lecture transcripts into exhaustive, textbook-grade revision notes "
        "and rigorous exam assessments for typed online university exams.\n\n"
        "STRICT QUALITY MANDATES:\n"
        "1. ABSOLUTELY NO SUPERFICIAL SUMMARIES: Never write brief meta-summaries or phrases like 'In this video, the professor introduces...'. "
        "Write the actual theoretical depth, academic principles, equations, and complete explanations directly.\n"
        "2. EXACT MATHEMATICAL FORMULAS & NOTATION:\n"
        "   - Render every single mathematical or financial formula using explicit KaTeX LaTeX block ($$...$$) and inline ($...$) syntax.\n"
        "   - In JSON strings, always double-escape backslashes for LaTeX (e.g. \\\\frac, \\\\beta, \\\\sum, \\\\text, \\\\sigma).\n"
        "   - For every formula, provide a comprehensive Markdown Variable Definition Table detailing: Variable, Academic Name, Units, and Economic Interpretation.\n"
        "   - Detail the underlying economic assumptions and mathematical boundary conditions (e.g., r > g, t >= 0).\n"
        "3. WORKED NUMERIC EXAMPLES:\n"
        "   - Provide concrete numerical calculations with realistic figures illustrating step-by-step formula application.\n"
        "4. COMPARATIVE MATRICES & DIAGRAMS:\n"
        "   - Include Markdown comparison tables contrasting conflicting concepts (e.g., Profit Maximization vs Shareholder Wealth Maximization, Real vs Financial Assets).\n"
        "   - Include at least ONE valid Mermaid flowchart (```mermaid flowchart TD ...```) with quoted node labels.\n"
        "5. COMMON EXAM TRAPS & PITFALLS:\n"
        "   - Highlight exact tricky nuances where students lose marks on university exams.\n"
        "6. ASSESSMENTS:\n"
        "   - 3-4 challenging timed MCQs with 4 options and thorough step-by-step explanations for the correct answer AND distractors.\n"
        "   - 2 typed subjective questions (5-mark and 10-mark) with complete model answers and grading rubrics.\n"
        "   - 4-5 high-yield flashcards with front/back."
    )

    user_prompt = f"""Course: {course_name}
Module: {module_name}
Lecture Topic: {topic_title}

Lecture Transcript:
\"\"\"
{transcript_text[:16000]}
\"\"\"

Synthesize the exhaustive academic revision notes and exam kit. Output valid JSON ONLY matching exactly this schema:
{{
  "notes_markdown": "# {topic_title}\\n\\n## 1. Executive Theoretical Exposition\\n[Comprehensive explanation of the lecture's core foundations, principles, and real-world mechanisms]\\n\\n## 2. Mathematical Formulations & Exact Equations\\n[Explicit KaTeX LaTeX block formulas ($$...$$) and inline variables ($...$), with full variable tables and constraints]\\n\\n## 3. Worked Numerical Demonstration & Step-by-Step Problem Solving\\n[Step 1, Step 2, Step 3 calculations with real numbers and final economic takeaway]\\n\\n## 4. Analytical Comparative Matrix\\n| Dimension | Concept A | Concept B |\\n|---|---|---|\\n...\\n\\n## 5. Architectural Flow & Decision Logic\\n```mermaid\\nflowchart TD\\n  A[\\\"Start Condition\\\"] --> B[\\\"Evaluation Rule\\\"]\\n```\\n\\n## 6. University Exam Pitfalls & Tricky Traps\\n* [Trap 1: Common formula misapplication]\\n* [Trap 2: Conceptual trap examiners use in MCQs]\\n\\n## 7. High-Yield Revision Flashpoints\\n* [Point 1]\\n* [Point 2]",
  "mcqs": [
    {{
      "id": 1,
      "question": "Rigorous conceptual or numerical exam problem...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_index": 0,
      "difficulty": "Tricky",
      "explanation": "Step-by-step mathematical or conceptual proof for why A is correct and why B, C, D are specific traps.",
      "key_concept": "Concept name"
    }}
  ],
  "subjective_questions": [
    {{
      "id": 1,
      "question": "Comprehensive 5-mark or 10-mark exam question...",
      "marks": 10,
      "suggested_time_minutes": 15,
      "model_answer": "Complete, structured typed model answer with headings, LaTeX equations, and analytical discussion.",
      "rubric": [
        {{"criterion": "Core theoretical definition and exact formulas", "marks": 4}},
        {{"criterion": "Analytical comparison and real-world application", "marks": 4}},
        {{"criterion": "Edge cases, limitations, and governance mechanisms", "marks": 2}}
      ]
    }}
  ],
  "flashcards": [
    {{
      "front": "Key term, formula name, or exam scenario",
      "back": "Exact definition, LaTeX formula, and rule"
    }}
  ]
}}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    raw = call_llm(messages, temperature=0.15, max_tokens=4096)
    return safe_parse_json(raw)
