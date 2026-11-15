"""
Module Test Generator for StudyEngine.
Generates 2 rigorous, university-level conceptual test sets for any course module:
- Set 1: Conceptual Mechanics & Core Diagnostics (Single & Multi-Select)
- Set 2: Applied Scenarios & Multi-Concept Case Test (Single & Multi-Select)
Each test stays under 25 questions (12-16 high-yield questions).
"""

from __future__ import annotations

import logging
import json
import re
from typing import Dict, List, Any, Optional
import json_repair

from .db import get_conn, save_module_test, get_module_tests, get_module_test_by_set
from .llm_client import call_llm, clean_text_formatting

logger = logging.getLogger("study_engine.test_generator")

def sanitize_question(q: Dict[str, Any], q_idx: int) -> Dict[str, Any]:
    """Ensures question has valid fields, clean text formatting, and valid correct_indices."""
    question_text = clean_text_formatting(q.get("question", f"Conceptual Question {q_idx}"))
    options = q.get("options", [])
    if not isinstance(options, list) or len(options) < 2:
        options = ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"]
    options = [clean_text_formatting(str(opt)) for opt in options]

    # Resolve correct_indices
    raw_indices = q.get("correct_indices")
    if raw_indices is None:
        raw_indices = q.get("correct_index")
    
    correct_indices: List[int] = []
    if isinstance(raw_indices, list):
        for idx in raw_indices:
            try:
                i = int(idx)
                if 0 <= i < len(options):
                    correct_indices.append(i)
            except (ValueError, TypeError):
                pass
    elif isinstance(raw_indices, (int, str)):
        try:
            i = int(raw_indices)
            if 0 <= i < len(options):
                correct_indices.append(i)
        except (ValueError, TypeError):
            pass

    if not correct_indices:
        correct_indices = [0]

    # Auto-detect type based on number of correct options
    q_type = q.get("type", "single_choice")
    if len(correct_indices) > 1:
        q_type = "multiple_choice"
        if "[Select all that apply]" not in question_text:
            question_text = f"{question_text} [Select all that apply]"
    elif len(correct_indices) == 1 and q_type == "multiple_choice":
        # Check if question has "[Select all that apply]" or user asked for multiple
        pass

    explanation = clean_text_formatting(q.get("explanation", "Conceptual reasoning based on lecture mechanics."))
    trap_warning = clean_text_formatting(q.get("trap_warning", "Be careful to separate cause from correlation."))
    key_concept = clean_text_formatting(q.get("key_concept", "Core Conceptual Principle"))
    difficulty = q.get("difficulty", "Challenging" if q_type == "multiple_choice" else "Moderate")

    return {
        "id": q_idx,
        "type": q_type,
        "difficulty": difficulty,
        "key_concept": key_concept,
        "question": question_text,
        "options": options,
        "correct_indices": correct_indices,
        "correct_index": correct_indices[0] if len(correct_indices) == 1 else correct_indices,
        "explanation": explanation,
        "trap_warning": trap_warning,
        "distractor_analysis": clean_text_formatting(q.get("distractor_analysis", ""))
    }

def extract_module_context(module_id: str) -> Dict[str, Any]:
    """Gathers all topics, syntheses, and key concepts for a module."""
    conn = get_conn()
    mod_row = conn.execute("""
        SELECT m.id, m.name as module_name, m.number, c.name as course_name, c.id as course_id
        FROM modules m
        JOIN courses c ON m.course_id = c.id
        WHERE m.id = ?
    """, (module_id,)).fetchone()

    if not mod_row:
        raise ValueError(f"Module {module_id} not found in database.")

    topics = conn.execute("""
        SELECT id, title, notes_markdown, transcript_text, duration_seconds
        FROM topics
        WHERE module_id = ?
        ORDER BY created_at ASC
    """, (module_id,)).fetchall()

    topic_summaries = []
    for t in topics:
        title = t["title"]
        notes = t["notes_markdown"] or ""
        # Pull key sections from notes if present
        snippet = ""
        if len(notes) > 100:
            # Extract section 1 and 2 or first 800 chars
            snippet = notes[:800].replace("\n\n", "\n")
        elif t["transcript_text"]:
            snippet = t["transcript_text"][:600]
        topic_summaries.append(f"### Topic: {title}\n{snippet}\n")

    return {
        "course_name": mod_row["course_name"],
        "module_name": mod_row["module_name"],
        "module_number": mod_row["number"],
        "topics_context": "\n".join(topic_summaries)
    }

def generate_module_test_set(
    module_id: str,
    set_number: int,
    course_name: str,
    module_name: str,
    topics_context: str,
    target_questions: int = 14
) -> Dict[str, Any]:
    """Generates one conceptual test set (Set 1 or Set 2) for the given module."""
    if set_number == 1:
        set_title = f"Set 1: Conceptual Mechanics & Core Diagnostics"
        set_type = "conceptual_diagnostics"
        focus_desc = (
            "Focus strictly on deep theoretical mechanics, cause-and-effect chains, parameter sensitivities "
            "(e.g., if Variable A increases, what happens to Variable B and why?), boundary conditions where assumptions break down, "
            "and core definitions versus deceptive traps."
        )
    else:
        set_title = f"Set 2: Applied Scenarios & Multi-Concept Case Test"
        set_type = "applied_scenarios"
        focus_desc = (
            "Focus strictly on realistic applied business dilemmas, situational mini-cases, multi-statement validity analyses "
            "('Which of the following statements are logically/conceptually sound? [Select all that apply]'), and evaluating trade-offs "
            "between alternative strategic decisions."
        )

    system_prompt = (
        "You are a distinguished university professor and senior psychometric examination designer.\n"
        "Your students are preparing for rigorous undergraduate degree examinations that strictly test conceptual comprehension, "
        "first-principles reasoning, and mental models rather than superficial rote memorization.\n\n"
        "STRICT QUESTION DESIGN PRINCIPLES:\n"
        "1. ZERO TRIVIA: Never ask for dates, isolated definitions, or superficial names. Ask 'WHY', 'UNDER WHAT CONDITION', and 'WHAT IS THE MECHANISM'.\n"
        "2. PARAMETER SENSITIVITY: Test what happens when underlying assumptions or parameters shift.\n"
        "3. MIX OF QUESTION TYPES:\n"
        "   - 'single_choice': Exactly 1 correct option out of 4 options (A, B, C, D).\n"
        "   - 'multiple_choice': 2 or 3 correct options out of 4 or 5 options. Mark these with '[Select all that apply]'.\n"
        "4. HIGH-YIELD DISTRACTORS: Every incorrect option must represent a genuine, subtle student fallacy or common misconception.\n"
        "5. COMPREHENSIVE EXPLANATION: Explain exactly why each correct option holds and the specific false premise behind each distractor.\n"
        "6. NO EM DASHES: Never use em dashes (—). Use clean, direct sentences.\n"
        "7. Output ONLY a valid JSON object matching the requested schema."
    )

    num_single = max(6, target_questions - 5)
    num_multi = max(4, target_questions - num_single)

    user_prompt = f"""Course: {course_name}
Module: {module_name}

Curated Lecture Topics & Content Summary:
\"\"\"
{topics_context[:10000]}
\"\"\"

EXAMINATION SPECIFICATION:
Create: "{set_title}"
Scope: {focus_desc}
Total Questions: {target_questions} questions (approximately {num_single} Single-Choice MCQs and {num_multi} Multiple-Correct MSQs).

Output ONLY a JSON object formatted as follows:
{{
  "title": "{set_title}",
  "test_type": "{set_type}",
  "description": "Rigorous conceptual assessment testing {module_name} fundamentals and analytical decision-making.",
  "total_questions": {target_questions},
  "questions": [
    {{
      "id": 1,
      "type": "single_choice",
      "difficulty": "Moderate",
      "key_concept": "Key Concept Name",
      "question": "Clear conceptual scenario or mechanism question...",
      "options": [
        "A) Plausible distractor representing a misconception",
        "B) Correct conceptual statement",
        "C) Plausible distractor representing an opposite effect",
        "D) Distractor confusing correlation with causation"
      ],
      "correct_indices": [1],
      "explanation": "Detailed step-by-step conceptual reasoning why B is correct and why A, C, and D are traps.",
      "trap_warning": "Common student gotcha or false intuition...",
      "distractor_analysis": "Why students mistakenly pick A or C."
    }},
    {{
      "id": {num_single + 1},
      "type": "multiple_choice",
      "difficulty": "Challenging",
      "key_concept": "Multi-Variable Concept Name",
      "question": "Which of the following statements regarding the mechanism are CONCEPTUALLY ACCURATE? [Select all that apply]",
      "options": [
        "A) First valid conceptual condition",
        "B) Subtle fallacy or violation of boundary assumption",
        "C) Second valid conceptual condition",
        "D) Third valid conceptual condition"
      ],
      "correct_indices": [0, 2, 3],
      "explanation": "In-depth breakdown proving options A, C, and D, and exposing the subtle trap in B.",
      "trap_warning": "Trap analysis for the multi-select question.",
      "distractor_analysis": "Explanation of the flawed premise in distractor B."
    }}
  ]
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    raw_response = call_llm(messages, temperature=0.15, max_tokens=3800)
    
    try:
        data = json_repair.loads(raw_response)
    except Exception as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        data = {}

    raw_questions = data.get("questions", [])
    if not isinstance(raw_questions, list) or len(raw_questions) == 0:
        logger.warning(f"No questions parsed from LLM response for {module_id} set {set_number}. Salvaging.")
        raw_questions = []

    clean_questions = []
    for idx, q in enumerate(raw_questions, start=1):
        if isinstance(q, dict):
            clean_questions.append(sanitize_question(q, idx))

    title = clean_text_formatting(data.get("title", set_title))
    description = clean_text_formatting(data.get("description", focus_desc))

    # Save to database
    save_module_test(
        module_id=module_id,
        set_number=set_number,
        title=title,
        test_type=set_type,
        questions=clean_questions
    )

    return {
        "id": f"{module_id}-set{set_number}",
        "module_id": module_id,
        "set_number": set_number,
        "title": title,
        "test_type": set_type,
        "description": description,
        "total_questions": len(clean_questions),
        "questions": clean_questions
    }

def generate_both_module_tests(
    module_id: str,
    force_regenerate: bool = False,
    questions_per_set: int = 14
) -> Dict[str, Any]:
    """Generates both Set 1 and Set 2 for a module and persists them in SQLite."""
    if not force_regenerate:
        existing = get_module_tests(module_id)
        if len(existing) >= 2:
            logger.info(f"Module {module_id} already has {len(existing)} test sets. Returning cached.")
            return {
                "module_id": module_id,
                "sets": existing,
                "cached": True
            }

    ctx = extract_module_context(module_id)
    course_name = ctx["course_name"]
    module_name = ctx["module_name"]
    topics_context = ctx["topics_context"]

    logger.info(f"Generating Set 1 for Module '{module_name}' ({module_id})...")
    set1 = generate_module_test_set(
        module_id=module_id,
        set_number=1,
        course_name=course_name,
        module_name=module_name,
        topics_context=topics_context,
        target_questions=questions_per_set
    )

    logger.info(f"Generating Set 2 for Module '{module_name}' ({module_id})...")
    set2 = generate_module_test_set(
        module_id=module_id,
        set_number=2,
        course_name=course_name,
        module_name=module_name,
        topics_context=topics_context,
        target_questions=questions_per_set
    )

    return {
        "module_id": module_id,
        "course_name": course_name,
        "module_name": module_name,
        "sets": [set1, set2],
        "cached": False
    }
