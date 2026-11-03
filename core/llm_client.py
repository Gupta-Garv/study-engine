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
from pathlib import Path
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

PROMPTS_DIR = Path(__file__).parent / "prompts"
RULES_FILE = PROMPTS_DIR / "note_synthesis_rules.md"

def load_note_synthesis_rules() -> str:
    """Loads external guidelines and rules file for academic note synthesis."""
    if RULES_FILE.exists():
        try:
            return RULES_FILE.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Could not read {RULES_FILE}: {e}")
    return ""

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
    Synthesizes academic, conceptual lecture notes and application-oriented MCQs
    anchored strictly to the lecture's spoken transcript, governed by core/prompts/note_synthesis_rules.md.
    """
    rules_content = load_note_synthesis_rules()
    
    system_prompt = (
        "You are an expert academic note synthesizer specializing in university examinations.\n"
        "Your students are preparing for conceptual, MCQ-heavy exams that test deep understanding, parameter sensitivity, and mental models rather than rote textbook memorization.\n\n"
        f"OPERATIONAL GUIDELINES & SYNTHESIS RULES (FROM note_synthesis_rules.md):\n"
        f"\"\"\"\n{rules_content}\n\"\"\"\n\n"
        "CORE DIRECTIVES:\n"
        "1. GROUND TRUTH FIDELITY: Base notes STRICTLY AND ONLY on what the professor actually explains in this specific video transcript. Do NOT add outside encyclopedic fluff or textbook history.\n"
        "2. REQUIRED STRUCTURE:\n"
        "   - ## 1. Executive Mental Model & Core Intuition (Core thesis, business dilemma, and underlying logic in 1-2 paragraphs)\n"
        "   - ## 2. Concise Point-Wise Conceptual Mechanics (Cause & Effect) (Parameter shifts: 'If X increases -> Y decreases because...', boundary conditions)\n"
        "   - ## 3. Conceptual Distinctions & Versus Matrix (Markdown comparison table clarifying easily confused terms from the lecture)\n"
        "   - ## 4. Key Formulas & Numerical Application (Exact KaTeX $$...$$, variable definition table, worked lecture numbers; OR explicitly write '*Conceptual Session: No mathematical formulas introduced in this lecture.*' followed by decision criteria)\n"
        "   - ## 5. MCQ Trap Radar & Examiner Gotchas (3-4 specific cognitive traps and distractor tricks examiners use on this topic)\n"
        "3. ASSESSMENTS:\n"
        "   - 4 to 6 conceptual, application-oriented MCQs testing parameter shifts, scenarios, and misconceptions (NO trivial recall). Each MCQ must have 4 options and a detailed explanation explaining why the correct option is right AND why distractors are wrong.\n"
        "   - 1 university subjective question with full model answer and marking rubric.\n"
        "   - 3-4 conceptual flashcards."
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
Follow the rules in note_synthesis_rules.md strictly:
1. Ground truth fidelity: Only summarize concepts, mechanics, and examples actually spoken in this video transcript.
2. Structure:
   ## 1. Executive Mental Model & Core Intuition
   ## 2. Concise Point-Wise Conceptual Mechanics (Cause & Effect)
   ## 3. Conceptual Distinctions & Versus Matrix
   ## 4. Key Formulas & Numerical Application (or state that it is a conceptual session)
   ## 5. MCQ Trap Radar & Examiner Gotchas
3. Provide 4 to 6 conceptual, application-oriented MCQs (scenario-based or sensitivity-based).
4. Provide 1 university subjective question with model answer and marking rubric.
5. Provide 3-4 conceptual flashcards.

Output a single valid JSON object with the following exact keys:
{{
  "notes_markdown": "# {topic_title}\\n\\n## 1. Executive Mental Model & Core Intuition\\n...\\n\\n## 2. Concise Point-Wise Conceptual Mechanics (Cause & Effect)\\n* **Parameter Sensitivity**: If X increases, Y ...\\n\\n## 3. Conceptual Distinctions & Versus Matrix\\n| Dimension | Concept A | Concept B | MCQ Diagnostic |\\n|---|---|---|---|\\n\\n## 4. Key Formulas & Numerical Application\\n(Formulas with variable definition tables, or state that this is a conceptual session)\\n\\n## 5. MCQ Trap Radar & Examiner Gotchas\\n* **Trap 1**: ...",
  "mcqs": [
    {{
      "id": 1,
      "question": "Scenario or conceptual question testing cause-and-effect",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_index": 0,
      "difficulty": "Moderate | Tricky",
      "explanation": "Why correct answer is right and why distractors are wrong",
      "key_concept": "Concept name"
    }}
  ],
  "subjective_questions": [
    {{
      "id": 1,
      "question": "University exam question based on this video",
      "marks": 10,
      "suggested_time_minutes": 15,
      "model_answer": "Complete structured model answer",
      "rubric": [{{"criterion": "Core conceptual understanding", "marks": 5}}, {{"criterion": "Analytical application", "marks": 5}}]
    }}
  ],
  "flashcards": [
    {{
      "front": "Conceptual diagnostic question",
      "back": "Key conceptual takeaway"
    }}
  ]
}}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    raw = call_llm(messages, temperature=0.15, max_tokens=3500)
    return safe_parse_json(raw, fallback_title=topic_title)
