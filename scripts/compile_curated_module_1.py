#!/usr/bin/env python3
"""
Compiles the streamlined, high-yield, exam-ready Master Revision Guide
for Module 1 of Family Business Strategy (db945ff9).
Balanced equilibrium: Fast 3-4 minute scan, focused strictly on frameworks,
systems, definitions, classifications, differentiations, and exam traps.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "study_vault.db"
ARTIFACT_DIR = Path("/Users/apple/.gemini/antigravity/brain/7b702f19-969e-42f3-9e07-fc24240181c2")

def get_streamlined_module_1_markdown() -> str:
    return """<a id="module-1"></a>
## Module 1: Introduction to Family Businesses (High-Yield Revision)

> **Cram Focus:** 3–4 minute visual review. Covers foundational definitions, the 2×2 configuration matrix, the 3 control tiers, the master differentiation table, core theoretical frameworks (Agency, Stewardship, SEW/FIBER, Familiness, 3-Circle, Goals, Ownership Competence), Indian institutional evolution, Anderson & Reeb (2003) empirical findings, and top exam traps.

---

### 1. Definition & Boundary Conditions
- **Chua, Chrisman, & Sharma Operational Definition (The 3 Pillars):**
  1. **Ownership Control:** Significant / controlling equity (typically >50% or dominant promoter voting block).
  2. **Management & Vision:** Family actively shapes strategic direction, board, or executive leadership.
  3. **Transgenerational Intent:** Deliberate plan and structure to pass ownership and leadership to the next generation.
- **Boundary Rules (Critical Exam Distinctions):**
  - **Related Founders ≠ Family Business:** Zerodha (Kamath brothers), Mamaearth (husband & wife), EaseMyTrip (Pitti brothers) are **entrepreneurial / founder-led startups** because they are in the 1st generation without transgenerational succession structures.
  - **Listed ≠ Non-Family:** Public listing does not change status if family retains promoter control (e.g., TCS / Tata Trusts, Reliance, Marico, Mahindra).
- **The Entrepreneurial Family Galaxy Model:** The family is the central sun; operating firms (wealth creation), family offices/trusts (wealth management), and foundations/councils (wealth preservation & legacy) are revolving planets.

---

### 2. The 2×2 Ownership vs. Management Matrix

| | **Family-Managed (Family Executives)** | **Professionally-Managed (External Executives)** |
| :--- | :--- | :--- |
| **High Family Ownership** | **Quadrant I: Family-Owned & Led**<br>• Family owns majority AND runs operations.<br>• *Examples:* Reliance Industries, Haldiram's, TVS Motor.<br>• *Trait:* Fast decisions, high alignment; risk of Founder's Trap / nepotism. | **Quadrant II: Family-Owned & Professionally-Led**<br>• Family retains equity/trusts; external professionals run operations.<br>• *Examples:* Tata / TCS, Mahindra & Mahindra, Marico.<br>• *Trait:* Separates ownership governance from daily management. |
| **Low Family Ownership** | **Quadrant III: Low Ownership & Family-Led**<br>• Family equity is diluted, but family holds strategic/board control.<br>• *Examples:* Historical Managing Agency houses; dual-class share firms.<br>• *Trait:* High **Type II Agency Risk** (controlling family vs minority public). | **Quadrant IV: Dispersed Non-Family Corporation**<br>• Widely held public shares; professional management.<br>• *Examples:* Infosys, L&T, HDFC Bank.<br>• *Trait:* Classic managerial firm; subject to **Type I Agency Costs**. |

---

### 3. The 3 Levels of Family Control & The Founder's Trap

| Level of Control | Focus & Scope | Real-World Levers & Examples |
| :--- | :--- | :--- |
| **1. Ownership Control** | Charter, values, capital protection ("Ghar ki daulat ghar ke andar"), wealth transfer. | Embedding cultural/religious norms (e.g., strict vegetarian canteens); emotional ownership ("firm as first child"). |
| **2. Strategic Control** | Long-term business scope, market entry, multi-gen pivots. | *Reliance Pivot:* Dhirubhai (Refining) → Mukesh (Telecom Jio & Retail) → Next-Gen (Green Energy & AI). |
| **3. Operational Control** | Day-to-day management (hiring, budgeting, operations). | Family executives vs outside professionals. Direct risk of Founder's Trap. |

> **⚠️ The Founder's Trap:** Firm expands beyond the founder's personal bandwidth, but the founder hoards all decisions ("gala" / cash drawer) and refuses to delegate, creating an operational bottleneck that stalls growth.

---

### 4. Master Comparison: Family vs. Non-Family Firms

| Dimension | Family Business | Non-Family / Public Corporation |
| :--- | :--- | :--- |
| **Planning Horizon** | **Generational (20+ years):** Long-term asset health. | **Short-Term ("QSQT" - Quarter Se Quarter Tak):** 90-day earnings. |
| **Core Objective** | **Bifocal:** Financial profit + **Socioemotional Wealth (SEW)**. | **Strict Shareholder Value:** Stock price, ROE, short-term EPS. |
| **Risk Profile** | **Capital Preservation (Conservative):** Protects family estate. | **Calculated Risk:** Higher willingness to leverage for growth. |
| **Funding Source** | **Internal & Debt:** Retained earnings, bank debt; **avoids equity dilution**. | **Open Market:** Public equity, Private Equity (PE/VC), bonds. |
| **Nature of Capital** | **Patient Capital:** Willing to wait 5–10 years for returns. | **Impatient Capital:** Demands immediate quarterly returns. |
| **Transparency** | **Closed-Loop / Opaque:** Discloses bare statutory minimums. | **High Transparency:** Audited disclosures, quarterly calls, town halls. |
| **Employment** | **Relational:** Loyalty, trust, "family" tenure, labor hoarding. | **Transactional:** Legal contracts, performance pay, hire-and-fire. |

---

### 5. Core Academic Frameworks (Cheat-Sheet)

#### A. Agency Theory vs. Stewardship Theory
- **Type I Agency Cost (Owner vs Manager):** Low in family firms because ownership and management are aligned.
- **Type II Agency Cost (Majority Family vs Minority Shareholders):** High in family firms. Controlling family may extract **"Private Benefits of Control"** (tunneling assets, transfer pricing, nepotistic jobs for relatives).
- **Stewardship Theory (Davis et al.):** Managers act as pro-organizational, collectivistic stewards of the family legacy, motivated by intrinsic mission rather than financial bonuses.

#### B. Socioemotional Wealth (SEW) & The FIBER Model (Berrone et al.)
Family firms prioritize non-financial utility over financial gain:
- **[F] Family Control:** Authority over board and executive strategy.
- **[I] Identification:** Family surname and public honor tied to corporate brand.
- **[B] Binding Social Ties:** Reciprocal relationships with community, staff, suppliers.
- **[E] Emotional Attachment:** Warmth, pride, and affective needs inside the enterprise.
- **[R] Renewal via Succession:** Commitment to dynastic family transfer.

#### C. Resource-Based View (RBV) & "Familiness" (Habbershon & Williams)
- **Familiness:** Unique bundle of resources arising from family-firm interaction.
  - *Positive Familiness:* Patient capital, high internal trust, tacit knowledge transfer, agile decisions.
  - *Negative Familiness ("Famisfortune"):* Incompetent relatives, sibling rivalry, emotional inertia, resistance to outside talent.

#### D. Systems Theory & Gersick's 3-Circle Model (1997)
- 3 Overlapping Subsystems: **Family**, **Ownership**, and **Business** → Creates **7 Stakeholder Sectors**.
- **The Inherent Conflict:** The *Family Circle* operates on **equality and unconditional love**; the *Business Circle* operates on **meritocracy and profitability**.

#### E. The 2×2 Goals Matrix
- **Family-Oriented Economic:** Family wealth, dividends, controlling equity.
- **Family-Oriented Non-Economic:** Family harmony, social prestige, legacy identity.
- **Firm-Oriented Economic:** Corporate growth, EBITDA, market share, ROIC.
- **Firm-Oriented Non-Economic:** Employee security, community goodwill, CSR.

#### F. Ownership Competence (3 Dimensions)
1. **Matching Competence:** *What to own?* (Aligning business portfolio with family strengths).
2. **Governance Competence:** *How to own?* (Structuring holding company, family council, voting trusts).
3. **Timing Competence:** *When to own?* (Timing market entries, acquisitions, or generational handovers).

---

### 6. Historical Evolution & The Indian Institutional Context

- **India's Mercantile Communities:** Marwaris, Parsis, Gujaratis, Chettiars (Nattukottai Chettiars), Banias, Sindhis, Bohras.
- **The Hundi System:** Indigenous credit bill of exchange and remittance mechanism; operated across long distances without banks, enforced solely by community trust and social sanctions.
- **Weber's Thesis Refuted:** Max Weber claimed Hindu culture/caste fatalism blocked capitalism. Business historians (Tripathi, Markovits, Timberg) refuted this: kinship networks acted as low-cost trust highways and capital pools.
- **HUF & The Karta:** Hindu Undivided Family legal entity; the **Karta** (patriarch/custodian) manages joint ancestral assets for all coparceners.
- **The Managing Agency System (1820s–1970):** British origin; adapted by Indian families (Tatas, Birlas). A promoter agency controlled vast operating companies with minimal equity, charging fees on **gross turnover** (not net profit). Abolished in **1970** → families adapted via holding companies.
- **License Raj (1951–1991):** Industrial licensing (IDRA 1951) and import substitution. Family houses pre-empted licenses, creating sprawling **unrelated conglomerate diversification**. **MRTP Act 1969** targeted Tatas & Birlas.
- **Post-1991 Liberalisation:** Abolished licensing; led to family business group demergers/splits (Bajaj, Ambani), non-core divestments, professionalization, and major pivots (Wipro: cooking oil → IT services).

---

### 7. Key Empirical Data & Longevity Rules

- **Anderson & Reeb (2003) Landmark Study (S&P 500, Journal of Finance):**
  - **33%** of S&P 500 firms are family-owned.
  - Family firms **significantly outperform non-family firms** in ROA and Tobin's Q.
  - **CEO Performance Hierarchy:**
    $$\\mathbf{Founder\\text{ }CEO} > \\mathbf{Outside\\text{ }Professional\\text{ }CEO} > \\mathbf{Descendant\\text{ }CEO} \\ge \\mathbf{Non\\text{-}Family\\text{ }Firms}$$
  - **Inverted U-Curve:** Performance peaks at **~30%** family equity ownership; higher stakes trigger entrenchment.
- **Crisis Resilience (2008 GFC & COVID-19):** Lower leverage, counter-cyclical capex, and **"labor hoarding"** (retaining employees builds intense loyalty and powers post-crisis rebound).
- **Macro Footprint:** Combined global family firms = **3rd largest economy in the world**; contribute **~79% of Indian GDP**. Mandated CSR under **Section 135 (Companies Act 2013)** = 2% of net profit.
- **Defying the 3-Generation Curse ("Shirtsleeves to shirtsleeves"):**
  - *Macro Factors:* Property rights stability (e.g., French Wendel steel collapsed in 1974 after nationalization). Capital market depth forces professionalization.
  - *Cultural Mechanism:* Japanese ***Mukoyoshi*** (adult son-in-law adoption) decouples talent from biology, enabling firms like Kongo Gumi to survive >1,000 years.
  - *Firm-Level Governance:* Family councils, constitutions, trusts, and separating ownership from management.

---

### 8. High-Yield Exam Trap Radar (Top 10 Fast Checks)

1. **Trap:** Related founders = Family business. → **Reality:** False. Startups like Zerodha lack multi-generational succession intent.
2. **Trap:** Listed companies cannot be family businesses. → **Reality:** False. TCS, Reliance, and Marico are listed family businesses.
3. **Trap:** Family firms avoid external equity due to low market credibility. → **Reality:** False. They avoid equity to **prevent dilution of control**.
4. **Trap:** Family firms have high Type I agency costs. → **Reality:** False. Type I (owner-manager) is low; **Type II (majority vs minority)** is the primary agency risk.
5. **Trap:** Descendant CEOs outperform Founder CEOs. → **Reality:** False. Founder CEOs perform best; Outside Professional CEOs outperform Descendants.
6. **Trap:** SEW theory says family firms maximize financial returns above all. → **Reality:** False. They willingly sacrifice financial profits to protect socioemotional wealth.
7. **Trap:** Max Weber proved Hindu culture fostered modern capitalism. → **Reality:** False. Weber claimed it was hostile; modern historians **refuted** him.
8. **Trap:** Managing Agency system was abolished because it failed to raise capital. → **Reality:** False. It raised immense capital; abolished in 1970 due to tunneling and fees on gross turnover.
9. **Trap:** The Japanese Mukoyoshi succession enforces biological primogeniture. → **Reality:** False. It deliberately bypasses biological heirs by adopting capable adult managers.
10. **Trap:** Professionalizing management causes the family to lose control. → **Reality:** False. Professionalizing operational management (Quadrant II) **preserves family ownership control**.

---
"""

def run():
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    row = c.execute('SELECT one_shot_markdown FROM course_one_shots WHERE course_id = "db945ff9"').fetchone()
    if not row:
        print("ERROR: db945ff9 not found in course_one_shots!")
        return

    current_md = row[0]

    # Locate Module 2
    mod2_marker = '<a id="module-2"></a>'
    mod2_idx = current_md.find(mod2_marker)
    if mod2_idx == -1:
        print("ERROR: Module 2 marker not found!")
        return

    mod2_to_8 = current_md[mod2_idx:]

    header = """# Family Business Strategy: Comprehensive Master Revision Guide

> **100% Curriculum-Complete Exam Review:** Curated specifically for rapid, last-minute cramming (1–2 hours before exams). Zero substantive theories, formulas, models, or empirical findings are omitted. Pure administrative fluff is removed, with generous visual spacing, bold technical definitions, worked numerical calculations, and examiner traps.

---

## Quick Module Navigation

- [Module 1: Introduction to Family Businesses](#module-1)
- [Module 2: Dynamics of Family Firm](#module-2)
- [Module 3: Succession in Family Firms](#module-3)
- [Module 4: Family Dynamics in Action​](#module-4)
- [Module 5: Management of Family Businesses](#module-5)
- [Module 6: Family Business Governance](#module-6)
- [Module 7: Family Firms, Communities, and External Stakeholders](#module-7)
- [Module 8: Institutional Contexts and Family Businesses](#module-8)

---

"""

    streamlined_mod1 = get_streamlined_module_1_markdown()

    combined_md = header + streamlined_mod1 + "\n\n" + mod2_to_8

    print(f"Old total length: {len(current_md):,} chars")
    print(f"New total length: {len(combined_md):,} chars (Streamlined Mod 1 = {len(streamlined_mod1):,} chars)")

    # Save to database
    c.execute("""
        UPDATE course_one_shots 
        SET one_shot_markdown = ?, updated_at = CURRENT_TIMESTAMP
        WHERE course_id = "db945ff9"
    """, (combined_md,))
    conn.commit()
    print("Database updated successfully!")

    # Export to study_data.js
    import sys
    sys.path.insert(0, str(BASE_DIR))
    from core import db
    print("Exporting static bundle to study_data.js...")
    db.export_static_data()

    # Save standalone Module 1 Artifact
    artifact_path = ARTIFACT_DIR / "family_business_module_1_master_revision.md"
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write("# Family Business Strategy: Module 1 Master Revision Guide\n\n" + streamlined_mod1)
    print(f"Saved standalone artifact to {artifact_path}")

if __name__ == "__main__":
    run()
