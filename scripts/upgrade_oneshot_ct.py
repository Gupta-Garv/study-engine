#!/usr/bin/env python3
"""
Upgrade Critical Thinking (d9173426) One-Shot Notes:
- Concise, module-wise (Modules 1-8), calibrated to Term 7 pattern (14 MCQs + 6 Short [20-30w] + 3 Cases [40-50w])
- Verified with check_katex_expressions() before saving to DB & exporting study_data.js
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import db
from scripts.note_quality_engine import check_katex_expressions

COURSE_ID = "d9173426"

ONE_SHOT_MD = r"""# Critical Thinking: Master Exam One-Shot (Modules 1 to 8)

> **Term 7 Paper Pattern:** **50 Marks | 120 Mins | No Calculator | No Negative Marking**
> - **Section A:** 14 MCQs x 1 mark = 14 marks
> - **Section B:** 6 Conceptual Questions x 2 marks = 12 marks (**20-30 words each**: *Contrast A vs. B in 1 crisp sentence + 1 concrete example*)
> - **Section C:** 3 Case Studies (6M [2x3] + 9M [3x3] + 9M [3x3] = 24 marks; **40-50 words per sub-question**: *Name Framework -> Diagnose Flaw/Omission -> Propose 1 Structural Fix / Residual Risk*)

---

## Case-to-Framework Quick Decoder (For Sec B & Sec C)

| If the Case / Question Describes... | Exact Framework / Bias to Name | High-Scoring Deliverable |
|---|---|---|
| 89% accurate pregnancy model mailing baby coupons | **Analytics-Ethics Gap (Target Case)** | Predictive accuracy != consent; use opt-in mixed bundles; flag data-breach risk |
| Engineers had valid O-ring data, launch still failed | **Logic vs. Evidence Completeness (Challenger)** | Missing zero-damage low-temp baseline + schedule pressure |
| Survey of 6-month active users or returning bombers | **Selection / Survivorship Bias (Wald)** | Look at the "invisible record" (week-1 churn, non-returning planes) |
| Press release blames pilot checklists, calls fix "enhancement" | **Close Reading: Euphemism & Omission (Boeing)** | Blame-shifting + hidden design flaws; audit vs. internal engineering memos |
| Leadership suppresses launch delays to beat rival | **Groupthink & Structural Devil's Advocacy** | Independent Safety Sign-Off to Board Risk Committee + protected Red-Team veto |
| "1% of 1.4B Indians buy our Rs 2,000 desk monthly" | **Base-Rate / TAM-SOM & Frequency Flaw** | Filter out non-buyers + durable goods are bought once in years, not monthly |
| "Campaign ran Tuesday, sales rose Thursday -> caused it" | **Post Hoc Ergo Propter Hoc** | Sequence != causation; control for festive seasonality & discounts |
| "Either slash R&D 40% today or go bankrupt" | **False Dilemma (Black-and-White)** | Surface middle options (phased capex, pricing tiers, working capital) |
| Junior spots fatal flaw in VP's plan, stays silent | **Nyaya Tarka & Face-Saving** | Private pre-meeting hypothesis testing ("what conditions could make this fail?") |
| "Survey says customers prefer white, skip pastel prototypes" | **Exposure Gap Analysis (Whites & Pastels)** | Customers prefer what they have seen; test novel designs via physical prototypes |

---

## Module 1: Foundations of Critical Thinking

- **Logic vs. Critical Thinking:** Logic checks whether a conclusion follows from given premises; Critical Thinking interrogates whether those premises are **complete, unbiased, and ethically sound**.
- **Evidence Triad:**
  - **Fact:** Directly observable, independently verifiable (`"Traffic fell 18% on Tuesday"`).
  - **Inference:** Causal/probabilistic step drawn from facts (`"Our Tuesday email caused the drop"`).
  - **Interpretation:** Subjective meaning assigned (`"Customers hate our brand"`).
- **Framing & Loss Aversion:** Identical payoffs flip choices depending on framing (`"Rs 100 card surcharge"` rejected vs. `"Rs 100 cash discount"` accepted). Visual scale truncation and selective time windows distort System 1 intuition.
- **Confirmation Bias vs. Motivated Reasoning:** Confirmation bias passively favors belief-consistent data; **Motivated Reasoning** actively recruits double-standards to defend a desired emotional/financial outcome.
- **Survivorship Bias (Wald's Bombers):** Returning planes excluded fatal hits on engines -> study non-survivors ("the invisible record") before acting.

---

## Module 2: Critical Reading & Interpretation

- **Explicit Claim vs. Implicit Position:** Explicit claims sit on the surface; implicit positions are unstated assumptions/blame-shifts revealed by **word choice, repetition, and strategic omission**.
- **Reasonable Person Test:** Interpret ambiguous text by what an ordinary, informed reader would fairly infer from plain wording—not the author's hidden private intent.
- **Confident Language vs. Evidence:** Intensifiers (`"undoubtedly"`, `"clearly"`, `"every leader knows"`) frequently mask missing sample sizes or weak data.
- **5 Cs of Narrative Persuasion (Hare-Tortoise Trap):** Clean retrospective stories (e.g., Blockbuster vs. Netflix, founder memoirs) create **hindsight coherence**, hiding luck, timing, and failed peers who copied identical tactics.
- **Counter-Reading (Boeing 737 MAX):** Audit public statements against internal records to expose euphemistic framing (`"crew workload enhancements"` masking defect corrections).

---

## Module 3: Constructing & Evaluating Arguments

- **C-E-R Triad:** **Claim** (what to believe) + **Evidence** (data/observations) + **Reasoning** (why evidence supports claim + **unstated assumptions**, e.g., Netflix 2006 assuming studio licensing & bandwidth reliability).
- **Toulmin's 6-Part Argument Model:**
  1. **Claim** (conclusion) | 2. **Grounds** (evidence/data) | 3. **Warrant** (logical principle bridging Grounds -> Claim) | 4. **Backing** (evidence proving the Warrant) | 5. **Qualifier** (`"probably"`, `"under normal tariffs"`) | 6. **Rebuttal** (boundary conditions where the claim fails).
- **Deductive vs. Inductive:**
  - **Deductive:** General rule -> necessary conclusion. **Valid** = conclusion follows from premises; **Sound** = Valid **AND** factually true premises. *(An argument can be Valid yet Unsound!)*
  - **Inductive:** Sample observations -> probable forecast (strength depends on sample representativeness, zero selection bias, and size).
- **Rhetorical Appeals:** **Ethos** (credibility) + **Pathos** (emotion) win attention, but collapse under due diligence without **Logos** (unit economics & verifiable evidence).

---

## Module 4: Fallacies & Cognitive Biases (Highest MCQ Yield)

### 4.1 Cognitive Biases (System 1 vs. System 2)
- **WYSIATI (What You See Is All There Is):** System 1 builds confident stories solely from visible facts, ignoring missing data and base rates.
- **Base Rate Neglect:** Ignoring a low prior probability (e.g., 2% true stars) when interpreting a 90%-accurate screening tool.
- **Sunk Cost Fallacy:** Pouring cash into a losing route/project because of past unrecoverable spend instead of marginal future NPV.
- **Availability Heuristic:** Overweighting vivid headlines (two viral EV fires) over fleet failure rates per million km.
- **Anchoring Bias:** First number on the table pulls final negotiation estimates insufficiently adjusted from it.
- **Planning Fallacy:** Optimistic "inside view" timelines ignoring historical reference-class duration ("outside view").
- **Hindsight Bias:** Rewriting uncertain past decisions as `"obvious from Day 1"` after seeing failure.

### 4.2 Logical Fallacies & Debate Tactics

| Fallacy / Tactic | Exact Mechanism |
|---|---|
| **Post Hoc Ergo Propter Hoc** | Assuming A caused B solely because A happened before B |
| **False Dilemma** | Forcing a fake two-choice extreme (`"cut 40% or go bankrupt"`) |
| **Slippery Slope** | Claiming a modest step inevitably triggers catastrophe without proving intermediate links |
| **Circular Reasoning** | Restating the conclusion as its own premise (`"trustworthy because people can trust us"`) |
| **Equivocation** | Shifting a word's meaning mid-argument (`"nothing is better than..."`) |
| **Bandwagon (Ad Populum)** | Copying peers (`"everyone runs Insta ads"`) without testing your own ICP fit |
| **Tu Quoque** | Deflecting critique by accusing the critic of past hypocrisy |
| **Ad Hominem vs. COI** | Attacking unrelated personal traits = Ad Hominem; exposing financial conflict of interest = **valid credibility check** |
| **Strawman vs. Steelman** | Strawman distorts opponent's weakest caricature; **Steelman** reconstructs their strongest case before countering |

---

## Module 5: Expertise, Authority & Value

- **Appeal to False Authority:** Citing prestige outside domain competence (e.g., cricketer endorsing crypto yields) or ignoring paid advisory conflicts of interest.
- **Credibility Audit:** Check sample size, control-group blinding, funding source/COI, and independent replication.
- **Fact-Value Distinction:** Empirical facts describe what **is** (cost savings); strategic/CSR choices require values defining what **ought** to be prioritized (worker welfare vs. short-term margin).
- **Epistemic Humility:** State explicit conditions under which your forecast would be falsified and update priors when disconfirming evidence arrives.

---

## Module 6: Analytical & Cross-Cultural Thinking

- **Nyaya 5-Step Inference vs. 3-Step Western Syllogism:** Nyaya adds **Udaharana** (a concrete shared empirical example grounding the universal causal rule *Vyapti*), uniting deductive structure with observational verification.
- **High-Context & Authority Bias (Nyaya Tarka):** In hierarchical settings, public contradiction causes loss of face; use private pre-meeting collaborative hypothesis testing to surface flaws safely.
- **Complexity vs. Confusion:** Systemic complexity comes from interdependent variables; confusion comes from vague terms and mixed units.
- **Blurry JPEG Heuristic:** Repeated executive summarization compresses away critical edge cases, creating false certainty.
- **Danger of a Single Story:** Flattening diverse regions/customers into one stereotype causes mispricing and missed niches.

---

## Module 7 & Module 8: Organisations & Critical Thinking in Practice

- **Organizational Accountability Audit:** Test espoused values (`"meritocratic learning culture"`) against observable promotion records and internal memos.
- **Fixing Groupthink:** Voluntary courage fails against hierarchy. Institute **Structural Devil's Advocacy**, protected **Safety Sign-Off** reporting to the Board Risk Committee, and **Pre-Mortems** (imagine failure 1 year ahead to legitimize risk discovery pre-launch).
- **Hustle Culture Premise Problem:** Falsely equates hours worked with value created; chronic fatigue degrades System 2 error-checking. **Strategic rest** preserves analytical rigor.
- **Practical Case Takeaways (M8):**
  - *Whites & Pastels:* Use physical prototypes + contextual observation to bridge the **Exposure Gap**.
  - *Kolhapuri Artisans:* Do not destroy craft authenticity with synthetic shortcuts; solve lead-time cash strain via milestone working-capital advances.
  - *Sangeeta Menon:* Frontline supplier listening catches operational red flags months before lagging quarterly financials.
  - *CSR Framing:* Judge social initiatives on measured beneficiary impact, not executive affinity.

---

## Last-15-Minute Exam Trap Radar

1. **Sec B (20-30w) & Sec C (40-50w):** Never pad with long intros—hit **Framework -> Diagnosis -> Fix/Risk** immediately.
2. **Valid != Sound:** Valid arguments can have false premises.
3. **Warrant vs. Backing:** Warrant = reasoning bridge; Backing = evidence supporting that bridge.
4. **Ad Hominem Trap:** Calling out a paid advisory Conflict of Interest is **NOT** Ad Hominem.
5. **Confirmation Bias vs. Motivated Reasoning:** Passive selective attention vs. active defense of desired outcome.
"""


def main():
    err = check_katex_expressions(ONE_SHOT_MD)
    assert not err, f"KaTeX error: {err}"
    wc = len(ONE_SHOT_MD.split())
    print(f"Critical Thinking One-Shot word count: {wc} words (down from 8,169 words!)")
    db.save_course_one_shot(COURSE_ID, ONE_SHOT_MD, "")
    db.export_static_data()
    print("Saved to DB and exported study_data.js cleanly.")


if __name__ == "__main__":
    main()
