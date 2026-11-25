#!/usr/bin/env python3
"""
Upgrade Corporate Finance (2989cdfe) One-Shot Notes & Dual-Mode Formula Sheet:
- Dual Formula Sheet: (1) Visual Formula Dependency Web (Mermaid + Derivation Chains) + (2) Tabular Reference Sheet
- 8-Module One-Shot: Concise exam-calibrated conceptual & numerical trap guide for 50 MCQs x 1.5m
- Verified with check_katex_expressions() before saving to DB & exporting study_data.js
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import db
from scripts.note_quality_engine import check_katex_expressions

COURSE_ID = "2989cdfe"

FORMULA_SHEET_MD = r"""# Corporate Finance: Dual Master Formula Sheet (Modules 1 to 8)

> **Exam Rules:** **50 MCQs x 1.5 Marks = 75 Marks | 120 Mins | No Negative Marking | Scientific Calculator + Soft-Copy Formula Sheet Allowed**

---

## Part 1: Visual Formula Dependency Web (How Every Equation Connects)

```mermaid
flowchart TD
    PV["1. Present Value: PV = CF_t / (1+r)^t"] --> EAR["EAR = (1 + APR/m)^m - 1"]
    PV --> ANN["Ordinary Annuity & Loan PMT (lands at t-1)"]
    ANN --> ADUE["Annuity Due = Ordinary Annuity x (1+r)"]
    ANN --> BOND["Bond Price = Coupon x PVAF(YTM,N) + FV / (1+YTM)^N"]
    BOND --> FISH["Exact Fisher: (1+r_real) = (1+r_nom)/(1+i)"]
    PV --> PERP["Perpetuity: PV = C / r"]
    PERP --> GPERP["Growing Perpetuity: PV = C_1 / (r - g)"]
    GPERP --> DDM["Gordon DDM: P_0 = D_1 / (r - g), where g = ROE x b"]
    DDM --> PVGO["PVGO = P_0 - E_1 / r"]
    PV --> NPV["Capital Budgeting: NPV = -I_0 + Sum PV(CF_t)"]
    NPV --> PIEAC["Capital Rationing: PI = PV/I_0 | Unequal Lives: EAC = PV(Cost)/PVAF"]

    VAR["2. Portfolio Variance: w1^2 s1^2 + w2^2 s2^2 + 2 w1 w2 Cov"] --> BETA["Beta = Cov(R_i, R_m) / Var(R_m)"]
    BETA --> UNLEV["Unlevering: Beta_A = Beta_E / (1 + D/E)"]
    UNLEV --> CAPM["CAPM / SML: r_i = r_f + Beta_i (E[R_m] - r_f)"]
    CAPM --> PV

    SH["3. Financing & M&A: Rights TERP = (N x P_cum + P_sub)/(N+1)"] --> RVAL["Value of 1 Right = P_cum - TERP"]
    SYN["M&A Synergy = V_AT - (V_A + V_T)"] --> ANPV["Acquirer NPV = Synergy - (Price Paid - V_T)"]
```

### Key Derivation Chains to Remember
1. **The TVM-to-Stock Chain:** Start with $PV = \frac{CF_t}{(1+r)^t}$. Sum infinite constant cash flows $\rightarrow \frac{C}{r}$. Add growth $g < r \rightarrow \frac{C_1}{r-g}$. Replace $C_1$ with next dividend $D_1 \rightarrow$ **Gordon DDM**. Subtract no-growth earnings value $\frac{E_1}{r} \rightarrow$ **PVGO**.
2. **The Risk-to-Discount-Rate Chain:** Portfolio diversification eliminates firm-specific variance, leaving covariance with the market ($\beta = \frac{\text{Cov}(R_i, R_m)}{\text{Var}(R_m)}$). Strip peer debt via $\beta_A = \frac{\beta_E}{1 + D/E}$, plug into **CAPM** to get $r$, and feed $r$ back into **NPV / DCF**.

---

## Part 2: Complete Tabular Formula Reference (Fast Exam Lookup)

### Module 2: Time Value of Money (TVM)

| Concept | Exact Formula | Variable Meanings & Calculator Trap |
|---|---|---|
| **Future / Present Value** | $$FV_t = PV(1+r)^t \quad,\quad PV = \frac{FV_t}{(1+r)^t}$$ | Match rate per period ($r/m$) with total periods ($n \times m$). |
| **Effective Annual Rate (EAR)** | $$EAR = \left(1 + \frac{APR}{m}\right)^m - 1$$ | $m$ = compounding periods/year (12 monthly, 4 quarterly, 2 semi-annual). |
| **Continuous Compounding** | $$FV = PV \cdot e^{r \cdot t}$$ | Use $e^x$ on scientific calculator. |
| **Ordinary Annuity PV & PMT** | $$PV = C \cdot \underbrace{\frac{1 - (1+r)^{-n}}{r}}_{PVAF(r,n)} \quad,\quad PMT = \frac{Loan}{PVAF(r,n)}$$ | **#1 Trap:** PVAF lands at $t-1$ (1 period *before* first payment). For CF starting at $t=4$, discount PVAF back 3 years. |
| **Annuity Due** | $$PV_{\text{due}} = PV_{\text{ord}} \times (1+r)$$ | Payments at *start* of each period. |
| **Perpetuity & Growing Perpetuity** | $$PV = \frac{C_1}{r} \quad,\quad PV = \frac{C_1}{r - g}$$ | Requires $r > g$. Always use **next** period's cash flow $C_1$, never $C_0$. |
| **Rule of 72** | $$t_{\text{double}} \approx \frac{72}{r\%}$$ | Quick doubling-time estimate (exact: $\ln 2 / \ln(1+r)$). |

### Module 3: Bonds, Inflation & Stock Valuation

| Concept | Exact Formula | Variable Meanings & Calculator Trap |
|---|---|---|
| **Bond Price** | $$P_B = C \cdot \frac{1 - (1+y)^{-N}}{y} + \frac{FV}{(1+y)^N}$$ | **Semi-annual trap:** Halve annual coupon, halve YTM ($y$), double years ($N$). Coupon $<$ YTM $\Rightarrow$ Discount bond. |
| **Perpetual (AT1) Bond** | $$P_0 = \frac{C}{y}$$ | Annual coupon divided by required yield $y$. |
| **Zero-Coupon Bond YTM** | $$YTM = \left(\frac{FV}{P_0}\right)^{1/N} - 1$$ | Never divide total gain linearly by $N$. |
| **Holding Period Return (HPR)** | $$HPR = \frac{C_1 + (P_1 - P_0)}{P_0}$$ | Equals YTM **only** if held to maturity; falling yields create capital gains ($HPR > YTM$). |
| **Exact Fisher Equation** | $$1 + r_{\text{real}} = \frac{1 + r_{\text{nom}}}{1 + i}$$ | Approximate $r_{\text{nom}} - i$ fails on exact-decimal MCQs. |
| **Gordon Growth Model (DDM)** | $$P_0 = \frac{D_1}{r - g} = \frac{D_0(1+g)}{r - g}$$ | Check carefully whether $D_0$ (just paid) or $D_1$ (next year) is given. |
| **Sustainable Growth Rate** | $$g = ROE \times b = ROE \times (1 - \text{Payout Ratio})$$ | **Trap:** Use **retention ratio** $b$, NOT payout ratio. |
| **PVGO (Growth Value)** | $$P_0 = \frac{E_1}{r} + PVGO \implies PVGO = P_0 - \frac{E_1}{r}$$ | $\frac{E_1}{r}$ = no-growth cash-cow value. |

### Module 4: Capital Budgeting

| Concept | Exact Formula | Decision Rule & Trap |
|---|---|---|
| **Net Present Value (NPV)** | $$NPV = -I_0 + \sum_{t=1}^{n} \frac{CF_t}{(1+r)^t}$$ | Accept if $NPV > 0$. Obeys **Value Additivity**: $NPV(A+B) = NPV(A)+NPV(B)$. |
| **Profitability Index (PI)** | $$PI = \frac{PV(\text{Future CFs})}{I_0} = 1 + \frac{NPV}{I_0}$$ | Rank divisible projects by PI under **hard capital rationing**. |
| **Equivalent Annual Cost (EAC)** | $$EAC = \frac{PV(\text{Total Costs})}{PVAF(r, n)}$$ | Use when comparing ongoing replacement equipment with **unequal lives**. |

### Module 5: Risk, Return & CAPM

| Concept | Exact Formula | Variable Meanings & Calculator Trap |
|---|---|---|
| **State-Based Return & Risk** | $$E[R] = \sum p_s R_s \quad,\quad \sigma = \sqrt{\sum p_s (R_s - E[R])^2}$$ | Probability-weighted, not simple unweighted average. |
| **Two-Stock Portfolio** | $$E[R_p] = w_1 R_1 + w_2 R_2$$ $$\sigma_p^2 = w_1^2\sigma_1^2 + w_2^2\sigma_2^2 + 2w_1w_2\rho_{12}\sigma_1\sigma_2$$ | Remember $\sqrt{\sigma_p^2}$! If $\rho = -1$ and weights match inverse $\sigma$, $\sigma_p = 0$. |
| **Beta ($\beta$)** | $$\beta_i = \frac{\text{Cov}(R_i, R_m)}{\sigma_m^2} = \frac{\rho_{im}\sigma_i}{\sigma_m}$$ | Portfolio Beta: $\beta_p = \sum w_i \beta_i$ (T-Bills have $\beta = 0$). |
| **Asset (Unlevered) Beta** | $$\beta_A = \frac{\beta_E}{1 + D/E}$$ | Assumes $\beta_{\text{Debt}} = 0$ and ignores tax shield; unlever peer $\beta_E$ before pricing all-equity projects. |
| **CAPM / SML & Alpha** | $$r_i = r_f + \beta_i(E[R_m] - r_f) \quad,\quad \alpha = E[R_{\text{est}}] - r_i$$ | $\alpha > 0$ plots **above SML** $\Rightarrow$ **Underpriced**. |

### Module 6, 7 & 8: Payouts, IPOs, Rights & M&A

| Concept | Exact Formula | Variable Meanings & Exam Trap |
|---|---|---|
| **Ex-Dividend Drop** | $$P_{\text{ex}} = P_{\text{cum}} - D$$ | Homemade dividend: sell shares at $P_{\text{ex}}$ to match target cash. |
| **IPO Underpricing Cost** | $$\text{Money Left on Table} = (P_{\text{close, Day 1}} - P_{\text{offer}}) \times \text{Shares}$$ | Only **Fresh Issue** enters firm; **OFS** proceeds go to selling owners. |
| **Rights Issue (TERP & Right)** | $$TERP = \frac{N \cdot P_{\text{cum}} + P_{\text{sub}}}{N + 1}$$ $$\text{Value of 1 Right} = P_{\text{cum}} - TERP = \frac{TERP - P_{\text{sub}}}{N}$$ | For a "1-for-$N$" issue (e.g., 1-for-4, $N=4$), doing nothing forfeits $\text{Value of 1 Right}$ per share. |
| **M&A Synergy & Premium** | $$\text{Synergy} = V_{AT} - (V_A + V_T)$$ $$\text{Premium} = \text{Price Paid} - V_T$$ $$NPV_A = \text{Synergy} - \text{Premium}$$ | In zero-synergy stock deals, EPS accretion contracts P/E so price stays flat. In conglomerate co-insurance, bondholders gain at shareholders' expense. |
"""

ONE_SHOT_MD = r"""# Corporate Finance: 8-Module Conceptual & Trap One-Shot

> **How to Use This Sheet:** Use the **Master Formula Sheet** tab for equations/chains and this **8-Module Guide** for every conceptual distinction and numerical trap tested in the **50-MCQ (75-mark)** exam.

---

## Module 1: Corporate Principles & Business Forms
- **Two Core Decisions:** **Investment Decisions** acquire real tangible/intangible assets (plants, R&D, patents/brands); **Financing Decisions** choose the debt/equity mix on the right-hand side of the balance sheet.
- **Wealth Maximization vs. Profit Maximization:** Accounting profit is a single-period **flow** variable blind to cash timing, capex, and risk. Share price / NPV is a **stock** variable discounting all risk-adjusted cash flows.
- **Business Forms (India):** **Public/Private Ltd** gives limited liability + perpetual life; **LLP / OPC** offers limited liability with lighter compliance; General Partnerships carry unlimited liability.
- **Cash Flow Cycle:** Value is created ONLY when project ROIC exceeds the market's **opportunity cost of capital**; otherwise return cash to investors.

## Module 2: Time Value of Money (TVM) Traps
- **APR vs. EAR:** Always convert quoted APR to **EAR** when compounding frequency $m > 1$.
- **Delayed Annuities:** Standard `PVAF` lands **1 period before the first payment** (e.g., first CF at $t=4 \implies$ PV lands at $t=3$, so discount back 3 years, NOT 4).
- **Negative Interest Rates:** Discounting by $(1+r)$ when $r < 0$ yields $PV > FV$.

## Module 3: Bonds & Stock Markets
- **Coupon vs. YTM:** Coupon $<$ YTM $\rightarrow$ **Discount** ($P < FV$); Coupon $>$ YTM $\rightarrow$ **Premium** ($P > FV$). Longer maturity increases duration and interest-rate sensitivity.
- **HPR vs. YTM:** YTM equals realized return ONLY if held to maturity; falling yields generate capital gains ($HPR > YTM$).
- **Flight to Safety:** Crisis demand bids safe Treasury prices UP and yields DOWN.
- **Order Book:** Market **buy** orders execute at the dealer's **Ask** (higher); market **sell** orders execute at **Bid** (lower). Narrower bid-ask spread = higher liquidity.

## Module 4: Capital Budgeting Rules
- **Why NPV Rules:** Only NPV obeys **Value Additivity** and maximizes rupee wealth regardless of scale.
- **4 IRR Pitfalls:** (1) **Multiple IRRs** when cash flows change signs >1 time (**Descartes' Rule**), (2) **Borrowing projects** (`+` then `-`: accept ONLY if $IRR < r$), (3) **Mutually exclusive scale bias** (pick higher NPV, not higher IRR), (4) **Differing lives** (use **EAC** for ongoing replacement).
- **Incremental Cash Flows:** **Ignore sunk costs** (already spent feasibility studies); **include opportunity costs** (foregone warehouse rent) and **cannibalization** of existing lines.
- **Payback vs. Discounted Payback:** Discounted Payback adds TVM discipline, but BOTH still ignore post-cutoff cash flows.
- **Crossover Rate:** The discount rate where $NPV_A = NPV_B$ equals the IRR of $(CF_B - CF_A)$.

## Module 5: Risk, Return & CAPM
- **Diversification:** Eliminates **unsystematic (firm-specific)** risk, leaving only **systematic (market) risk** measured by Beta. Adding a high-SD stock can still *lower* portfolio risk if covariance is low/negative.
- **SML & Alpha:** Positive $\alpha$ plots **above the SML** = **underpriced** (bargain).
- **Asset Beta:** Never apply a leveraged peer's Equity Beta directly to an unlevered project—unlever via $\beta_A = \beta_E / (1 + D/E)$.

## Module 6: Corporate Payout Decisions
- **MM Payout Equivalence:** In frictionless markets with fixed CAPEX, a Rs 5 dividend (ex-div price drops Rs 5) and an equal-rupee fair-value share buyback leave shareholder wealth identical (buyback reduces cash & shares proportionately, so price per share stays flat).
- **Homemade Dividends:** Investors sell shares at $P_{\text{ex}}$ to manufacture desired cash.
- **Non-Cash Actions:** Stock splits, bonus issues, and reverse splits (used to avoid delisting) create zero cash/value directly.
- **Signaling & Agency:** Regular dividend cuts signal permanent earnings weakness (special dividends do not). Returning surplus cash curbs **Free Cash Flow** empire-building. Open-market buybacks offer maximum timing flexibility.

## Module 7: Financing Decisions (IPOs, SEOs, Rights, Bonds)
- **Primary vs. OFS:** Only **Fresh Issue** cash funds the company; **OFS** cash goes to selling shareholders.
- **Winner's Curse (Rock):** Uninformed retail gets full allocation in cold/overpriced IPOs and rationed allocation in hot IPOs -> IPOs must be underpriced on average.
- **SEBI Sept 2024 Study:** Highlighted heavy short-term **flipping** by retail/NII investors in week 1 of listing.
- **SEO Announcement Drop (-2% to -3%):** Asymmetric information (investors infer management thinks stock is overvalued).
- **Rights Issues:** Protect existing owners via pro-rata allocation; doing nothing (neither subscribing nor selling rights) causes an immediate wealth transfer as shares go ex-rights to TERP.
- **Callable Bonds:** Carry higher yields to compensate bondholders for issuer prepayment risk when rates fall.

## Module 8: Mergers & Acquisitions (M&A)
- **Empirical Winner:** Target shareholders capture large premiums (20-30%); Acquirer shareholders earn ~0 or slightly negative announcement returns on average.
- **Cash vs. Stock:** Acquirers confident their shares are **undervalued** prefer paying **Cash** to keep synergy upside; **Stock** shares risk/overvaluation.
- **Four Dubious Motives:**
  1. **Hubris (Roll):** Honest valuation overconfidence in auctions.
  2. **Agency:** Self-interested empire-building for CEO perks/size.
  3. **EPS Accretion (Bootstrap) Fallacy:** Zero-synergy stock deal lifts EPS mechanically while blended P/E contracts proportionately.
  4. **Co-Insurance:** Unrelated diversification lowers default risk -> transfers wealth **to Bondholders from Shareholders** unless the firm re-leverages.
"""


def main():
    err1 = check_katex_expressions(FORMULA_SHEET_MD)
    assert not err1, f"Formula sheet KaTeX error: {err1}"
    err2 = check_katex_expressions(ONE_SHOT_MD)
    assert not err2, f"One-Shot KaTeX error: {err2}"
    print(f"CF Formula Sheet: {len(FORMULA_SHEET_MD.split())} words | CF One-Shot: {len(ONE_SHOT_MD.split())} words")
    db.save_course_one_shot(COURSE_ID, ONE_SHOT_MD, FORMULA_SHEET_MD)
    db.export_static_data()
    print("Saved to DB and exported study_data.js cleanly.")


if __name__ == "__main__":
    main()
