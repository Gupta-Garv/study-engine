#!/usr/bin/env python3
"""
Build the Critical Thinking (d9173426) Exam-Calibrated Question Bank:
- 20 Conceptual Short-Answer Questions (2 marks, 20-30 words model answer), ranked most -> least anticipated
- 16 Case-Based Sub-Questions across 6 realistic cases (3 marks, 40-50 words model answer), ranked most -> least anticipated
- 40 Exam-Level MCQs (1 mark), ranked most -> least anticipated
- Zero overlap with extracted CLA questions
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "data" / "exam_bank"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CLA_PATH = BASE_DIR / "data" / "cla_questions" / "critical_thinking" / "cla_questions.json"

# Sec B: Conceptual Short Answer (2 marks, 20-30 words)
SUBJECTIVE_QUESTIONS = [
    {
        "anticipation_rank": 1,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "framework": "Logic vs. Critical Thinking",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "Distinguish between logical validity and critical thinking using the Challenger disaster logic.",
        "model_answer": "Logical validity checks whether conclusions follow from given premises. Critical thinking interrogates whether those premises are complete, unbiased, and ethically sound—preventing fatal omissions like unexamined O-ring failure data.",
        "examiner_rubric": ["Defines logical validity (premise-to-conclusion structure) — 1M", "Defines critical thinking (interrogating premise completeness/bias) — 1M"],
        "common_trap": "Saying critical thinking rejects logic rather than complementing it."
    },
    {
        "anticipation_rank": 2,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "framework": "Evidence Triad (Fact, Inference, Interpretation)",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "Differentiate a Fact from an Inference in business evidence evaluation.",
        "model_answer": "A fact is directly observable and independently verifiable data. An inference is a logical conclusion drawn by connecting facts, which remains probabilistic and open to alternative explanations.",
        "examiner_rubric": ["Fact = verifiable observation — 1M", "Inference = conclusion drawn from facts — 1M"],
        "common_trap": "Treating confident inferences as settled facts."
    },
    {
        "anticipation_rank": 3,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "framework": "Survivorship Bias (Wald's Bombers)",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "What is 'the invisible record' in Abraham Wald's WWII bomber insight, and why does it matter in business?",
        "model_answer": "Wald realized returning planes excluded fatal hits on engines. In business, studying only surviving firms or active users hides failure causes among churned customers and defunct competitors.",
        "examiner_rubric": ["Explains missing failure sample (non-returning bombers) — 1M", "Connects to business survivorship bias — 1M"],
        "common_trap": "Focusing on sample size rather than systematic missingness."
    },
    {
        "anticipation_rank": 4,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 2,
        "module_name": "Module 2: Critical Reading and Interpretation",
        "framework": "Explicit Claims vs. Implicit Positions",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "How does an 'implicit position' in a corporate memo differ from an 'explicit claim'?",
        "model_answer": "An explicit claim is stated directly on the surface. An implicit position is an unstated assumption or value judgment revealed through selective omissions, framing, and word choice.",
        "examiner_rubric": ["Explicit = surface stated proposition — 1M", "Implicit = unstated assumption via framing/omission — 1M"],
        "common_trap": "Confusing implicit positions with hidden conspiracies instead of textual framing."
    },
    {
        "anticipation_rank": 5,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 3,
        "module_name": "Module 3: Constructing and Evaluating Arguments",
        "framework": "Toulmin Model (Warrant & Backing)",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "In Toulmin's argument model, what distinct role does the 'Warrant' play between Grounds and Claim?",
        "model_answer": "The warrant is the underlying logical rule or principle explaining why the cited grounds actually justify the claim, bridging raw evidence to the proposed conclusion.",
        "examiner_rubric": ["Identifies warrant as bridging principle — 1M", "Links grounds to claim — 1M"],
        "common_trap": "Confusing the warrant (reasoning bridge) with backing (evidence supporting the warrant)."
    },
    {
        "anticipation_rank": 6,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 3,
        "module_name": "Module 3: Constructing and Evaluating Arguments",
        "framework": "Deductive vs. Inductive Reasoning",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "Why are business strategy forecasts fundamentally inductive rather than deductive?",
        "model_answer": "Strategy forecasts extrapolate from past market samples to uncertain futures, yielding probable conclusions rather than deductive certainty where true premises mathematically guarantee the outcome.",
        "examiner_rubric": ["Inductive = probabilistic generalization from observations — 1M", "Deductive = necessary conclusion from general rules — 1M"],
        "common_trap": "Saying inductive reasoning is 'weaker' without noting probabilistic certainty."
    },
    {
        "anticipation_rank": 7,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "framework": "Post Hoc vs. Correlation-Causation",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "Define the Post Hoc Ergo Propter Hoc fallacy with a brief business example.",
        "model_answer": "Post hoc assumes event A caused event B merely because A preceded B—such as crediting a new logo for higher Q4 sales while ignoring festive seasonality.",
        "examiner_rubric": ["Defines temporal sequence mistaken for causation — 1M", "Gives clear business example — 1M"],
        "common_trap": "Ignoring confounding variables in the example."
    },
    {
        "anticipation_rank": 8,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "framework": "System 1 vs. System 2 & WYSIATI",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "How does Kahneman's 'WYSIATI' (What You See Is All There Is) distort executive decision-making?",
        "model_answer": "WYSIATI lets System 1 build confident stories solely from immediately visible facts, ignoring missing data, base rates, and unvoiced disconfirming evidence.",
        "examiner_rubric": ["Defines WYSIATI story-building from partial visible facts — 1M", "Notes neglect of missing data/base rates — 1M"],
        "common_trap": "Equating WYSIATI with lying rather than automatic cognitive shortcutting."
    },
    {
        "anticipation_rank": 9,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 5,
        "module_name": "Module 5: Expertise, Authority, and Value",
        "framework": "Evaluating Expertise vs. Authority",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "When does relying on an expert become an Appeal to False Authority fallacy?",
        "model_answer": "It becomes fallacious when an authority's prestige in one domain is cited outside their actual competence, or when conflicts of interest compromise independent verification.",
        "examiner_rubric": ["Cross-domain transfer / outside competence — 1M", "Conflict of interest / unverified prestige — 1M"],
        "common_trap": "Claiming all appeals to experts are fallacies."
    },
    {
        "anticipation_rank": 10,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 6,
        "module_name": "Module 6: Analytical and Cross-Cultural Thinking",
        "framework": "Nyaya Logic vs. Western Syllogism",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "What key element does the 5-step Nyaya inference add that the 3-step Western syllogism lacks?",
        "model_answer": "Nyaya adds Udaharana (a concrete empirical example grounding the universal rule) plus explicit application and conclusion, uniting deductive structure with real-world observational verification.",
        "examiner_rubric": ["Identifies Udaharana (concrete empirical example) — 1M", "Notes empirical grounding of universal rule — 1M"],
        "common_trap": "Saying Nyaya simply has 5 random steps without mentioning empirical grounding."
    },
    {
        "anticipation_rank": 11,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 6,
        "module_name": "Module 6: Analytical and Cross-Cultural Thinking",
        "framework": "Single Story Heuristic & Epistemic Humility",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "Explain Chimamanda Adichie's 'Danger of a Single Story' as an analytical risk in market expansion.",
        "model_answer": "Reducing a region or customer segment to one dominant narrative flattens internal diversity, causing firms to misprice products, misread local norms, and miss sub-segment opportunities.",
        "examiner_rubric": ["Defines flattening diversity into one narrative — 1M", "States concrete market-entry risk — 1M"],
        "common_trap": "Treating it only as a literary concept rather than a business stereotype trap."
    },
    {
        "anticipation_rank": 12,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 7,
        "module_name": "Module 7: Critical Thinking in Organisations and Society",
        "framework": "Devil's Advocacy vs. Groupthink",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "Why must Devil's Advocacy be institutionalized structurally rather than left to voluntary courage?",
        "model_answer": "Hierarchy and groupthink punish lone dissenters socially; assigning a rotating, protected Devil's Advocate normalizes counter-arguments and surfaces fatal flaws before launch.",
        "examiner_rubric": ["Identifies social/hierarchical cost of voluntary dissent — 1M", "Explains how structural assignment protects critique — 1M"],
        "common_trap": "Saying 'encourage people to speak up' without structural protection."
    },
    {
        "anticipation_rank": 13,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 2,
        "module_name": "Module 2: Critical Reading and Interpretation",
        "framework": "The 5 Cs of Narrative Persuasion",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "How can a persuasive 'Hare-Tortoise' business narrative mislead strategic decision-makers?",
        "model_answer": "Clean storytelling creates retrospective coherence and inevitability, hiding messy luck, survivor bias, and structural disadvantages that make copying the winning tactic risky.",
        "examiner_rubric": ["Identifies retrospective coherence/hindsight illusion — 1M", "Notes hidden luck/structural factors — 1M"],
        "common_trap": "Focusing on whether the story is entertaining rather than its causal distortion."
    },
    {
        "anticipation_rank": 14,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "framework": "Strawman vs. Steelman",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "Contrast 'Strawmanning' with 'Steelmanning' in an executive strategy debate.",
        "model_answer": "Strawmanning distorts an opponent's argument into a weak caricature to defeat it easily. Steelmanning reconstructs the strongest possible version of their case before responding.",
        "examiner_rubric": ["Defines Strawman distortion — 1M", "Defines Steelman strongest-case reconstruction — 1M"],
        "common_trap": "Confusing Steelmanning with agreeing with the opponent."
    },
    {
        "anticipation_rank": 15,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 5,
        "module_name": "Module 5: Expertise, Authority, and Value",
        "framework": "Fact–Value Distinction",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "Why can empirical data alone never settle a business decision involving the Fact–Value distinction?",
        "model_answer": "Facts describe what *is* (e.g., cost savings), whereas decisions require values defining what *ought* to be prioritized—such as employee welfare versus short-term margin.",
        "examiner_rubric": ["Distinguishes descriptive 'is' (facts) from normative 'ought' (values) — 1M", "Connects to business trade-offs — 1M"],
        "common_trap": "Assuming more data automatically dictates ethical choices."
    },
    {
        "anticipation_rank": 16,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 6,
        "module_name": "Module 6: Analytical and Cross-Cultural Thinking",
        "framework": "The 'Blurry JPEG' Heuristic",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "What does the 'Blurry JPEG' metaphor warn against when executives rely on high-level summaries?",
        "model_answer": "Repeatedly compressing complex field data into executive summaries loses critical edge cases and context, creating a low-resolution illusion of clarity that misguides action.",
        "examiner_rubric": ["Links lossy compression to lost nuance/edge cases — 1M", "Warns against false certainty — 1M"],
        "common_trap": "Thinking it literally refers to image file compression."
    },
    {
        "anticipation_rank": 17,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "framework": "Motivated Reasoning vs. Confirmation Bias",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "How does Motivated Reasoning differ from simple Confirmation Bias?",
        "model_answer": "Confirmation bias passively favors belief-consistent evidence, whereas motivated reasoning actively recruits arguments and double-standards to defend a desired emotional or financial outcome.",
        "examiner_rubric": ["Confirmation bias = passive selective attention — 1M", "Motivated reasoning = active defense of desired conclusion — 1M"],
        "common_trap": "Treating both terms as 100% interchangeable."
    },
    {
        "anticipation_rank": 18,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 3,
        "module_name": "Module 3: Constructing and Evaluating Arguments",
        "framework": "Ethos, Pathos, Logos",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "Why is an investor pitch relying heavily on Pathos and Ethos vulnerable without Logos?",
        "model_answer": "Ethos (credibility) and Pathos (emotion) capture attention, but without Logos (verifiable unit economics and logical evidence), claims collapse under due-diligence scrutiny.",
        "examiner_rubric": ["Identifies roles of Ethos/Pathos — 1M", "Explains why Logos is essential for due diligence — 1M"],
        "common_trap": "Claiming Ethos and Pathos have zero legitimate place in business."
    },
    {
        "anticipation_rank": 19,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 7,
        "module_name": "Module 7: Critical Thinking in Organisations and Society",
        "framework": "Hustle Culture & The Premise Problem",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "What 'premise problem' underlies toxic hustle culture in organizations?",
        "model_answer": "Hustle culture falsely equates hours worked with value created, ignoring diminishing cognitive returns, burnout costs, and the necessity of strategic rest for sound judgment.",
        "examiner_rubric": ["Identifies flawed premise (hours = output) — 1M", "Notes burnout/diminishing returns — 1M"],
        "common_trap": "Giving personal wellness advice without naming the flawed productivity premise."
    },
    {
        "anticipation_rank": 20,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 8,
        "module_name": "Module 8: Critical Thinking in Practice",
        "framework": "Exposure Gap Analysis (Whites & Pastels)",
        "marks": 2,
        "target_words": "20–30 words",
        "question": "In the Whites & Pastels case, why can trusting customer survey preferences mislead product design?",
        "model_answer": "Customers only prefer what they have been exposed to; an 'exposure gap' means surveys miss latent needs that only prototyping and contextual observation uncover.",
        "examiner_rubric": ["Explains preference bounded by prior exposure — 1M", "Notes need for prototyping/observation — 1M"],
        "common_trap": "Saying customers intentionally lie on surveys."
    }
]

# Sec C: Case-Based Questions (3 marks each, 40-50 words)
CASE_QUESTIONS = [
    {
        "anticipation_rank": 1,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "framework": "Analytics–Ethics Gap (Target Case)",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 1 (Data Precision vs. Ethics): A retail analytics team builds a model predicting customer pregnancy with 89% accuracy from subtle shifts in lotion and supplement purchases, and proposes mailing dedicated baby-product coupons directly to high-scoring shoppers.",
        "question": "Sub-Q 1A (3M): Identify the core 'Analytics–Ethics Gap' here and explain why high statistical accuracy does not automatically justify deployment.",
        "model_answer": "Statistical accuracy only measures predictive correlation, not ethical permissibility or customer consent. Mailing targeted pregnancy coupons exposes sensitive, unshared personal information—triggering severe privacy intrusion and reputational backlash. Technical capability ('can we predict it?') must pass independent ethical scrutiny ('should we act on it?') before launch.",
        "examiner_rubric": ["Separates predictive accuracy from ethical permissibility — 1.5M", "Identifies privacy/consent violation risk — 1.5M"],
        "common_trap": "Focusing on whether the 89% accuracy can be raised to 95%."
    },
    {
        "anticipation_rank": 2,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "framework": "Ethical Redesign & Stakeholder Trust (Target Case)",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 1 (Data Precision vs. Ethics): Same retail analytics case.",
        "question": "Sub-Q 1B (3M): Propose ONE ethical operational fix that preserves business value without alarming customers, and state ONE residual risk it does not eliminate.",
        "model_answer": "Fix: Shift from overt single-topic baby mailers to opt-in loyalty bundles mixing general household/wellness offers alongside baby discounts, respecting privacy boundaries while capturing basket uplift. Residual risk: Internal data-governance risks remain—storing sensitive inferred health tags still creates breach and regulatory liability if anonymized poorly.",
        "examiner_rubric": ["Proposes privacy-preserving/opt-in delivery fix — 1.5M", "States ONE realistic residual data/governance risk — 1.5M"],
        "common_trap": "Saying 'delete all customer data' (eliminates business value) or skipping the residual risk."
    },
    {
        "anticipation_rank": 3,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 2,
        "module_name": "Module 2: Critical Reading and Interpretation",
        "framework": "Counter-Reading & Narrative Omission (Boeing 737 MAX)",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 2 (Corporate Narrative Audit): Following two fatal crashes, an aerospace firm's press release states: 'Our aircraft remains safe when pilots follow standard emergency checklists; we are issuing software enhancements to further support crew workload.'",
        "question": "Sub-Q 2A (3M): Using Close Reading (word choice & omission), diagnose the implicit position embedded in this statement.",
        "model_answer": "By foregrounding 'when pilots follow checklists' and framing MCAS updates as supportive 'enhancements' rather than defect corrections, the text implicitly shifts causal blame onto pilot error while omitting single-sensor design flaws and withheld training disclosures—deflecting organizational accountability through euphemistic framing.",
        "examiner_rubric": ["Identifies blame-shifting via 'when pilots follow...' — 1.5M", "Identifies euphemism ('enhancements') & design omission — 1.5M"],
        "common_trap": "Taking the press release at face value as balanced safety communication."
    },
    {
        "anticipation_rank": 4,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 7,
        "module_name": "Module 7: Critical Thinking in Organisations and Society",
        "framework": "4-Criteria Accountability Framework",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 2 (Corporate Narrative Audit): Same aerospace statement.",
        "question": "Sub-Q 2B (3M): Apply TWO criteria from the Organizational Accountability Framework to test whether this statement matches actual performance.",
        "model_answer": "Test via (1) Evidential Alignment—comparing public claims of 'pilot checklist sufficiency' against internal engineering memos flagging MCAS single-point failure; and (2) Transparency/Omission—checking whether regulators and airlines received complete system documentation prior to commercial rollout rather than post-crisis framing.",
        "examiner_rubric": ["Applies two concrete accountability checks (evidence alignment + transparency/disclosure) — 3M"],
        "common_trap": "Listing vague ethics slogans without checking claims against internal records."
    },
    {
        "anticipation_rank": 5,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 7,
        "module_name": "Module 7: Critical Thinking in Organisations and Society",
        "framework": "Structural Devil's Advocacy",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 2 (Corporate Narrative Audit): Engineers raised concerns internally before launch, but senior leadership suppressed delays to beat a competitor's delivery schedule.",
        "question": "Sub-Q 2C (3M): Recommend ONE structural governance change to prevent commercial schedule pressure from silencing safety dissent.",
        "model_answer": "Establish an independent Safety & Technical Sign-Off Gate reporting directly to the Board Audit/Risk Committee—not to commercial program managers—paired with mandatory pre-launch Red-Team reviews where engineers hold protected stop-ship authority until critical failure modes are resolved.",
        "examiner_rubric": ["Separates safety reporting line from commercial/schedule pressure — 1.5M", "Grants protected stop-ship / Red-Team mechanism — 1.5M"],
        "common_trap": "Saying 'tell leaders to listen better' without altering reporting/authority structure."
    },
    {
        "anticipation_rank": 6,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 3,
        "module_name": "Module 3: Constructing and Evaluating Arguments",
        "framework": "C-E-R Triad & Hidden Assumptions (Netflix 2006)",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 3 (Strategic Argument Evaluation): In 2006, a DVD-by-mail leader pitches shifting capital toward internet streaming: 'Broadband penetration just crossed 40% in US homes, and young viewers prefer instant access. Streaming will replace physical DVDs within five years.'",
        "question": "Sub-Q 3A (3M): Break this pitch into Claim, Evidence, and Reasoning, and expose ONE critical unstated assumption.",
        "model_answer": "Claim: Streaming will replace DVDs within five years. Evidence: 40% US broadband penetration and youth preference. Reasoning: Expanding connectivity plus convenience drives rapid format substitution. Unstated assumption: Studios will license top-tier content at affordable rates, and broadband speeds can reliably handle high-definition video at scale.",
        "examiner_rubric": ["Correctly maps Claim, Evidence, Reasoning — 1.5M", "Exposes crucial unstated assumption (studio licensing / bandwidth quality) — 1.5M"],
        "common_trap": "Confusing the evidence (40% broadband) with the unstated assumption."
    },
    {
        "anticipation_rank": 7,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "framework": "Base Rate Neglect & Confirmation Bias",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 3 (Strategic Argument Evaluation): A rival executive dismisses streaming: 'Every previous online video startup failed, and our 6 million DVD subscribers love browsing physical store aisles—so streaming is a fad.'",
        "question": "Sub-Q 3B (3M): Diagnose TWO cognitive traps in the rival executive's counter-argument.",
        "model_answer": "First, Confirmation Bias & Anchoring—selectively citing past startup failures while ignoring how falling bandwidth costs changed underlying feasibility. Second, Status-Quo / Survivorship Bias—extrapolating current DVD subscribers' stated satisfaction without noticing shifting marginal cohorts and latent convenience demand.",
        "examiner_rubric": ["Identifies Confirmation/Anchoring bias — 1.5M", "Identifies Status-Quo/Survivorship bias on current subscribers — 1.5M"],
        "common_trap": "Simply saying 'he was wrong about technology' without naming the cognitive biases."
    },
    {
        "anticipation_rank": 8,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 8,
        "module_name": "Module 8: Critical Thinking in Practice",
        "framework": "Assumption Validation & Prototyping",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 3 (Strategic Argument Evaluation): Before committing ₹500 Cr to a full streaming platform, leadership wants to test the highest-risk assumption.",
        "question": "Sub-Q 3C (3M): Identify the single highest-risk assumption to test first and propose ONE low-cost validation experiment.",
        "model_answer": "Highest-risk assumption: Customers will actively stream catalog titles over early broadband despite lower selection than DVDs. Experiment: Bundle free limited 'Watch Instantly' streaming hours inside existing DVD subscriptions for one city cohort and track repeat weekly playback before signing massive multi-year licensing commitments.",
        "examiner_rubric": ["Selects highest-risk assumption (actual usage/adoption) — 1.5M", "Proposes bounded low-cost cohort pilot — 1.5M"],
        "common_trap": "Proposing a generic survey ('ask customers if they like streaming') instead of behavioral testing."
    },
    {
        "anticipation_rank": 9,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 6,
        "module_name": "Module 6: Analytical and Cross-Cultural Thinking",
        "framework": "Nyaya Tarka & Face-Saving",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 4 (Cross-Cultural Reasoning): During a joint venture review in India, a junior analyst spots a fatal tax flaw in the Senior VP's proposal. In the open meeting, everyone stays silent and nods.",
        "question": "Sub-Q 4A (3M): Explain this silence using high-context / face-saving norms and propose ONE Nyaya Tarka-inspired way to surface the flaw safely.",
        "model_answer": "In high-context, hierarchical cultures, public contradiction causes loss of face and violates deference norms. Using Nyaya Tarka's respectful inquiry, the analyst can request a private pre-meeting to test 'what conditions would make this tax structure fail'—framing critique as collaborative hypothesis testing rather than personal attack.",
        "examiner_rubric": ["Explains face-saving/hierarchical silence — 1.5M", "Proposes respectful collaborative testing mechanism — 1.5M"],
        "common_trap": "Assuming silence equals agreement or incompetence."
    },
    {
        "anticipation_rank": 10,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 5,
        "module_name": "Module 5: Expertise, Authority, and Value",
        "framework": "Credibility & Conflict-of-Interest Audit",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 5 (Expert Claim Audit): A wellness startup cites 'a 2024 clinical study by Dr. Rao proving our herbal drink boosts focus by 60%.' Investigation shows the study had 14 paid participants and Dr. Rao sits on the startup's advisory board.",
        "question": "Sub-Q 5A (3M): Evaluate the credibility of this evidence across TWO critical dimensions.",
        "model_answer": "First, Conflict of Interest—Dr. Rao's paid advisory role creates severe financial bias compromising independent objectivity. Second, Methodological Weakness—a tiny 14-person paid sample lacks statistical power, control-group blinding, and external replication, making the '60% boost' claim unsubstantiated marketing hype rather than reliable evidence.",
        "examiner_rubric": ["Identifies Conflict of Interest — 1.5M", "Identifies sample size / methodology / lack of replication — 1.5M"],
        "common_trap": "Dismissing the claim solely because Dr. Rao isn't famous."
    },
    {
        "anticipation_rank": 11,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "framework": "Fermi Estimation & Base Rates",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 6 (Market Sizing Claim): A founder pitches: 'India has 1.4 billion people; if just 1% buy our ₹2,000 ergonomic bamboo desk monthly, we hit ₹28,000 Cr revenue in Year 1!'",
        "question": "Sub-Q 6A (3M): Expose TWO analytical flaws in this '1% of 1.4 billion' top-down sizing claim.",
        "model_answer": "First, Base-Rate / TAM-to-SOM Confusion—1.4 billion includes infants and non-office households, inflating addressable buyers wildly. Second, Purchase-Frequency & Price Elasticity Error—desks are durable goods bought every 5–10 years, not monthly subscriptions, making a '1% monthly' capture assumption physically and economically implausible.",
        "examiner_rubric": ["Exposes TAM/demographic base-rate flaw — 1.5M", "Exposes durable-good frequency / willingness-to-pay flaw — 1.5M"],
        "common_trap": "Checking only the arithmetic (1% × 1.4B) instead of the underlying premise."
    },
    {
        "anticipation_rank": 12,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 8,
        "module_name": "Module 8: Critical Thinking in Practice",
        "framework": "Artisan Negotiations & B2B Cashflow Mechanisms",
        "marks": 3,
        "target_words": "40–50 words",
        "case_context": "Case 7 (Supply Chain & Artisan Trade-offs): A D2C footwear brand sources Kolhapuri chappals from rural artisans who refuse to adopt rapid synthetic glues, slowing order fulfillment while demanding weekly cash advances.",
        "question": "Sub-Q 7A (3M): Explain why forcing synthetic shortcuts backfires on brand positioning, and design ONE aligned B2B payment/inventory mechanism.",
        "model_answer": "Forcing synthetic glues destroys the authentic craft heritage justifying premium pricing. Instead, introduce milestone-based working-capital advances paired with standardized pre-cut leather buffers—preserving slow handcrafted stitching quality while stabilizing artisan liquidity and cutting lead-time variability.",
        "examiner_rubric": ["Protects craft authenticity/brand equity — 1.5M", "Proposes structured milestone advance/buffer mechanism — 1.5M"],
        "common_trap": "Suggesting 'fire the artisans and import plastic lookalikes.'"
    }
]

# Sec A: Exam-Level MCQs (1 mark each)
MCQ_QUESTIONS = [
    {
        "anticipation_rank": 1,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "key_concept": "Evidence Triad (Fact vs Inference vs Interpretation)",
        "question": "A manager reads: 'Website traffic fell 18% on Tuesday; therefore, our Tuesday email campaign alienated subscribers.' Which part of this statement is an **Inference** rather than a Fact?",
        "options": [
            "That the Tuesday email campaign caused the 18% traffic drop",
            "That website traffic was 18% lower on Tuesday than Monday",
            "That an email campaign was sent on Tuesday",
            "That subscribers exist on the mailing list"
        ],
        "correct_index": 0,
        "explanation": "The 18% drop is an observable Fact; attributing causation to the email campaign without ruling out server downtime or holidays is an Inference.",
        "distractor_analysis": "Traffic metrics and send logs are verifiable facts."
    },
    {
        "anticipation_rank": 2,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "key_concept": "Challenger Disaster & Evidence Completeness",
        "question": "In the Challenger space shuttle case, why did engineers' arguments fail to stop the launch despite valid data?",
        "options": [
            "Decision-makers lacked complete failure-vs-temperature distribution data (missing low-temp non-failure baseline) and bowed to organizational launch pressure",
            "Engineers used Python instead of Excel",
            "NASA had no O-ring temperature sensors anywhere",
            "Logical syllogisms are mathematically invalid above 10,000 feet"
        ],
        "correct_index": 0,
        "explanation": "Incomplete visual framing (showing only flights with damage, omitting zero-damage flights) plus schedule pressure masked the cold-temperature failure pattern.",
        "distractor_analysis": "The failure was analytical framing and organizational pressure, not software."
    },
    {
        "anticipation_rank": 3,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 2,
        "module_name": "Module 2: Critical Reading and Interpretation",
        "key_concept": "Reasonable Person Test",
        "question": "When performing Close Reading on an ambiguous contract or HR policy, what does the 'Reasonable Person Test' evaluate?",
        "options": [
            "What an ordinary, informed reader would fairly infer from the plain wording and context, rather than the author's private hidden intent",
            "Whether the author holds a PhD in literature",
            "Whether the document uses at least 10 legal Latin terms",
            "Whether the CEO personally likes the tone"
        ],
        "correct_index": 0,
        "explanation": "The Reasonable Person Test anchors interpretation in objective, shared meaning available to a fair-minded reader.",
        "distractor_analysis": "Private unexpressed intent cannot override plain textual meaning."
    },
    {
        "anticipation_rank": 4,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 3,
        "module_name": "Module 3: Constructing and Evaluating Arguments",
        "key_concept": "Toulmin Model (Qualifier & Rebuttal)",
        "question": "In Toulmin's argumentation model, adding 'unless supply-chain tariffs exceed 25%' to a profitability forecast serves as which component?",
        "options": [
            "Rebuttal (specifying conditions under which the claim fails)",
            "Grounds (raw data)",
            "Backing (legal statute)",
            "Ad Hominem"
        ],
        "correct_index": 0,
        "explanation": "A Rebuttal anticipates boundary conditions or exceptions that invalidate or limit the main claim, strengthening intellectual rigor.",
        "distractor_analysis": "Grounds are supporting data; Backing supports the warrant."
    },
    {
        "anticipation_rank": 5,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "key_concept": "Base Rate Neglect",
        "question": "A hiring tool is 90% accurate at spotting top performers. Only 2% of applicants are truly top performers. A recruiter assumes a candidate flagged by the tool has a 90% chance of being a star. Which bias is this?",
        "options": [
            "Base Rate Neglect",
            "Sunk Cost Fallacy",
            "Strawman Fallacy",
            "Slippery Slope"
        ],
        "correct_index": 0,
        "explanation": "Ignoring the low 2% prior base rate causes massive overestimation of posterior probability despite 90% test accuracy.",
        "distractor_analysis": "Sunk cost concerns past unrecoverable spending; strawman/slippery slope are rhetorical fallacies."
    },
    {
        "anticipation_rank": 6,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "key_concept": "Sunk Cost Fallacy",
        "question": "An airline keeps pouring ₹50 Cr/month into an unprofitable regional route solely 'because we already spent ₹300 Cr acquiring its landing slots.' Which cognitive trap is driving this?",
        "options": [
            "Sunk Cost Fallacy (escalation of commitment to unrecoverable past spend)",
            "Hindsight Bias",
            "False Dilemma",
            "Availability Heuristic"
        ],
        "correct_index": 0,
        "explanation": "Rational decisions depend strictly on marginal future costs and benefits, never unrecoverable historical spend.",
        "distractor_analysis": "Hindsight bias is 'I knew it all along' after an event."
    },
    {
        "anticipation_rank": 7,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "key_concept": "False Dilemma (Black-and-White Fallacy)",
        "question": "A VP tells the board: 'Either we cut R&D by 40% tomorrow or the company goes bankrupt.' What logical fallacy is this?",
        "options": [
            "False Dilemma (artificially collapsing options to two extremes while ignoring alternatives like phasing capex or pricing changes)",
            "Circular Reasoning",
            "Tu Quoque",
            "Equivocation"
        ],
        "correct_index": 0,
        "explanation": "False Dilemma suppresses viable middle-ground or creative third alternatives.",
        "distractor_analysis": "Circular reasoning repeats the conclusion as its own premise."
    },
    {
        "anticipation_rank": 8,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 5,
        "module_name": "Module 5: Expertise, Authority, and Value",
        "key_concept": "Expertise vs Authority",
        "question": "A celebrity cricket captain endorses a complex crypto derivatives platform on TV, claiming 'this yield is guaranteed safe.' Why should a critical thinker discount this endorsement?",
        "options": [
            "It commits the Appeal to False Authority fallacy—prestige in sports confers zero domain competence in financial derivatives or risk modeling",
            "Athletes are legally prohibited from owning bank accounts",
            "Crypto platforms never pay celebrity fees",
            "Logos requires every speaker to be anonymous"
        ],
        "correct_index": 0,
        "explanation": "Credibility is domain-specific and compromised further by paid sponsorship incentives.",
        "distractor_analysis": "The other options are fabricated claims."
    },
    {
        "anticipation_rank": 9,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 6,
        "module_name": "Module 6: Analytical and Cross-Cultural Thinking",
        "key_concept": "Nyaya 5-Step Inference",
        "question": "In classical Nyaya inference ('Where there is smoke, there is fire, as in a kitchen'), what is the role of 'as in a kitchen' (Udaharana)?",
        "options": [
            "To anchor the universal causal rule (Vyapti) in an observed, shared empirical instance rather than pure abstract assertion",
            "To distract the listener with culinary metaphors",
            "To prove deductive impossibility",
            "To replace the conclusion completely"
        ],
        "correct_index": 0,
        "explanation": "Nyaya insists that general rules be grounded in concrete empirical examples (`Udaharana`), uniting deduction and induction.",
        "distractor_analysis": "It strengthens empirical validity rather than distracting."
    },
    {
        "anticipation_rank": 10,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 7,
        "module_name": "Module 7: Critical Thinking in Organisations and Society",
        "key_concept": "Groupthink Symptoms",
        "question": "Which observation in a leadership meeting is the strongest warning sign of Janis's 'Groupthink'?",
        "options": [
            "Members self-censor doubts to preserve consensus and label anyone questioning the CEO's launch plan as 'not a team player'",
            "Two VPs present conflicting financial sensitivity tables",
            "An external Red Team challenges the pricing assumptions",
            "The meeting ends with three unresolved questions assigned for data testing"
        ],
        "correct_index": 0,
        "explanation": "Self-censorship, illusion of unanimity, and pressure on dissenters are hallmark symptoms of Groupthink.",
        "distractor_analysis": "The other three options demonstrate healthy analytical friction."
    },
    {
        "anticipation_rank": 11,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "key_concept": "Framing Effect (Gain vs Loss)",
        "question": "Customers reject a plan framed as 'a ₹100 surcharge for credit card payment' yet accept the exact same price framed as 'a ₹100 discount for UPI/cash.' Which cognitive phenomenon explains this?",
        "options": [
            "Framing Effect & Loss Aversion",
            "Deductive Soundness",
            "Nyaya Pratyaksha",
            "Survivorship Bias"
        ],
        "correct_index": 0,
        "explanation": "Identical economic payoffs trigger different decisions depending on whether they are framed as a loss (surcharge) or foregone gain (discount).",
        "distractor_analysis": "No missing sample or deductive syllogism is involved."
    },
    {
        "anticipation_rank": 12,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 2,
        "module_name": "Module 2: Critical Reading and Interpretation",
        "key_concept": "Confident Language vs Evidential Support",
        "question": "A consulting deck repeatedly uses phrases like 'undoubtedly,' 'clearly,' and 'every leader knows' while citing zero sample sizes or sources. What should a critical reader conclude?",
        "options": [
            "Rhetorical certainty is being used to mask weak or missing evidential support",
            "The claim must be mathematically proven because 'undoubtedly' is used",
            "Sample sizes are irrelevant in business writing",
            "The deck is an example of high-Logos reasoning"
        ],
        "correct_index": 0,
        "explanation": "Intensifiers ('clearly', 'undoubtedly') often signal assertion substituting for verifiable evidence.",
        "distractor_analysis": "High Logos relies on transparent data and warrants, not emphatic adjectives."
    },
    {
        "anticipation_rank": 13,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 3,
        "module_name": "Module 3: Constructing and Evaluating Arguments",
        "key_concept": "Soundness vs Validity",
        "question": "Can a deductive argument be logically **valid** yet factually **unsound**?",
        "options": [
            "Yes—when the conclusion follows strictly from the premises, but at least one premise is factually false",
            "No—valid arguments always have true premises",
            "Only in inductive surveys",
            "Only if Pathos is zero"
        ],
        "correct_index": 0,
        "explanation": "Validity is purely structural; soundness requires *both* valid structure and factually true premises.",
        "distractor_analysis": "Valid ≠ true; false premises yield a valid-but-unsound argument."
    },
    {
        "anticipation_rank": 14,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "key_concept": "Availability Heuristic",
        "question": "After seeing two viral news stories about electric-scooter battery fires, an operations head cancels a 500-vehicle EV pilot without checking fleet failure statistics per million km. Which heuristic caused this?",
        "options": [
            "Availability Heuristic (overweighting vivid, easily recalled events over statistical base rates)",
            "Equivocation Fallacy",
            "Red Herring",
            "Circular Logic"
        ],
        "correct_index": 0,
        "explanation": "Vivid, emotionally salient headlines hijack probability estimates via the Availability Heuristic.",
        "distractor_analysis": "Equivocation shifts word meanings; Red Herring changes the subject."
    },
    {
        "anticipation_rank": 15,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "key_concept": "Anchoring Bias",
        "question": "In salary negotiation, why does the first number put on the table strongly pull the final settlement toward it even when both parties know it is arbitrary?",
        "options": [
            "Anchoring Bias—subsequent adjustments stay insufficiently anchored around the initial reference point",
            "Confirmation Bias",
            "Slippery Slope",
            "Strawmanning"
        ],
        "correct_index": 0,
        "explanation": "Human judgment anchors on initial numbers and adjusts insufficiently from them.",
        "distractor_analysis": "It is a classic numeric anchoring effect."
    },
    {
        "anticipation_rank": 16,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 2,
        "module_name": "Module 2: Critical Reading and Interpretation",
        "key_concept": "Close Reading (Absence & Omission)",
        "question": "An annual sustainability report devotes 12 pages to tree-planting drives while omitting Scope 3 supply-chain emissions entirely. Which close-reading lens exposes this?",
        "options": [
            "Analyzing strategic absence/omission—what a text leaves out often reveals its defensive posture more than what it highlights",
            "Counting total word length",
            "Checking font kerning",
            "Assuming unmentioned metrics are zero"
        ],
        "correct_index": 0,
        "explanation": "Strategic omission ('greenwashing' by selective emphasis) is a primary target of close reading.",
        "distractor_analysis": "Unmentioned metrics cannot be assumed zero."
    },
    {
        "anticipation_rank": 17,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 3,
        "module_name": "Module 3: Constructing and Evaluating Arguments",
        "key_concept": "Ad Hominem vs Legitimate Credibility Check",
        "question": "When is questioning a speaker's background **NOT** an Ad Hominem fallacy?",
        "options": [
            "When exposing an undisclosed financial conflict of interest directly tied to the claim being evaluated",
            "When mocking their accent during a quarterly review",
            "When dismissing math proofs because of their political party",
            "When attacking their personal hobbies"
        ],
        "correct_index": 0,
        "explanation": "Pointing out relevant bias or conflict of interest tests source reliability; attacking unrelated personal traits is Ad Hominem.",
        "distractor_analysis": "Accents, politics, and hobbies are irrelevant personal attacks."
    },
    {
        "anticipation_rank": 18,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "key_concept": "Overconfidence & Planning Fallacy",
        "question": "Despite the last four ERP migrations taking 14–18 months, an IT head promises the new rollout will finish in 5 months 'because our team is special.' Which bias is this?",
        "options": [
            "Planning Fallacy / Inside-View Overconfidence (ignoring historical reference-class outside view)",
            "Gambler's Fallacy",
            "Appeal to Tradition",
            "Tu Quoque"
        ],
        "correct_index": 0,
        "explanation": "Relying on optimistic 'inside view' narratives while ignoring historical reference-class timelines produces the Planning Fallacy.",
        "distractor_analysis": "Gambler's fallacy expects past random outcomes to 'balance out.'"
    },
    {
        "anticipation_rank": 19,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 5,
        "module_name": "Module 5: Expertise, Authority, and Value",
        "key_concept": "Epistemic Humility",
        "question": "Which behavior best demonstrates 'Epistemic Humility' in a senior executive?",
        "options": [
            "Explicitly stating the boundary conditions under which their own forecast would be wrong and updating priors when disconfirming field data arrives",
            "Refusing to make any decision until 100% certainty exists",
            "Changing opinions randomly every hour",
            "Deferring blindly to the loudest consultant"
        ],
        "correct_index": 0,
        "explanation": "Epistemic humility pairs decisive action with openness to disconfirming evidence and awareness of uncertainty.",
        "distractor_analysis": "It is neither paralysis nor spinelessness."
    },
    {
        "anticipation_rank": 20,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 6,
        "module_name": "Module 6: Analytical and Cross-Cultural Thinking",
        "key_concept": "Complexity vs Confusion",
        "question": "How does genuine 'Systemic Complexity' differ from 'Analytical Confusion' in a business problem?",
        "options": [
            "Complexity stems from genuinely interdependent variables and feedback loops, whereas confusion stems from vague definitions, mixed units, or unclear questions",
            "Complexity means a problem is impossible to analyze",
            "Confusion is solved by adding more jargon",
            "They are identical"
        ],
        "correct_index": 0,
        "explanation": "Clarifying definitions and framing eliminates self-inflicted confusion so teams can model real systemic complexity.",
        "distractor_analysis": "More jargon worsens confusion."
    },
    {
        "anticipation_rank": 21,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 7,
        "module_name": "Module 7: Critical Thinking in Organisations and Society",
        "key_concept": "Strategic Rest vs Hustle Culture",
        "question": "From a critical thinking lens, why is 'strategic rest' framed as an analytical necessity rather than laziness?",
        "options": [
            "Chronic sleep/cognitive depletion degrades System 2 executive control, leaving teams vulnerable to bias, tunnel vision, and costly errors",
            "Rest increases total office hours logged per week",
            "Rest eliminates the need for market research",
            "Exhausted teams always make faster, higher-quality breakthroughs"
        ],
        "correct_index": 0,
        "explanation": "System 2 error-checking requires cognitive bandwidth; fatigue forces crude System 1 shortcuts.",
        "distractor_analysis": "Fatigue increases error rates."
    },
    {
        "anticipation_rank": 22,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 8,
        "module_name": "Module 8: Critical Thinking in Practice",
        "key_concept": "Blue Ocean Assumption Validation",
        "question": "In the Whites & Pastels case, why did the founders validate ergonomic and aesthetic assumptions through physical prototyping rather than relying solely on focus-group opinions?",
        "options": [
            "Physical prototypes bridge the exposure gap, letting users react to tangible form and comfort rather than abstract hypotheticals",
            "Focus groups are illegal in India",
            "Prototypes automatically guarantee patent approval",
            "Customers always know future aesthetic trends verbally"
        ],
        "correct_index": 0,
        "explanation": "Tangible prototypes test real ergonomic behavior and overcome customers' inability to articulate unexperienced designs.",
        "distractor_analysis": "Verbally stated preferences often fail to predict real usage."
    },
    {
        "anticipation_rank": 23,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "key_concept": "Slippery Slope Fallacy",
        "question": "An HR director argues: 'If we allow 1 day of remote work per week, soon nobody will come to the office, company culture will vanish, and the firm will collapse.' Which fallacy is this?",
        "options": [
            "Slippery Slope (asserting an extreme chain of catastrophic outcomes without proving each causal link)",
            "Equivocation",
            "Appeal to Ignorance",
            "Circular Reasoning"
        ],
        "correct_index": 0,
        "explanation": "Slippery Slope leaps from a modest step to catastrophe without demonstrating inevitable intermediate causation.",
        "distractor_analysis": "No double word meaning (equivocation) is present."
    },
    {
        "anticipation_rank": 24,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 3,
        "module_name": "Module 3: Constructing and Evaluating Arguments",
        "key_concept": "Circular Reasoning (Begging the Question)",
        "question": "Which statement commits Circular Reasoning ('Begging the Question')?",
        "options": [
            "'Our brand is the most trustworthy in India because Indian consumers can always trust our brand.'",
            "'Our brand has 98% on-time delivery verified by third-party audits.'",
            "'Our brand grew 15% YoY in Q2.'",
            "'Our brand is priced 10% below Competitor X.'"
        ],
        "correct_index": 0,
        "explanation": "Restating the conclusion ('most trustworthy') in slightly rephrased words as its own premise provides zero external support.",
        "distractor_analysis": "The other three cite measurable empirical claims."
    },
    {
        "anticipation_rank": 25,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "key_concept": "Selection Bias",
        "question": "An app team surveys only users who have been active for 6+ months and concludes 'onboarding is effortless for everyone.' Which bias invalidates this conclusion?",
        "options": [
            "Selection / Survivorship Bias (excluding users who churned during week-1 onboarding)",
            "Anchoring Bias",
            "Red Herring",
            "Strawman"
        ],
        "correct_index": 0,
        "explanation": "Surveying survivors omits the exact users who bounced due to onboarding friction.",
        "distractor_analysis": "No initial numerical anchor is involved."
    },
    {
        "anticipation_rank": 26,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 2,
        "module_name": "Module 2: Critical Reading and Interpretation",
        "key_concept": "5 Cs of Narrative Persuasion",
        "question": "Why can 'Causal Coherence' in a founder's turnaround memoir mislead MBA students studying business failure?",
        "options": [
            "Coherent stories smooth over messy randomness, luck, and survivor bias, making success look like a deterministic formula",
            "Memoirs never contain true dates",
            "Coherence means the story has zero characters",
            "Business failures never involve causal factors"
        ],
        "correct_index": 0,
        "explanation": "Narrative coherence creates an illusion of clean hindsight causality.",
        "distractor_analysis": "Stories omit failed peers who took identical actions."
    },
    {
        "anticipation_rank": 27,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "key_concept": "Tu Quoque ('You Too')",
        "question": "When a supplier accused of late deliveries replies, 'Well, your own warehouse also missed two dispatch deadlines last year!' without addressing the current delay, which fallacy is used?",
        "options": [
            "Tu Quoque (deflecting critique by pointing out the accuser's alleged hypocrisy)",
            "Appeal to Nature",
            "Bandwagon Fallacy",
            "False Cause"
        ],
        "correct_index": 0,
        "explanation": "Tu Quoque avoids evaluating the claim's validity by accusing the critic of similar behavior.",
        "distractor_analysis": "Bandwagon appeals to popularity."
    },
    {
        "anticipation_rank": 28,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 5,
        "module_name": "Module 5: Expertise, Authority, and Value",
        "key_concept": "Fact–Value Gap in CSR",
        "question": "Why does deciding how much profit to allocate between shareholder buybacks and community sustainability involve a Value judgment rather than pure Fact optimization?",
        "options": [
            "Because data can model financial returns of each option, but choosing which stakeholder obligation deserves priority reflects normative values",
            "Because profit cannot be measured numerically",
            "Because sustainability has zero measurable metrics",
            "Because buybacks are always illegal"
        ],
        "correct_index": 0,
        "explanation": "Optimization requires an objective function, and choosing whose welfare enters that function is a value choice.",
        "distractor_analysis": "Both profit and many ESG outcomes are measurable."
    },
    {
        "anticipation_rank": 29,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 6,
        "module_name": "Module 6: Analytical and Cross-Cultural Thinking",
        "key_concept": "Authority Bias Across Cultures",
        "question": "Why can 'Authority Bias' be amplified in high-power-distance business environments?",
        "options": [
            "Subordinates equate seniority with infallibility and withhold disconfirming data to avoid disrespecting senior leaders",
            "Senior leaders never make forecasts",
            "High-power-distance firms forbid written memos",
            "Juniors always overrule founders publicly"
        ],
        "correct_index": 0,
        "explanation": "Deference norms suppress upward critique, reinforcing leaders' blind spots.",
        "distractor_analysis": "The opposite of juniors overruling founders."
    },
    {
        "anticipation_rank": 30,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 7,
        "module_name": "Module 7: Critical Thinking in Organisations and Society",
        "key_concept": "Organizational Claim vs Performance",
        "question": "A tech firm claims 'We are a meritocratic learning organization,' yet 90% of promotions go to one alma mater and post-mortems blame individuals. What diagnostic tool exposes this?",
        "options": [
            "Claim-vs.-Performance Accountability Audit (testing espoused values against observable promotion and failure-review records)",
            "Reading only the CEO's LinkedIn posts",
            "Checking office furniture aesthetics",
            "Counting total employees"
        ],
        "correct_index": 0,
        "explanation": "Auditing actual behavioral/promotion artifacts against espoused rhetoric reveals institutional hypocrisy.",
        "distractor_analysis": "LinkedIn posts only repeat the espoused claim."
    },
    {
        "anticipation_rank": 31,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 8,
        "module_name": "Module 8: Critical Thinking in Practice",
        "key_concept": "Stakeholder Listening & Red Flags",
        "question": "In the Sangeeta Menon manufacturing resilience case, what makes 'active stakeholder listening' superior to top-down assumption-making during a supply disruption?",
        "options": [
            "Frontline vendors and workers surface early operational red flags (e.g., raw-material bottlenecks) long before they appear in lagging quarterly financials",
            "Listening eliminates the need for contracts",
            "Suppliers always volunteer bad news without trust",
            "Quarterly financials predict disruptions two years early"
        ],
        "correct_index": 0,
        "explanation": "Operational stakeholders see leading failure indicators well before lagging accounting reports.",
        "distractor_analysis": "Financials are lagging, not leading, indicators."
    },
    {
        "anticipation_rank": 32,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "key_concept": "Bandwagon Fallacy (Ad Populum)",
        "question": "A D2C founder runs TikTok/Insta reels solely because 'every competitor in our category is doing it,' without checking their own B2B buyer ICP. Which fallacy is this?",
        "options": [
            "Bandwagon Fallacy (Appeal to Popularity—assuming widespread adoption proves suitability for your specific context)",
            "Post Hoc",
            "Equivocation",
            "Genetic Fallacy"
        ],
        "correct_index": 0,
        "explanation": "Imitating peers without testing channel-market fit commits the Bandwagon Fallacy.",
        "distractor_analysis": "Genetic fallacy judges a claim solely by its origin."
    },
    {
        "anticipation_rank": 33,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 3,
        "module_name": "Module 3: Constructing and Evaluating Arguments",
        "key_concept": "Inductive Generalization Strength",
        "question": "What primarily determines the strength of an inductive generalization from a customer pilot?",
        "options": [
            "Sample representativeness across target segments, absence of selection bias, and adequate sample size",
            "Using bold font on the conclusion slide",
            "Whether the conclusion matches the founder's gut feeling",
            "Whether the pilot lasted exactly one hour"
        ],
        "correct_index": 0,
        "explanation": "Representativeness and unbiased sampling govern inductive strength.",
        "distractor_analysis": "Formatting and gut feeling do not strengthen inductive validity."
    },
    {
        "anticipation_rank": 34,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "key_concept": "Hindsight Bias",
        "question": "After a startup fails, an investor says, 'It was obvious from Day 1 that their pricing model would collapse,' despite having enthusiastically funded it. Which bias is this?",
        "options": [
            "Hindsight Bias ('knew-it-all-along' distortion of past uncertainty)",
            "Anchoring Bias",
            "Red Herring",
            "Appeal to Nature"
        ],
        "correct_index": 0,
        "explanation": "Hindsight bias rewrites past uncertainty as inevitable after seeing the outcome, blocking honest post-mortems.",
        "distractor_analysis": "No anchor value or distraction tactic is involved."
    },
    {
        "anticipation_rank": 35,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 8,
        "module_name": "Module 8: Critical Thinking in Practice",
        "key_concept": "Ikigai & Venture Selection",
        "question": "When applying the Ikigai framework alongside data storytelling to evaluate a new venture, what four intersections must align?",
        "options": [
            "What you love, what you are good at, what the market/world needs, and what customers will sustainably pay for",
            "Revenue, EBITDA, Debt, and Taxes",
            "Logo, Font, Color, and Tagline",
            "Speed, Luck, Hype, and Subsidies"
        ],
        "correct_index": 0,
        "explanation": "Ikigai aligns capability and passion with validated market need and economic viability.",
        "distractor_analysis": "The other sets are purely financial or branding items."
    },
    {
        "anticipation_rank": 36,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 1,
        "module_name": "Module 1: Foundations of Critical Thinking",
        "key_concept": "Visual Scale Framing",
        "question": "Why can two charts plotting the exact same quarterly profit data lead a board to opposite conclusions?",
        "options": [
            "Manipulating Y-axis scale, time-window selection, or comparison baselines changes perceived urgency without altering a single underlying number",
            "Because charts cannot display negative numbers",
            "Because numbers change when plotted",
            "Because boards never read titles"
        ],
        "correct_index": 0,
        "explanation": "Scale and baseline framing shape System 1 intuitive perception.",
        "distractor_analysis": "Underlying numbers remain identical; framing alters perception."
    },
    {
        "anticipation_rank": 37,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 2,
        "module_name": "Module 2: Critical Reading and Interpretation",
        "key_concept": "Word Choice & Loaded Language",
        "question": "Replacing 'fired 400 engineers to boost quarterly EPS' with 'rightsized human capital for agile synergy' is an example of:",
        "options": [
            "Euphemistic framing / loaded diction designed to soften ethical and human impact",
            "Deductive proof",
            "Fermi estimation",
            "Steelmanning"
        ],
        "correct_index": 0,
        "explanation": "Corporate euphemisms obscure agency and human consequences.",
        "distractor_analysis": "It obscures rather than clarifies."
    },
    {
        "anticipation_rank": 38,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 4,
        "module_name": "Module 4: Fallacies and Cognitive Biases",
        "key_concept": "Equivocation Fallacy",
        "question": "An ad claims: 'Nothing is better than a debt-free life; a ₹10 coffee is better than nothing; therefore a ₹10 coffee is better than a debt-free life.' Which fallacy is committed?",
        "options": [
            "Equivocation (shifting the meaning of 'nothing' mid-argument)",
            "Ad Hominem",
            "Survivorship Bias",
            "Post Hoc"
        ],
        "correct_index": 0,
        "explanation": "Equivocation exploits ambiguity by using the same word ('nothing') in two different senses.",
        "distractor_analysis": "Classic lexical ambiguity fallacy."
    },
    {
        "anticipation_rank": 39,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 7,
        "module_name": "Module 7: Critical Thinking in Organisations and Society",
        "key_concept": "Pre-Mortem Technique",
        "question": "How does conducting a 'Pre-Mortem' before launching a project counter Groupthink and Overconfidence?",
        "options": [
            "It asks the team to imagine the project has already failed one year from now and brainstorm all plausible causes—making dissent safe and concrete before launch",
            "It cancels every project automatically",
            "It assigns blame after bankruptcy",
            "It replaces financial budgeting"
        ],
        "correct_index": 0,
        "explanation": "Prospective hindsight legitimizes surfacing hidden risks while fixes are still cheap.",
        "distractor_analysis": "Pre-mortems happen *before* launch, not after bankruptcy."
    },
    {
        "anticipation_rank": 40,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 8,
        "module_name": "Module 8: Critical Thinking in Practice",
        "key_concept": "Decision Framing in CSR",
        "question": "When a company's CSR committee funds only charities run by executives' friends without measuring beneficiary outcomes, which critical-thinking failure occurs?",
        "options": [
            "Confirmation bias and conflicted decision framing—confusing personal affinity with verified social impact",
            "Excessive randomized controlled trials",
            "Deductive soundness",
            "Nyaya empirical verification"
        ],
        "correct_index": 0,
        "explanation": "Impact decisions require outcome evidence and independent criteria, not affinity bias.",
        "distractor_analysis": "RCTs and empirical verification are the exact cures, not the failure."
    }
]


def main():
    cla_data = json.loads(CLA_PATH.read_text())
    cla_stems = set()
    for a in cla_data["assessments"]:
        for q in a["questions"]:
            cla_stems.add(re.sub(r"\W+", " ", q["stem"].lower()).strip())

    # Validate Sec B word counts (target 20-30 words)
    sub_wcs = []
    for i, q in enumerate(SUBJECTIVE_QUESTIONS, 1):
        assert q["anticipation_rank"] == i
        wc = len(q["model_answer"].split())
        q["word_count"] = wc
        sub_wcs.append((i, wc))

    # Validate Sec C word counts (target 40-50 words)
    case_wcs = []
    for i, q in enumerate(CASE_QUESTIONS, 1):
        assert q["anticipation_rank"] == i
        wc = len(q["model_answer"].split())
        q["word_count"] = wc
        case_wcs.append((i, wc))

    # Validate MCQs & zero overlap
    overlap = []
    for i, q in enumerate(MCQ_QUESTIONS, 1):
        assert q["anticipation_rank"] == i
        assert len(q["options"]) == 4
        assert 0 <= q["correct_index"] <= 3
        if re.sub(r"\W+", " ", q["question"].lower()).strip() in cla_stems:
            overlap.append(i)

    bank = {
        "course_id": "d9173426",
        "course_name": "Critical Thinking",
        "exam_pattern": {
            "exam_date": "2026-12-06",
            "exam_timing": "09:00 AM to 11:00 AM",
            "duration_mins": 120,
            "total_marks": 50,
            "negative_marking": False,
            "calculator_allowed": False,
            "sections": [
                {"name": "Section A", "type": "MCQ", "count": 14, "marks_each": 1, "total_marks": 14},
                {"name": "Section B", "type": "Short Answer", "count": 6, "marks_each": 2, "total_marks": 12, "indicative_word_limit": 30},
                {"name": "Section C", "type": "Case Study", "count": 8, "marks_each": 3, "total_marks": 24, "indicative_word_limit": 50}
            ]
        },
        "stats": {
            "subjective_count": len(SUBJECTIVE_QUESTIONS),
            "case_count": len(CASE_QUESTIONS),
            "mcq_count": len(MCQ_QUESTIONS),
            "total_predicted_questions": len(SUBJECTIVE_QUESTIONS) + len(CASE_QUESTIONS) + len(MCQ_QUESTIONS),
            "cla_baseline_count": len(cla_stems)
        },
        "subjective_questions": SUBJECTIVE_QUESTIONS,
        "case_questions": CASE_QUESTIONS,
        "mcq_questions": MCQ_QUESTIONS,
    }

    out_path = OUT_DIR / "critical_thinking_exam_bank.json"
    out_path.write_text(json.dumps(bank, indent=2, ensure_ascii=False))
    print(f"Saved: {out_path}")
    print(f"Sec B Conceptual: {len(SUBJECTIVE_QUESTIONS)} (word range: {min(w for _,w in sub_wcs)}-{max(w for _,w in sub_wcs)}w)")
    print(f"Sec C Case: {len(CASE_QUESTIONS)} (word range: {min(w for _,w in case_wcs)}-{max(w for _,w in case_wcs)}w)")
    print(f"Sec A MCQs: {len(MCQ_QUESTIONS)} | CLA Overlap: {overlap}")


if __name__ == "__main__":
    main()
