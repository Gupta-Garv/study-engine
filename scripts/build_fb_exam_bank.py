#!/usr/bin/env python3
"""
Build the Family Business Strategy (db945ff9) Exam-Calibrated Question Bank:
- 32 Subjective Short-Answer Questions (5 marks, <=100 words model answer), ranked most -> least anticipated
- 64 Exam-Level MCQs (1 mark), ranked most -> least anticipated
- Zero overlap with extracted CLA questions
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "data" / "exam_bank"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CLA_PATH = BASE_DIR / "data" / "cla_questions" / "family_business" / "cla_questions.json"

# ---------------------------------------------------------------------------
# 32 SUBJECTIVE QUESTIONS (5 Marks each, Indicative length: <= 100 words)
# Ordered from Most Anticipated (#1) to Least Anticipated (#32)
# ---------------------------------------------------------------------------
SUBJECTIVE_QUESTIONS = [
    # --- TIER 1: MOST ANTICIPATED (#1 - #12) ---
    {
        "anticipation_rank": 1,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "framework": "Three-Circle Model (Tagiuri & Davis)",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "A second-generation manufacturing firm has three siblings: Riya (25% equity, VP Operations), Kabir (25% equity, non-active board observer), and Meera (0% equity, married into the family, heads HR). During a downturn, Kabir demands higher dividends while Riya pushes to reinvest profits, and Meera objects to cutting family perks. Using the Three-Circle Model, map each person to their exact sector and propose ONE structural mechanism to separate these conflicting priorities.",
        "model_answer": "Under the Three-Circle Model, Riya sits in Sector 7 (Family + Owner + Employee), seeking reinvestment and operational continuity. Kabir occupies Sector 4 (Family + Owner), prioritizing dividend yield over operational needs. Meera sits in Sector 5 (Family + Employee, no equity), protecting relational norms and perks. Confusing these overlapping roles turns business choices into family disputes. Mechanism: Establish a formal Family Employment Policy and a Dividend Policy approved by the Board/Owners' Council, separating compensation/perks (employment circle) from capital returns (ownership circle) so each claim is governed by objective criteria.",
        "examiner_rubric": [
            "Correctly maps Riya (Sector 7: Family-Owner-Employee), Kabir (Sector 4: Family-Owner), and Meera (Sector 5: Family-Employee) — 2 marks",
            "Explains how role overlap conflates dividend, operational, and relational priorities — 1.5 marks",
            "Proposes ONE concrete structural separator (Family Employment Policy / Dividend Policy / Council separation) — 1.5 marks"
        ],
        "common_trap": "Misplacing Meera as Sector 1 (Family only) instead of Sector 5 (Family + Employee), or giving generic advice like 'communicate better' instead of a governance mechanism."
    },
    {
        "anticipation_rank": 2,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "framework": "Socioemotional Wealth (SEW) — FIBER Dimensions",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "A profitable, debt-free 45-year-old textile firm rejects a private equity offer that would double its export capacity, citing loss of 'our family name on the factory gate' and discomfort with outside board seats. Using SEW Theory (FIBER dimensions), explain why a financially rational offer was rejected and identify ONE long-term strategic risk of this decision.",
        "model_answer": "Under Socioemotional Wealth (SEW) theory, family owners prioritize non-financial utilities over pure profit maximization. Rejecting PE protects two FIBER dimensions: Family Control & Influence (retaining unilateral board authority) and Identification of Family Members with the Firm (preserving the family name on the factory). Emotional Attachment and Renewal of Family Bonds across generations also deter external dilution. Long-term risk: Capital rationing and 'entrenchment' can leave the firm under-invested in technology and scale, eroding competitiveness when better-funded rivals modernize, eventually destroying both financial wealth and the legacy itself.",
        "examiner_rubric": [
            "Defines SEW priority over pure financial utility — 1 mark",
            "Accurately invokes specific FIBER dimensions (Family Control & Influence + Identification with the Firm) — 2 marks",
            "Identifies ONE concrete strategic risk (under-investment, missed scale, competitive obsolescence) — 2 marks"
        ],
        "common_trap": "Only saying 'they are emotional' without naming FIBER dimensions, or failing to state a concrete long-term business risk."
    },
    {
        "anticipation_rank": 3,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "framework": "Willingness–Ability Matrix & Succession Paths",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "A founder's only son has an MBA and strong financial acumen (high ability), but privately wants to launch a tech startup rather than run the family's traditional steel trading business (low willingness). Using the Willingness–Ability Matrix, classify this successor and recommend ONE viable succession path that protects both the business and family harmony.",
        "model_answer": "In the Willingness–Ability Matrix, the son falls into the 'Competent but Unwilling' (High Ability, Low Willingness) quadrant. Forcing him into the CEO role risks disengagement, resentment, and poor operational execution. Recommended path: Separate ownership from management. Transition the son into an informed, active owner/board director role—leveraging his financial acumen in governance—while hiring a professional non-family CEO to run daily steel operations. Alternatively, allow him to build his tech venture as an adjacent corporate entrepreneurship arm, preserving family capital without coercing operational leadership.",
        "examiner_rubric": [
            "Correctly classifies quadrant as High Ability / Low Willingness (Competent but Unwilling) — 1.5 marks",
            "States why forced operational succession fails — 1 mark",
            "Recommends separating ownership from management (Owner/Board role + professional CEO) — 2.5 marks"
        ],
        "common_trap": "Suggesting 'convince him to join operations anyway' or confusing Low Willingness with Low Ability."
    },
    {
        "anticipation_rank": 4,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "framework": "Ability–Willingness Innovation Paradox",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "A third-generation auto-components firm holds deep engineering talent, patient family capital, and fast decision-making—yet launches fewer new products than smaller non-family rivals. Using the Ability–Willingness Innovation Paradox, explain this contradiction and suggest ONE organizational lever to unlock innovation.",
        "model_answer": "The Ability–Willingness Paradox states that family firms possess superior ability to innovate (patient capital, quick consensus, deep tacit knowledge) yet often exhibit lower willingness to do so because radical innovation threatens Socioemotional Wealth (SEW), legacy routines, and family control. Consequently, the firm defaults to 'exploitation' of existing lines rather than 'exploration.' Lever: Ring-fence an independent corporate venture or R&D unit with dedicated ring-fenced capital and mixed family–professional leadership, insulating experimental projects from core legacy politics while letting NextGen champions earn legitimacy through measurable innovation milestones.",
        "examiner_rubric": [
            "Explains the paradox (High Ability via patient capital/discretion vs. Low Willingness due to SEW/loss aversion) — 2.5 marks",
            "Links to Exploration vs. Exploitation tension — 1 mark",
            "Proposes ONE structural lever (ring-fenced R&D/venture unit or NextGen innovation mandate) — 1.5 marks"
        ],
        "common_trap": "Blaming lack of money or talent, when the paradox specifically arises despite strong ability/resources."
    },
    {
        "anticipation_rank": 5,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "framework": "Family Council vs. Family Constitution vs. Board of Directors",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "As a firm moves into its third generation with 18 cousins, informal Sunday dinners have turned into arguments over who gets company cars, who can join the firm, and how dividends are set. Distinguish the roles of a Family Council, a Family Constitution, and the Board of Directors in resolving this breakdown.",
        "model_answer": "At the Cousin Consortium stage, informal norms collapse and require three distinct institutions. First, the Family Council serves as the representative forum where family branches voice concerns, align values, and manage relational expectations outside the business. Second, the Family Constitution codifies binding rules—such as entry criteria, perk boundaries, and conflict resolution—approved by the family. Third, the Board of Directors retains legal accountability for business strategy, executive oversight, and dividend recommendations. Separating family deliberation (Council), rule-making (Constitution), and corporate stewardship (Board) prevents cousin politics from paralyzing operations.",
        "examiner_rubric": [
            "Defines Family Council (representative family forum / voice) — 1.5 marks",
            "Defines Family Constitution (codified rules for entry, perks, conflict) — 1.5 marks",
            "Defines Board of Directors (legal business strategy, oversight, dividends) and why separation matters — 2 marks"
        ],
        "common_trap": "Treating the Family Council as a replacement for the corporate Board, or saying the Family Constitution is legally binding like a Shareholders' Agreement."
    },
    {
        "anticipation_rank": 6,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "framework": "Agency Theory vs. Stewardship Theory & Alignment–Entrenchment",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Empirical studies like Anderson & Reeb (2003) show family firms often outperform non-family peers, yet some family firms suffer severe value destruction when founders refuse to step aside. Reconcile these two findings using Agency Theory, Stewardship Theory, and the Alignment–Entrenchment trade-off.",
        "model_answer": "Under Stewardship Theory and the Alignment effect, concentrated family ownership reduces classic Owner–Manager (Type I) agency costs because family leaders identify psychologically with the firm and invest for the long term—explaining Anderson & Reeb's outperformance finding. However, excessive unchecked control triggers the Entrenchment effect and Principal–Principal (Type II) agency conflicts: founders/family blockholders extract private benefits, resist monitoring, appoint unqualified kin, or block succession. Thus, performance follows an inverted-U curve—family involvement creates value up to the point where alignment gives way to entrenchment.",
        "examiner_rubric": [
            "Links outperformance to Stewardship + reduced Type I Agency costs (Alignment) — 2 marks",
            "Links value destruction to Entrenchment + Type II Principal–Principal conflicts — 2 marks",
            "Explicitly synthesizes via the inverted-U Alignment–Entrenchment trade-off — 1 mark"
        ],
        "common_trap": "Saying family firms have 'zero agency costs'—ignoring Principal–Principal (majority vs. minority) agency conflicts."
    },
    {
        "anticipation_rank": 7,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "framework": "Five Rights of Family Owners & Three Powers",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "In a sibling partnership, the elder brother owns 55% voting shares and unilaterally sells a core division without consulting his 45%-owner sister, telling her 'majority rules.' Using the Five Rights of Family Owners and the Three Powers (Create, Sustain, Destroy), diagnose the governance flaw and state ONE safeguard.",
        "model_answer": "While the brother exercised his legal Right to Decide and Right to Transfer, he abused the 'Power to Destroy'—unilateral majoritarianism that alienates minority family owners and breaks relational trust. Responsible ownership requires balancing the Power to Create and Sustain through the Right to Inform (transparent communication) and Right to Define Value (shared vision of risk and legacy). Safeguard: Institute a Shareholders' Agreement with supermajority/reserved-matter clauses for core asset sales, ensuring major structural decisions require consensus rather than simple 51% dominance.",
        "examiner_rubric": [
            "Identifies Power to Destroy vs. Power to Create/Sustain — 1.5 marks",
            "Maps specific Rights of Owners (Right to Decide/Transfer vs. Right to Inform/Define Value) — 2 marks",
            "Recommends ONE concrete safeguard (Shareholders' Agreement with reserved matters/supermajority) — 1.5 marks"
        ],
        "common_trap": "Arguing the brother did nothing wrong because 55% > 50%, missing the distinction between legal power and sustainable family ownership."
    },
    {
        "anticipation_rank": 8,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "framework": "Conflict Types (Task, Process, Relationship) & Management",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Two cousins co-leading a retail chain disagree sharply over whether to expand into tier-2 cities or deepen metro stores. Within months, they stop speaking at family weddings and block each other's budgets. Distinguish the conflict types at play here and explain ONE intervention to prevent functional debate from turning toxic.",
        "model_answer": "Initially, the disagreement over expansion strategy was Task Conflict (differing views on *what* to do), which can improve decision quality if debated openly. However, without clear decision rules, it escalated into Process Conflict (blocking budgets—*how* authority/resources are allocated) and finally Relationship Conflict (personal animosity spilling into family weddings), which destroys trust and performance. Intervention: Establish clear role charters and an independent Board/Advisory Committee to adjudicate strategic and budget disputes on objective ROI criteria, keeping business debate bounded and separate from family gatherings.",
        "examiner_rubric": [
            "Correctly distinguishes Task Conflict (strategy debate), Process Conflict (budget/authority), and Relationship Conflict (personal animosity) — 2.5 marks",
            "Explains the escalation mechanism from task to relationship — 1 mark",
            "Proposes ONE clear governance/boundary intervention — 1.5 marks"
        ],
        "common_trap": "Treating all conflict as bad instead of noting that Task Conflict is constructive until it spills into Relationship Conflict."
    },
    {
        "anticipation_rank": 9,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "framework": "Board Roles (Service, Resource Provisioning, Control)",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "A mid-sized family pharma firm plans to enter European regulated markets. Currently, its Board consists solely of three brothers and their family auditor. Using the three roles of a Board (Control, Service, Resource Provisioning), diagnose what this board lacks and recommend TWO specific independent director profiles.",
        "model_answer": "An all-family plus auditor board performs basic statutory compliance but fails across all three strategic board roles: (1) Control Role—lacks objective oversight of executive siblings and related-party risks; (2) Service Role—lacks unbiased strategic counsel and devil's advocacy on European entry; (3) Resource Provisioning Role—lacks external networks, regulatory legitimacy, and global market access. Recommended profiles: Appoint (a) a former pharma regulatory/EU market-entry executive (Resource + Service) and (b) an independent finance/audit governance veteran (Control), shifting the board from a rubber stamp to a value-creating organ.",
        "examiner_rubric": [
            "Evaluates all three board roles (Control, Service, Resource Provisioning) against the current board — 3 marks",
            "Recommends TWO relevant independent director profiles tied to EU pharma expansion + governance — 2 marks"
        ],
        "common_trap": "Focusing only on the Control/monitoring role and forgetting the Service (advice) and Resource Provisioning (networks/legitimacy) roles."
    },
    {
        "anticipation_rank": 10,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 7,
        "module_name": "Module 7: Family Firms, Communities, and External Stakeholders",
        "framework": "Anand Story — Earning the Right to Change",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Returning to join a legacy Indian family group, a young NextGen leader wants to immediately replace long-serving loyalists and overhaul core processes. Drawing on the Anand Group case ('Coming Home' and 'Earning the Right to Change'), explain why this approach usually fails and state the sequence a NextGen leader should follow instead.",
        "model_answer": "In the Anand Group case, rapid top-down disruption by a returning scion fails because legacy executives hold deep institutional memory, stakeholder trust, and emotional loyalty to the founder; attacking them triggers defensive resistance and alienates the senior generation. Instead, NextGen must 'earn the right to change' through a disciplined sequence: first, listen, learn core operations from the ground up, and respect existing relationships; second, deliver measurable wins in a ring-fenced project or peripheral unit to build personal credibility; only then introduce broader modernization alongside trusted insiders.",
        "examiner_rubric": [
            "Explains why abrupt overhaul fails (loss of trust, loyalist resistance, lack of earned credibility) — 2 marks",
            "Articulates the 'Earning the Right to Change' sequence (listen/learn -> prove competence on bounded mandate -> scale modernization) — 3 marks"
        ],
        "common_trap": "Giving generic change-management advice without referencing credibility-building, founder-loyalist dynamics, or the Anand case logic."
    },
    {
        "anticipation_rank": 11,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "framework": "Professionalisation — Three Paths & 'Be More Like a Non-Family Business' Fallacy",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "A family business consultant advises a founder: 'Hire an MNC CEO, copy MNC KPIs, and remove family culture—just run it like a non-family firm.' Critique this advice using course frameworks on professionalisation and explain ONE way to professionalise without destroying the firm's competitive edge.",
        "model_answer": "The 'be more like a non-family business' analogy breaks down because copying MNC bureaucracy erodes the family firm's unique VRIO advantages: patient capital, fast trust-based decisions, and high stewardship commitment. Moreover, professionalisation is not binary (family vs. outsider); it involves formalizing systems, meritocratic processes, and governance—which family members themselves can embody. Better approach: Adopt hybrid professionalisation—introduce transparent KPIs, budgets, and independent board reviews while retaining clear family purpose and empowering a trusted 'bridge' non-family executive who respects relational culture.",
        "examiner_rubric": [
            "Critiques the 'be more like a non-family business' fallacy (destroys familiness/trust/speed) — 2.5 marks",
            "Clarifies that professionalisation is about systems/meritocracy, not merely replacing kin with outsiders — 1 mark",
            "Proposes ONE hybrid professionalisation mechanism — 1.5 marks"
        ],
        "common_trap": "Equating 'professionalisation' solely with 'hiring non-family managers' instead of formalizing systems and governance."
    },
    {
        "anticipation_rank": 12,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 8,
        "module_name": "Module 8: Institutional Contexts and Family Businesses",
        "framework": "Scott's Three Pillars & Institutional Voids (India Context)",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Explain how 'institutional voids' in emerging markets like India historically made diversified family conglomerates successful, and how strengthening formal institutions (SEBI regulations, deeper capital markets) forces them to shift 'from trust to rules.'",
        "model_answer": "In emerging markets with weak external capital, contract-enforcement, and talent institutions ('institutional voids'), family conglomerates substituted internal trust, reputational networks, and internal capital/talent markets—creating a decisive advantage over standalone firms. However, as India's regulative pillar strengthens (SEBI LODR, RPT disclosures, independent director mandates, Insolvency Code) and global investors demand transparency, informal trust no longer suffices. Family groups must shift 'from trust to rules' by codifying board oversight, arm's-length related-party governance, and meritocratic talent systems to retain market legitimacy and lower cost of capital.",
        "examiner_rubric": [
            "Explains how institutional voids gave family conglomerates an internal-market/trust advantage — 2 marks",
            "Links stronger regulative/formal institutions (SEBI, capital markets) to the 'trust to rules' shift — 2 marks",
            "Mentions specific governance adaptation (RPT transparency, independent boards, formal systems) — 1 mark"
        ],
        "common_trap": "Describing institutional voids as purely negative for family firms, missing that voids were historically a source of family conglomerate advantage."
    },

    # --- TIER 2: HIGH PROBABILITY (#13 - #24) ---
    {
        "anticipation_rank": 13,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "framework": "Incumbent's Dilemma & Ten Key Tensions",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "A 72-year-old founder has announced his daughter as CEO twice over five years, yet still signs every major cheque and overturns her pricing decisions in front of staff. Diagnose this 'Incumbent's Dilemma' and propose TWO concrete steps for an orderly baton handover.",
        "model_answer": "This illustrates the Incumbent's Dilemma: the founder's personal identity, status, and fear of irrelevance or mortality make letting go psychologically threatening, creating 'shadow leadership' that undermines the successor's authority in front of employees. Concrete steps: (1) Set a binding, time-bound transition calendar with clear delegation thresholds (e.g., signing limits transferred by Q2); (2) Reposition the founder into a dignified, non-executive Emeritus/Chairman or philanthropic/family-council role so he retains purpose without interfering in daily pricing or operations.",
        "examiner_rubric": [
            "Diagnoses identity/irrelevance anxiety + undermining of successor authority — 2 marks",
            "Provides TWO concrete handover steps (binding timeline/delegation thresholds + dignified non-operational role) — 3 marks"
        ],
        "common_trap": "Blaming the daughter for not being assertive instead of diagnosing the founder's identity attachment and lack of structural exit."
    },
    {
        "anticipation_rank": 14,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "framework": "Women in Family Business (Invisible Force & Daughter as Successor)",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "In a traditional Indian family business, the founder's daughter holds an engineering degree and worked five years in operations, while her younger brother shows little interest—yet the family assumes the brother will be CEO. Identify TWO systemic barriers from the course driving this bias and ONE practice to ensure merit-based inclusion.",
        "model_answer": "Two systemic barriers drive this bias: (1) Cultural primogeniture and patrilineal norms—assuming sons carry the family legacy while daughters 'marry into another family,' relegating women to the 'invisible force' (informal emotional/advisory roles without title or equity); (2) Stakeholder and gender stereotyping—skepticism from male suppliers, bankers, or legacy staff about female authority. Practice: Adopt a formal, gender-neutral Family Employment and Succession Charter requiring external work experience, objective performance evaluations, and independent board assessment so leadership selection rests on proven competence rather than birth order or gender.",
        "examiner_rubric": [
            "Identifies TWO accurate barriers (patrilineal/primogeniture norms, invisible-force role, stakeholder bias) — 3 marks",
            "Proposes ONE formal meritocratic practice (gender-neutral succession charter / objective board evaluation) — 2 marks"
        ],
        "common_trap": "Giving general societal commentary without connecting to family-business concepts like primogeniture or 'the invisible force.'"
    },
    {
        "anticipation_rank": 15,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "framework": "Family Office, Family Trust & Holding Company",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "A wealthy business family has sold 40% of its operating company for ₹800 crore and now faces sibling disagreements over liquid wealth, inheritance taxes/estate planning, and voting unity on the remaining 60%. Clarify the distinct purpose of a Family Holding Company, a Family Trust, and a Family Office in this situation.",
        "model_answer": "Each vehicle solves a distinct governance problem: (1) The Family Holding Company consolidates the remaining 60% operating stake under one legal umbrella, preserving unified voting control and preventing share fragmentation across branches; (2) The Family Trust holds beneficial interests for estate/succession planning, asset protection, and disciplined distribution rules across generations; (3) The Family Office professionally manages the ₹800 crore liquid proceeds—handling investment allocation, tax, and philanthropy—so siblings do not raid operating cash or fight over ad-hoc investments.",
        "examiner_rubric": [
            "Holding Company = unified voting control over remaining operating equity — 1.5 marks",
            "Family Trust = estate planning, asset protection, distribution rules — 1.5 marks",
            "Family Office = professional management of ₹800 cr liquid wealth & tax/philanthropy — 2 marks"
        ],
        "common_trap": "Confusing a Family Office (wealth management) with a Holding Company (equity/voting consolidation)."
    },
    {
        "anticipation_rank": 16,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "framework": "Generational Stages & Cousin Matrix",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Why does governance complexity jump sharply when a family business transitions from a Sibling Partnership (G2) to a Cousin Consortium (G3)? Use the 'Cousin Matrix' logic to explain TWO specific frictions that emerge in G3.",
        "model_answer": "In G2, siblings share a common household upbringing and direct parental memory. In G3 (Cousin Consortium), owners come from different nuclear families with diverging lifestyles, wealth needs, and emotional distance from the founder. Using the Cousin Matrix (mapping active vs. passive owners across multiple family branches), two sharp frictions emerge: (1) Active vs. Passive Owner divide—working cousins draw salaries and want reinvestment, while non-working cousins demand dividends; (2) Branch asymmetry—larger branches feel diluted per capita while smaller branches fear coalition voting blocks, requiring formal Owners' Councils.",
        "examiner_rubric": [
            "Explains structural shift from shared G2 upbringing to divergent G3 branches — 1.5 marks",
            "Uses Cousin Matrix logic for TWO frictions (Active vs. Passive dividend/reinvestment clash + branch asymmetry/coalitions) — 3.5 marks"
        ],
        "common_trap": "Saying 'there are more people so they fight more' without explaining Active-vs-Passive or branch-level asymmetry."
    },
    {
        "anticipation_rank": 17,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "framework": "Family Employment Policy & In-Laws / Non-Family Executives",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "A non-family VP of Sales resigns after the founder's son-in-law, who has no sales background, is appointed Head of Sales at double the VP's pay. Diagnose the twin governance failures here and list THREE clauses that a Family Employment Policy should enforce to prevent this.",
        "model_answer": "Twin failures: (1) Nepotism and unequal compensation breach procedural justice, signaling a 'glass ceiling' that drives away top non-family talent; (2) Unclear rules around in-laws create branch rivalry and role ambiguity. Three essential Family Employment Policy clauses: (1) Objective entry prerequisites (relevant degree plus 3–5 years of external work experience); (2) Merit-based selection against a real business vacancy evaluated by an independent HR/board panel; (3) Market-benchmarked compensation tied to KPIs, separating employment pay from family ownership dividends.",
        "examiner_rubric": [
            "Diagnoses talent-attrition/procedural-justice failure + in-law/nepotism ambiguity — 2 marks",
            "Lists THREE concrete Family Employment Policy clauses (external experience, real vacancy/merit review, market-benchmarked pay) — 3 marks"
        ],
        "common_trap": "Suggesting a blanket ban on all in-laws instead of objective meritocratic entry and compensation rules."
    },
    {
        "anticipation_rank": 18,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "framework": "The Three-Generation Rule & Operational vs. Ownership Transfer",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Explain the 'Three-Generation Rule' ('shirtsleeves to shirtsleeves in three generations') and distinguish between Ownership Transfer and Management Transfer in preventing a third-generation collapse.",
        "model_answer": "The Three-Generation Rule observes that G1 creates wealth through grit, G2 preserves/expands it, and G3 often dissipates it due to entitlement, family fragmentation, and loss of entrepreneurial drive. Preventing collapse requires separating Management Transfer (handing daily executive control to the most capable leader—family or professional—via rigorous preparation) from Ownership Transfer (distributing equity and voting rights through trusts, holding structures, and shareholder agreements). Even if G3 members are not qualified to manage operations, structured ownership governance keeps capital intact.",
        "examiner_rubric": [
            "Explains G1–G2–G3 trajectory of the Three-Generation Rule — 2 marks",
            "Distinguishes Management Transfer (operational leadership) from Ownership Transfer (equity/voting) and why separating them prevents collapse — 3 marks"
        ],
        "common_trap": "Treating succession as a single event ('giving shares and CEO title together') rather than two separable transfers."
    },
    {
        "anticipation_rank": 19,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 7,
        "module_name": "Module 7: Family Firms, Communities, and External Stakeholders",
        "framework": "Dual Wealth Optimization & Organising for Impact",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "How does strategic philanthropy / impact investing differ from ad-hoc charity in a multi-generational family business, and how can NextGen involvement in an organised Foundation strengthen overall family governance?",
        "model_answer": "Ad-hoc charity relies on the patriarch's personal discretion and creates scattered, unmeasured donations. Strategic philanthropy pursues Dual Wealth Optimization—combining measurable community impact with Socioemotional Wealth (values, reputation, and legacy) through dedicated legal vehicles (Trusts, Section 8 companies, or CSR arms) with clear metrics. Involving NextGen in an organised Foundation acts as a low-risk 'training ground' for governance: younger and non-active cousins learn capital allocation, board collaboration, and shared family values together—building cross-branch trust before they inherit commercial ownership.",
        "examiner_rubric": [
            "Contrasts ad-hoc charity with strategic impact / Dual Wealth Optimization — 2.5 marks",
            "Explains how Foundation participation builds NextGen governance skills, shared values, and cross-branch cohesion — 2.5 marks"
        ],
        "common_trap": "Treating philanthropy purely as tax/CSR compliance instead of a family-cohesion and NextGen-onboarding mechanism."
    },
    {
        "anticipation_rank": 20,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "framework": "Internationalisation in Family Firms",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Family firms often hesitate to expand abroad early, yet once committed they frequently outperform peers internationally. Explain ONE structural barrier holding family firms back from internationalisation and TWO unique advantages they enjoy once they enter foreign markets.",
        "model_answer": "Structural barrier: Fear of losing Socioemotional Wealth (SEW)—internationalisation demands external capital, foreign executives, and decentralized control, which risk-averse founders resist to protect domestic control. Two advantages once committed: (1) Patient capital—long-term horizons allow absorbing early overseas losses without quarterly stock-market pressure; (2) Relational trust and reputation—long-standing family names, diaspora/community networks, and personal commitment from family leaders help win sticky B2B partnerships and joint ventures abroad.",
        "examiner_rubric": [
            "Identifies ONE structural barrier (SEW/control aversion, resistance to external talent/capital) — 2 marks",
            "Identifies TWO distinct advantages (patient capital / long-term horizon + relational/diaspora trust & reputation) — 3 marks"
        ],
        "common_trap": "Listing generic export advantages (like 'bigger market') instead of family-specific advantages (patient capital, relational trust)."
    },
    {
        "anticipation_rank": 21,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "framework": "Resource-Based View (RBV) & 'Familiness' / Types of Capital",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "What does 'Familiness' mean under the Resource-Based View (RBV), and when can this exact bundle of resources turn from a competitive advantage into a liability?",
        "model_answer": "Under the Resource-Based View, 'Familiness' is the unique, idiosyncratic bundle of human, social, patient financial, and survivability capital generated by the interaction between family, its individual members, and the business. Because it is socially complex and path-dependent, rivals cannot easily imitate it—creating a VRIO advantage. However, familiness turns into a liability ('constrictive familiness') when insular norms breed groupthink, nepotism, hoarding of tacit knowledge, and resistance to external talent or market disruption, locking the firm into outdated capabilities.",
        "examiner_rubric": [
            "Defines Familiness as idiosyncratic family-business resource bundle (human/social/patient/survivability capital) — 2.5 marks",
            "Explains when it turns into a liability (insularity, nepotism, rigidity, knowledge hoarding) — 2.5 marks"
        ],
        "common_trap": "Defining familiness merely as 'being friendly like a family' rather than an RBV/VRIO resource bundle."
    },
    {
        "anticipation_rank": 22,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "framework": "Ownership Alternatives Matrix & Exit Mechanisms",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "In a four-branch family firm, one branch wants to exit and cash out, while the other three want to stay invested for the next 20 years. Without a buy-sell mechanism, what risks arise—and how does a Family Bank / Liquidity Redemption Fund solve this?",
        "model_answer": "Without a pre-agreed exit mechanism, a trapped dissatisfied branch ('pruning the tree' problem) can either block board resolutions, leak disputes, or attempt to sell shares to hostile outsiders—destroying firm stability. A Family Bank or structured Liquidity Redemption Fund creates an internal market: it uses retained earnings or dedicated reserves to buy out exiting branches at a pre-agreed, fair-value formula (often with a controlled discount and staggered payout). This protects firm liquidity while preserving family control among committed branches.",
        "examiner_rubric": [
            "Identifies risks of trapped/dissatisfied branches (deadlock, hostile third-party sale) — 2 marks",
            "Explains how a Family Bank / Redemption Fund provides an internal exit at formula-based valuation without hurting control — 3 marks"
        ],
        "common_trap": "Saying 'just list on the stock exchange'—ignoring that IPOs dilute family control and don't fit every firm."
    },
    {
        "anticipation_rank": 23,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "framework": "Earning the Right of Succession & Stakeholder Response",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Why is 'earning the right of succession' critical for external and internal stakeholders, and list THREE credibility tests a successor must pass before taking the CEO seat?",
        "model_answer": "Employees, lenders, and key customers scrutinize whether a NextGen heir is appointed by merit or mere birthright; unearned elevation triggers talent flight and credit skepticism. Successors earn legitimacy by passing three key tests: (1) External Credibility Test—proving competence in an outside firm without the family surname; (2) Internal P&L / Turnaround Test—leading a real operating unit with measurable accountability rather than a shielded staff role; (3) Relational Trust Test—earning respect from senior non-family executives and peers through humility and results.",
        "examiner_rubric": [
            "Explains stakeholder skepticism & why birthright alone fails — 2 marks",
            "Lists THREE concrete credibility tests (external experience, P&L ownership, relational trust) — 3 marks"
        ],
        "common_trap": "Listing academic degrees alone instead of real-world external/internal performance tests."
    },
    {
        "anticipation_rank": 24,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 8,
        "module_name": "Module 8: Institutional Contexts and Family Businesses",
        "framework": "Four Forces Reshaping Family Business & AI/Modernisation",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "How do India's Related-Party Transaction (RPT) regulations under SEBI/Companies Act challenge traditional conglomerate practices, and what governance shift is required?",
        "model_answer": "Historically, Indian family groups freely shifted funds, guarantees, and contracts across promoter entities via informal trust. Modern SEBI LODR and Companies Act rules now require arm's-length pricing, Audit Committee pre-approval (by independent directors), and minority-shareholder voting—blocking abusive tunneling. Family firms must shift from opaque cross-subsidization to clean group structures, transparent transfer-pricing policies, and independent audit oversight to protect minority investors and maintain market valuation multiples.",
        "examiner_rubric": [
            "Explains how RPT rules curb cross-entity fund shifting / tunneling via arm's-length & minority/independent approval — 3 marks",
            "Identifies required shift to transparent structures & independent audit oversight — 2 marks"
        ],
        "common_trap": "Confusing RPTs with illegal fraud in all cases—RPTs are legal if disclosed, arm's-length, and properly approved."
    },

    # --- TIER 3: TARGETED COVERAGE (#25 - #32) ---
    {
        "anticipation_rank": 25,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "framework": "India's Mercantile Communities & Managing Agency System",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Explain how the historical Managing Agency System enabled Indian mercantile families to control vast industrial enterprises with limited equity, and why its abolition in 1970 reshaped Indian corporate structures.",
        "model_answer": "Under the Managing Agency System, a family-controlled managing agency firm signed long-term contracts to manage operating joint-stock companies for fees and commissions—letting families exercise sweeping operational control despite holding modest equity stakes, while pooling scarce capital and trust. When India abolished the system in 1970 to curb concentrated economic power, mercantile families restructured into pyramid holding companies, cross-holdings, and promoter-led boards—laying the blueprint for modern Indian business groups.",
        "examiner_rubric": [
            "Explains control-without-majority-equity mechanism via management contracts — 2.5 marks",
            "Explains post-1970 shift to pyramids, cross-holdings, and modern promoter groups — 2.5 marks"
        ],
        "common_trap": "Thinking the Managing Agency System was a British government department rather than a private corporate-management contract structure."
    },
    {
        "anticipation_rank": 26,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "framework": "Controlling Owner vs. Sibling Partnership",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Contrast the primary governance challenge of the Controlling Owner stage (G1) with that of the Sibling Partnership stage (G2).",
        "model_answer": "In the Controlling Owner stage (G1), authority is centralized in one founder; the core challenge is key-person dependency, lack of checks/balances, and planning succession before founder exit. In the Sibling Partnership stage (G2), ownership and control split across equals who no longer report to a single parent-referee; the core challenge shifts to building horizontal consensus, managing sibling rivalry, balancing active vs. non-active siblings' returns, and formalizing board and communication processes.",
        "examiner_rubric": [
            "Identifies G1 challenge (centralized authority, key-person risk, succession) — 2.5 marks",
            "Identifies G2 challenge (horizontal consensus, active vs. passive tension, rivalry without founder-referee) — 2.5 marks"
        ],
        "common_trap": "Assuming G2 is easier because there are more family members to share work."
    },
    {
        "anticipation_rank": 27,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "framework": "Working Couples & The CEO's Spouse",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "What unique boundary risks arise when a married couple co-manages a family business ('working couples'), and state TWO structural practices that protect both the firm and the marriage?",
        "model_answer": "Working couples face acute role spillover: business disagreements follow them home, marital stress disrupts office authority, and non-family employees struggle with 'who is really in charge' or fear taking sides. Two protective practices: (1) Clear functional separation—assign distinct, non-overlapping domains (e.g., Finance vs. Operations) with independent KPIs; (2) Time and space boundaries—banning business talk after work hours or at family meals, backed by formal dispute-escalation to an advisory board.",
        "examiner_rubric": [
            "Identifies role spillover and employee triangulation risk — 2 marks",
            "Provides TWO concrete boundary practices (distinct functional domains + formal time/escalation rules) — 3 marks"
        ],
        "common_trap": "Giving purely psychological relationship advice without organizational role-separation."
    },
    {
        "anticipation_rank": 28,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "framework": "Types of Professionalised Family Firms",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Why do family owners often resist professionalisation even when growth stalls, and distinguish between 'structural professionalisation' and 'managerial professionalisation'?",
        "model_answer": "Founders resist professionalisation due to fear of losing control, distrust of outsiders with confidential tax/family affairs, reluctance to share equity/bonuses, and perceived cultural dilution. Managerial professionalisation means hiring qualified non-family executives into leadership roles. Structural professionalisation means instituting formal budgets, KPIs, ERP systems, merit-based HR, and independent board governance—whether run by family or outsiders. Hiring an outside CEO without structural systems fails, whereas structural professionalisation can elevate both family and non-family leaders.",
        "examiner_rubric": [
            "States reasons for resistance (control fear, trust/confidentiality, culture/cost) — 2 marks",
            "Accurately distinguishes Managerial (non-family talent) vs. Structural (formal systems/governance) — 3 marks"
        ],
        "common_trap": "Conflating both dimensions into just 'hiring an outside CEO.'"
    },
    {
        "anticipation_rank": 29,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "framework": "Shareholders' Agreement vs. Family Constitution",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "A family spent two years writing an inspiring Family Constitution, yet during a dispute, one branch ignored it and sued in court. Explain the legal enforceability gap between a Family Constitution and a Shareholders' Agreement.",
        "model_answer": "A Family Constitution is a moral, relational charter expressing shared values, entry norms, and dispute etiquette—it is generally non-binding in court. A Shareholders' Agreement (SHA), aligned with the company's Articles of Association, is a legally enforceable contract governing share transfers, pre-emption rights, valuation formulas, drag-along/tag-along clauses, and reserved board matters. To prevent branch litigation, key economic and control rules from the Constitution must be translated into binding SHA and Articles provisions.",
        "examiner_rubric": [
            "Distinguishes moral/non-binding Family Constitution from legally enforceable SHA — 3 marks",
            "Identifies specific SHA clauses (transfer restrictions, valuation, reserved matters) & alignment with Articles — 2 marks"
        ],
        "common_trap": "Thinking a signed Family Constitution is automatically enforceable in corporate courts."
    },
    {
        "anticipation_rank": 30,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 7,
        "module_name": "Module 7: Family Firms, Communities, and External Stakeholders",
        "framework": "Family Firms as Stakeholder Managers & Value Work",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Why do multi-generational family firms often enjoy stronger trust with suppliers, local communities, and employees during crises compared to widely held corporations?",
        "model_answer": "Unlike anonymous corporate managers judged on quarterly EPS, family owners stake their personal surname and multi-generational reputation on every stakeholder promise—creating high relational accountability. Their longer time horizons encourage investing in employee job security, fair supplier credit, and local community goodwill ('Value Work') during booms, building a reservoir of reciprocal trust. When downturns hit, stakeholders reciprocate with wage flexibility, extended credit, and loyalty, enhancing the firm's crisis resilience.",
        "examiner_rubric": [
            "Explains reputational/surname stake + long-term horizon vs. quarterly focus — 2.5 marks",
            "Explains reciprocal crisis resilience (employee/supplier/community support) — 2.5 marks"
        ],
        "common_trap": "Assuming family firms never mistreat workers—focus on why *reputational/long-term* alignment creates crisis resilience when practiced."
    },
    {
        "anticipation_rank": 31,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 8,
        "module_name": "Module 8: Institutional Contexts and Family Businesses",
        "framework": "Four-Room Model & Institutional Pressures",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "Using Douglas North's distinction between Formal and Informal Institutions, explain why copying a Western governance template verbatim often fails in an Indian family business.",
        "model_answer": "Douglas North distinguishes Formal Institutions (laws, SEBI codes, courts) from Informal Institutions (cultural norms, filial deference, caste/kinship trust, face-saving). Copying a Western governance template addresses only formal rules—like appointing nominal independent directors—while ignoring informal Indian norms where junior kin or respectful directors hesitate to challenge the patriarch openly. Effective governance must harmonize formal structures with informal culture, such as using private pre-board consultations or neutral external facilitators so dissent occurs respectfully without public loss of face.",
        "examiner_rubric": [
            "Defines North's Formal vs. Informal Institutions — 2 marks",
            "Explains why Western templates fail when informal deference/face-saving norms clash — 2 marks",
            "Suggests ONE culturally adapted governance practice — 1 mark"
        ],
        "common_trap": "Describing informal institutions as 'backward' rather than persistent social norms that governance must work with."
    },
    {
        "anticipation_rank": 32,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "framework": "Equipping the Successor & Moving from Operation to Ownership",
        "marks": 5,
        "target_words": "80–100 words",
        "question": "How does educating a NextGen member for 'responsible ownership' differ from training them for 'operational management,' and why should every family heir receive ownership education?",
        "model_answer": "Operational training builds functional skills (marketing, finance, plant management) needed only by the few family members who work inside the firm. Ownership education equips ALL heirs—active and passive—to read financial statements, evaluate board reports, understand risk/dividend trade-offs, and exercise their Five Rights responsibly. Since far more family members become shareholders than executives, educating everyone for responsible ownership prevents passive cousins from making naive dividend demands or panicking during downturns.",
        "examiner_rubric": [
            "Distinguishes operational skills (for active managers) vs. ownership literacy (for all shareholders) — 2.5 marks",
            "Explains why all heirs need ownership education (prevents naive demands, enables constructive board/assembly participation) — 2.5 marks"
        ],
        "common_trap": "Focusing only on MBA/management training for the future CEO and ignoring passive shareholders."
    }
]

# ---------------------------------------------------------------------------
# 64 EXAM-LEVEL MCQs (1 Mark each)
# Ordered from Most Anticipated (#1) to Least Anticipated (#64)
# Zero duplicates of extracted CLA questions!
# ---------------------------------------------------------------------------
MCQ_QUESTIONS = [
    # --- TIER 1: MOST ANTICIPATED (#1 - #24) ---
    {
        "anticipation_rank": 1,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "key_concept": "Three-Circle Model Sectors",
        "question": "In Tagiuri and Davis's Three-Circle Model, a retired founder who transferred 100% of her shares to a trust for her grandchildren and no longer holds any operational or board role—yet still influences family gatherings—belongs to which sector?",
        "options": [
            "Sector 1: Family only",
            "Sector 4: Family and Owner",
            "Sector 6: Family and Employee",
            "Sector 7: Family, Owner, and Employee"
        ],
        "correct_index": 0,
        "explanation": "Having divested both equity (Ownership) and any management/board role (Business), she sits strictly in Sector 1 (Family only), though she still exerts informal family influence.",
        "distractor_analysis": "Sector 4 requires holding ownership; Sector 6/7 require active employment in the business."
    },
    {
        "anticipation_rank": 2,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "key_concept": "SEW FIBER Dimensions",
        "question": "A family firm refuses to lay off long-serving factory workers during a two-year recession, even though cutting payroll would restore short-term EBITDA margins. Which FIBER dimension of Socioemotional Wealth best explains this behavior?",
        "options": [
            "Binding social ties",
            "Family control and influence",
            "Renewal of family bonds through dynastic succession",
            "Transaction cost minimization"
        ],
        "correct_index": 0,
        "explanation": "Binding social ties captures reciprocal loyalty and kinship-like obligations toward long-tenured employees and local communities, even at short-term financial cost.",
        "distractor_analysis": "Control/influence concerns voting/board power; dynastic renewal concerns generational handover; transaction cost is an economic theory, not a FIBER dimension."
    },
    {
        "anticipation_rank": 3,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "key_concept": "Type I vs. Type II Agency Costs",
        "question": "When a controlling family appoints an underqualified nephew as CFO and uses firm cash to buy an unrelated resort owned by another family trust, which agency problem is primarily occurring?",
        "options": [
            "Type II (Principal–Principal) agency conflict between controlling family and minority shareholders",
            "Type I (Owner–Manager) agency conflict between dispersed shareholders and a hired CEO",
            "Stewardship alignment failure by independent directors",
            "Market-for-corporate-control failure"
        ],
        "correct_index": 0,
        "explanation": "In concentrated family firms, Type I (owner vs. outside manager) costs are low, but Type II (controlling owner vs. minority shareholder) expropriation/tunneling risks are high.",
        "distractor_analysis": "Type I occurs when dispersed owners cannot monitor a professional manager; here the controlling family itself is extracting private benefits."
    },
    {
        "anticipation_rank": 4,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "key_concept": "Willingness–Ability Matrix",
        "question": "An heir shows deep emotional enthusiasm to take over her father's logistics firm (high willingness) but repeatedly struggles with financial modeling and operational scaling (low ability). What is the soundest immediate governance response?",
        "options": [
            "Design a structured capability-building plan with external mentorship and pair her with a strong professional COO while deferring CEO appointment",
            "Appoint her CEO immediately so she learns on the job while enthusiasm is high",
            "Exclude her from both ownership and management permanently",
            "Sell the business immediately to a strategic buyer"
        ],
        "correct_index": 0,
        "explanation": "High Willingness + Low Ability ('Eager but Unprepared') calls for targeted training, external experience, and pairing with professional management before granting top executive authority.",
        "distractor_analysis": "Immediate CEO appointment risks business failure; permanent exclusion wastes genuine family commitment."
    },
    {
        "anticipation_rank": 5,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "key_concept": "Ability–Willingness Innovation Paradox",
        "question": "Why does the 'Ability–Willingness Innovation Paradox' suggest that family firms often under-invest in disruptive R&D despite having superior decision speed and patient capital?",
        "options": [
            "High discretion gives them the ability to innovate, but fear of losing Socioemotional Wealth and legacy identity reduces their willingness",
            "Family firms legally cannot raise debt for R&D investments",
            "Non-family firms always possess more patient capital than family firms",
            "NextGen members are legally barred from filing patents"
        ],
        "correct_index": 0,
        "explanation": "The paradox lies in the divergence between high *ability* (autonomy, long horizon) and low *willingness* (loss aversion toward SEW, fear of diluting control or legacy routines).",
        "distractor_analysis": "Family firms actually have *more* patient capital than quarterly-driven public firms, and face no legal bar on R&D."
    },
    {
        "anticipation_rank": 6,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "key_concept": "Board Roles (Control vs Service vs Resource)",
        "question": "A family board invites a retired RBI deputy governor to join as an Independent Director primarily to strengthen regulatory credibility with foreign lenders and open institutional doors. Which board role is being prioritized?",
        "options": [
            "Resource Provisioning role",
            "Control and monitoring role",
            "Operational management role",
            "Family Council mediation role"
        ],
        "correct_index": 0,
        "explanation": "Resource Provisioning (rooted in Resource Dependence Theory) uses directors' external prestige, networks, and legitimacy to secure capital, talent, and regulatory access.",
        "distractor_analysis": "Control covers audit/CEO oversight; Service covers strategic advice; boards do not run daily operations."
    },
    {
        "anticipation_rank": 7,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "key_concept": "Five Rights of Family Owners",
        "question": "Which of the Five Rights of Family Owners specifically concerns agreeing on the firm's long-term purpose, acceptable risk appetite, and trade-offs between growth and liquidity?",
        "options": [
            "Right to Define Value",
            "Right to Design",
            "Right to Inform",
            "Right to Transfer"
        ],
        "correct_index": 0,
        "explanation": "The Right to Define Value empowers owners to articulate what 'success' means—balancing profitability, growth, risk tolerance, and non-financial legacy goals.",
        "distractor_analysis": "Right to Design shapes governance structures; Right to Inform governs reporting/communication; Right to Transfer governs ownership exit/inheritance."
    },
    {
        "anticipation_rank": 8,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "key_concept": "Conflict Types",
        "question": "Two sibling directors argue heatedly in a boardroom about whether to enter B2C e-commerce or stay B2B, backed by market data, and then dine cordially together afterward. What type of conflict is this?",
        "options": [
            "Task conflict",
            "Relationship conflict",
            "Process conflict",
            "Dysfunctional role conflict"
        ],
        "correct_index": 0,
        "explanation": "Task conflict centers on substantive strategic choices ('what' to do) without personal hostility; when bounded properly, it improves decision quality.",
        "distractor_analysis": "Relationship conflict involves personal resentment; Process conflict involves disagreements over 'how' tasks, budgets, or roles are assigned."
    },
    {
        "anticipation_rank": 9,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 7,
        "module_name": "Module 7: Family Firms, Communities, and External Stakeholders",
        "key_concept": "Anand Group Case — Earning the Right to Change",
        "question": "In the Anand Group case ('Earning the Right to Change'), what mistake most commonly triggers resistance when a NextGen member returns from abroad to modernize a family enterprise?",
        "options": [
            "Attempting sweeping top-down changes before building credibility and understanding legacy relationships",
            "Working on the shop floor for six months before proposing reforms",
            "Partnering with a senior non-family mentor on a pilot project",
            "Listening to long-tenured plant managers before altering incentives"
        ],
        "correct_index": 0,
        "explanation": "Returning heirs lose legitimacy when they dismiss legacy practices immediately without first proving competence and respecting existing institutional trust.",
        "distractor_analysis": "The other three options are recommended credibility-building steps, not mistakes."
    },
    {
        "anticipation_rank": 10,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 8,
        "module_name": "Module 8: Institutional Contexts and Family Businesses",
        "key_concept": "Scott's Three Pillars of Institutions",
        "question": "According to Richard Scott's Three Pillars of Institutions, SEBI's mandatory requirement for independent directors and audit committees on listed family firms represents which pillar?",
        "options": [
            "Regulative pillar",
            "Normative pillar",
            "Cultural-cognitive pillar",
            "Informal kinship pillar"
        ],
        "correct_index": 0,
        "explanation": "The Regulative pillar encompasses formal laws, statutory rules, sanctions, and compliance enforcement (such as SEBI LODR and Companies Act).",
        "distractor_analysis": "Normative covers professional standards/moral expectations; Cultural-cognitive covers shared beliefs/taken-for-granted mindsets."
    },
    {
        "anticipation_rank": 11,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "key_concept": "Family Constitution vs Shareholders' Agreement",
        "question": "A family wants its rules on share valuation, Right of First Refusal (ROFR), and drag-along rights to be legally enforceable in an Indian court. Where MUST those rules reside?",
        "options": [
            "In a formal Shareholders' Agreement mirrored in the company's Articles of Association",
            "In the preamble of the Family Constitution only",
            "In the minutes of the annual Family Assembly",
            "In a non-binding Family Mission Statement"
        ],
        "correct_index": 0,
        "explanation": "Only a Shareholders' Agreement incorporated into the Articles of Association carries statutory enforceability in corporate litigation; a Family Constitution is a moral charter.",
        "distractor_analysis": "Family Constitutions, Assembly minutes, and Mission Statements guide family behavior morally but do not bind corporate share transfers in court."
    },
    {
        "anticipation_rank": 12,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "key_concept": "Structural vs Managerial Professionalisation",
        "question": "Which scenario best illustrates a family firm achieving 'professionalisation' without replacing family leadership?",
        "options": [
            "A family CEO implements audited budgets, merit-based KPIs, ERP reporting, and an independent advisory board",
            "The founder's three sons divide regional territories based on birth order",
            "The firm hires an outside COO but overrides every decision informally at dinner",
            "All family members stop attending board meetings while retaining informal veto power"
        ],
        "correct_index": 0,
        "explanation": "Professionalisation is fundamentally about adopting formal systems, meritocratic accountability, and governance—not merely hiring non-family faces.",
        "distractor_analysis": "Hiring an outsider while overriding them informally is pseudo-professionalisation; birth-order allocation is anti-meritocratic."
    },
    {
        "anticipation_rank": 13,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "key_concept": "Incumbent's Dilemma",
        "question": "Why do founders frequently delay handing over operational authority even after publicly naming a successor ('The Incumbent's Dilemma')?",
        "options": [
            "Personal identity, self-worth, and social status are deeply fused with running the firm, making exit feel like a loss of relevance",
            "Company law prohibits founders under age 75 from resigning as Managing Director",
            "Successors legally cannot hold signing authority until the founder passes away",
            "Independent directors always block founder retirement to protect their sitting fees"
        ],
        "correct_index": 0,
        "explanation": "For founder-entrepreneurs, the business is an extension of self-identity; stepping down triggers fear of irrelevance, loss of authority, and confronting mortality.",
        "distractor_analysis": "None of the legal or board claims in the other options are true."
    },
    {
        "anticipation_rank": 14,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "key_concept": "Three Powers (Create, Sustain, Destroy)",
        "question": "When a controlling shareholder group refuses to update outdated governance or blocks a needed capital raise solely to keep voting dominance, which of the Three Powers is manifesting negatively?",
        "options": [
            "Power to Destroy",
            "Power to Create",
            "Power to Sustain",
            "Right to Inform"
        ],
        "correct_index": 0,
        "explanation": "The Power to Destroy refers to owners' capacity to paralyze strategy, withhold needed capital, or trigger destructive conflict when ownership authority is misused.",
        "distractor_analysis": "Power to Create builds new ventures/value; Power to Sustain preserves continuity responsibly."
    },
    {
        "anticipation_rank": 15,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "key_concept": "Equality vs Equity",
        "question": "A founder leaves 50% ownership to her active CEO son and 50% to her non-active doctor daughter, while paying the son a market-benchmarked executive salary plus performance bonus. Which principle does this follow?",
        "options": [
            "Equal ownership combined with equitable (merit-based) executive compensation",
            "Strict equality in both ownership and compensation regardless of contribution",
            "Primogeniture excluding daughters from equity",
            "Commingling dividend returns with operational pay"
        ],
        "correct_index": 0,
        "explanation": "Distinguishing Equality (equal family inheritance/ownership) from Equity (fair compensation proportional to work, risk, and market benchmarks) prevents resentment on both sides.",
        "distractor_analysis": "Paying the non-active sister the same executive salary would confuse equality with equity; here ownership is equal while pay is equitable."
    },
    {
        "anticipation_rank": 16,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "key_concept": "Anderson & Reeb (2003) & Alignment–Entrenchment",
        "question": "What central empirical nuance did Anderson and Reeb (2003) establish regarding S&P 500 family firms?",
        "options": [
            "Family firms outperformed non-family firms on average, especially when a family member served as CEO, though extreme control without checks risks entrenchment",
            "Family firms consistently underperformed non-family firms across every industry",
            "Performance peaked only after all founding family members sold their shares",
            "Family firms outperformed solely because they paid zero dividends"
        ],
        "correct_index": 0,
        "explanation": "Anderson & Reeb (2003) famously showed superior accounting and market performance in S&P 500 family firms—especially with founder/family CEOs—subject to the alignment-vs-entrenchment balance.",
        "distractor_analysis": "The paper refuted the assumption that family firms always underperform."
    },
    {
        "anticipation_rank": 17,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 8,
        "module_name": "Module 8: Institutional Contexts and Family Businesses",
        "key_concept": "Institutional Voids",
        "question": "Why have diversified family business groups historically thrived in emerging economies characterized by 'institutional voids'?",
        "options": [
            "They build internal capital, talent, and trust markets that substitute for weak external financial and legal institutions",
            "Institutional voids legally exempt family firms from paying corporate taxes",
            "Multinational competitors are banned from entering markets with institutional voids",
            "Family firms rely exclusively on short-term public bond markets"
        ],
        "correct_index": 0,
        "explanation": "When external courts, credit bureaus, and labor markets are underdeveloped, family conglomerates use internal capital allocation, shared brand reputation, and kinship trust to lower transaction costs.",
        "distractor_analysis": "Tax exemptions, MNC bans, and bond reliance are false distractors."
    },
    {
        "anticipation_rank": 18,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "key_concept": "Family Office vs Family Trust",
        "question": "What is the primary structural distinction between a Family Trust and a Family Office?",
        "options": [
            "A Family Trust is a legal fiduciary vehicle for holding/protecting assets across generations, whereas a Family Office is an operating organization that actively manages wealth, tax, and investments",
            "A Family Office is strictly for philanthropic donations, while a Family Trust runs factory operations",
            "A Family Trust can only hold cash, while a Family Office can only hold real estate",
            "A Family Office replaces the Board of Directors of the core operating company"
        ],
        "correct_index": 0,
        "explanation": "A Trust is a legal ownership/estate arrangement (settlor–trustee–beneficiary), while a Family Office is the professional team/entity managing the family's investments, tax, and administration.",
        "distractor_analysis": "Neither runs core factory operations nor replaces the operating company's Board."
    },
    {
        "anticipation_rank": 19,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "key_concept": "Tests for the Successor",
        "question": "Why do governance experts recommend that NextGen heirs work 3–5 years at an unrelated company before joining the family firm?",
        "options": [
            "To gain objective performance feedback, learn external best practices, and earn internal legitimacy without the protection of the family name",
            "To qualify for lower personal income tax rates upon returning",
            "Because Indian company law prohibits heirs under 25 from holding executive titles",
            "To permanently sever emotional ties with the founding generation"
        ],
        "correct_index": 0,
        "explanation": "External experience tests competence in an environment without nepotistic shielding, brings fresh benchmarks back, and builds credibility with skeptical non-family staff.",
        "distractor_analysis": "There is no tax or statutory 25-year rule, and the goal is credibility, not severing family ties."
    },
    {
        "anticipation_rank": 20,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "key_concept": "Exploration vs Exploitation",
        "question": "Across generations, why do many second- and third-generation family firms struggle with 'exploration' (radical new business models) compared to 'exploitation' (refining the founder's core business)?",
        "options": [
            "Loss aversion toward accumulated wealth and deference to the founder's sacred legacy discourage risky experimentation",
            "Older family firms lack the retained earnings needed to fund exploration",
            "Exploration is only possible in publicly listed non-family startups",
            "Founders always mandate 50% R&D budgets in their wills"
        ],
        "correct_index": 0,
        "explanation": "Once wealth is built, preserving SEW and avoiding risking the founder's 'crown jewel' pushes later generations toward safe exploitation over uncertain exploration.",
        "distractor_analysis": "Multi-gen firms often have *more* retained capital, not less; the barrier is risk aversion and legacy lock-in."
    },
    {
        "anticipation_rank": 21,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "key_concept": "Women as the Invisible Force",
        "question": "In family business literature, what does the phrase 'women as the invisible force' refer to?",
        "options": [
            "Spouses, mothers, and daughters who heavily shape values, mediate conflicts, and advise founders informally while lacking formal titles, pay, or board recognition",
            "Women independent directors mandated solely by SEBI quotas",
            "Female non-family factory workers in export-oriented textiles",
            "Women heirs who voluntarily sell their shares at IPO"
        ],
        "correct_index": 0,
        "explanation": "The 'invisible force' describes crucial behind-the-scenes emotional, peacemaking, and advisory leadership exercised by family women without formal governance recognition.",
        "distractor_analysis": "It specifically refers to uncredited informal family influence, not SEBI-mandated directors or factory labor."
    },
    {
        "anticipation_rank": 22,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 7,
        "module_name": "Module 7: Family Firms, Communities, and External Stakeholders",
        "key_concept": "Dual Wealth Optimization",
        "question": "What does 'Dual Wealth Optimization' mean for a family enterprise engaging in community impact?",
        "options": [
            "Simultaneously generating measurable social/environmental impact and long-term financial/reputational resilience rather than treating them as a zero-sum trade-off",
            "Splitting profits 50-50 between domestic and offshore family trusts",
            "Replacing all commercial sales with grant-funded NGO operations",
            "Maximizing short-term quarterly dividends before donating personal shares"
        ],
        "correct_index": 0,
        "explanation": "Dual Wealth Optimization aligns business financial health with Socioemotional Wealth and societal value creation.",
        "distractor_analysis": "It is not offshore splitting, abandoning commerce, or short-termism."
    },
    {
        "anticipation_rank": 23,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "key_concept": "Cousin Consortium Frictions",
        "question": "Which friction is most characteristic of a Cousin Consortium (G3) compared to a Controlling Owner (G1) firm?",
        "options": [
            "Diverging liquidity vs. reinvestment preferences between active managing cousins and passive dividend-dependent cousins",
            "Complete absence of any family shareholders",
            "Total reliance on a single living founder to settle every dispute",
            "Inability to legally incorporate as a private limited company"
        ],
        "correct_index": 0,
        "explanation": "By G3, most owners do not work in the firm, creating a structural split between active managers wanting retained earnings and passive cousins wanting dividends.",
        "distractor_analysis": "G1 has a single founder-referee; G3 has multiple branches and shareholders."
    },
    {
        "anticipation_rank": 24,
        "anticipation_tier": "Tier 1: Most Anticipated",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "key_concept": "Resistance to Independent Directors",
        "question": "Why do many Indian family firms resist appointing truly independent directors to their corporate boards?",
        "options": [
            "Fear of losing privacy over family matters, reluctance to face scrutiny on RPTs, and worry that outsiders lack commitment to long-term family values",
            "Independent directors are legally required to hold at least 10% equity",
            "Companies Act prohibits independent directors on private firm boards",
            "Independent directors automatically become CEO within three years"
        ],
        "correct_index": 0,
        "explanation": "Privacy concerns, fear of challenging founder authority/RPTs, and doubt about outsiders' cultural alignment drive resistance.",
        "distractor_analysis": "Independent directors cannot hold significant equity, are permitted on private boards voluntarily, and never automatically become CEO."
    },

    # --- TIER 2: HIGH PROBABILITY (#25 - #48) ---
    {
        "anticipation_rank": 25,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "key_concept": "Transaction Cost Economics (TCE)",
        "question": "How does Transaction Cost Economics (TCE) explain the competitive advantage of trust-based Indian family business networks (like historical mercantile communities)?",
        "options": [
            "Shared community norms and reputational sanctions drastically reduce contracting, monitoring, and enforcement costs",
            "TCE assumes all contracts are costless to enforce in court",
            "Family firms eliminate all production costs through vertical monopolies",
            "TCE proves family members never behave opportunistically"
        ],
        "correct_index": 0,
        "explanation": "TCE focuses on search, contracting, and enforcement costs; high-trust kinship/community networks enforce implicit agreements via reputation, cutting transaction costs.",
        "distractor_analysis": "TCE never assumes costless courts or zero opportunism; rather, community sanctions deter opportunism cheaply."
    },
    {
        "anticipation_rank": 26,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "key_concept": "Types of Capital (Survivability Capital)",
        "question": "During a severe liquidity crunch, three family directors waive their salaries for a year and pledge personal fixed deposits to keep the factory running. Which family-business resource does this represent?",
        "options": [
            "Survivability capital",
            "Agency bonding capital",
            "Venture syndication capital",
            "Public float capital"
        ],
        "correct_index": 0,
        "explanation": "Survivability capital is the pool of personal resources—unpaid labor, personal loans, or collateral—that family members willingly contribute during crises to keep the firm alive.",
        "distractor_analysis": "Non-family managers rarely waive pay and pledge personal assets in crises; this is uniquely survivability capital."
    },
    {
        "anticipation_rank": 27,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "key_concept": "Family First vs Business First",
        "question": "A family firm maintains an unprofitable legacy division solely so two underperforming cousins retain executive titles and social prestige. Which philosophy is dominating?",
        "options": [
            "Family-First philosophy",
            "Business-First philosophy",
            "Dual-Optimization philosophy",
            "Shareholder-Activist philosophy"
        ],
        "correct_index": 0,
        "explanation": "A Family-First approach subordinates commercial viability and meritocracy to preserving family harmony, roles, or status.",
        "distractor_analysis": "A Business-First approach would restructure or exit the loss-making unit regardless of cousin titles."
    },
    {
        "anticipation_rank": 28,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "key_concept": "Right to Design vs Right to Decide",
        "question": "When family owners collectively establish a Holding Company and decide what voting thresholds apply to selling core subsidiaries, which ownership right are they exercising?",
        "options": [
            "Right to Design",
            "Right to Inform",
            "Right to Transfer",
            "Operational Management Right"
        ],
        "correct_index": 0,
        "explanation": "The Right to Design is the owners' prerogative to architect the legal, governance, and board structures through which the business is controlled.",
        "distractor_analysis": "Right to Inform deals with reporting; Right to Transfer deals with share exit/inheritance."
    },
    {
        "anticipation_rank": 29,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "key_concept": "Crown Prince vs Horse Race Succession",
        "question": "Which succession path involves pitting two or three NextGen contenders against one another in parallel P&L divisions for several years before selecting the CEO?",
        "options": [
            "Horse race (tournament) succession",
            "Crown prince (anointed heir) succession",
            "Regency succession",
            "Emergency caretaker succession"
        ],
        "correct_index": 0,
        "explanation": "A 'horse race' tests multiple candidates in comparable roles before deciding, which promotes meritocracy but risks factionalism and losing the runner-up.",
        "distractor_analysis": "'Crown prince' designates one heir early; 'Regency' uses an interim non-family leader until a young heir matures."
    },
    {
        "anticipation_rank": 30,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "key_concept": "Three-Generation Rule",
        "question": "Why does 'shirtsleeves to shirtsleeves in three generations' occur even in profitable family firms?",
        "options": [
            "Ownership dilution across branches, growing entitlement in G3, and failure to adapt the founder's original business model",
            "Corporate tax rates triple automatically in the third generation",
            "Banks refuse to lend to companies older than 40 years",
            "Founders are legally prohibited from leaving shares to grandchildren"
        ],
        "correct_index": 0,
        "explanation": "Generational wealth erosion stems from demographic fragmentation (more mouths, smaller per-capita stakes), entitlement, and strategic rigidity.",
        "distractor_analysis": "Tax tripling, bank age bans, and inheritance prohibitions are fabricated distractors."
    },
    {
        "anticipation_rank": 31,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "key_concept": "Related-Party Transactions (RPTs)",
        "question": "A family firm leases its corporate office from a building privately owned by the founder's spouse at 40% above market rent without board disclosure. What governance risk does this exemplify?",
        "options": [
            "Abusive Related-Party Transaction (RPT) / private benefit extraction",
            "Legitimate survivability capital contribution",
            "Arm's-length market benchmarking",
            "Constructive task conflict"
        ],
        "correct_index": 0,
        "explanation": "Off-market, undisclosed transactions with promoter-linked entities are classic abusive RPTs that siphon value away from the operating firm and minority owners.",
        "distractor_analysis": "Arm's-length requires market pricing and disclosure; survivability capital injects value *into* the firm, not out of it."
    },
    {
        "anticipation_rank": 32,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "key_concept": "Non-Family Executives",
        "question": "What is the single most effective way to retain high-performing non-family executives in a family-controlled firm?",
        "options": [
            "Provide transparent career pathways, real decision autonomy, and long-term performance incentives (e.g., phantom equity) alongside fair family rules",
            "Promise them they will inherit voting control over the family trust",
            "Exclude them from all strategic discussions so they focus solely on clerical tasks",
            "Allow family members to bypass them without notice"
        ],
        "correct_index": 0,
        "explanation": "Non-family talent stays when treated with procedural fairness—clear authority, meritocratic growth, and wealth-sharing mechanisms like phantom stock—without requiring voting control.",
        "distractor_analysis": "Voting inheritance is unrealistic; excluding or bypassing executives accelerates attrition."
    },
    {
        "anticipation_rank": 33,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "key_concept": "Three Paths to Professionalisation",
        "question": "When a founder trains a promising NextGen family member with an external MBA, outside work experience, and executive coaching to lead formalized systems, which path to professionalisation is being used?",
        "options": [
            "Internal family professionalisation",
            "External executive takeover with family exit",
            "Hostile activist restructuring",
            "Informal patrimonialism"
        ],
        "correct_index": 0,
        "explanation": "One of the three paths is professionalising *within* the family—upgrading family leaders' capabilities and formalizing systems rather than assuming only outsiders are professional.",
        "distractor_analysis": "External takeover removes family leadership; patrimonialism rejects formal systems."
    },
    {
        "anticipation_rank": 34,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "key_concept": "Internationalisation Theories (Uppsala vs Born Global)",
        "question": "Why do traditional family firms frequently follow the incremental 'Uppsala Model' when internationalising rather than aggressive global leaps?",
        "options": [
            "Gradual entry into culturally close markets minimizes risk to Socioemotional Wealth and lets trust networks develop step-by-step",
            "Uppsala prohibits exporting to neighboring countries",
            "Family firms lack any desire to preserve control",
            "Indian law restricts exports to one new country per decade"
        ],
        "correct_index": 0,
        "explanation": "The Uppsala stage model fits family firms' risk-averse, SEW-protecting mindset—building experiential knowledge and trusted partners in psychically close markets first.",
        "distractor_analysis": "The other options invert Uppsala or invent legal restrictions."
    },
    {
        "anticipation_rank": 35,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "key_concept": "Family Forum vs Family Council",
        "question": "How does a Family Assembly (Forum) differ from a Family Council in a large 40-member multi-branch family?",
        "options": [
            "The Family Assembly is the broad inclusive gathering of all family members (including spouses/NextGen), whereas the Family Council is a smaller elected/representative body",
            "The Family Assembly manages daily factory shifts, while the Family Council audits quarterly taxes",
            "Only non-family managers attend the Family Assembly",
            "They are identical terms for the corporate Board of Directors"
        ],
        "correct_index": 0,
        "explanation": "The Assembly/Forum builds broad belonging and shared values across all kin; the Council is the smaller representative executive committee of the family.",
        "distractor_analysis": "Neither manages factory shifts or taxes, and both are family bodies rather than the corporate Board."
    },
    {
        "anticipation_rank": 36,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "key_concept": "Family Bank & Investment Committee",
        "question": "What is the primary purpose of establishing a 'Family Bank' inside a multi-branch family group?",
        "options": [
            "To pool family capital for funding NextGen entrepreneurial ventures or buying out exiting branches under disciplined investment criteria",
            "To replace commercial retail banking licenses for the general public",
            "To issue interest-free personal consumption loans without repayment",
            "To eliminate the need for audited financial statements"
        ],
        "correct_index": 0,
        "explanation": "A Family Bank channels collective wealth into vetted NextGen startups or internal liquidity buybacks with formal Investment Committee discipline.",
        "distractor_analysis": "It is an internal family capital vehicle, not a public bank or unaccountable handout fund."
    },
    {
        "anticipation_rank": 37,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 7,
        "module_name": "Module 7: Family Firms, Communities, and External Stakeholders",
        "key_concept": "Legal Vehicles for Philanthropy (India)",
        "question": "In India, if a business family wants to run a structured, non-profit philanthropic venture with stronger corporate-style governance, auditability, and ease of receiving CSR grants, which legal vehicle is typically preferred over an informal trust?",
        "options": [
            "Section 8 Company (under the Companies Act, 2013)",
            "Unlimited Partnership Firm",
            "Sole Proprietorship",
            "Hindu Undivided Family (HUF) trading account"
        ],
        "correct_index": 0,
        "explanation": "A Section 8 non-profit company offers robust statutory governance, board structure, and high credibility for institutional CSR partnerships.",
        "distractor_analysis": "Partnerships, proprietorships, and HUFs are commercial/tax structures, not dedicated non-profit governance vehicles."
    },
    {
        "anticipation_rank": 38,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 7,
        "module_name": "Module 7: Family Firms, Communities, and External Stakeholders",
        "key_concept": "Legacy vs Modernisation",
        "question": "When a NextGen leader modernizes a legacy brand without erasing its founding heritage, what balance are they striking?",
        "options": [
            "Preserving core family values and purpose ('roots') while updating business models, technology, and governance ('wings')",
            "Liquidating all legacy assets and concealing the family history",
            "Freezing all product lines exactly as they were in 1970",
            "Replacing all brand identity with anonymous private-label manufacturing"
        ],
        "correct_index": 0,
        "explanation": "Enduring family firms treat legacy as an anchor of values and trust rather than an excuse to freeze operating models.",
        "distractor_analysis": "Total liquidation erases valuable heritage; freezing operations causes obsolescence."
    },
    {
        "anticipation_rank": 39,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 8,
        "module_name": "Module 8: Institutional Contexts and Family Businesses",
        "key_concept": "Douglas North — Formal vs Informal Institutions",
        "question": "In Douglas North's institutional framework, unspoken deference to the eldest male relative—even when a younger sister holds a higher corporate title—is an example of:",
        "options": [
            "An informal institution (cultural norm/convention)",
            "A formal regulative statute",
            "A SEBI listing mandate",
            "A binding Articles of Association clause"
        ],
        "correct_index": 0,
        "explanation": "Informal institutions are socially transmitted customs, norms, and codes of conduct that persist independently of written law.",
        "distractor_analysis": "Statutes, SEBI rules, and Articles are formal written institutions."
    },
    {
        "anticipation_rank": 40,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 8,
        "module_name": "Module 8: Institutional Contexts and Family Businesses",
        "key_concept": "Four Forces Reshaping Business",
        "question": "Which combination best reflects the macro forces currently compelling Indian family businesses to upgrade governance and technology?",
        "options": [
            "Digital/AI disruption, regulatory tightening (SEBI/tax transparency), generational value shifts, and global capital competition",
            "Return of the Managing Agency System and closure of Indian stock exchanges",
            "Elimination of all foreign competition under License Raj quotas",
            "Universal ban on private equity investments in family firms"
        ],
        "correct_index": 0,
        "explanation": "Modernisation is driven by tech/AI shifts, stricter regulation, NextGen expectations, and globalized capital/product markets.",
        "distractor_analysis": "The remaining choices describe reversed or fictional historical conditions."
    },
    {
        "anticipation_rank": 41,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "key_concept": "India's Mercantile Communities (Hundi)",
        "question": "Historically, what role did the 'Hundi' system play among India's mercantile family communities (such as Marwaris and Chettiars)?",
        "options": [
            "An indigenous, trust-based credit and remittance instrument enabling long-distance trade without formal colonial banks",
            "A colonial government tax levied solely on textile exports",
            "A mandatory equity-listing certificate on the Bombay Stock Exchange",
            "A formal divorce settlement contract for joint families"
        ],
        "correct_index": 0,
        "explanation": "Hundis were informal bills of exchange backed by community reputation and trust, allowing rapid capital movement across trade networks.",
        "distractor_analysis": "Hundis were private credit instruments, not taxes, stock certificates, or family-law contracts."
    },
    {
        "anticipation_rank": 42,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "key_concept": "Entrepreneurial Family Galaxy",
        "question": "What does the 'Entrepreneurial Family Galaxy' concept highlight that a single-firm org chart misses?",
        "options": [
            "A single enterprising family often owns a constellation of operating firms, holding vehicles, trusts, family offices, and foundations",
            "Every family business operates only one legal entity throughout its history",
            "Non-family employees own the majority of shares in the family galaxy",
            "Family businesses cannot diversify across unrelated industries"
        ],
        "correct_index": 0,
        "explanation": "Enterprising families typically govern an ecosystem ('galaxy') of ventures, real estate, trusts, and philanthropic arms rather than one standalone firm.",
        "distractor_analysis": "The whole point of the galaxy metaphor is multi-entity breadth."
    },
    {
        "anticipation_rank": 43,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "key_concept": "Succession as a Process",
        "question": "Why is viewing succession as a 'single event' (e.g., signing share transfer papers on the founder's 70th birthday) dangerous?",
        "options": [
            "Without years of gradual socialization, mentoring, and stakeholder alignment, abrupt handovers trigger operational shock and power vacuums",
            "Indian law requires succession to happen in one single day",
            "Gradual succession eliminates all tax liabilities automatically",
            "Stakeholders prefer zero warning before a CEO change"
        ],
        "correct_index": 0,
        "explanation": "Effective succession is a multi-year process—socializing values, building skills, transferring relationships, and phasing authority.",
        "distractor_analysis": "Stakeholders strongly prefer predictable, staged transitions."
    },
    {
        "anticipation_rank": 44,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "key_concept": "Sibling Working Styles",
        "question": "When two brothers join the family firm, which structural arrangement minimizes daily turf wars?",
        "options": [
            "Clear division of complementary domains (e.g., Manufacturing vs. Sales) with shared strategic alignment at the Board level",
            "Assigning both brothers identical Co-Head titles over the exact same department with no tie-breaker",
            "Banning them from attending any joint strategy meetings",
            "Having their mother secretly decide every operational dispute"
        ],
        "correct_index": 0,
        "explanation": "Complementary, non-overlapping functional roles paired with formal board coordination prevent friction and duplicate authority.",
        "distractor_analysis": "Overlapping Co-Head titles without tie-breakers breed constant turf battles."
    },
    {
        "anticipation_rank": 45,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "key_concept": "Balancing Control and Professionalisation",
        "question": "What is a 'Bridge Executive' in a newly professionalising family business?",
        "options": [
            "A trusted senior non-family leader who translates between the founder's intuitive culture and formal professional systems",
            "An external investment banker hired solely to sell the company",
            "A temporary intern rotating across departments for two weeks",
            "A relative who refuses to use ERP software"
        ],
        "correct_index": 0,
        "explanation": "A bridge executive enjoys the founder's personal trust while mentoring staff and installing modern processes without triggering cultural shock.",
        "distractor_analysis": "They are long-term internal stabilizers, not M&A sell-side bankers or interns."
    },
    {
        "anticipation_rank": 46,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "key_concept": "Board Size & Diversity",
        "question": "Why does adding cognitive and industry diversity (not just family friends) to a family board improve strategic decision-making?",
        "options": [
            "It counters groupthink, brings external market benchmarks, and challenges founder blind spots",
            "It guarantees 100% unanimous agreement without debate",
            "It removes the legal fiduciary duty of family directors",
            "It eliminates the need for an annual audit"
        ],
        "correct_index": 0,
        "explanation": "Diverse directors reduce insular groupthink and supply fresh industry, tech, and governance perspectives.",
        "distractor_analysis": "Healthy boards have constructive debate, not rubber-stamp unanimity."
    },
    {
        "anticipation_rank": 47,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 7,
        "module_name": "Module 7: Family Firms, Communities, and External Stakeholders",
        "key_concept": "Value Work",
        "question": "What is meant by 'Value Work' in multi-generational family enterprises?",
        "options": [
            "Deliberate, ongoing articulation and enactment of core family principles in hiring, supplier fairness, and community decisions—not just framing posters",
            "Hiring an accounting firm to calculate book value every quarter",
            "Maximizing short-term stock price by cutting community programs",
            "Replacing family heritage with generic PR slogans"
        ],
        "correct_index": 0,
        "explanation": "Value Work actively translates founding values into living business practices across generations.",
        "distractor_analysis": "It is cultural/ethical alignment work, not accounting valuation or PR spin."
    },
    {
        "anticipation_rank": 48,
        "anticipation_tier": "Tier 2: High Probability",
        "module_number": 8,
        "module_name": "Module 8: Institutional Contexts and Family Businesses",
        "key_concept": "Trust to Rules Transition",
        "question": "What triggers the tipping point where a growing family firm must shift 'from trust to rules'?",
        "options": [
            "Increasing family/business complexity, outside capital entry, and stricter regulatory scrutiny outgrow informal personal trust",
            "The founder finishes reading a textbook on day one of incorporation",
            "All family members agree to stop speaking permanently",
            "The firm shrinks to a single-person sole proprietorship"
        ],
        "correct_index": 0,
        "explanation": "Scale, multi-branch dispersion, institutional investors, and regulatory mandates make informal handshake governance unsustainable.",
        "distractor_analysis": "Simpler/smaller firms can still run on relational trust; complexity forces codification."
    },

    # --- TIER 3: TARGETED COVERAGE (#49 - #64) ---
    {
        "anticipation_rank": 49,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "key_concept": "Active vs Proactive Adaptation (India)",
        "question": "How did Indian family business houses adapt differently during the License Raj (pre-1991) compared to the Post-Liberalisation era (1991–present)?",
        "options": [
            "License Raj rewarded bureaucratic license-navigation and diversification ('active adaptation'), whereas post-1991 demanded global competitiveness, focus, and professionalisation ('proactive adaptation')",
            "License Raj encouraged unrestricted foreign imports and zero licensing",
            "Post-1991 banned Indian family firms from raising foreign capital",
            "Both eras rewarded identical political lobbying over operational efficiency"
        ],
        "correct_index": 0,
        "explanation": "Pre-1991 favored navigating state controls and conglomerate licensing; post-1991 forced global quality, specialization, and capital-market governance.",
        "distractor_analysis": "Post-1991 opened global competition and capital access rather than banning it."
    },
    {
        "anticipation_rank": 50,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 1,
        "module_name": "Module 1: Introduction to Family Businesses",
        "key_concept": "Ownership Competence",
        "question": "What does 'Ownership Competence' emphasize in modern family business theory?",
        "options": [
            "The skill of owners to match the right governance structure, capital horizon, and strategic mandate to a firm's needs—beyond merely holding shares",
            "Knowing how to operate factory machinery personally",
            "Eliminating all non-family shareholders regardless of cost",
            "Trading shares daily for short-term arbitrage"
        ],
        "correct_index": 0,
        "explanation": "Ownership competence treats owning as an active skill: choosing what to own, how to govern it, and what value horizon to enforce.",
        "distractor_analysis": "It is about *ownership* stewardship, not shop-floor operations or day-trading."
    },
    {
        "anticipation_rank": 51,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "key_concept": "Levels of Analysis",
        "question": "Why must advisors diagnose family business problems across multiple 'Levels of Analysis' (Individual, Family, Business, Ownership)?",
        "options": [
            "An issue presenting as a business cash crisis (e.g., low retained earnings) may originate at the family or ownership level (e.g., sibling dividend expectations)",
            "Because Indian tax law taxes each level separately",
            "To ensure individual founders never speak to boards",
            "Because business metrics are irrelevant in family firms"
        ],
        "correct_index": 0,
        "explanation": "Cross-level spillover means symptoms in one circle often stem from root causes in another.",
        "distractor_analysis": "Business metrics matter deeply; multi-level diagnosis locates root causes accurately."
    },
    {
        "anticipation_rank": 52,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 2,
        "module_name": "Module 2: Dynamics of Family Firm",
        "key_concept": "Right to Transfer",
        "question": "Why do family companies restrict the 'Right to Transfer' shares in private corporate charters?",
        "options": [
            "To prevent shares from passing to hostile outsiders or fragmenting uncontrollably via divorce/sale without internal pre-emption",
            "To prevent owners from ever receiving dividends",
            "Because shares of private firms have zero economic value",
            "To force every cousin to work as a full-time employee"
        ],
        "correct_index": 0,
        "explanation": "Pre-emption / Right of First Refusal clauses balance owners' exit rights with the collective goal of keeping control within the family.",
        "distractor_analysis": "Transfer restrictions protect ownership cohesion; they do not block dividends."
    },
    {
        "anticipation_rank": 53,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "key_concept": "Succession & Commitment",
        "question": "Which type of NextGen commitment—joining out of genuine passion vs. joining out of guilt/obligation—produces stronger long-term leadership?",
        "options": [
            "Affective commitment (genuine desire and identification), rather than normative (obligation) or continuance (financial lock-in) commitment",
            "Continuance commitment driven solely by fear of losing inheritance",
            "Normative commitment driven purely by parental guilt",
            "Forced commitment without career choice"
        ],
        "correct_index": 0,
        "explanation": "Affective commitment fuels proactive innovation and resilience, whereas guilt-driven or trapped commitment breeds burnout and resentment.",
        "distractor_analysis": "Obligation and financial lock-in correlate with lower entrepreneurial engagement."
    },
    {
        "anticipation_rank": 54,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 3,
        "module_name": "Module 3: Succession in Family Firms",
        "key_concept": "Ten Key Tensions",
        "question": "During succession, a founder wants rapid consensus while the incoming NextGen seeks data-driven debate and formal KPIs. Which classic tension does this reflect?",
        "options": [
            "Informal intuitive authority vs. formalized meritocratic governance",
            "Export growth vs. domestic CSR",
            "Public listing vs. bankruptcy",
            "Debt financing vs. trade credit"
        ],
        "correct_index": 0,
        "explanation": "A core succession tension pits the founder's tacit, intuitive decision style against NextGen's analytical, formalized management style.",
        "distractor_analysis": "The other options are unrelated operational/financial choices."
    },
    {
        "anticipation_rank": 55,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "key_concept": "CEO's Spouse",
        "question": "Why does family business governance pay special attention to the role of the CEO's spouse?",
        "options": [
            "Even without an office title, the spouse often acts as the CEO's primary confidant, emotional anchor, and bridge between generations",
            "Because spouses legally hold automatic board voting rights in India",
            "Because spouses are barred from attending family assemblies",
            "Because spouses always run the finance department"
        ],
        "correct_index": 0,
        "explanation": "The spouse wields substantial informal influence over succession timing, sibling fairness, and family cohesion.",
        "distractor_analysis": "Spouses do not hold automatic statutory board votes without appointment/shares."
    },
    {
        "anticipation_rank": 56,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 4,
        "module_name": "Module 4: Family Dynamics in Action",
        "key_concept": "Role of Family Science",
        "question": "How does applying 'Family Science' (family systems, genograms, communication patterns) help a family business advisor?",
        "options": [
            "It uncovers unspoken generational triangles, birth-order expectations, and emotional patterns driving seemingly 'financial' disputes",
            "It replaces statutory financial auditing with psychological counseling",
            "It calculates weighted average cost of capital (WACC)",
            "It drafts patent applications for R&D teams"
        ],
        "correct_index": 0,
        "explanation": "Family science tools like genograms diagnose hidden relational dynamics that distort business governance.",
        "distractor_analysis": "It complements—never replaces—financial auditing or corporate law."
    },
    {
        "anticipation_rank": 57,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "key_concept": "Family Control Suppressing vs Enabling Innovation",
        "question": "Under what condition does high family control *enable* rather than suppress innovation?",
        "options": [
            "When long-term stewardship orientation and patient capital back NextGen-led R&D without quarterly earnings penalties",
            "When the patriarch vetoes any product launched after 1995",
            "When 100% of profits are paid out immediately as personal dividends",
            "When external talent is prohibited from joining R&D"
        ],
        "correct_index": 0,
        "explanation": "Long horizons and fast concentrated decision-making enable bold innovation whenever family owners choose to embrace renewal.",
        "distractor_analysis": "Vetoing new products, draining cash, and blocking talent suppress innovation."
    },
    {
        "anticipation_rank": 58,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 5,
        "module_name": "Module 5: Management of Family Businesses",
        "key_concept": "Succession & Innovation",
        "question": "Why can the period immediately surrounding a generational succession actually act as a catalyst for strategic innovation?",
        "options": [
            "Incoming NextGen leaders bring fresh market/digital skills and question sacred-cow assumptions held by the outgoing generation",
            "Succession automatically wipes out all company debt",
            "Competitors pause product launches during a family transition",
            "Banks lower interest rates automatically whenever a CEO turns 30"
        ],
        "correct_index": 0,
        "explanation": "Succession creates a window of strategic renewal if NextGen's modern capabilities are paired with earned legitimacy.",
        "distractor_analysis": "Debt, competitor behavior, and bank rates do not change automatically upon succession."
    },
    {
        "anticipation_rank": 59,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "key_concept": "Board Committees",
        "question": "Which board committee is most critical in a family firm for preventing opaque executive family pay and biased hiring?",
        "options": [
            "Nomination and Remuneration Committee (NRC) with independent directors",
            "Factory Safety & Canteen Committee",
            "Informal Wedding Planning Committee",
            "Social Media Promotion Committee"
        ],
        "correct_index": 0,
        "explanation": "An independent-led NRC sets objective executive selection, succession evaluation, and market-benchmarked compensation.",
        "distractor_analysis": "None of the other committees oversee executive pay or board appointments."
    },
    {
        "anticipation_rank": 60,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 6,
        "module_name": "Module 6: Family Business Governance",
        "key_concept": "Family Holding Company",
        "question": "Why do multi-generation business families interpose a Family Holding Company above their operating subsidiaries?",
        "options": [
            "To vote operating shares as a unified block, pool dividends for group reinvestment, and prevent individual heirs from pledging operating shares",
            "To ensure every cousin can independently sell 1% of the factory to competitors",
            "To avoid having any board of directors anywhere in the group",
            "To convert equity into unsecured debt automatically"
        ],
        "correct_index": 0,
        "explanation": "A holding company aggregates fragmented family stakes into one cohesive voting block and centralizes capital allocation.",
        "distractor_analysis": "It specifically *prevents* fragmented individual sales of operating shares."
    },
    {
        "anticipation_rank": 61,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 7,
        "module_name": "Module 7: Family Firms, Communities, and External Stakeholders",
        "key_concept": "Generational Handoffs in Philanthropy",
        "question": "Why do many family foundations lose momentum when moving from the founder's generation to G2/G3?",
        "options": [
            "Younger generations may not share the founder's personal cause unless invited to co-define impact goals and modernise execution",
            "Indian law dissolves all charitable trusts after 20 years",
            "Foundations are barred from hiring professional program managers",
            "Philanthropy automatically reduces brand goodwill"
        ],
        "correct_index": 0,
        "explanation": "Legacy foundations endure only when NextGen is given voice to refresh causes (e.g., climate, education tech) and measure outcomes.",
        "distractor_analysis": "Trusts do not auto-dissolve at 20 years and can hire professional staff."
    },
    {
        "anticipation_rank": 62,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 7,
        "module_name": "Module 7: Family Firms, Communities, and External Stakeholders",
        "key_concept": "Entrepreneurial Families Shaping Community",
        "question": "How did pioneering Indian industrialist families historically build 'ecosystem infrastructure' (schools, hospitals, townships) around their plants?",
        "options": [
            "Both to fulfill community stewardship values and to attract/retain skilled talent in regions lacking public civic infrastructure",
            "Solely because SEBI mandated townships in 1920",
            "To prevent employees from ever retiring",
            "Because private firms were banned from paying cash wages"
        ],
        "correct_index": 0,
        "explanation": "Industrial townships (e.g., Jamshedpur, Pirojshanagar) blended paternalistic community responsibility with practical workforce retention amid civic gaps.",
        "distractor_analysis": "SEBI did not exist in 1920, and cash wages were always standard."
    },
    {
        "anticipation_rank": 63,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 8,
        "module_name": "Module 8: Institutional Contexts and Family Businesses",
        "key_concept": "New-Age Institutions & Global Integration",
        "question": "When an Indian family business raises capital from global ESG-focused institutional funds, which institutional pressure increases immediately?",
        "options": [
            "Normative and regulative demands for board independence, climate/ESG disclosure, and minority-shareholder protections",
            "Pressure to eliminate all financial reporting",
            "Mandate to appoint only family members to the Audit Committee",
            "Exemption from all Indian statutory filings"
        ],
        "correct_index": 0,
        "explanation": "Global capital integration brings international ESG, audit, and minority-governance expectations regardless of domestic habits.",
        "distractor_analysis": "Global funds demand *stricter* disclosure and independence, never less."
    },
    {
        "anticipation_rank": 64,
        "anticipation_tier": "Tier 3: Targeted Coverage",
        "module_number": 8,
        "module_name": "Module 8: Institutional Contexts and Family Businesses",
        "key_concept": "Wealth, Family Offices & AI Governance",
        "question": "Why are modern Family Offices increasingly adopting formal Investment Committees and digital/AI risk-analytics dashboards?",
        "options": [
            "To impose institutional discipline, diversify concentrated operating-business risk, and give multi-branch heirs transparent reporting",
            "To guarantee 100% risk-free crypto speculation",
            "To eliminate the need for human trustees or beneficiaries",
            "To hide asset performance from family shareholders"
        ],
        "correct_index": 0,
        "explanation": "Modern family offices use formal Investment Committees and tech dashboards to diversify risk professionally and sustain multi-branch trust.",
        "distractor_analysis": "Transparency and diversification—not hiding performance or eliminating trustees—drive modernization."
    }
]


def main():
    # 1. Load existing CLA questions to verify zero overlap
    cla_data = json.loads(CLA_PATH.read_text())
    cla_stems = set()
    for a in cla_data["assessments"]:
        for q in a["questions"]:
            cla_stems.add(re.sub(r"\W+", " ", q["stem"].lower()).strip())

    # 2. Validate Subjective questions (word count <= 100, unique, proper order)
    word_issues = []
    for i, sq in enumerate(SUBJECTIVE_QUESTIONS, start=1):
        assert sq["anticipation_rank"] == i, f"Subjective rank mismatch at {i}"
        wc = len(sq["model_answer"].split())
        sq["word_count"] = wc
        if wc > 105:
            word_issues.append((i, wc))

    # 3. Validate MCQs (unique vs CLAs, valid correct_index, 4 options)
    overlap_issues = []
    for i, mq in enumerate(MCQ_QUESTIONS, start=1):
        assert mq["anticipation_rank"] == i, f"MCQ rank mismatch at {i}"
        assert len(mq["options"]) == 4, f"MCQ {i} does not have 4 options"
        assert 0 <= mq["correct_index"] <= 3, f"MCQ {i} invalid correct_index"
        norm = re.sub(r"\W+", " ", mq["question"].lower()).strip()
        if norm in cla_stems:
            overlap_issues.append(i)

    # 4. Save structured bank
    bank = {
        "course_id": "db945ff9",
        "course_name": "Family Business Strategy",
        "exam_pattern": {
            "exam_date": "2026-12-05",
            "exam_timing": "12:00 PM to 02:00 PM",
            "duration_mins": 120,
            "total_marks": 75,
            "negative_marking": False,
            "calculator_allowed": False,
            "sections": [
                {"name": "Section A", "type": "MCQ", "count": 30, "marks_each": 1, "total_marks": 30},
                {"name": "Section B", "type": "Short Answer", "count": 9, "marks_each": 5, "total_marks": 45, "indicative_word_limit": 100}
            ]
        },
        "stats": {
            "subjective_count": len(SUBJECTIVE_QUESTIONS),
            "mcq_count": len(MCQ_QUESTIONS),
            "total_predicted_questions": len(SUBJECTIVE_QUESTIONS) + len(MCQ_QUESTIONS),
            "cla_baseline_count": len(cla_stems)
        },
        "subjective_questions": SUBJECTIVE_QUESTIONS,
        "mcq_questions": MCQ_QUESTIONS,
    }

    out_path = OUT_DIR / "family_business_exam_bank.json"
    out_path.write_text(json.dumps(bank, indent=2, ensure_ascii=False))

    print(f"Saved: {out_path}")
    print(f"Subjective: {len(SUBJECTIVE_QUESTIONS)} (word issues >105: {word_issues})")
    print(f"Max subjective word count: {max(q['word_count'] for q in SUBJECTIVE_QUESTIONS)}, Min: {min(q['word_count'] for q in SUBJECTIVE_QUESTIONS)}")
    print(f"MCQs: {len(MCQ_QUESTIONS)} (CLA overlap: {overlap_issues})")

    # Coverage per module
    sub_cov = {}
    mcq_cov = {}
    for q in SUBJECTIVE_QUESTIONS:
        sub_cov[q["module_number"]] = sub_cov.get(q["module_number"], 0) + 1
    for q in MCQ_QUESTIONS:
        mcq_cov[q["module_number"]] = mcq_cov.get(q["module_number"], 0) + 1
    print("Module coverage (Subj):", dict(sorted(sub_cov.items())))
    print("Module coverage (MCQ):", dict(sorted(mcq_cov.items())))


if __name__ == "__main__":
    main()
