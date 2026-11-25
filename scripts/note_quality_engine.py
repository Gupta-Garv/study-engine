#!/usr/bin/env python3
"""
Closed-Loop Examiner-Grade Note Synthesis & Verification Engine (v4 — 95%+ Textbook Standard).

Architecture:
- Processes strictly ONE subject and ONE module at a time sequentially.
- Within a module, runs videos concurrently (max_workers=3, thread-safe under NIM 35 req/min cap),
  passing a lightweight module topic outline to eliminate cross-video recap bloat.
- Generator (Nemotron 30B Lightning) -> Dual-Layer Critic (Deterministic + Faculty Examiner LLM)
  -> Escalating Refiner (Nemotron 550B Ultra on Pass 2+) until >= 95% accuracy & 0 real flaws.
- Compiles a deduplicated, table/grid-heavy Module One-Shot section + exports study_data.js.
"""

import sys
import os
import re
import json
import time
import argparse
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import db
from core.llm_client import call_llm, _invoke_model, PRIMARY_MODEL, clean_text_formatting
import json_repair

STRONG_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
KATEX_JS = BASE_DIR / "scratch" / "katex.min.js"
REPORTS_DIR = BASE_DIR / "data" / "verification_reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def get_exam_blueprint(course_id: str) -> str:
    if course_id == "d9173426":  # Critical Thinking
        return """SUBJECT: Critical Thinking (IIMB BBA DBE)
EXAM PATTERN:
- Section A: 14 MCQs (1 mark each = 14 marks)
- Section B: 6 Short Conceptual Questions (2 marks each = 12 marks; target exam answers: ~20-30 words)
- Section C: 3 Case-Based Sets (8 questions x 3 marks = 24 marks; target exam answers: ~40-50 words)
- No negative marking. 72% OF MARKS ARE FRAMEWORK & CASE-APPLICATION QUESTIONS!

EDITORIAL & CONTENT STANDARDS:
- Focus on Frameworks, Cognitive Mechanisms, Argument Evaluation Tools, and Named Case Applications taught in THIS video.
- Faculty ask case-diagnostic questions ("Using this framework, what reasoning flaw occurred and how should a critical thinker fix it?").
- Clearly separate corporate PR/damage-control workarounds from true critical thinking or analytical principles (never label a concealment tactic or workaround as a "recommended analytical fix").
- Adapt structure naturally: Comparison Tables for contrasts, 2x2 Grids for quadrants, numbered steps for methods, tight bullets for concepts.
- For short recap videos (<350 transcript words), write a crisp 55-115 word synthesis focusing on how concepts connect."""

    elif course_id == "deb83564":  # Data Visualisation
        return """SUBJECT: Data Visualisation and Storytelling Using Data (IIMB BBA DBE)
EXAM PATTERN:
- Section A: 14 MCQs (1 mark each = 14 marks)
- Section B: 8 MSQs - Multiple-Select Questions (2 marks each = 16 marks = 53.3% of total marks; negative marking per wrong checkbox!)
- No calculator. Duration: 60 mins.

EDITORIAL & CONTENT STANDARDS:
- Isolate multi-condition design rules, exact thresholds (e.g., pie <4 slices vs bar), and "True Condition vs. Common Misconception" boundaries so MSQs are unambiguous.
- For conceptual/design modules (M1-M2): Use Comparison Tables / Chart Selection Matrices (business question -> best chart -> why, stakeholder vs. user, cognitive load, colorblindness, Gestalt rules). Do NOT expect Power BI/DAX steps in M1-M2 unless taught in that video.
- For Power BI modules (M3-M4): Skip verbose UI mouse-click narration. Extract ONLY the exact DAX measure formula/syntax, data modeling/filter-context rules, visual design rationale, and implementation pitfalls."""

    elif course_id == "2989cdfe":  # Corporate Finance
        return """SUBJECT: Corporate Finance (IIMB BBA DBE)
EXAM PATTERN:
- Section A ONLY: 50 MCQs x 1.5 marks = 75 marks (120 mins). No negative marking.
- Scientific Calculator ALLOWED. Soft copy of the Formula Sheet IS PROVIDED in the exam!

EDITORIAL & CONTENT STANDARDS (MATH-FRIENDLY & BOOK-ACCURATE):
- Because the formula sheet is provided, the student needs FORMULA RECOGNITION, INTERPRETATION, AND STEP-BY-STEP SOLVING—not blind memorization.
- Explain clearly where math-averse students get confused, without writing baby-talk.
- STRICT FORMULA FIDELITY: Use the EXACT equation and variable symbols taught in THIS video transcript. Render math cleanly like a textbook using valid KaTeX (`$...$` inline, `$$...$$` display).
- For quantitative lectures, organize around:
  1. **Formula & Variable Legend** (exact textbook KaTeX + units/periodicity).
  2. **When to Use It (Question Triggers)** (exact exam wording clues pointing to this formula and how to extract inputs).
  3. **Step-by-Step Solving Guide & Worked Example** (walk through the professor's calculation + scientific calculator traps).
- For conceptual lectures, omit math sections and use comparison tables / directional arrows (`↑`, `↓`, `→`)."""

    return "General University Exam Preparation."


def check_katex_expressions(markdown_text: str) -> List[str]:
    """Validates all KaTeX expressions via Node KaTeX 0.16.8."""
    errors = []
    if any(ch in markdown_text for ch in ["\x08", "\x0c", "\r"]):
        errors.append("Corrupted control character (\\x08/\\x0c/\\r) detected.")
    if re.search(r"(?<![\\A-Za-z])ightarrow", markdown_text) or "\\\\frac" in markdown_text or "\\\\text" in markdown_text:
        errors.append("Broken or double-escaped LaTeX command (e.g., ightarrow or \\\\frac).")

    exprs = []
    for m in re.finditer(r"\$\$(.+?)\$\$", markdown_text, re.DOTALL):
        exprs.append(m.group(1).strip())
    stripped = re.sub(r"\$\$.+?\$\$", " ", markdown_text, flags=re.DOTALL)
    for m in re.finditer(r"(?<!\$)\$(?!\s*\d[\d,\.]*(?:\s*(?:million|billion|thousand|crore|lakh|k|m|b|%|\)|,|;|\.|\s|$)))([^\$\n]{1,180}?)\$(?!\d)", stripped):
        cand = m.group(1).strip()
        if any(tok in cand for tok in ["\\", "^", "_", "=", "+", "-", "/", "*", ">", "<"]) or re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", cand):
            exprs.append(cand)

    if not exprs or not KATEX_JS.exists():
        return errors

    node_script = """
    const fs = require('fs');
    const katex = require(process.argv[1]);
    const exprs = JSON.parse(fs.readFileSync(0, 'utf8'));
    const errs = [];
    for (const e of exprs) {
        try {
            katex.renderToString(e, { throwOnError: true, strict: false });
        } catch (err) {
            errs.push(`KaTeX syntax error in [${e}]: ${err.message}`);
        }
    }
    console.log(JSON.stringify(errs));
    """
    try:
        proc = subprocess.run(
            ["node", "-e", node_script, str(KATEX_JS)],
            input=json.dumps(exprs),
            capture_output=True,
            text=True,
            timeout=10
        )
        if proc.returncode == 0 and proc.stdout.strip():
            errors.extend(json.loads(proc.stdout.strip()))
    except Exception as e:
        errors.append(f"KaTeX validator exception: {e}")

    return errors


def get_max_allowed_words(t_words: int) -> int:
    if t_words <= 0:
        return 140
    if t_words < 350:
        return min(230, max(125, int(t_words * 0.72)))
    return min(680, max(190, int(t_words * 0.52)))


def deterministic_audit(topic_title: str, notes_md: str, transcript_text: str, course_id: str) -> List[str]:
    """Strict deterministic quality & polish checks."""
    issues = []
    t_words = len((transcript_text or "").split())
    n_words = len((notes_md or "").split())

    if not notes_md or n_words < 30:
        issues.append("Notes are empty or too short (< 30 words).")
        return issues

    max_allowed = get_max_allowed_words(t_words)
    if t_words > 0 and n_words > max_allowed:
        issues.append(f"Notes too lengthy ({n_words} words vs {t_words} transcript words; max <= {max_allowed}).")
    if t_words >= 750 and n_words < 75:
        issues.append(f"Notes appear under-covered ({n_words} words for a {t_words}-word lecture).")

    lines = [l.strip() for l in notes_md.splitlines() if l.strip()]
    first_line = lines[0] if lines else ""
    if not first_line.startswith("# "):
        issues.append("Notes must start cleanly with `# Title` on line 1.")
    if first_line.lower() in ["# video", "# lecture", "# topic"]:
        issues.append("Generic `# Video` header found; must use specific conceptual title.")
    if topic_title.lower().strip() in ["video", "lecture", "topic"]:
        issues.append("Topic title is generic `Video`; must use specific conceptual title.")

    banned_patterns = [
        (r"\(transcript[- ]?(?:sourced|labeled|closing|derived|based)\)", "AI meta-label '(Transcript-...)' found"),
        (r"word\s*count\s*[:\-]", "Printed 'Word count:' artifact inside notes"),
        (r"\((?:20[-–]30|40[-–]50|20|30)\s*words?\)", "Printed '(20-30 words)' prompt label inside notes"),
        (r"\(exam[- ]?ready\)", "Printed '(Exam-Ready)' meta-label inside notes"),
        (r"diagnostic anchor", "Robotic 'Diagnostic Anchor' label; use natural heading like 'Exam Takeaway'"),
        (r"core mechanics", "Generic boilerplate heading 'Core Mechanics'"),
        (r"no mathematical formulas", "Negative boilerplate 'no mathematical formulas'"),
        (r"</|<<|>>|<<<|>>>|\bEND_NOTES\b|\bEND_TITLE\b", "Stray HTML/delimiter bracket artifact (</, <<, >>>)"),
    ]
    low_md = notes_md.lower()
    for pat, msg in banned_patterns:
        if re.search(pat, low_md):
            issues.append(msg)

    if "—" in notes_md:
        issues.append("Contains forbidden em dash ('—').")

    last_line = lines[-1] if lines else ""
    if last_line in ["<", "</", "<<", "```", "---"]:
        issues.append(f"Trailing incomplete line/tag at end of notes: '{last_line}'")

    issues.extend(check_katex_expressions(notes_md))
    return issues


def parse_pure_markdown_note(raw: str, fallback_title: str) -> Tuple[str, str]:
    """Cleans pure Markdown response and extracts title directly from # H1."""
    text = raw.strip()
    text = re.sub(r"^```(?:markdown|md)?\s*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?```\s*$", "", text).strip()
    text = re.sub(r"<+\s*/?(?:TITLE|END_TITLE|NOTES|END_NOTES)\s*>+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\s*</\s*$", "", text).strip()
    text = re.sub(r"\s*—\s*", ", ", text).replace("—", ", ").replace("–", "-")
    text = re.sub(r"\bDiagnostic\s+Anchors?\b", "Exam Takeaways", text, flags=re.IGNORECASE)
    text = re.sub(r"\bExam\s+Exam\s+Takeaways?\b", "Exam Takeaways", text, flags=re.IGNORECASE)
    text = re.sub(r"\bCore\s+Mechanics\b", "Key Mechanics", text, flags=re.IGNORECASE)

    m_h1 = re.search(r"^#\s+([^\n]+)", text, re.MULTILINE)
    if m_h1:
        title = clean_text_formatting(m_h1.group(1).strip())
        if title.lower() in ["video", "lecture", "topic"]:
            title = fallback_title if fallback_title.lower() != "video" else "Core Conceptual Framework"
            text = re.sub(r"^#\s+[^\n]+", f"# {title}", text, count=1, flags=re.MULTILINE)
    else:
        title = fallback_title if fallback_title.lower() != "video" else "Core Conceptual Framework"
        text = f"# {title}\n\n{text}"

    return title, text.strip()


def generate_topic_note(
    course_id: str,
    module_name: str,
    raw_title: str,
    transcript_text: str,
    module_roadmap_hint: str
) -> Tuple[str, str]:
    """Generates finished, publication-grade Markdown notes strictly within word budget."""
    t_words = len((transcript_text or "").split())
    max_words = get_max_allowed_words(t_words)
    if t_words < 350:
        target_range = f"55–{max_words - 10} words (compact synthesis)"
    elif t_words < 750:
        target_range = f"115–{min(200, max_words - 20)} words"
    elif t_words < 1400:
        target_range = f"170–{min(270, max_words - 30)} words"
    else:
        target_range = f"220–{min(340, max_words - 40)} words"

    blueprint = get_exam_blueprint(course_id)

    prompt = f"""You are a senior IIM professor writing FINISHED, PUBLICATION-GRADE university revision notes for ONE lecture.

{blueprint}

MODULE: {module_name}
RAW LECTURE LABEL: {raw_title}
OTHER LECTURES IN THIS MODULE (for context on scope—focus strictly on what THIS transcript teaches):
{module_roadmap_hint}

TRANSCRIPT LENGTH: {t_words} words
TARGET NOTE LENGTH: {target_range}
STRICT HARD LIMIT: MUST BE <= {max_words} WORDS TOTAL! (Every word above {max_words} triggers automatic rejection.)

QUALITY & FINISHING LAWS:
1. **Finished Textbook Polish (Zero AI Draft Artifacts):**
   - Read smoothly from start to finish. Use crisp prose, tables, or tight bullets—never padded fluff.
   - NEVER output robotic labels like `(Transcript-Sourced)`, `(Transcript Closing)`, `(20-30 words)`, `(Exam-Ready)`, `Diagnostic Anchor`, `Word count:`, `Core Mechanics`, or stray tags (`</`, `<<<`).
   - Use natural headings (e.g., `## Core Framework`, `## Case Study: Target's Pregnancy Model`, `## Exam Takeaway`).
2. **Strict Grounding (No Cross-Video Contamination):**
   - Use ONLY concepts, researchers, companies, case studies, numbers, and formulas actually spoken in THIS transcript.
   - Distinguish corporate damage-control tactics from true critical thinking / analytical solutions.
3. **Adaptive Visual Structure:**
   - Start with `# <Specific Descriptive Title>` and `> **Core Takeaway:** <1-2 crisp sentences>`.
   - Use Markdown tables for contrasts, 2x2 grids for quadrants, numbered steps for workflows/solving, and crisp bullets. Never duplicate table contents in bullets. Zero em dashes (`—`).

ORIGINAL LECTURE TRANSCRIPT:
{transcript_text[:38000]}

Output ONLY the finished Markdown starting directly with `# <Specific Descriptive Title>` on line 1 (<= {max_words} words!)."""

    tok_budget = min(1300, max(380, int(max_words * 2.3)))
    raw_resp = call_llm([{"role": "user", "content": prompt}], temperature=0.12, max_tokens=tok_budget)
    return parse_pure_markdown_note(raw_resp, raw_title)


def critic_evaluate_note(
    course_id: str,
    module_name: str,
    title: str,
    notes_md: str,
    transcript_text: str
) -> Dict[str, Any]:
    """Strict 100-point Examiner & Editorial Polish Critic (fair, high bar, zero pedantic nitpicking)."""
    hard_issues = deterministic_audit(title, notes_md, transcript_text, course_id)
    blueprint = get_exam_blueprint(course_id)
    t_words = len((transcript_text or '').split())
    n_words = len((notes_md or '').split())
    max_words = get_max_allowed_words(t_words)

    critic_prompt = f"""You are a senior IIM Faculty Examiner & Academic Textbook Editor auditing study notes against the ORIGINAL transcript.

{blueprint}

TITLE: {title}
MODULE: {module_name}
TRANSCRIPT WORDS: {t_words} | NOTE WORDS: {n_words} (Max allowed: {max_words})

ORIGINAL TRANSCRIPT:
{transcript_text[:38000]}

NOTES TO AUDIT:
{notes_md}

AUDIT RUBRIC (100 points total):
1. **fidelity (0–30):** Are all concepts, frameworks, case facts, researchers, numbers, and formulas accurate to THIS transcript? Deduct heavily if anything is hallucinated from outside the transcript, directionally inverted, or logically mislabeled (e.g., calling a PR cover-up a "recommended critical thinking fix").
2. **framework_case_depth (0–30):** Does it preserve the substantive frameworks, mechanisms, and key lecture case analogies needed to answer faculty application questions?
3. **editorial_finish (0–25):** Does it read like finished, cohesive, publication-grade notes? Deduct heavily for awkward fragmented sections, abrupt/tacked-on closing lines, redundant bullets, or robotic meta-labels.
4. **conciseness_and_fit (0–15):** Is it <= {max_words} words, compact on recaps, cleanly formatted (tables/grids where contrasts exist), and fitted to the exam pattern?

IMPORTANT CALIBRATION RULES:
- **DO NOT nitpick** valid concise paraphrasing (e.g., "pregnancy prediction score" vs "assigned a pregnancy prediction score" is 100% fine!) or minor conversational filler/jokes.
- **DO NOT expect practice MCQs** or word-count labels inside study notes.
- If the notes are factually faithful, capture all core frameworks/cases clearly, read cleanly like finished study notes with zero robotic meta-labels, and stay <= {max_words} words with zero hallucinations, you MUST score them **95–100** (e.g., 29 + 29 + 24 + 14 = 96) with `"issues": []`!

Return ONLY valid JSON:
{{
  "fidelity": <int 0-30>,
  "framework_case_depth": <int 0-30>,
  "editorial_finish": <int 0-25>,
  "conciseness_and_fit": <int 0-15>,
  "has_hallucination_or_inversion": <true or false>,
  "total_score": <int 0-100>,
  "issues": ["list ONLY genuine factual errors, missing core frameworks/cases, mislabeled lessons, awkward unfinished prose, or word bloat"],
  "fix_instructions": "Concise editorial instructions if total_score < 95, else empty string."
}}"""

    raw = call_llm([{"role": "user", "content": critic_prompt}], temperature=0.1, max_tokens=900)
    try:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        parsed = json_repair.loads(m.group(0) if m else raw)
        if not isinstance(parsed, dict):
            parsed = {}
    except Exception:
        parsed = {}

    sub_keys = ["fidelity", "framework_case_depth", "editorial_finish", "conciseness_and_fit"]
    if all(isinstance(parsed.get(k), (int, float)) for k in sub_keys):
        llm_score = int(sum(parsed[k] for k in sub_keys))
    else:
        llm_score = int(parsed.get("total_score", 0) or 0)

    llm_issues = parsed.get("issues", [])
    if not isinstance(llm_issues, list):
        llm_issues = [str(llm_issues)] if llm_issues else []

    has_hallucination = bool(parsed.get("has_hallucination_or_inversion", False))
    for iss in llm_issues:
        low = str(iss).lower()
        if any(flag in low for flag in ["not in the transcript", "not in transcript", "hallucination", "inverted", "reversed relative to", "fabricat", "mislabel"]):
            has_hallucination = True

    penalty = 0
    if hard_issues:
        penalty = min(40, 15 * len(hard_issues))
    if has_hallucination:
        penalty = max(penalty, 20)

    final_score = max(0, llm_score - penalty)
    all_issues = hard_issues + [i for i in llm_issues if i]
    passed = (final_score >= 95) and (len(hard_issues) == 0) and (not has_hallucination)

    return {
        "llm_score": llm_score,
        "final_score": final_score,
        "breakdown": {k: parsed.get(k, 0) for k in sub_keys},
        "has_hallucination": has_hallucination,
        "hard_issues": hard_issues,
        "llm_issues": llm_issues,
        "all_issues": all_issues,
        "fix_instructions": parsed.get("fix_instructions", ""),
        "passed": passed,
    }


def compress_note_to_budget(current_title: str, current_notes: str, max_words: int) -> Tuple[str, str]:
    """Aggressive editorial compression pass until strictly <= max_words."""
    cur_t, cur_n = current_title, current_notes
    for attempt_idx, ratio in enumerate((0.70, 0.52, 0.36)):
        n_words = len(cur_n.split())
        if n_words <= max_words:
            break
        target_w = max(60, int(max_words * ratio))
        excess = max(25, n_words - target_w)
        prompt = f"""You are a ruthless textbook copy-editor. REWRITE these study notes so the entire output is strictly UNDER {max_words} words (target ~{target_w} words). Do NOT copy verbatim—you MUST delete at least {excess} words (note: every whitespace-separated token including `|` table pipes counts toward the limit).

HOW TO CUT AT LEAST {excess} WORDS:
- Replace full prose paragraphs with terse 1-line bullet phrases (6-12 words each).
- Convert verbose tables into tight bullet lines (or a tiny 3-row table without spaces around `|`).
- Keep ALL core frameworks, formulas, rules, and 1 concise reference case/takeaway.
- Keep clean finished Markdown starting with `# {cur_t}` (no meta-labels, no em dashes).

SOURCE DRAFT ({n_words} words -> MUST BE <= {max_words} words):
{cur_n}

Output ONLY the rewritten concise Markdown starting with `# {cur_t}`."""
        tok_budget = min(1200, max(300, int(max_words * 1.9)))
        try:
            raw = _invoke_model(STRONG_MODEL, [{"role": "user", "content": prompt}], temperature=0.25 + 0.1 * attempt_idx, max_tokens=tok_budget, timeout=45.0)
        except Exception:
            raw = call_llm([{"role": "user", "content": prompt}], temperature=0.25, max_tokens=tok_budget)
        cand_t, cand_n = parse_pure_markdown_note(raw, cur_t)
        if len(cand_n.split()) < len(cur_n.split()):
            cur_t, cur_n = cand_t, cand_n
    return cur_t, cur_n


def refine_topic_note(
    course_id: str,
    module_name: str,
    current_title: str,
    current_notes: str,
    transcript_text: str,
    audit_result: Dict[str, Any],
    use_strong_model: bool = True
) -> Tuple[str, str]:
    """Fixes every flagged issue using 550B Ultra model and enforces finished textbook quality + length ceiling."""
    blueprint = get_exam_blueprint(course_id)
    t_words = len((transcript_text or "").split())
    n_words = len((current_notes or "").split())
    max_words = get_max_allowed_words(t_words)

    # If the ONLY issue is word length, run pure copy-edit compression instead of regenerating from transcript
    if len(audit_result.get("hard_issues", [])) == 1 and "Notes too lengthy" in audit_result["hard_issues"][0] and not audit_result.get("llm_issues"):
        return compress_note_to_budget(current_title, current_notes, max_words)

    target_w = min(310, max(75, int(max_words * 0.78)))
    issues_txt = "\n".join(f"- {iss}" for iss in audit_result["all_issues"])
    trim_msg = (
        f"\nCRITICAL LENGTH OVERFLOW: Current draft has {n_words} words! You MUST DELETE/COMPRESS at least {n_words - target_w} words so the output is strictly <= {max_words} words (aim for ~{target_w} words) while keeping the key frameworks and cases."
        if n_words > max_words else ""
    )

    prompt = f"""You are a senior academic editor polishing study notes from {audit_result['final_score']}/100 to **98/100 FINISHED TEXTBOOK QUALITY**.

{blueprint}

MODULE: {module_name}
CURRENT TITLE: {current_title}
TRANSCRIPT WORDS: {t_words}
CURRENT DRAFT WORDS: {n_words}
TARGET FINAL LENGTH: ~{target_w} words (ABSOLUTE HARD CEILING: <= {max_words} words — DO NOT EXPAND!){trim_msg}

ISSUES TO FIX:
{issues_txt}
EDITORIAL GUIDANCE: {audit_result.get('fix_instructions', '')}

CURRENT DRAFT:
{current_notes}

ORIGINAL TRANSCRIPT (ONLY SOURCE OF FACTS):
{transcript_text[:38000]}

STRICT RULES FOR FINAL POLISHED NOTES:
- Fix EVERY flagged gap, hallucination, inversion, or logical mislabeling strictly from THIS transcript.
- Make the whole note read seamlessly like finished, authoritative exam notes—NO awkward tacked-on closing sentences, NO robotic labels (`(Transcript-Sourced)`, `(20-30 words)`, `Diagnostic Anchor`, `Word count:`, `Core Mechanics`), NO stray tags (`</`, `<<<`), NO em dashes (`—`).
- STAY STRICTLY <= {max_words} WORDS! Keep every section tight and dense.

Output ONLY the final finished Markdown starting directly with `# <Specific Descriptive Title>` on line 1."""

    tok_budget = min(1300, max(380, int(max_words * 2.3)))
    msgs = [{"role": "user", "content": prompt}]
    if use_strong_model:
        try:
            raw_resp = _invoke_model(STRONG_MODEL, msgs, temperature=0.1, max_tokens=tok_budget, timeout=60.0)
        except Exception:
            raw_resp = call_llm(msgs, temperature=0.1, max_tokens=tok_budget)
    else:
        raw_resp = call_llm(msgs, temperature=0.1, max_tokens=tok_budget)

    return parse_pure_markdown_note(raw_resp, current_title)


def compile_module_oneshot(course_id: str, mod_num: int, mod_name: str, curated_topics: List[Dict[str, str]]) -> str:
    """Synthesizes a polished, deduplicated, table/grid-first Master One-Shot section using STRONG_MODEL."""
    blueprint = get_exam_blueprint(course_id)

    topics_blob = []
    for i, t in enumerate(curated_topics, 1):
        topics_blob.append(f"### Lecture {i}: {t['title']}\n{t['notes']}")
    combined_input = "\n\n---\n\n".join(topics_blob)

    prompt = f"""You are compiling a polished **Master One-Shot Revision Section** for ONE entire module from its verified lecture notes.

{blueprint}

MODULE: {mod_name} (Module {mod_num})

GOAL:
A student revising 1–2 hours before the exam should scan this entire module in **3 to 5 minutes** and feel 100% confident with finished, crystal-clear tables, grids, frameworks, case diagnostics, and exam traps.

RULES:
1. **Merge & Deduplicate:** Unify overlapping concepts from different videos into cohesive sections.
2. **Table & Grid First:** Clean Markdown Tables for differentiations and Grids for taxonomies. Keep named case studies tight (`Case -> Error/Mechanism -> Principle`).
3. **Finished Editorial Standard:** Zero AI meta-labels (`Transcript-Sourced`, `20-30 words`, `Diagnostic Anchor`, `Word count:`), zero em dashes (`—`), zero stray tags (`</`, `<<<`).
4. **Header Format:** Start with:
<a id="module-{mod_num}"></a>
## {mod_name}

followed by `> **Cram Focus:** ...`, clean numbered subsections (`### 1. ...`), and end with `### Exam Trap Radar`.
5. **Length:** 650–1,200 words total for the module One-Shot.

VERIFIED MODULE LECTURE NOTES:
{combined_input[:28000]}

Return ONLY pure Markdown starting directly with `<a id="module-{mod_num}"></a>`."""

    try:
        raw = _invoke_model(STRONG_MODEL, [{"role": "user", "content": prompt}], temperature=0.12, max_tokens=2400, timeout=60.0)
    except Exception:
        raw = call_llm([{"role": "user", "content": prompt}], temperature=0.12, max_tokens=2400)

    md = raw.strip()
    md = re.sub(r"^```(?:markdown|md)?\s*\n?", "", md, flags=re.IGNORECASE)
    md = re.sub(r"\n?```\s*$", "", md).strip()
    md = re.sub(r"`(<a\s+id=[\"']module-\d+[\"']>\s*</a>)`", r"\1", md)
    md = re.sub(r"\s*—\s*", ", ", md).replace("—", ", ").replace("–", "-")
    if f'<a id="module-{mod_num}"></a>' not in md:
        md = f'<a id="module-{mod_num}"></a>\n{md}'
    return md.strip()


def rebuild_course_header(course_id: str, course_name: str, body_md: str) -> str:
    conn = db.get_conn()
    mods = conn.execute(
        """
        SELECT m.id, m.number, m.name, COUNT(t.id) as cnt
        FROM modules m
        LEFT JOIN topics t ON t.module_id = m.id
        WHERE m.course_id = ?
        GROUP BY m.id
        HAVING cnt > 0
        ORDER BY m.number ASC
        """,
        (course_id,)
    ).fetchall()

    nav_lines = ["## Quick Module Navigation\n"]
    for m in mods:
        m_low = m["name"].lower()
        if "module 0" in m_low or "welcome" in m_low or "mid-term" in m_low or "live session" in m_low:
            continue
        if course_id == "2989cdfe" and m["id"] == "2989cdfe-m5":
            continue
        nav_lines.append(f"- [{m['name']}](#module-{m['number']})")

    header = (
        f"# {course_name}: High-Yield Exam Revision Hub\n\n"
        "> **Master Revision Guide:** Built for rapid exam cramming—frameworks, comparison matrices, case diagnostics, and formula triggers distilled directly from course lectures.\n\n"
        "---\n\n"
        + "\n".join(nav_lines)
        + "\n\n---\n\n"
    )

    first_mod_idx = body_md.find('<a id="module-')
    if first_mod_idx != -1:
        body_md = body_md[first_mod_idx:]
    return header + body_md


def update_course_oneshot_module(course_id: str, course_name: str, mod_num: int, new_mod_section: str):
    conn = db.get_conn()
    row = conn.execute(
        "SELECT one_shot_markdown, formula_sheet_markdown FROM course_one_shots WHERE course_id = ?",
        (course_id,)
    ).fetchone()
    existing_md = row["one_shot_markdown"] if row else ""
    formula_md = row["formula_sheet_markdown"] if row else ""

    anchor = f'<a id="module-{mod_num}"></a>'
    if anchor in existing_md:
        start_idx = existing_md.find(anchor)
        m_next = re.search(r'<a id="module-\d+"></a>', existing_md[start_idx + len(anchor):])
        if m_next:
            end_idx = start_idx + len(anchor) + m_next.start()
            updated_body = existing_md[:start_idx] + new_mod_section + "\n\n---\n\n" + existing_md[end_idx:]
        else:
            updated_body = existing_md[:start_idx] + new_mod_section + "\n"
    else:
        updated_body = (existing_md.rstrip() + "\n\n---\n\n" + new_mod_section + "\n") if existing_md else new_mod_section + "\n"

    final_md = rebuild_course_header(course_id, course_name, updated_body)
    db.save_course_one_shot(course_id, final_md, formula_md)


def _process_single_video(
    idx: int,
    total: int,
    t: Dict[str, Any],
    course_id: str,
    mod_name: str,
    roadmap_hint: str,
    min_score: int,
    max_iters: int
) -> Dict[str, Any]:
    tid = t["id"]
    raw_title = t["title"]
    transcript = (t["transcript_text"] or "").strip()
    t_words = len(transcript.split())

    if t_words < 30:
        return {"skipped": True, "idx": idx, "topic_id": tid, "title": raw_title}

    best_title, best_notes = generate_topic_note(course_id, mod_name, raw_title, transcript, roadmap_hint)
    best_audit = critic_evaluate_note(course_id, mod_name, best_title, best_notes, transcript)
    init_score = best_audit["final_score"]
    print(f"[{idx}/{total}] [{tid}] Pass 1: {init_score}/100 (Passed={best_audit['passed']}, Words={len(best_notes.split())}) Title='{best_title}'")

    attempt = 1
    while not best_audit["passed"] and attempt < max_iters:
        attempt += 1
        use_strong = (attempt >= 2)
        print(f"   🔧 [{idx}/{total}] [{tid}] Refining (Attempt {attempt}/{max_iters}, Strong={use_strong}) Issues={best_audit['all_issues'][:2]}")
        cand_title, cand_notes = refine_topic_note(
            course_id, mod_name, best_title, best_notes, transcript, best_audit, use_strong_model=use_strong
        )
        cand_audit = critic_evaluate_note(course_id, mod_name, cand_title, cand_notes, transcript)
        print(f"   🔍 [{idx}/{total}] [{tid}] Pass {attempt}: {cand_audit['final_score']}/100 (Passed={cand_audit['passed']}, Words={len(cand_notes.split())})")

        max_w_v = get_max_allowed_words(t_words)
        shorter_progress = len(cand_notes.split()) < len(best_notes.split()) and len(best_notes.split()) > max_w_v
        if (cand_audit["final_score"] >= best_audit["final_score"]) or (len(cand_audit["hard_issues"]) < len(best_audit["hard_issues"])) or shorter_progress:
            best_title, best_notes, best_audit = cand_title, cand_notes, cand_audit

    return {
        "skipped": False,
        "idx": idx,
        "topic_id": tid,
        "old_title": raw_title,
        "new_title": best_title,
        "notes": best_notes,
        "transcript_words": t_words,
        "note_words": len(best_notes.split()),
        "initial_score": init_score,
        "final_score": best_audit["final_score"],
        "attempts": attempt,
        "passed": best_audit["passed"],
        "has_hallucination": best_audit["has_hallucination"],
        "final_issues": best_audit["all_issues"],
        "breakdown": best_audit["breakdown"]
    }


def process_module(course_id: str, module_id: str, min_score: int = 95, max_iters: int = 4, workers: int = 3):
    conn = db.get_conn()
    course = conn.execute("SELECT id, name FROM courses WHERE id = ?", (course_id,)).fetchone()
    mod = conn.execute("SELECT id, number, name FROM modules WHERE id = ?", (module_id,)).fetchone()
    if not course or not mod:
        raise ValueError(f"Invalid course_id={course_id} or module_id={module_id}")

    topics = [dict(r) for r in conn.execute(
        "SELECT id, title, transcript_text FROM topics WHERE module_id = ? ORDER BY rowid ASC",
        (module_id,)
    ).fetchall()]

    # Build lightweight module roadmap hint from topic openings so recaps stay ultra-concise
    roadmap_lines = []
    for i, t in enumerate(topics, 1):
        first_sent = (t["transcript_text"] or "")[:140].replace("\n", " ").strip()
        roadmap_lines.append(f"{i}. {t['title']}: {first_sent}...")
    roadmap_hint = "\n".join(roadmap_lines)

    print(f"\n==================================================================")
    print(f"📘 COURSE: {course['name']} | MODULE {mod['number']}: {mod['name']} ({len(topics)} videos) | GATE >= {min_score}%")
    print(f"==================================================================")

    results_by_idx = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {
            ex.submit(_process_single_video, idx, len(topics), t, course_id, mod["name"], roadmap_hint, min_score, max_iters): idx
            for idx, t in enumerate(topics, 1)
        }
        for fut in as_completed(futures):
            res = fut.result()
            results_by_idx[res["idx"]] = res

    ordered = [results_by_idx[i] for i in sorted(results_by_idx.keys()) if not results_by_idx[i]["skipped"]]

    for r in ordered:
        with conn:
            conn.execute(
                "UPDATE topics SET title = ?, notes_markdown = ?, status = 'completed', error_message = '' WHERE id = ?",
                (r["new_title"], r["notes"], r["topic_id"])
            )

    avg_score = round(sum(r["final_score"] for r in ordered) / max(1, len(ordered)), 1)
    pass_count = sum(1 for r in ordered if r["passed"])

    # Targeted recovery pass if any topics failed or module avg < min_score
    if avg_score < min_score:
        print(f"\n⚠️ Module avg {avg_score}% < {min_score}%. Running targeted recovery on {len(ordered) - pass_count} failing topic(s)...")
        for r in ordered:
            if not r["passed"]:
                t_orig = next((x for x in topics if x["id"] == r["topic_id"]), None)
                if not t_orig:
                    continue
                t_txt = (t_orig["transcript_text"] or "").strip()
                t_max = get_max_allowed_words(len(t_txt.split()))
                cur_n = r["notes"]
                cur_t = r["new_title"]
                for extra_try in range(2):
                    if len(cur_n.split()) > t_max:
                        cur_t, cur_n = compress_note_to_budget(cur_t, cur_n, t_max)
                    else:
                        aud_cur = critic_evaluate_note(course_id, mod["name"], cur_t, cur_n, t_txt)
                        cur_t, cur_n = refine_topic_note(course_id, mod["name"], cur_t, cur_n, t_txt, aud_cur, use_strong_model=True)
                    aud_new = critic_evaluate_note(course_id, mod["name"], cur_t, cur_n, t_txt)
                    print(f"   🩹 Recovery [{r['topic_id']}] try {extra_try+1}: {aud_new['final_score']}/100 (Words={len(cur_n.split())}/{t_max})")
                    shorter_rec = len(cur_n.split()) < len(r["notes"].split()) and len(r["notes"].split()) > t_max
                    if aud_new["final_score"] >= r["final_score"] or len(aud_new["hard_issues"]) < len(r["final_issues"]) or shorter_rec:
                        r["new_title"] = cur_t
                        r["notes"] = cur_n
                        r["note_words"] = len(cur_n.split())
                        r["final_score"] = aud_new["final_score"]
                        r["passed"] = aud_new["passed"]
                        r["final_issues"] = aud_new["all_issues"]
                    if r["passed"]:
                        break
                with conn:
                    conn.execute(
                        "UPDATE topics SET title = ?, notes_markdown = ?, status = 'completed', error_message = '' WHERE id = ?",
                        (r["new_title"], r["notes"], r["topic_id"])
                    )
        avg_score = round(sum(r["final_score"] for r in ordered) / max(1, len(ordered)), 1)
        pass_count = sum(1 for r in ordered if r["passed"])

    curated_for_oneshot = [{"id": r["topic_id"], "title": r["new_title"], "notes": r["notes"]} for r in ordered]
    mod_low = mod["name"].lower()
    if "live session" in mod_low or "module 0" in mod_low or "welcome" in mod_low:
        mod_oneshot_md = ""
        os_katex_errs = []
    else:
        print(f"\n🧩 Compiling Master Module {mod['number']} One-Shot Section...")
        mod_oneshot_md = compile_module_oneshot(course_id, mod["number"], mod["name"], curated_for_oneshot)
        os_katex_errs = check_katex_expressions(mod_oneshot_md)
        if os_katex_errs:
            print(f"   ⚠️ One-Shot KaTeX issues detected: {os_katex_errs}")
        update_course_oneshot_module(course_id, course["name"], mod["number"], mod_oneshot_md)

    print("📦 Exporting static bundle to study_data.js...")
    db.export_static_data()

    report_topics = [{k: v for k, v in r.items() if k != "notes"} for r in ordered]
    report = {
        "course_id": course_id,
        "course_name": course["name"],
        "module_id": module_id,
        "module_number": mod["number"],
        "module_name": mod["name"],
        "videos_processed": len(ordered),
        "videos_passed_gate": pass_count,
        "min_score_target": min_score,
        "module_avg_accuracy": avg_score,
        "module_gate_passed": avg_score >= min_score,
        "oneshot_words": len(mod_oneshot_md.split()),
        "oneshot_katex_errors": os_katex_errs,
        "topics": report_topics
    }
    rep_path = REPORTS_DIR / f"{module_id}.json"
    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n==================================================================")
    print(f"✅ MODULE COMPLETE: {mod['name']}")
    print(f"   Avg Accuracy Score: {avg_score}% (Gate >= {min_score}%: {'PASS' if avg_score >= min_score else 'FAIL'})")
    print(f"   Videos Passing >= {min_score}%: {pass_count}/{len(ordered)}")
    print(f"   Module One-Shot Length: {len(mod_oneshot_md.split())} words")
    print(f"   Verification Report: {rep_path}")
    print(f"==================================================================")
    return report


def recover_module(course_id: str, module_id: str, min_score: int = 95, max_iters: int = 3):
    """Recovers ONLY failing/unpassed topics from a prior verification report, then updates One-Shot and report."""
    conn = db.get_conn()
    course = conn.execute("SELECT id, name FROM courses WHERE id = ?", (course_id,)).fetchone()
    mod = conn.execute("SELECT id, number, name FROM modules WHERE id = ?", (module_id,)).fetchone()
    if not course or not mod:
        raise ValueError(f"Invalid course_id={course_id} or module_id={module_id}")

    rep_path = REPORTS_DIR / f"{module_id}.json"
    if not rep_path.exists():
        return process_module(course_id, module_id, min_score=min_score, max_iters=max_iters)

    prev_rep = json.load(open(rep_path, "r", encoding="utf-8"))
    prev_by_id = {t["topic_id"]: t for t in prev_rep.get("topics", [])}

    topics = [dict(r) for r in conn.execute(
        "SELECT id, title, notes_markdown, transcript_text FROM topics WHERE module_id = ? ORDER BY rowid ASC",
        (module_id,)
    ).fetchall()]

    print(f"\n🩹 RECOVERY PASS | {course['name']} | Module {mod['number']}: {mod['name']}")
    ordered = []
    changed_any = False

    for t in topics:
        tid = t["id"]
        t_txt = (t["transcript_text"] or "").strip()
        t_words = len(t_txt.split())
        if t_words < 30:
            continue
        prev = prev_by_id.get(tid)
        cur_t = t["title"]
        cur_n = t["notes_markdown"] or ""

        if prev and prev.get("passed"):
            # Re-run fast deterministic check only to ensure clean labels/KaTeX
            cur_t, cur_n_clean = parse_pure_markdown_note(cur_n, cur_t)
            if cur_n_clean != cur_n:
                with conn:
                    conn.execute("UPDATE topics SET title = ?, notes_markdown = ? WHERE id = ?", (cur_t, cur_n_clean, tid))
                cur_n = cur_n_clean
            ordered.append({
                "skipped": False,
                "idx": prev["idx"],
                "topic_id": tid,
                "old_title": prev["old_title"],
                "new_title": cur_t,
                "notes": cur_n,
                "transcript_words": t_words,
                "note_words": len(cur_n.split()),
                "initial_score": prev["initial_score"],
                "final_score": prev["final_score"],
                "attempts": prev["attempts"],
                "passed": True,
                "has_hallucination": prev["has_hallucination"],
                "final_issues": [],
                "breakdown": prev["breakdown"]
            })
            continue

        # Topic failed or missing: re-evaluate first after deterministic sanitize, then compress/refine
        changed_any = True
        cur_t, cur_n = parse_pure_markdown_note(cur_n, cur_t)
        best_audit = critic_evaluate_note(course_id, mod["name"], cur_t, cur_n, t_txt)
        best_t, best_n = cur_t, cur_n
        print(f"   🔍 [{tid}] Re-check: {best_audit['final_score']}/100 (Passed={best_audit['passed']}, Words={len(best_n.split())}/{get_max_allowed_words(t_words)}) Issues={best_audit['all_issues']}")

        attempt = 0
        while not best_audit["passed"] and attempt < max_iters:
            attempt += 1
            max_w = get_max_allowed_words(t_words)
            only_len_llm = all(
                any(k in x.lower() for k in ["word", "length", "limit", "exceed", "concise"])
                for x in best_audit.get("llm_issues", [])
            )
            if len(best_audit.get("hard_issues", [])) >= 1 and any("Notes too lengthy" in x for x in best_audit["hard_issues"]) and only_len_llm:
                cand_t, cand_n = compress_note_to_budget(best_t, best_n, max_w)
            else:
                cand_t, cand_n = refine_topic_note(course_id, mod["name"], best_t, best_n, t_txt, best_audit, use_strong_model=True)
            cand_aud = critic_evaluate_note(course_id, mod["name"], cand_t, cand_n, t_txt)
            print(f"   🔧 [{tid}] Recovery {attempt}/{max_iters}: {cand_aud['final_score']}/100 (Passed={cand_aud['passed']}, Words={len(cand_n.split())}/{max_w})")
            got_under_cap = (len(cand_n.split()) <= max_w < len(best_n.split())) or (len(cand_n.split()) < len(best_n.split()) and len(best_n.split()) > max_w)
            if (cand_aud["final_score"] >= best_audit["final_score"]) or (len(cand_aud["hard_issues"]) < len(best_audit["hard_issues"])) or got_under_cap:
                best_t, best_n, best_audit = cand_t, cand_n, cand_aud

        with conn:
            conn.execute(
                "UPDATE topics SET title = ?, notes_markdown = ?, status = 'completed', error_message = '' WHERE id = ?",
                (best_t, best_n, tid)
            )
        ordered.append({
            "skipped": False,
            "idx": prev["idx"] if prev else len(ordered) + 1,
            "topic_id": tid,
            "old_title": prev["old_title"] if prev else cur_t,
            "new_title": best_t,
            "notes": best_n,
            "transcript_words": t_words,
            "note_words": len(best_n.split()),
            "initial_score": prev["initial_score"] if prev else best_audit["final_score"],
            "final_score": best_audit["final_score"],
            "attempts": (prev["attempts"] if prev else 1) + attempt,
            "passed": best_audit["passed"],
            "has_hallucination": best_audit["has_hallucination"],
            "final_issues": best_audit["all_issues"],
            "breakdown": best_audit["breakdown"]
        })

    avg_score = round(sum(r["final_score"] for r in ordered) / max(1, len(ordered)), 1)
    pass_count = sum(1 for r in ordered if r["passed"])

    curated_for_oneshot = [{"id": r["topic_id"], "title": r["new_title"], "notes": r["notes"]} for r in ordered]
    mod_low = mod["name"].lower()
    if "live session" in mod_low or "module 0" in mod_low or "welcome" in mod_low:
        mod_oneshot_md = ""
        os_katex_errs = []
    else:
        print(f"🧩 Updating Master Module {mod['number']} One-Shot Section...")
        mod_oneshot_md = compile_module_oneshot(course_id, mod["number"], mod["name"], curated_for_oneshot)
        os_katex_errs = check_katex_expressions(mod_oneshot_md)
        update_course_oneshot_module(course_id, course["name"], mod["number"], mod_oneshot_md)

    if changed_any:
        db.export_static_data()

    report_topics = [{k: v for k, v in r.items() if k != "notes"} for r in ordered]
    report = {
        "course_id": course_id,
        "course_name": course["name"],
        "module_id": module_id,
        "module_number": mod["number"],
        "module_name": mod["name"],
        "videos_processed": len(ordered),
        "videos_passed_gate": pass_count,
        "min_score_target": min_score,
        "module_avg_accuracy": avg_score,
        "module_gate_passed": avg_score >= min_score,
        "oneshot_words": len(mod_oneshot_md.split()),
        "oneshot_katex_errors": os_katex_errs,
        "topics": report_topics
    }
    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✅ RECOVERED {mod['name']}: Avg={avg_score}% ({pass_count}/{len(ordered)} passed >= {min_score}%) Gate={'PASS' if avg_score >= min_score else 'FAIL'}")
    return report


def main():
    parser = argparse.ArgumentParser(description="Process modules sequentially with closed-loop Critic >= 95% verification.")
    parser.add_argument("--course", required=True, help="Course ID (e.g. d9173426)")
    parser.add_argument("--module", help="Single Module ID (e.g. d9173426-m1)")
    parser.add_argument("--modules", help="Comma-separated Module IDs to process strictly one-by-one in order")
    parser.add_argument("--recover", action="store_true", help="Only recover failing topics from existing report(s)")
    parser.add_argument("--min-score", type=int, default=95)
    parser.add_argument("--max-iters", type=int, default=4)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()

    mod_list = []
    if args.modules:
        mod_list = [m.strip() for m in args.modules.split(",") if m.strip()]
    elif args.module:
        mod_list = [args.module.strip()]
    else:
        raise SystemExit("Provide --module or --modules")

    for mid in mod_list:
        if args.recover:
            recover_module(args.course, mid, min_score=args.min_score, max_iters=min(3, args.max_iters))
        else:
            process_module(args.course, mid, min_score=args.min_score, max_iters=args.max_iters, workers=args.workers)


if __name__ == "__main__":
    main()
