# Academic Note Synthesis Standard & Rules (Conceptual & MCQ Focused)

## 1. Core Philosophy & Examination Target
University exams in this discipline are heavily **MCQ-based and test deep conceptual understanding**, not rote memorization of textbook definitions. 

Examiners do NOT ask: *"What is the definition of Agency Theory?"*
Examiners DO ask:
- *"If a manager rejects a positive NPV project because it carries high personal career risk, which specific agency conflict is demonstrated?"*
- *"When interest rates rise from 8% to 10%, why does the present value of a distant cash flow drop by a larger percentage than a near-term cash flow?"*
- *"Under what specific boundary condition does Profit Maximization fail to align with Shareholder Wealth Maximization?"*

The notes must equip the student to solve tricky, application-based conceptual MCQs effortlessly on exam day.

---

## 2. Strict Ground-Truth Fidelity (No Fluff / No Outside Padding)
- **Anchor strictly to the lecture's spoken transcript.** Do NOT pad the notes with random outside encyclopedia paragraphs, long historical biographies, or tangential trivia the professor never mentioned.
- Keep the writing concise, sharp, high-density, and structured.
- Every section must serve a purpose: understanding the concept, mastering the mechanics, and avoiding exam traps.

---

## 3. Required Output Note Structure
Every generated lecture note MUST follow this exact 5-part architecture in `notes_markdown`:

### Part 1: Executive Mental Model & Core Intuition
- Explain the central concept or dilemma discussed in this lecture in 1–2 crisp, intuitive paragraphs.
- State the core thesis: *Why does this concept exist? What real-world friction, risk, or business dilemma does it resolve?*

### Part 2: Concise Point-Wise Conceptual Mechanics (Cause & Effect)
- High-yield, bulleted takeaways explaining the working mechanics.
- Highlight **parameter shifts and sensitivity**:
  - *"If [Variable A] increases $\rightarrow$ [Outcome B] decreases because [Economic Reason]."*
- Highlight boundary conditions: *When does this rule hold, and when does it break down?*

### Part 3: Conceptual Distinctions & Comparison Matrix
- Exams love testing subtle distinctions between two closely related or confusable terms.
- Provide a clean Markdown comparison table comparing concepts discussed in this lecture (e.g., Profit Maximization vs. Wealth Maximization; Real Assets vs. Financial Assets; Equity Agency Cost vs. Debt Agency Cost; Primary Market vs. Secondary Market).
- Table format:
  `| Dimension | Concept A | Concept B | MCQ Diagnostic / Key Test |`

### Part 4: Key Formulas & Numerical Application
- **IF formulas are discussed in this lecture:**
  - Provide exact KaTeX LaTeX display equations (`$$...$$`).
  - Provide a Variable Definition Table:
    `| Symbol | Parameter Name | Units / Interpretation | Effect when Increased |`
  - Step-by-step worked example from the lecture showing how numbers are plugged in.
- **IF the lecture is purely qualitative/conceptual:**
  - Explicitly write: `*Conceptual Session: No mathematical formulas introduced in this lecture.*`
  - Summarize the qualitative decision rule (e.g., Criteria matrix, decision rule, or governance mechanism).

### Part 5: MCQ Trap Radar & Examiner Gotchas
- 3–4 specific conceptual traps examiners set to catch unprepared students:
  - **Trap 1: The Distractor Trap**: (e.g., Confusing accounting profit with economic value).
  - **Trap 2: The Horizon / Time Value Trap**: (e.g., Ignoring timing or risk when comparing projects).
  - **Trap 3: The Boundary Assumption Trap**: (e.g., Assuming a rule holds when market conditions change).

---

## 4. Assessment Specifications

### Conceptual MCQs (4 to 6 Questions per Lecture)
- Must test **conceptual understanding, scenarios, cause-and-effect, and edge cases**.
- Prohibit trivial recall or trivia questions (e.g., "What year was X published?").
- Include 4 options (A, B, C, D).
- Provide a comprehensive `explanation` that explains:
  1. Why the correct option is conceptually sound.
  2. Why the tempting distractors are conceptually flawed.

### Subjective Question (1 Question)
- 1 university-style exam question (5 to 10 marks).
- Complete model answer broken into structured points with an explicit marking rubric.

### Revision Flashcards (3 to 4 Flashcards)
- Front: A conceptual diagnostic prompt (e.g., *"Why does maximizing current EPS fail as a corporate financial objective?"*).
- Back: Crisp, punchy conceptual takeaway.

