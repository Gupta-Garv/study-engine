# Academic Note Synthesis Standard & Rules (Conceptual & MCQ Focused)

## 1. Target Audience & Writing Style
The reader is a **3rd-year undergraduate university student** preparing for high-stakes, conceptual, MCQ-based semester exams. 
The notes must deliver full academic depth and rigor, but the writing must be **direct, crisp, and effortless to comprehend**.

### Strict Sentence & Vocabulary Constraints:
- **Zero Em Dashes (`—`):** Never use em dashes or hyphens to connect clauses or insert parenthetical thoughts. Use standard periods. Break complex thoughts into separate, clear sentences.
- **Simple, Direct Sentences:** Write in active voice (Subject-Verb-Object). Avoid stacking dependent clauses. Keep each sentence focused on one clear idea. If a sentence takes more than one breath to read, split it.
- **No Pretentious Academic Fluff:** Ban unnecessary SAT-level words like "dichotomy", "held in abeyance", "probabilistic outcome", "inevitable principal-agent friction", "manifests as", and "perpetual succession paradigm". Use clear, professional finance terminology (e.g., "opportunity cost", "net present value", "discount rate", "risk tolerance", "cash flow", "agency conflict").
- **Clean Unicode Arrows for Mechanics:** Always use clean Unicode symbols (`→`, `↑`, `↓`) for cause-and-effect relationships. Do NOT use LaTeX `\rightarrow` inside explanatory text (e.g., write `Interest Rate (r) ↑  →  Present Value (PV) ↓`).

---

## 2. Strict Ground-Truth Fidelity (No Outside Padding)
- **Anchor 100% to the Lecture Transcript:** Only summarize concepts, principles, and mechanisms that the professor actually explains in this specific video. Do NOT pad the notes with random outside encyclopedia paragraphs or textbook history.
- **Short Overview / Roadmap Videos:** If a video is a 1-minute intro outlining the syllabus (like Lecture 1), summarize it cleanly as a module roadmap. Do NOT guess or hallucinate outside theories (like "Separation Principle", "Hedging Principle", or "Double Taxation").
- **Preserve the Professor's Real-World Examples:** Whenever the professor mentions specific companies, people, or stories, ALWAYS include them in the notes. University examiners frequently build MCQ scenarios around the professor's exact lecture examples:
  - *Infosys:* Over 2 million shareholders holding over 4 billion shares (illustrates why owners cannot run daily operations and must delegate authority to professional managers).
  - *Gautam Adani & Mukesh Ambani:* Net worth as a stock variable (measured at a specific point in time) versus income/profit as a flow variable (measured over a time period).
  - *Tyco International CEO:* Spending $2M on his wife's birthday party and billing $1M to the company (direct agency cost), purchasing unneeded corporate jets, and paying external auditors to inspect financial statements (monitoring costs).
- **No Irrelevant Foreign Assumptions:** Stick to the legal and financial framework presented in the lecture (e.g., Indian Partnership Act 1932, Companies Act). Do not import US-specific textbook assumptions like US C-Corp double taxation unless explicitly taught.

---

## 3. Required Output Note Structure
Every generated lecture note MUST follow this exact 5-part architecture in `notes_markdown`:

### Part 1: Executive Mental Model & Core Intuition
- Explain the central concept or dilemma discussed in this lecture in 1–2 direct, clear paragraphs.
- State the core thesis: *Why does this concept exist? What business problem, financial friction, or decision dilemma does it resolve?*
- Do not use em dashes. Keep sentences punchy and informative.

### Part 2: Concise Point-Wise Conceptual Mechanics (Cause & Effect)
- Bullet points explaining the working rules and mechanics.
- Highlight **parameter shifts and sensitivity**:
  - `Parameter Shift: If Interest Rate (r) ↑  →  Present Value (PV) ↓ because future cash flows are discounted more heavily.`
- Highlight **boundary conditions**: State clearly when the rule holds and when it breaks down.

### Part 3: Conceptual Distinctions & Versus Matrix
- University exams constantly test subtle differences between easily confusable concepts.
- Provide a clean Markdown comparison table comparing concepts discussed in this lecture (e.g., *Profit Maximization vs. Wealth Maximization*; *Real Assets vs. Financial Assets*; *Sole Proprietorship vs. Partnership*; *Private Limited vs. Public Limited*).
- Include an explicit **MCQ Diagnostic** column explaining what the examiner tests.
  `| Dimension | Concept A | Concept B | MCQ Diagnostic / Examiner Test |`

### Part 4: Key Formulas & Numerical Application
- **IF formulas are discussed in this lecture:**
  - Display exact KaTeX LaTeX equations (`$$...$$`).
  - Provide a Variable Definition Table:
    `| Symbol | Parameter Name | Units / Meaning | Effect when Parameter Increases |`
  - Step-by-step worked numerical example from the lecture showing how numbers are plugged in.
- **IF the lecture is purely qualitative/conceptual:**
  - Explicitly write: `*Conceptual Session: No mathematical formulas introduced in this lecture.*`
  - Summarize the qualitative decision criteria or decision rule table.

### Part 5: MCQ Trap Radar & Examiner Gotchas
- 3–4 specific cognitive traps and distractor tricks examiners set on this topic:
  - **Trap 1: The Distractor Trap** (e.g., Confusing accounting profit with economic value).
  - **Trap 2: The "Zero Risk" Fallacy** (e.g., Assuming zero risk means zero time value of money).
  - **Trap 3: The Boundary Assumption Trap** (e.g., Assuming a rule holds when market conditions change).

---

## 4. Assessment Specifications

### Conceptual MCQs (4 to 6 Questions per Lecture)
- Must test **conceptual understanding, scenarios, cause-and-effect, and edge cases**.
- Prohibit trivial trivia questions (e.g., "What year was X published?").
- Include 4 plausible options (A, B, C, D).
- Provide a thorough `explanation` detailing:
  1. Why the correct option is conceptually right.
  2. Why each distractor option is a trap and conceptually flawed.

### Subjective Question (1 Question)
- 1 university-style exam question (5 to 10 marks).
- Complete model answer broken into structured points with an explicit marking rubric.

### Revision Flashcards (3 to 4 Flashcards)
- Front: A conceptual diagnostic prompt (e.g., *"Why does maximizing current EPS fail as a corporate financial objective?"*).
- Back: Crisp, punchy conceptual takeaway.
