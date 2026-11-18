# Adaptive Academic Note Synthesis Standard (v2 — High-Signal, Zero-Bloat)

## 1. Core Objective: Beat Watching the Video at 2x
A student reading ONLY these notes must understand **100% of what the professor taught** (every mechanism, formula, number, framework, and named example) in **half the time it takes to watch the video at 2x speed**.

### Strict Word Budget (Scaled to Transcript Length)
- **Short video (< 350 transcript words / 1–3 min):** 130–210 words (~45-second read).
- **Standard lecture (350–900 transcript words / 3–7 min):** 200–320 words (~75-second read).
- **Medium lecture (900–1,800 transcript words / 7–15 min):** 280–420 words (~1.5-minute read).
- **Long deep-dive (> 1,800 transcript words / 15+ min):** 380–540 words (~2-minute read).

### Style & Clarity Laws
- **Zero Repetition:** Never explain the same idea twice across different sections. Every line must carry new information.
- **No Walls of Text:** Keep bullets to 1–2 crisp lines, each starting with a **bold lead-in phrase**.
- **Simple, Direct Active Voice:** Zero em dashes (`—`). Zero pretentious SAT filler words.
- **Clean Unicode Arrows:** Use `→`, `↑`, `↓` for cause-and-effect and parameter shifts (e.g., `Discount rate (r) ↑ → Present Value (PV) ↓`).
- **Strict Ground Truth:** Include ONLY concepts, companies, researchers, years, and figures actually spoken in this specific transcript. Never invent outside examples or theories.

---

## 2. Adaptive Structure (Let the Lecture Dictate the Format)
Do NOT force a fixed 5-part template on every video. Select ONLY the blocks that genuinely fit the transcript:

1. **Top Line (Always):** Start with `# {Topic Title}` followed immediately by a 1–2 sentence blockquote:
   `> **Core Takeaway:** <The single sharpest thesis of this lecture.>`

2. **Conditional Content Blocks (Include ONLY When Earned by the Transcript):**
   - **2×2 Matrix or Comparison Table:** Include ONLY when the professor explicitly contrasts 2+ categories, a 2×2 quadrant framework, or side-by-side concepts. If you render a table, do NOT repeat those same rows again as bullet points.
   - **Formulas & Worked Numerical:** Include ONLY when the lecture teaches equations or quantitative calculations. Format formulas in clean KaTeX (`$$...$$`), define symbols concisely, and walk through the professor's exact numerical example with **verified intermediate arithmetic** (double-check every intermediate value, e.g., `$800,000 / 1.07 = $747,664`, `$747,664 - $700,000 = $47,664`). If there is no math, **OMIT this section completely** (NEVER write "Conceptual session: no mathematical formulas").
   - **Step-by-Step Workflow / Framework / Timeline:** Include ONLY when the lecture teaches sequential stages, eras, or a multi-step analytical workflow.
   - **Named Examples & Empirical Evidence:** Preserve the professor's exact company names, researchers, years, and figures inline or in compact 1-line bullets.

3. **Core Mechanics (Always — concise, zero overlap with any table above):**
   - Tight cause-and-effect bullets showing how variables, incentives, or trade-offs interact (`→`, `↑`, `↓`).

4. **MCQ Trap Radar (Always — sharp & standardized):**
   - Exactly **2 to 3** crisp traps targeting exact misconceptions examiners test on this lecture, formatted consistently as:
     `1. **Trap:** <Common misconception> → **Reality:** <Sharp correction>`

---

## 3. Assessment Specifications (When Generating Full Package)
- **Conceptual MCQs (4 to 6):** Scenario-based or cause-and-effect questions testing deep understanding with thorough explanations of correct answers and distractors.
- **Subjective Question (1):** University-style 5–10 mark question with structured model answer and marking rubric.
- **Flashcards (3 to 4):** Crisp diagnostic prompt on front, punchy takeaway on back.
