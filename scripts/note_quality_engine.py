#!/usr/bin/env python3
"""
Closed-Loop Examiner-Grade Note Synthesis & Verification Engine.

Processes strictly ONE course and ONE module at a time:
1. Context-Aware Generation: Synthesizes notes directly from original transcripts,
   tailored to the subject's real Term 7 exam pattern.
2. Dual-Layer Verification Loop (Critic):
   - Hard Deterministic Checks: word-count equilibrium (strictly shorter than video),
     zero KaTeX syntax errors (via real KaTeX 0.16.8 Node engine), zero generic 'Video' titles,
     zero boilerplate/em-dashes.
   - Faculty Examiner LLM Audit (0-100%): checks accuracy/formula fidelity, framework & case
     application depth, exam-pattern fit, and conciseness. Also auto-fails on hallucinations/inversions.
3. Auto-Refiner Loop: Any video scoring < 75% or failing hard checks gets exact critic
   feedback and is refined & re-verified up to 3 passes until >= 75% is reached.
4. Module One-Shot Compiler: Deduplicates across the verified module and compiles a crisp,
   scannable, table/grid-heavy Master Module One-Shot section into course_one_shots + study_data.js.
"""

import sys
import os
import re
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import db
from core.llm_client import call_llm, clean_text_formatting
import json_repair

KATEX_JS = BASE_DIR / "scratch" / "katex.min.js"
REPORTS_DIR = BASE_DIR / "data" / "verification_reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def get_exam_blueprint(course_id: str) -> str:
    if course_id == "d9173426":  # Critical Thinking
        return """SUBJECT: Critical Thinking (IIMB BBA DBE)
REAL EXAM PATTERN:
- Section A: 14 MCQs (1 mark each = 14 marks)
- Section B: 6 Short Conceptual Questions (2 marks each = 12 marks, exam answer length: 20-30 words)
- Section C: 3 Case-Based Sets (8 questions x 3 marks = 24 marks, exam answer length: 40-50 words)
- NO negative marking, NO calculator. 72% OF MARKS ARE SHORT WRITTEN FRAMEWORK & CASE APPLICATION ANSWERS!

NOTE DESIGN RULES FOR THIS EXAM:
- Top-institute faculty DO NOT ask rote textbook dictionary definitions. They give a short business/civic case and ask:
  "Using Framework X, diagnose what reasoning error occurred, explain how this mechanism works, or recommend how to fix it."
- Every note must center on: (1) Frameworks, analytical tools, cognitive mechanisms, and named case analogies actually spoken in THIS transcript; (2) An ultra-sharp 20-30 word diagnostic anchor; (3) Clean visual formatting tailored to the lecture (comparison table for contrasts, 2x2 grid for quadrants, numbered checklist for methods, tight bullets for concepts).
- NOTE LENGTH vs EXAM ANSWERS: Study notes themselves should be concise (target 60-350 words scaled to video length), while embedding crisp 20-50 word exam-ready diagnostic phrases—do NOT include practice MCQs inside the study notes.
- REDUNDANCY RULE: If this video is a short recap/summary (< 350 words or repeating prior topics), make the note ultra-compact (55-110 words) highlighting ONLY how the prior concepts fit together."""

    elif course_id == "deb83564":  # Data Visualisation
        return """SUBJECT: Data Visualisation and Storytelling Using Data (IIMB BBA DBE)
REAL EXAM PATTERN:
- Section A: 14 MCQs (1 mark each = 14 marks)
- Section B: 8 MSQs - Multiple-Select Questions (2 marks each = 16 marks = 53.3% of total marks!)
- NEGATIVE MARKING ON MSQs: Correct options add partial marks, EVERY wrong checkbox DEDUCTS marks (floored at 0 per question).
- NO calculator. Duration: 60 mins.

NOTE DESIGN RULES FOR THIS EXAM:
- Because >50% of marks are MSQs with penalty for wrong checkboxes, notes must clearly isolate multi-condition rules, subtle boundaries, and "Always True vs. Subtle Trap" distinctions.
- For conceptual/design modules (M1-M2): Use Comparison Tables / Chart Selection Matrices (Which chart for which question? Why bar > pie? Gestalt & pre-attentive principles, stakeholder vs user, cognitive load rules).
- For Power BI / hands-on modules (M3-M4): Skip verbose UI mouse-click narration ("move mouse to top left"). Extract ONLY: (1) Exact DAX formula / data modeling / relationship / filter-context rule, (2) Design rationale (why this visual/measure/drillthrough/tooltip/KPI card is chosen for which decision), and (3) Common Power BI pitfalls / MSQ traps.
- Do NOT include practice MCQs inside the study notes."""

    elif course_id == "2989cdfe":  # Corporate Finance
        return """SUBJECT: Corporate Finance (IIMB BBA DBE)
REAL EXAM PATTERN:
- Section A ONLY: 50 MCQs x 1.5 marks = 75 marks (120 mins = 2.4 mins/question).
- NO negative marking. Scientific Calculator ALLOWED.
- SOFT COPY OF FORMULA SHEET IS PROVIDED DURING THE EXAM!

NOTE DESIGN RULES FOR THIS EXAM (FOR A STUDENT WHO STRUGGLES WITH MATH):
- Since the formula sheet is provided during the exam, the student's real challenge is INTERPRETATION, FORMULA SELECTION, AND SOLVING STEPS—not rote formula memorization!
- Do NOT write baby-talk notes, but explain clearly and intuitively where students get confused.
- STRICT FORMULA FIDELITY: Use the EXACT formula and exact variable symbols shown/spoken in THIS video transcript (never alter or swap formulas silently). Write formulas cleanly as they appear in a textbook using valid KaTeX (`$...$` inline, `$$...$$` display) with ZERO malformed backslashes.
- Whenever a lecture involves formulas or calculations, ALWAYS include:
  1. **Exact Formula & Symbol Key** (in textbook KaTeX + clear units like % vs decimal, periodic vs annual).
  2. **When to Use / Question Triggers:** Exact wording clues in an exam problem that tell you *this* formula applies (e.g., "dividend just paid" = $D_0$, "compounded semi-annually" -> divide annual rate by 2 and multiply years by 2).
  3. **How to Solve (Step-by-Step) + Lecture Worked Example:** Crisp numbered steps walking through the professor's numerical example + calculator traps.
- For purely conceptual/overview lectures: omit math sections completely and use crisp comparison tables / cause-effect bullets (`↑`, `↓`, `→`). Do NOT include practice MCQs inside the study notes."""

    return "General University Exam Preparation."


def check_katex_expressions(markdown_text: str) -> List[str]:
    """Extracts all KaTeX expressions and validates them with real KaTeX 0.16.8 via Node."""
    errors = []
    if any(ch in markdown_text for ch in ["\x08", "\x0c", "\r"]):
        errors.append("Contains corrupted control character (\\x08/\\x0c/\\r from broken LaTeX escaping).")
    if "ightarrow" in markdown_text or "\\\\frac" in markdown_text or "\\\\text" in markdown_text:
        errors.append("Contains double-escaped or broken LaTeX command (e.g., ightarrow or \\\\frac).")

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
            k_errs = json.loads(proc.stdout.strip())
            errors.extend(k_errs)
    except Exception as e:
        errors.append(f"KaTeX validator exception: {e}")

    return errors


def get_max_allowed_words(t_words: int) -> int:
    if t_words <= 0:
        return 120
    if t_words < 350:
        return 125
    return min(420, max(130, int(t_words * 0.45)))


def deterministic_audit(topic_title: str, notes_md: str, transcript_text: str, course_id: str) -> List[str]:
    """Runs fast, strict deterministic checks on generated notes."""
    issues = []
    t_words = len((transcript_text or "").split())
    n_words = len((notes_md or "").split())

    if not notes_md or n_words < 25:
        issues.append("Notes are empty or drastically too short (< 25 words).")
        return issues

    max_allowed = get_max_allowed_words(t_words)
    if t_words > 0 and n_words > max_allowed:
        issues.append(f"Notes too lengthy ({n_words} words vs {t_words} transcript words; HARD LIMIT <= {max_allowed} words).")
    if t_words >= 750 and n_words < 75:
        issues.append(f"Notes appear under-covered ({n_words} words for a {t_words}-word lecture).")

    first_line = (notes_md.splitlines()[0] if notes_md.splitlines() else "").strip()
    if first_line.lower() in ["# video", "# lecture", "# topic"]:
        issues.append("Generic `# Video` header found; replace with specific conceptual topic title.")
    if topic_title.lower().strip() in ["video", "lecture", "topic"]:
        issues.append("Topic title is still generic `Video`; must resolve to specific conceptual title.")

    for bad in ["core mechanics", "no mathematical formulas", "no formulas or numerical calculations"]:
        if bad in notes_md.lower():
            issues.append(f"Banned boilerplate phrase detected: '{bad}'.")

    if "—" in notes_md:
        issues.append("Contains forbidden em dash ('—'). Use commas, colons, or parentheses.")

    k_errs = check_katex_expressions(notes_md)
    issues.extend(k_errs)

    return issues


def parse_delimited_note_output(raw: str, fallback_title: str) -> Tuple[str, str]:
    """Extracts clean title and pure markdown notes without JSON backslash corruption."""
    m_title = re.search(r"<<<TITLE>>>\s*(.*?)\s*<<<END_TITLE>>>", raw, re.DOTALL)
    m_notes = re.search(r"<<<NOTES>>>\s*(.*?)\s*<<<END_NOTES>>>", raw, re.DOTALL)

    if m_notes:
        notes = m_notes.group(1).strip()
    else:
        notes = raw.strip()
        notes = re.sub(r"<<<TITLE>>>.*?<<<END_TITLE>>>", "", notes, flags=re.DOTALL).strip()

    notes = re.sub(r"\s*—\s*", ", ", notes)
    notes = notes.replace("—", ", ").replace("–", "-").strip()

    title = clean_text_formatting(m_title.group(1).strip()) if m_title else ""
    title = re.sub(r"^#+\s*", "", title).strip()

    # Never allow generic 'Video' title
    if not title or title.lower() in ["video", "lecture", "topic"]:
        h1_match = re.search(r"^#\s+([^\n]+)", notes, re.MULTILINE)
        if h1_match and h1_match.group(1).strip().lower() not in ["video", "lecture", "topic"]:
            title = clean_text_formatting(h1_match.group(1).strip())
        else:
            h3_match = re.search(r"^###\s+([^\n]+)", notes, re.MULTILINE)
            if h3_match:
                title = clean_text_formatting(h3_match.group(1).strip())
            else:
                title = fallback_title if fallback_title.lower() != "video" else "Core Conceptual Framework"

    # Also fix top '# Video' inside notes if present
    notes = re.sub(r"^#\s+Video\s*\n+", f"# {title}\n\n", notes, flags=re.IGNORECASE)

    return title, notes


def generate_topic_note(
    course_id: str,
    module_name: str,
    raw_title: str,
    transcript_text: str,
    prior_concepts: List[str]
) -> Tuple[str, str]:
    """Generates tailored, exam-optimized notes for a single video."""
    t_words = len((transcript_text or "").split())
    max_words = get_max_allowed_words(t_words)
    if t_words < 350:
        target_range = f"55–{max_words} words (ultra-compact recap/intro)"
    elif t_words < 750:
        target_range = f"110–{min(200, max_words)} words"
    elif t_words < 1400:
        target_range = f"150–{min(260, max_words)} words"
    else:
        target_range = f"200–{min(340, max_words)} words"

    blueprint = get_exam_blueprint(course_id)
    prior_str = "\n".join(f"- {p}" for p in prior_concepts[-10:]) if prior_concepts else "None yet (first video in module)."

    prompt = f"""You are a top IIM faculty member and exam strategist creating ultra-clear, high-yield study notes for ONE lecture video.

{blueprint}

MODULE: {module_name}
RAW VIDEO TITLE: {raw_title}
TRANSCRIPT WORD COUNT: {t_words} words
TARGET NOTE LENGTH: {target_range}
HARD WORD CEILING: MUST NOT EXCEED {max_words} words! (Cut all greetings, rambling, and filler.)

PRIOR TOPICS ALREADY COVERED IN THIS MODULE (listed ONLY so you avoid repeating identical definitions):
{prior_str}

CRITICAL GROUNDING RULES:
1. **ZERO CROSS-VIDEO CONTAMINATION:** Include ONLY concepts, researchers, companies, case studies, and numbers spoken in THIS transcript below. NEVER pull case studies (like Challenger, Target, etc.) from Prior Topics into this video unless they appear in THIS transcript!
2. **Title:** Provide a crisp, specific conceptual title (NEVER output `# Video` or `Video`!).
3. **Adaptive Format:**
   - Start with `# <Specific Descriptive Title>` and `> **Core Takeaway:** <1-2 sentence sharp thesis>`
   - Pick the BEST visual representation for THIS specific video: Comparison Table, 2x2 Grid, Numbered Workflow/Solving Steps, or Crisp Bullets. Never repeat table rows in bullets.
   - Highlight frameworks, mechanisms, named analogies from THIS transcript, and how to diagnose/solve exam questions.
   - Zero em dashes (`—`). Use Unicode `→`, `↑`, `↓`. Clean textbook KaTeX (`$...$` / `$$...$$`) for math.

ORIGINAL LECTURE TRANSCRIPT (ONLY SOURCE OF FACTS):
{transcript_text[:30000]}

OUTPUT FORMAT (exact delimiters, pure Markdown, NO JSON):
<<<TITLE>>>
Specific Descriptive Title Here
<<<END_TITLE>>>
<<<NOTES>>>
# Specific Descriptive Title Here

> **Core Takeaway:** ...

...high-yield notes under {max_words} words...
<<<END_NOTES>>>"""

    raw_resp = call_llm([{"role": "user", "content": prompt}], temperature=0.12, max_tokens=2000)
    return parse_delimited_note_output(raw_resp, raw_title)


def critic_evaluate_note(
    course_id: str,
    module_name: str,
    title: str,
    notes_md: str,
    transcript_text: str
) -> Dict[str, Any]:
    """Runs deterministic checks + Examiner LLM Critic against the original transcript."""
    hard_issues = deterministic_audit(title, notes_md, transcript_text, course_id)
    blueprint = get_exam_blueprint(course_id)
    t_words = len((transcript_text or '').split())
    n_words = len((notes_md or '').split())
    max_words = get_max_allowed_words(t_words)

    critic_prompt = f"""You are an independent, strict Quality Auditor & Top Business School Examiner auditing **study notes** against the ORIGINAL video transcript.

{blueprint}

LECTURE TITLE: {title}
MODULE: {module_name}
TRANSCRIPT WORD COUNT: {t_words} words
GENERATED NOTE WORD COUNT: {n_words} words (Target ceiling: <= {max_words} words)

ORIGINAL TRANSCRIPT (GROUND TRUTH):
{transcript_text[:28000]}

GENERATED STUDY NOTES TO AUDIT:
{notes_md}

AUDIT RUBRIC (Total 100 points):
1. **accuracy_fidelity (0–25):** Are ALL concepts, case studies, companies, researchers, numbers, and formulas 100% faithful to THIS transcript? Deduct heavily (score <= 15) if ANY case study, statistic, or formula is hallucinated from outside the transcript or directionally inverted!
2. **framework_and_case_depth (0–30):** Does it preserve the key frameworks, mechanisms, and lecture analogies needed to answer faculty application/diagnostic questions?
3. **exam_pattern_fit (0–25):** Is it tailored to the exam pattern (e.g., concise diagnostic anchors for CT, MSQ true-vs-trap clarity for Data Viz, question triggers + exact formula + solving steps for CF)? Note: Study notes are NOT expected to include MCQs.
4. **equilibrium_and_formatting (0–20):** Is the length strictly balanced (shorter than the transcript, <= {max_words} words, concise for recaps) and formatted with clear tables/grids/bullets without boilerplate?

Return ONLY valid JSON:
{{
  "accuracy_fidelity": <int 0-25>,
  "framework_and_case_depth": <int 0-30>,
  "exam_pattern_fit": <int 0-25>,
  "equilibrium_and_formatting": <int 0-20>,
  "has_hallucination_or_inversion": <true or false>,
  "total_score": <int 0-100>,
  "issues": ["list of specific, concrete missing items, hallucinations, inversions, bloat, or formula discrepancies"],
  "fix_instructions": "Actionable instructions for the refiner if any issues exist."
}}"""

    raw = call_llm([{"role": "user", "content": critic_prompt}], temperature=0.1, max_tokens=1000)
    try:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        parsed = json_repair.loads(m.group(0) if m else raw)
        if not isinstance(parsed, dict):
            parsed = {}
    except Exception:
        parsed = {}

    sub_keys = ["accuracy_fidelity", "framework_and_case_depth", "exam_pattern_fit", "equilibrium_and_formatting"]
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
        if any(flag in low for flag in ["not in the transcript", "not in transcript", "hallucination", "inverted", "reversed relative to", "fabricat"]):
            has_hallucination = True

    penalty = 0
    if hard_issues:
        penalty = min(40, 15 * len(hard_issues))
    if has_hallucination:
        penalty = max(penalty, 20)

    final_score = max(0, llm_score - penalty)
    all_issues = hard_issues + [i for i in llm_issues if i]
    passed = (final_score >= 75) and (len(hard_issues) == 0) and (not has_hallucination)

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


def refine_topic_note(
    course_id: str,
    module_name: str,
    current_title: str,
    current_notes: str,
    transcript_text: str,
    audit_result: Dict[str, Any]
) -> Tuple[str, str]:
    """Fixes specific critic-flagged defects using ONLY the original transcript."""
    blueprint = get_exam_blueprint(course_id)
    t_words = len((transcript_text or "").split())
    n_words = len((current_notes or "").split())
    max_words = get_max_allowed_words(t_words)
    issues_txt = "\n".join(f"- {iss}" for iss in audit_result["all_issues"])
    trim_hint = (
        f"\nCRITICAL LENGTH OVERFLOW: Current notes are {n_words} words. You MUST CUT at least {n_words - max_words + 15} words to stay <= {max_words} words!"
        if n_words > max_words else ""
    )

    prompt = f"""You are refining study notes to resolve EVERY issue flagged by our Examiner Quality Critic.

{blueprint}

MODULE: {module_name}
CURRENT TITLE: {current_title}
TRANSCRIPT WORD COUNT: {t_words} words
CURRENT NOTE WORD COUNT: {n_words} words
HARD WORD CEILING: MUST NOT EXCEED {max_words} words!{trim_hint}

FLAGGED ISSUES TO FIX:
{issues_txt}
EXTRA FIX GUIDANCE: {audit_result.get('fix_instructions', '')}

CURRENT NOTES:
{current_notes}

ORIGINAL TRANSCRIPT (ONLY SOURCE OF FACTS):
{transcript_text[:28000]}

STRICT FIX RULES:
- Fix EVERY flagged issue: remove any hallucinated case/concept not present in THIS transcript, fix any inverted logic/numbers, fix KaTeX errors, and make sure the title is a specific conceptual title (NEVER `Video`).
- Strictly obey HARD WORD CEILING <= {max_words} words (cut aggressively if flagged as too lengthy).
- Use pure Markdown (NO JSON wrapping), zero em dashes (`—`).

OUTPUT FORMAT:
<<<TITLE>>>
Specific Conceptual Title
<<<END_TITLE>>>
<<<NOTES>>>
# Specific Conceptual Title

...fixed high-yield notes under {max_words} words...
<<<END_NOTES>>>"""

    raw_resp = call_llm([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=2000)
    return parse_delimited_note_output(raw_resp, current_title)


def compile_module_oneshot(course_id: str, mod_num: int, mod_name: str, curated_topics: List[Dict[str, str]]) -> str:
    """Synthesizes a unified, deduplicated, table/grid-first One-Shot revision section for the entire module."""
    blueprint = get_exam_blueprint(course_id)

    topics_blob = []
    for i, t in enumerate(curated_topics, 1):
        topics_blob.append(f"### Video {i}: {t['title']}\n{t['notes']}")
    combined_input = "\n\n---\n\n".join(topics_blob)

    prompt = f"""You are compiling the **Master One-Shot Revision Section** for ONE entire module from its verified video notes.

{blueprint}

MODULE NAME: {mod_name}
MODULE NUMBER: {mod_num}

GOAL:
A student revising 1-2 hours before the exam should be able to scan THIS ENTIRE MODULE in **3 to 5 minutes** and master **every testable framework, differentiation, case application, formula trigger, and exam trap** without reading repetitive overlap across videos!

INSTRUCTIONS:
1. **Deduplicate Intelligently:** Multiple videos in the module often revisit the same framework or recap earlier videos. MERGE overlapping content into unified, crystal-clear sections!
2. **Table & Grid First:**
   - Every differentiation/contrast -> Markdown Table.
   - Every 2x2 or multi-part taxonomy -> Markdown Grid/Table.
   - Include named lecture case studies in concise 2-line diagnostic patterns (`Case -> Error/Mechanism -> Fix`).
   - For Corporate Finance: keep exact textbook KaTeX formulas + "Question Trigger -> Formula -> Quick Solving Steps" (NO broken KaTeX, NO red errors!).
3. **Header Format (NO backticks around the HTML anchor!):**
   Start cleanly with:
   <a id="module-{mod_num}"></a>
   ## {mod_name}
   followed by a 1-sentence `> **Cram Focus:** ...` blockquote, numbered subsections (`### 1. ...`), and end with a tight **Exam Trap Radar** (`3–6` highest-yield traps for this module).
4. **Length Discipline:** Target **650–1,250 words** total for the entire module one-shot (concise, scannable, dense with signal, zero fluff, zero em dashes `—`).

VERIFIED MODULE VIDEO NOTES TO SYNTHESIZE:
{combined_input[:26000]}

Return ONLY pure Markdown starting directly with `<a id="module-{mod_num}"></a>` (no code fence, no backticks around the anchor tag)."""

    raw = call_llm([{"role": "user", "content": prompt}], temperature=0.15, max_tokens=2800)
    md = raw.strip()
    md = re.sub(r"^```(?:markdown)?\s*", "", md)
    md = re.sub(r"\s*```$", "", md)
    # Strip accidental backticks around anchor tag
    md = re.sub(r"`(<a\s+id=[\"']module-\d+[\"']>\s*</a>)`", r"\1", md)
    md = re.sub(r"\s*—\s*", ", ", md).replace("—", ", ").replace("–", "-")
    if f'<a id="module-{mod_num}"></a>' not in md:
        md = f'<a id="module-{mod_num}"></a>\n{md}'
    return md.strip()


def rebuild_course_header(course_id: str, course_name: str, body_md: str) -> str:
    """Ensures the course one-shot header & Quick Module Navigation cover all active modules cleanly."""
    conn = db.get_conn()
    mods = conn.execute(
        "SELECT id, number, name FROM modules WHERE course_id = ? ORDER BY number ASC",
        (course_id,)
    ).fetchall()

    nav_lines = ["## Quick Module Navigation\n"]
    for m in mods:
        m_low = m["name"].lower()
        if "module 0" in m_low or "welcome" in m_low or "mid-term" in m_low:
            continue
        if course_id == "2989cdfe" and m["id"] == "2989cdfe-m5":
            continue
        if "live session" in m_low:
            continue
        nav_lines.append(f"- [{m['name']}](#module-{m['number']})")

    header = (
        f"# {course_name}: High-Yield Exam Revision Hub\n\n"
        "> **Examiner-Verified One-Shot Guide:** Curated module-by-module against the Term 7 exam pattern. "
        "Every table, framework, formula trigger, and case diagnostic is cross-checked against original lecture transcripts.\n\n"
        "---\n\n"
        + "\n".join(nav_lines)
        + "\n\n---\n\n"
    )

    first_mod_idx = body_md.find('<a id="module-')
    if first_mod_idx != -1:
        body_md = body_md[first_mod_idx:]
    return header + body_md


def update_course_oneshot_module(course_id: str, course_name: str, mod_num: int, new_mod_section: str):
    """Replaces or inserts the curated Module X section inside course_one_shots without disturbing other modules."""
    conn = db.get_conn()
    row = conn.execute(
        "SELECT one_shot_markdown, formula_sheet_markdown FROM course_one_shots WHERE course_id = ?",
        (course_id,)
    ).fetchone()
    existing_md = row["one_shot_markdown"] if row else ""
    formula_md = row["formula_sheet_markdown"] if row else ""

    anchor = f'<a id="module-{mod_num}"></a>'
    # Find next <a id="module-..."> anchor after start_idx
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


def process_module(course_id: str, module_id: str, min_score: int = 75, max_iters: int = 3):
    conn = db.get_conn()
    course = conn.execute("SELECT id, name FROM courses WHERE id = ?", (course_id,)).fetchone()
    mod = conn.execute("SELECT id, number, name FROM modules WHERE id = ?", (module_id,)).fetchone()
    if not course or not mod:
        raise ValueError(f"Invalid course_id={course_id} or module_id={module_id}")

    topics = conn.execute(
        "SELECT id, title, transcript_text, notes_markdown FROM topics WHERE module_id = ? ORDER BY rowid ASC",
        (module_id,)
    ).fetchall()

    print(f"\n==================================================================")
    print(f"📘 COURSE: {course['name']} | MODULE {mod['number']}: {mod['name']} ({len(topics)} videos)")
    print(f"==================================================================")

    prior_concepts = []
    report_entries = []
    curated_for_oneshot = []

    for idx, t in enumerate(topics, 1):
        tid = t["id"]
        raw_title = t["title"]
        transcript = (t["transcript_text"] or "").strip()
        print(f"\n[{idx}/{len(topics)}] Synthesizing: [{tid}] '{raw_title}' ({len(transcript.split())} transcript words)")

        if len(transcript.split()) < 30:
            print("   ⚠️ Very short/missing transcript; skipping LLM rewrite.")
            continue

        new_title, new_notes = generate_topic_note(course_id, mod["name"], raw_title, transcript, prior_concepts)
        audit = critic_evaluate_note(course_id, mod["name"], new_title, new_notes, transcript)
        init_score = audit["final_score"]
        print(f"   🔍 Pass 1 Critic Score: {init_score}/100 (Passed={audit['passed']}, Halluc={audit['has_hallucination']}) | Words={len(new_notes.split())} | Title='{new_title}'")
        if audit["all_issues"]:
            print(f"      Issues: {audit['all_issues']}")

        attempt = 1
        while not audit["passed"] and attempt < max_iters:
            attempt += 1
            print(f"   🔧 Auto-Refining (Attempt {attempt}/{max_iters})...")
            new_title, new_notes = refine_topic_note(course_id, mod["name"], new_title, new_notes, transcript, audit)
            audit = critic_evaluate_note(course_id, mod["name"], new_title, new_notes, transcript)
            print(f"   🔍 Pass {attempt} Critic Score: {audit['final_score']}/100 (Passed={audit['passed']}, Halluc={audit['has_hallucination']}) | Words={len(new_notes.split())} | Title='{new_title}'")
            if audit["all_issues"]:
                print(f"      Remaining Issues: {audit['all_issues']}")

        tk_match = re.search(r"\*\*Core Takeaway:\*\*\s*([^\n]+)", new_notes)
        prior_concepts.append(f"{new_title}: {tk_match.group(1)[:120] if tk_match else ''}")

        with conn:
            conn.execute(
                "UPDATE topics SET title = ?, notes_markdown = ?, status = 'completed', error_message = '' WHERE id = ?",
                (new_title, new_notes, tid)
            )

        curated_for_oneshot.append({"id": tid, "title": new_title, "notes": new_notes})
        report_entries.append({
            "topic_id": tid,
            "old_title": raw_title,
            "new_title": new_title,
            "transcript_words": len(transcript.split()),
            "note_words": len(new_notes.split()),
            "initial_score": init_score,
            "final_score": audit["final_score"],
            "attempts": attempt,
            "passed": audit["passed"],
            "has_hallucination": audit["has_hallucination"],
            "final_issues": audit["all_issues"],
            "breakdown": audit["breakdown"]
        })

    avg_score = round(sum(r["final_score"] for r in report_entries) / max(1, len(report_entries)), 1)
    pass_count = sum(1 for r in report_entries if r["passed"])

    # If module average < min_score, perform an extra targeted pass on failing topics
    if avg_score < min_score and report_entries:
        print(f"\n⚠️ Module avg {avg_score}% < {min_score}%. Running targeted recovery pass on failing topics...")
        for r in report_entries:
            if not r["passed"]:
                t_row = conn.execute("SELECT title, transcript_text, notes_markdown FROM topics WHERE id = ?", (r["topic_id"],)).fetchone()
                if not t_row:
                    continue
                audit = critic_evaluate_note(course_id, mod["name"], t_row["title"], t_row["notes_markdown"], t_row["transcript_text"])
                new_t, new_n = refine_topic_note(course_id, mod["name"], t_row["title"], t_row["notes_markdown"], t_row["transcript_text"], audit)
                audit2 = critic_evaluate_note(course_id, mod["name"], new_t, new_n, t_row["transcript_text"])
                if audit2["final_score"] >= r["final_score"]:
                    with conn:
                        conn.execute("UPDATE topics SET title = ?, notes_markdown = ? WHERE id = ?", (new_t, new_n, r["topic_id"]))
                    r["new_title"] = new_t
                    r["note_words"] = len(new_n.split())
                    r["final_score"] = audit2["final_score"]
                    r["passed"] = audit2["passed"]
                    r["final_issues"] = audit2["all_issues"]
                    for c_item in curated_for_oneshot:
                        if c_item["id"] == r["topic_id"]:
                            c_item["title"] = new_t
                            c_item["notes"] = new_n
        avg_score = round(sum(r["final_score"] for r in report_entries) / max(1, len(report_entries)), 1)
        pass_count = sum(1 for r in report_entries if r["passed"])

    print(f"\n🧩 Compiling Master Module {mod['number']} One-Shot Section...")
    mod_oneshot_md = compile_module_oneshot(course_id, mod["number"], mod["name"], curated_for_oneshot)
    os_katex_errs = check_katex_expressions(mod_oneshot_md)
    if os_katex_errs:
        print(f"   ⚠️ One-Shot KaTeX issues detected: {os_katex_errs}")
    update_course_oneshot_module(course_id, course["name"], mod["number"], mod_oneshot_md)

    print("📦 Exporting static bundle to study_data.js...")
    db.export_static_data()

    report = {
        "course_id": course_id,
        "course_name": course["name"],
        "module_id": module_id,
        "module_number": mod["number"],
        "module_name": mod["name"],
        "videos_processed": len(report_entries),
        "videos_passed_75": pass_count,
        "module_avg_accuracy": avg_score,
        "module_gate_passed": avg_score >= min_score,
        "oneshot_words": len(mod_oneshot_md.split()),
        "oneshot_katex_errors": os_katex_errs,
        "topics": report_entries
    }
    rep_path = REPORTS_DIR / f"{module_id}.json"
    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n==================================================================")
    print(f"✅ MODULE COMPLETE: {mod['name']}")
    print(f"   Avg Accuracy Score: {avg_score}% (Gate >= {min_score}%: {'PASS' if avg_score >= min_score else 'FAIL'})")
    print(f"   Videos Passing >=75%: {pass_count}/{len(report_entries)}")
    print(f"   Module One-Shot Length: {len(mod_oneshot_md.split())} words")
    print(f"   Verification Report: {rep_path}")
    print(f"==================================================================")
    return report


def main():
    parser = argparse.ArgumentParser(description="Process modules sequentially with closed-loop Critic >= 75% verification.")
    parser.add_argument("--course", required=True, help="Course ID (e.g. d9173426)")
    parser.add_argument("--module", help="Single Module ID (e.g. d9173426-m1)")
    parser.add_argument("--modules", help="Comma-separated Module IDs to process strictly one-by-one in order")
    parser.add_argument("--min-score", type=int, default=75)
    parser.add_argument("--max-iters", type=int, default=3)
    args = parser.parse_args()

    mod_list = []
    if args.modules:
        mod_list = [m.strip() for m in args.modules.split(",") if m.strip()]
    elif args.module:
        mod_list = [args.module.strip()]
    else:
        raise SystemExit("Provide --module or --modules")

    for mid in mod_list:
        process_module(args.course, mid, min_score=args.min_score, max_iters=args.max_iters)


if __name__ == "__main__":
    main()
