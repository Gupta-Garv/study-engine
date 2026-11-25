#!/usr/bin/env python3
"""
Upgrade Family Business Strategy (db945ff9) One-Shot Notes:
- Concise, module-wise (Modules 1-8), zero fluff (~3,000-3,500 words)
- Grounded in course notes + calibrated to Term 7 paper pattern (30 MCQs + 9 Short Answers <= 100w)
- Verified with check_katex_expressions() before saving to DB & exporting study_data.js
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import db
from scripts.note_quality_engine import check_katex_expressions

COURSE_ID = "db945ff9"

ONE_SHOT_MD = r"""# Family Business Strategy: Master Exam One-Shot (Modules 1 to 8)

> **Term 7 Paper Pattern:** **75 Marks | 120 Mins | No Calculator | No Negative Marking**
> - **Section A:** 30 MCQs x 1 mark = 30 marks (tests exact framework distinctions, Indian context, and governance traps)
> - **Section B:** 9 Short Answer Questions x 5 marks = 45 marks (**<= 100 words each**: *Name Framework -> Diagnose Exact Tension -> Propose 1 Structural Fix -> Note 1 Risk/Trade-off*)

---

## Case-to-Framework Quick Decoder (Read First)

| If the Exam Scenario Describes... | Invoke This Exact Framework | Key Grader Terms |
|---|---|---|
| Siblings/in-laws fighting over dividends vs. reinvestment vs. perks | **Three-Circle Model (Tagiuri & Davis)** | Sector 4, Sector 5, Sector 7, Dividend + Employment Policy |
| Rejects lucrative PE/acquisition to protect family name or board control | **Socioemotional Wealth (SEW - FIBER)** | Family Control, Identification, Capital Rationing risk |
| Competent MBA heir wants own startup instead of family firm | **Willingness-Ability Matrix** | High Ability / Low Willingness -> Separate Ownership & Management |
| 55% owner unilaterally sells core unit telling 45% sister "majority rules" | **Five Rights & Three Powers of Owners** | Power to Destroy, Right to Inform/Define Value, SHA Reserved Matters |
| 18 cousins in G3 argue at dinners over cars, jobs, and payouts | **Family Council vs. Constitution vs. Board** | Deliberation (Council), Moral Rules (Constitution), Strategy (Board) |
| 72-year-old founder names successor twice but still signs every cheque | **The Incumbent's Dilemma** | Identity fusion, shadow leadership, Emeritus transition |
| Non-family VP quits after unskilled in-law is hired at double pay | **Family Employment Policy & Justice** | External work (3-5 yrs), real vacancy, market-benchmarked KPI pay |
| Rich patient capital yet launches fewer new products than rivals | **Ability-Willingness Innovation Paradox** | Exploration vs. Exploitation, SEW loss aversion, ring-fenced R&D |
| Returning NextGen heir fires loyalists and forces sudden overhaul | **Anand Group: Earning the Right to Change** | Listen -> bounded pilot win -> earn legitimacy -> modernize |
| Family branch ignores Family Constitution and sues in court | **Constitution vs. Shareholders' Agreement** | Moral non-binding charter vs. legally enforceable SHA + Articles |

---

## Module 1: Foundations, Theories & Indian Context

### 1.1 Ownership-Management Quadrants & Performance
- **Four Quadrants:** High/Low Family Ownership crossed with Family/Professional Management. A promoter-owned listed firm with a hired outside CEO sits in **High Family Ownership + Professional Management**.
- **Anderson & Reeb (2003):** S&P 500 family firms outperformed non-family peers on average, especially with a founder/family CEO, up to the point where control turns into **entrenchment**.
- **Alignment vs. Entrenchment (Inverted-U):** Concentrated ownership aligns long-term incentives initially; excessive unchecked control breeds minority expropriation and resistance to change.

### 1.2 Core Theoretical Lenses (High-Yield MCQ & 5M Targets)

| Theory | Core Mechanism in Family Firms | Classic Failure / Trap |
|---|---|---|
| **Agency Theory** | Low **Type I** (Owner-Manager) cost; high **Type II** (Controlling Family vs. Minority Shareholders) cost | Tunneling via off-market RPTs, appointing unqualified kin |
| **Stewardship Theory** | Family leaders identify psychologically with firm, acting as long-term stewards beyond pay | Blind loyalty to failing legacy lines |
| **SEW (FIBER)** | **F**amily control, **I**dentification with firm, **B**inding social ties, **E**motional attachment, **R**enewal across generations | Rejecting value-adding PE/R&D solely to guard SEW |
| **Resource-Based View (RBV)** | **Familiness**: idiosyncratic bundle of human, social, patient financial, and **survivability capital** (waiving pay/pledging personal assets in crises) | **Constrictive familiness**: insularity, groupthink, knowledge hoarding |
| **Transaction Cost (TCE)** | Kinship/community trust enforces implicit contracts cheaply via reputational sanctions | Fails when scale/complexity outgrows informal trust |
| **Ownership Competence** | Active skill of matching governance, capital horizon, and strategy to firm needs (beyond just holding shares) | Confusing passive shareholding with competent stewardship |

### 1.3 Indian Historical Evolution
- **Mercantile Communities & Hundi:** Marwaris, Chettiars, Parsis, and Gujaratis used **Hundis** (indigenous trust-based credit/remittance bills) to move capital across trade networks without colonial banks.
- **Managing Agency System (abolished 1970):** Long-term management contracts let mercantile families control vast joint-stock enterprises on modest equity; abolition triggered restructuring into **pyramid holding companies and cross-holdings**.
- **License Raj vs. Post-1991:** Pre-1991 rewarded bureaucratic license-navigation (**active adaptation**); post-1991 liberalisation forced global competitiveness, focus, and professionalisation (**proactive adaptation**).

---

## Module 2: Dynamics of the Family Firm (Three-Circle, Rights & Stages)

### 2.1 The Three-Circle Model (Tagiuri & Davis)
Every person in the family enterprise ecosystem occupies exactly **1 of 7 sectors**:
- **Sector 1 (Family only):** Retired founder with zero shares/role, or non-working spouse.
- **Sector 4 (Family + Owner):** Passive sibling/cousin shareholder -> prioritizes **dividends, liquidity, capital preservation**.
- **Sector 5 (Family + Employee):** In-law or NextGen working in HR/ops with **0% equity** -> prioritizes **fair pay, career progression, perks**.
- **Sector 7 (Family + Owner + Employee):** Active founder or managing sibling -> prioritizes **reinvestment, growth, operational control**.
- **Exam Rule:** Never treat a Sector 5 working in-law as Sector 1. Governance fixes role overlap by separating **Employment Policy** (salary/merit) from **Dividend Policy** (capital returns).

### 2.2 Three Powers & Five Rights of Family Owners
- **Three Powers:** **Power to Create** (entrepreneurial renewal), **Power to Sustain** (stewardship), **Power to Destroy** (unilateral 51% dominance, blocking capital, weaponizing vetoes).
- **Five Rights:**
  1. **Right to Design:** Architect legal, board, and holding structures.
  2. **Right to Decide:** Reserved strategic choices and board appointments.
  3. **Right to Define Value:** Agree on risk appetite, growth vs. dividend balance, and non-financial legacy goals.
  4. **Right to Inform:** Transparent financial and governance reporting to all owners.
  5. **Right to Transfer:** Share exit, inheritance, and **Right of First Refusal (ROFR)** rules.

### 2.3 Generational Evolution & The Cousin Matrix
- **G1 Controlling Owner:** Centralized founder authority; main risks are key-person dependency and unstarted succession.
- **G2 Sibling Partnership:** Ownership splits across equals without a parent-referee; main challenge is horizontal consensus and balancing active vs. passive siblings.
- **G3 Cousin Consortium (Cousin Matrix):** Owners live in separate nuclear households with diluted emotional ties. Two sharp frictions emerge:
  1. **Active vs. Passive Divide:** Working cousins want retained earnings for capex; non-working cousins demand cash dividends.
  2. **Branch Asymmetry:** Larger branches feel diluted per capita while smaller branches fear voting coalitions.

---

## Module 3: Succession in Family Firms

### 3.1 The Three-Generation Rule & Dual Transfer
- **"Shirtsleeves to shirtsleeves in three generations"** happens from demographic equity dilution, NextGen entitlement, and failure to adapt G1's core model.
- **Separate Two Transfers:**
  - **Management Transfer:** Handing executive CEO authority to the best leader (family or professional).
  - **Ownership Transfer:** Passing equity and voting control via trusts, holding companies, and SHAs.
- **Ownership Education:** Every heir (even passive ones) must learn to read P&Ls, risk, and dividend trade-offs so they exercise ownership rights responsibly.

### 3.2 Willingness x Ability Matrix (High-Frequency 5M Case)

| Quadrant | Profile | Exact Succession Path |
|---|---|---|
| **High Will + High Ability** | Prepared & committed heir | Groom via 3-5 yrs external work + real P&L ownership -> CEO |
| **Low Will + High Ability** | Competent but prefers own path | **Separate Ownership from Management**: Board/Owner role + Professional CEO |
| **High Will + Low Ability** | Eager but unprepared | Structured training + pair with strong professional COO; defer CEO |
| **Low Will + Low Ability** | Disengaged | Fair passive ownership / liquidity exit; keep out of management |

### 3.3 Incumbent's Dilemma, Paths & Successor Tests
- **Incumbent's Dilemma:** Founder's identity and self-worth are fused with the firm, causing 'shadow leadership' (overturning the successor's decisions). **Fix:** Binding handover calendar + dignified non-operational role (Chairman Emeritus / Family Council / Foundation).
- **Succession Paths:** **Crown Prince** (single anointed heir), **Horse Race** (parallel P&L tournament across contenders; risks losing runner-up), **Regency** (interim non-family CEO until young heir matures).
- **Three Credibility Tests ("Earning the Right"):** (1) **External Credibility** (3-5 yrs outside without surname shield), (2) **Internal P&L / Turnaround Test** (real operating accountability), (3) **Relational Trust** with senior non-family executives.
- **Commitment Types:** **Affective** (genuine passion) drives innovation; **Normative** (guilt/duty) and **Continuance** (financial lock-in) breed burnout.

---

## Module 4: Family Dynamics in Action

- **Equality vs. Equity:** Treat children with **Equality** in family inheritance/equity if desired, but enforce **Equity** (merit + market-benchmarked KPIs) in executive compensation and promotions.
- **Family Employment Policy (3 Mandatory Clauses):** (1) Relevant degree + 3-5 years external experience, (2) Real business vacancy + independent HR/board review, (3) Market-benchmarked pay separate from dividends. Prevents non-family talent attrition ("glass ceiling").
- **Related-Party Transactions (RPTs):** Off-market, undisclosed leases or contracts with promoter relatives (e.g., paying 40% above market rent to a spouse's building) represent **private benefit extraction / abusive RPTs**.
- **Women in Family Business:** Cultural primogeniture historically pushed women into the **"Invisible Force"** (unpaid, untitled peacemakers and advisors). Formal gender-neutral charters unlock daughter succession.
- **Working Couples & CEO's Spouse:** Guard against home-to-office spillover and employee triangulation by assigning **distinct non-overlapping functional domains** and banning business talk after hours.
- **Conflict Progression:** **Task Conflict** (healthy strategic debate on *what* to do) escalates into **Process Conflict** (fighting over budgets/authority) and **Relationship Conflict** (personal hostility) when decision rules are missing.

---

## Module 5: Management of Family Businesses

### 5.1 Professionalisation (Without Destroying Familiness)
- **"Be More Like a Non-Family Business" Fallacy:** Copying MNC bureaucracy kills the family firm's VRIO advantages (patient capital, fast trust decisions).
- **Structural vs. Managerial Professionalisation:**
  - **Structural:** Formal budgets, ERP, audited KPIs, merit HR, independent board (family CEOs can and should run structural systems).
  - **Managerial:** Hiring qualified non-family executives, often anchored by a **Bridge Executive** who translates between founder intuition and modern systems.

### 5.2 Innovation Paradox & Internationalisation
- **Ability-Willingness Innovation Paradox:** Family firms have **high ability** (autonomy, patient capital) yet **low willingness** (SEW loss aversion) -> favoring safe **Exploitation** over risky **Exploration**. **Fix:** Ring-fence an independent corporate venture/R&D unit with dedicated capital.
- **Internationalisation:** SEW/control fears delay early foreign entry (favoring gradual **Uppsala** expansion into culturally close markets). Once committed, **patient capital** and **relational/diaspora trust** turn into major advantages.

---

## Module 6: Family Business Governance

### 6.1 Corporate Board Roles & Committees
- **Three Board Roles:** **Control** (monitoring CEO, RPTs, audit), **Service** (strategic counsel, devil's advocacy), **Resource Provisioning** (external networks, lender credibility, regulatory access).
- **Why Firms Resist Independent Directors:** Fear of losing family privacy, scrutiny on RPTs, and doubt about outsiders' long-term alignment.
- **Key Committee:** **Nomination & Remuneration Committee (NRC)** led by independents prevents biased family hiring and opaque pay.

### 6.2 Family vs. Ownership Governance Institutions (High-Yield Distinction)

| Institution | Scope & Membership | Legal Enforceability | Primary Purpose |
|---|---|---|---|
| **Family Assembly / Forum** | Broad, inclusive (all kin, spouses, NextGen) | Non-binding | Values, education, annual cohesion |
| **Family Council** | Smaller elected branch representatives | Non-binding | Voice family concerns, draft policies, resolve friction |
| **Family Constitution** | Written family charter | **Moral / Non-binding** | Entry rules, conflict etiquette, shared vision |
| **Shareholders' Agreement (SHA)** | Shareholders (mirrored in Articles) | **Legally Enforceable** | ROFR, share valuation formulas, drag/tag-along, reserved matters |
| **Family Holding Company** | Corporate parent above op-cos | Legal entity | Unified voting block, central dividend pooling |
| **Family Trust** | Settlor -> Trustee -> Beneficiaries | Fiduciary legal vehicle | Estate succession, asset protection, distribution discipline |
| **Family Office** | Professional investment/tax team | Operating entity | Manage liquid non-operating wealth, tax, philanthropy |
| **Family Bank / Redemption Fund** | Internal capital pool | Contractual/Board | Fund NextGen ventures or buy out exiting branches ("pruning the tree") |

---

## Module 7: Communities, Impact & The Anand Case

- **Dual Wealth Optimization:** Combine financial resilience with measurable community impact (using **Section 8 Companies** in India for cleaner governance and CSR credibility than informal trusts).
- **NextGen Onboarding via Philanthropy:** An organised Foundation acts as a low-stakes governance training ground where active and passive cousins learn capital allocation and shared **Value Work** together.
- **The Anand Group Case ("Coming Home" & "Earning the Right to Change"):** Returning NextGen scions fail when they abruptly fire loyalists or trash legacy systems. **Required sequence:** (1) Listen and respect institutional memory, (2) Prove competence via measurable wins in a bounded/peripheral unit, (3) Modernize alongside trusted insiders.

---

## Module 8: Institutional Contexts & Regulatory Landscape

- **Institutional Voids:** In emerging markets with weak external credit, contract enforcement, and talent markets, diversified family conglomerates substituted **internal capital, talent, and trust markets**.
- **Richard Scott's Three Pillars:**
  1. **Regulative:** Laws, SEBI LODR, Companies Act 2013, Insolvency Code (IBC), mandatory Audit Committee & minority RPT approvals.
  2. **Normative:** Professional standards, ESG expectations from global institutional investors.
  3. **Cultural-Cognitive:** Taken-for-granted beliefs and filial deference.
- **Douglas North (Formal vs. Informal):** Copying Western formal board templates fails if it ignores informal Indian deference/face-saving norms; effective governance uses private pre-board consultations to surface dissent respectfully.
- **Trust to Rules Shift:** Scale, outside investors, AI/digital disruption, and strict SEBI RPT transparency force family groups to move from handshake trust to codified rules.

---

## Last-15-Minute MCQ & 5-Mark Trap Radar

1. **In-law with 0% shares working in the firm** -> **Sector 5** (Family + Employee), NOT Sector 1.
2. **Family Constitution vs. SHA** -> Constitution is **morally binding only**; court enforceability requires an **SHA + Articles of Association**.
3. **Family Office vs. Holding Co** -> Holding Co locks **operating voting control**; Family Office manages **liquid wealth/tax**.
4. **Professionalisation** -> Means **formal systems & governance** (Structural), not firing all family.
5. **Agency Costs** -> Family firms lower **Type I** (Owner-Manager) but raise **Type II** (Controlling Family vs. Minority).
6. **RPTs** -> Legal **only if** disclosed, arm's-length priced, and approved by independent Audit Committee/minority shareholders.
7. **Task vs. Relationship Conflict** -> Task conflict is constructive; poor governance lets it spill into Process and Relationship conflict.
8. **Equality vs. Equity** -> Equal ownership shares can coexist with equitable (merit/KPI) executive salaries.
"""


def main():
    err = check_katex_expressions(ONE_SHOT_MD)
    assert not err, f"KaTeX error: {err}"
    wc = len(ONE_SHOT_MD.split())
    print(f"Family Business One-Shot word count: {wc} words (down from 411,810 chars!)")
    db.save_course_one_shot(COURSE_ID, ONE_SHOT_MD, "")
    db.export_static_data()
    print("Saved to DB and exported study_data.js cleanly.")


if __name__ == "__main__":
    main()
