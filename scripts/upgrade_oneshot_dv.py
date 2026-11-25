#!/usr/bin/env python3
"""
Upgrade Data Visualisation for Business Decisions (deb83564) One-Shot Notes:
- Concise, module-wise (Modules 1-5), calibrated to Term 7 pattern (14 MCQs + 8 MSQs floored at 0)
- Verified with check_katex_expressions() before saving to DB & exporting study_data.js
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import db
from scripts.note_quality_engine import check_katex_expressions

COURSE_ID = "deb83564"

ONE_SHOT_MD = r"""# Data Visualisation for Business Decisions: Master Exam One-Shot (Modules 1 to 5)

> **Term 7 Paper Pattern:** **30 Marks | 60 Mins | No Calculator**
> - **Section A:** 14 MCQs x 1 mark = 14 marks
> - **Section B:** 8 MSQs x 2 marks = 16 marks (**Partial/Negative Marking floored at 0 per question**: `+(2/k)` per right option, `-(2/k)` per wrong option, min `0`. **Never guess unsure options on MSQs.**)

---

## Exam Symptom-to-Rule Decoder

| If the Exam Question Describes... | Exact Rule / Feature to Pick |
|---|---|
| Bar chart looks exaggerated because Y-axis starts at 100 | **Zero-Baseline Rule**: Bar/Column charts encode magnitude by length and MUST start at 0 |
| Aggregate conversion rose, yet every single channel dropped | **Simpson's Paradox / Mix-Shift Bias**: Segment weights shifted; inspect subgroups |
| Dynamic Profit Margin % that recalculates when slicers change | **DAX Measure** (`DIVIDE(SUM(Profit), SUM(Sales))`), never Calculated Column |
| Clicking one bar accidentally filters a fixed Target Card | **Edit Interactions**: Set source visual's effect on Target Card to **None** |
| Single line chart must switch between Sales, Profit, Discount % | **Field Parameters** (dynamic metric switcher via slicer) |
| Bridge 2017 Profit to 2018 Profit across +/- category drivers | **Waterfall Chart** |
| Plot Revenue (Crores) and Profit Margin (%) together over time | **Combo Chart** (Line + Clustered Column with secondary Y-axis) |
| Unexpected `(Blank)` row appears in a Power BI visual | **Referential Integrity**: Fact foreign keys missing from Dimension, or trailing blank Excel rows |
| Wide spreadsheet has 12 columns `Jan` to `Dec` | **Power Query Unpivot Columns** -> tall `Month` + `Value` columns |
| Navigation button does nothing in Power BI Desktop | **Desktop Authoring Rule**: Hold `Ctrl + Click` in Desktop (single-click in Service) |

---

## Module 1: Understanding Business Data Visualisation

### 1.1 Observation vs. Insight vs. Recommendation (Guaranteed MCQ)
- **Observation:** Purely *what* happened (`"North zone return rate is 24% in October"`).
- **Insight:** *Why* it happened / causal mechanism (`"North returns spiked among CoD footwear orders due to missing mobile size charts"`).
- **Recommendation:** Concrete action (`"Deploy a mobile size-guide popup before Friday"`).

### 1.2 Chart Selection Matrix

| Analytical Question | Best Chart | Avoid |
|---|---|---|
| Trend over continuous time | **Line Chart** | Pie / Unordered bars |
| Rank / compare 8+ discrete categories | **Sorted Horizontal Bar Chart** | Pie Chart (>5 slices), Line Chart |
| Cumulative +/- bridge between two totals | **Waterfall Chart** | 100% Stacked Area |
| Percentage mix share over time | **100% Stacked Area / Column** | Pie series |
| Two metrics, vastly different scales (Rs Cr vs. %) | **Combo Chart (Line + Column, 2nd Y-axis)** | Single-axis chart |
| Two continuous measures + outlier quadrants | **Scatter Plot + Avg/Target Reference Lines** | Bar chart |

### 1.3 Misleading Visuals & Statistical Traps
- **Truncated Axes:** Bars MUST start at zero; zoomed baselines are only valid on line charts when clearly labeled.
- **Rates vs. Raw Counts:** Compare **rates (%)** (e.g., Return Rate %) rather than raw return counts when store/region volumes differ.
- **Correlation != Causation:** Check for confounding variables (e.g., summer heat driving both ice-cream sales and drownings).
- **60-30-10 Color Rule & Accessibility:** 60% neutral canvas, 30% structural surfaces, 10% purposeful alert color. Never rely on red/green alone (~8% male color-vision deficiency); pair colors with `▲`/`▼` or `+`/`-`.

---

## Module 2: Designing Effective Dashboards

### 2.1 Requirements Framework (Why, What, How/When, Where)
- **Users vs. Sponsors:** A VP **Sponsor** approves the budget, whereas frontline analysts/managers are the daily **Users**. Designing solely for the sponsor creates shelfware.
- **Strategic (Executive) vs. Operational (Frontline):**
  - *Executive:* Periodic KPIs, YoY/Target comparisons, top-left anchor, **Progressive Disclosure** (summary first, details via drill-down/tooltips).
  - *Operational:* Live/intraday wall-screen exceptions and granular queues.

### 2.2 Architecture, Data Audit & MVP
- **Hybrid Architecture:** Standardize 1 **certified core overview** (prevents "metric drift" across teams) + tailored departmental drill-down pages.
- **Data Source Audit:** Check refresh latency, entity hygiene (`"Calcutta"` vs. `"Kolkata"`), restated/revised historical data (show `"Last Refreshed"` timestamp), and extraction bottlenecks (e.g., legacy PDFs).
- **MVP Strategy:** Scope Phase 1 at **High Business Value $\cap$ Immediate Data Feasibility**. Defer blocked pipelines (e.g., unbuilt social NLP APIs) to Phase 2.
- **4-Part KPI Card:** (1) Cleanly scaled headline value (`Rs 4.2 Cr`, not 12 decimals), (2) Benchmark (Target/Prior), (3) Accessible directional delta, (4) Micro-trend/time window.
- **Mockups Before Code:** Lock low-fidelity wireframe sign-off *before* writing DAX to prevent expensive scope rework.

---

## Module 3: Building Visualisations with Power BI

### 3.1 Power Query Hygiene (`Transform Data`)
Perform all structural cleaning upstream before loading:
1. Remove top junk/banner rows and trailing blank/subtotal rows; promote true headers.
2. Trim whitespace and standardize inconsistent labels (`Calcutta` -> `Kolkata`).
3. Enforce exact types (`Date`, `Fixed Decimal`, `Whole Number`) and **Unpivot** wide cross-tab columns.
4. Drop unused high-cardinality columns to keep VertiPaq compression fast.

### 3.2 Star Schema Data Modeling
- **Fact Tables (`FactSales`):** Quantitative transaction events + numeric metrics + foreign keys.
- **Dimension Tables (`DimProduct`, `DimCustomer`, `DimDate`):** Descriptive slicing attributes.
- **Cardinality & Flow:** **One-to-Many (`1:*`) single-direction** from Dimensions to Facts. Avoid Many-to-Many (`*:*`) bidirectional spiderwebs.
- **Dedicated `DimDate`:** Mark a single `DimDate` as Date Table and disable Auto Date/Time so time-intelligence works cleanly across multiple facts. Hide technical ID keys in Report View.

### 3.3 Calculated Columns vs. DAX Measures (Guaranteed MCQ & MSQ)

| Dimension | Calculated Column | DAX Measure |
|---|---|---|
| **Evaluation Context** | Row context (at data refresh) | **Filter context** (dynamic at query/slicer time) |
| **Memory Storage** | Stored in RAM for every row | Zero row-level RAM (computed on fly) |
| **Best Use Case** | Static slicer/axis buckets (`Small / Med / Large`) | All aggregations & **ratios** (`DIVIDE(SUM(Profit), SUM(Sales))`) |

---

## Module 4 & Module 5: Interactive Reports, Diagnostics & Power BI Service

### 4.1 Interactive Controls & Scope Locking
- **Field Parameters:** Let users toggle metrics (`Sales` / `Profit` / `Discount %`) on one single visual.
- **Visual-Level `Top N` Filter:** Dynamically rank Top 5/6 entities inside active slicers.
- **Edit Interactions & Sync Slicers:** Isolate fixed-scope visuals (e.g., `"2018 Product Mix"` or fixed company target cards) from global multi-year slicers so titles never contradict displayed data.
- **Table Formatting:** Right-align numbers, left-align text, keep consistent decimals.

### 4.2 Growth & Profitability Diagnostics (Superstore Workflow)
- **Dual Trend + Waterfall:** Decompose YoY growth drivers cleanly.
- **Discount % vs. Profit Ratio % Scatter Matrix:** Add average/target reference lines on both axes to expose the high-discount/negative-profit margin-leak quadrant.
- **QA Sign & Threshold Traps:** Test `0`, `<` vs. `<=`, and decimal vs. percent (`0.15` vs. `15`) on conditional formatting; reset slicers to default view before publishing; verify button `Default / Hover / Press` states (`Ctrl + Click` in Desktop).

### 4.3 Publishing & Cloud Service (`Reports` vs. `Dashboards`)
- **Power BI Report:** Multi-page interactive file built on **1 Semantic Model** (Desktop & Service).
- **Power BI Dashboard:** **Single-page canvas in Power BI Service only**, pinning tiles from **1 or more reports**.
- **Pin Live Page vs. Visual Tiles:** **Pin Live Page** keeps full slicer/cross-filter interactivity on the dashboard; individual tiles are static entry snapshots.
- **Master Copy Governance:** Publish 1 Master Semantic Model to a shared Workspace/App rather than emailing `.pbix` files (prevents version sprawl).
- **Live Session `(Blank)` Fix:** `(Blank)` rows signal unmatched Fact foreign keys missing from Dimensions or uncleaned Excel trailing rows.

---

## Last-15-Minute MSQ & MCQ Trap Radar

1. **MSQ Guessing:** Never guess unsure options (`-(2/k)` penalty per wrong selection, floored at `0`).
2. **Calculated Column Ratio Trap:** Never average row-level margins; always write a **DAX Measure**.
3. **Bar Baseline:** Bars MUST start at `0`.
4. **Desktop Navigation:** Buttons need **`Ctrl + Click`** in Power BI Desktop.
5. **Reports vs. Dashboards:** Multi-page + single model = Report; Single-page + multi-model tiles in Service = Dashboard.
6. **Pin Live Page:** Preserves slicers on a dashboard; individual pinned tiles do not.
"""


def main():
    err = check_katex_expressions(ONE_SHOT_MD)
    assert not err, f"KaTeX error: {err}"
    wc = len(ONE_SHOT_MD.split())
    print(f"Data Visualisation One-Shot word count: {wc} words")
    db.save_course_one_shot(COURSE_ID, ONE_SHOT_MD, "")
    db.export_static_data()
    print("Saved to DB and exported study_data.js cleanly.")


if __name__ == "__main__":
    main()
