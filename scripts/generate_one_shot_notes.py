#!/usr/bin/env python3
"""
Intelligent One-Shot Revision Hub & Master Formula Sheet Generator.
Compiles hyper-condensed, beautifully formatted, exam-focused master review notes
for all 5 degree courses.

Key Principles:
1. CURATED & INTELLIGENT: Filters out fluff, administrative intros, and repetitive sub-videos.
   Focuses strictly on high-yield exam concepts, models, frameworks, and calculations.
2. MODULE-BY-MODULE SYNTHESIS: Unified, structured chapters per module with clean typography,
   generous whitespace, callouts, and distinction tables.
3. MATHEMATICAL RIGOR (Corporate Finance):
   - Track 1: Complete Master Formula Sheet & Alphabetical Variable Index.
   - Track 2: 8-Module Revision with Step-by-Step Problem Solving Recipes & Worked Examples.
"""

import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import db

# ==============================================================================
# COURSE 1: CORPORATE FINANCE (2989cdfe)
# ==============================================================================

def get_corporate_finance_formula_sheet() -> str:
    return """# Corporate Finance: Master Formula Reference & Symbol Index

> **Exam Cram Focus:** Exhaustive mathematical formula sheet covering Modules 1 through 8. Every single variable, subscript, and parameter is defined with standard units, boundary constraints, and common calculation gotchas.

---

## 1. Alphabetical Variable Legend & Symbol Index

| Symbol | Economic & Mathematical Meaning | Standard Unit | Key Constraints / Boundaries | Common Exam Traps & Gotchas |
| :--- | :--- | :--- | :--- | :--- |
| $PV$ | **Present Value:** Discounted value today of future cash flows | Currency ($ / ₹) | $PV \\le FV$ when discount rate $r > 0$ | Using annual rate for monthly/semi-annual cash flows. |
| $FV$ | **Future Value:** Compounded value at horizon date $t$ | Currency ($ / ₹) | $FV = PV(1+r)^t$ | Confusing simple interest with compound interest. |
| $C$ or $CF_t$ | **Cash Flow:** Periodic payment or net inflow at period $t$ | Currency ($ / ₹) | Constant for annuities; variable for projects | Omitting period 0 initial cash outlay ($I_0$). |
| $r$ | **Discount Rate / Required Return / Cost of Capital** | % or decimal | Must match compounding periodicity | Forgetting to divide annual rate by $m$ (e.g. $r/2$ for semi-annual). |
| $t$ or $n$ | **Number of Periods / Time Horizon** | Periods (years/months) | Must match compounding periodicity | Forgetting to multiply years by $m$ (e.g. $5 \\text{ yrs} \\times 2 = 10$). |
| $m$ | **Compounding Frequency per Year** | Periods per year | $m=1$ (annual), $m=2$ (semi), $m=12$ (monthly) | Omitting $m$ in exponent when computing $EAR$. |
| $EAR$ | **Effective Annual Rate:** True annualized interest earned | % per annum | $EAR \\ge APR$; $EAR = (1 + APR/m)^m - 1$ | Using nominal $APR$ directly in multi-year present value formulas. |
| $APR$ | **Annual Percentage Rate:** Quoted nominal interest rate | % per annum | Quoted rate without inter-year compounding | Assuming $APR = EAR$; valid only when $m = 1$. |
| $g$ | **Constant Growth Rate:** Perpetual cash flow / dividend growth | % per annum | **Strictly $r > g$**; if $g \\ge r$, formula diverges | Using $g$ larger than the overall economic / GDP growth rate. |
| $D_0$ | **Current Dividend:** Most recently paid historical dividend | Currency per share | Paid in past ($t=0$); not discounted directly | Plugging $D_0$ into numerator instead of expected $D_1 = D_0(1+g)$. |
| $D_1$ | **Expected Dividend:** Dividend to be received at end of year 1 | Currency per share | $D_1 = D_0(1+g)$ | Confusing "just paid dividend" ($D_0$) with "next dividend" ($D_1$). |
| $P_0$ | **Current Stock / Bond Price:** Intrinsic market price at $t=0$ | Currency per share / bond | $P_0 = PV(\\text{Future Inflows})$ | Comparing clean price with dirty price without adding accrued interest. |
| $F$ | **Face Value (Par Value) of Bond** | Currency (typically $1,000) | Constant principal repaid at maturity $T$ | Forgetting that face value is repaid at end alongside the final coupon. |
| $y$ or $YTM$ | **Yield to Maturity:** Internal rate of return on bond | % per annum | Rate where $PV(\\text{coupons} + \\text{face value}) = P_0$ | Halving annual $YTM$ for semi-annual bonds but forgetting to double periodic $y$ back to annual. |
| $b$ | **Retention Ratio (Plowback Ratio)** | Unitless ratio ($0$ to $1$) | $b = 1 - \\text{Dividend Payout Ratio}$ | Subtracting $b$ from 100 instead of 1.0 when expressed as a decimal. |
| $ROE$ | **Return on Equity:** Net Income / Total Equity | % per annum | Drives sustainable growth: $g = b \\times ROE$ | Using total assets instead of shareholder equity in the denominator. |
| $NPV$ | **Net Present Value:** Incremental wealth created by project | Currency ($ / ₹) | **Decision Rule:** Accept project if $NPV > 0$ | Forgetting to subtract initial investment $I_0$ at time 0. |
| $IRR$ | **Internal Rate of Return:** Discount rate that yields $NPV = 0$ | % per annum | Accept if $IRR > r$; fails for non-normal cash flows | Choosing highest $IRR$ over highest $NPV$ for mutually exclusive projects. |
| $PI$ | **Profitability Index:** Ratio of $PV$ of inflows to initial outlay | Unitless ratio | $PI = PV(\\text{Inflows}) / I_0 = 1 + (NPV / I_0)$ | Ranking projects by highest $PI$ without considering capital budget limits. |
| $E(R)$ | **Expected Return of Asset or Portfolio** | % per annum | Probability-weighted average return | Failing to verify that portfolio weights $\\sum w_i = 1.0$. |
| $\\sigma$ | **Standard Deviation:** Total volatility / total risk | % per annum | $\\sigma = \\sqrt{\\text{Variance}}$; $\\sigma \\ge 0$ | Assuming portfolio risk is simply the weighted average of individual standard deviations. |
| $\\rho_{ij}$ | **Correlation Coefficient:** Co-movement between two assets | Unitless ratio | **Strict Range:** $-1.0 \\le \\rho_{ij} \\le +1.0$ | Believing diversification benefits require $\\rho < 0$; any $\\rho < 1.0$ diversifies risk. |
| $Cov(i,j)$ | **Covariance:** Unscaled directional co-movement | Variance units | $Cov(i,j) = \\rho_{ij} \\sigma_i \\sigma_j$ | Mixing up covariance with correlation coefficient. |
| $\\beta_i$ | **Beta (Systematic Risk):** Sensitivity to market movements | Unitless sensitivity | Market Beta $\\beta_m = 1.0$; Risk-free Beta $\\beta_f = 0$ | Thinking Beta measures total risk; Beta measures only non-diversifiable market risk. |
| $R_f$ | **Risk-Free Rate:** Return on sovereign government security | % per annum | Minimal default and liquidity risk | Using short-term T-bill rate when evaluating long-term 20-year corporate project. |
| $R_m$ | **Market Return:** Expected return on market portfolio | % per annum | $E(R_m) > R_f$ for positive risk compensation | Confusing Market Return $E(R_m)$ with Market Risk Premium $[E(R_m) - R_f]$. |
| $MRP$ | **Market Risk Premium:** Incremental reward for market risk | % per annum | $MRP = E(R_m) - R_f$ | Double subtracting $R_f$ when the problem already gives "market risk premium". |
| $WACC$ | **Weighted Average Cost of Capital:** Overall hurdle rate | % per annum | Weighted by **Market Values**, not book values | Forgetting the $(1 - T_c)$ tax shield adjustment on cost of debt $r_d$. |
| $r_e$ | **Cost of Equity:** Required return demanded by stockholders | % per annum | Derived via CAPM or Gordon Growth model | Using historical dividend growth instead of forward-looking required rate. |
| $r_d$ | **Pre-tax Cost of Debt:** Current borrowing yield on firm bonds | % per annum | Current market $YTM$, not historic coupon | Forgetting to multiply by $(1 - T_c)$ in the $WACC$ equation. |
| $T_c$ | **Marginal Corporate Tax Rate** | % or decimal | Reduces after-tax cost of debt: $r_d(1 - T_c)$ | Applying tax shield to equity ($r_e$); equity dividends are not tax-deductible. |
| $E$ | **Market Value of Equity** | Currency ($ / ₹) | $E = \\text{Share Price} \\times \\text{Number of Shares}$ | Using balance sheet book value of equity instead of market value. |
| $D$ | **Market Value of Debt** | Currency ($ / ₹) | Total market worth of outstanding debt | Confusing face value with market price of bonds when interest rates have shifted. |
| $V$ | **Total Firm Value:** Combined enterprise value | Currency ($ / ₹) | $V = E + D$ | Forgetting to re-calculate $V$ after debt issuance or share repurchase. |
| $V_L$ | **Value of Levered Firm:** Firm with interest-bearing debt | Currency ($ / ₹) | With taxes: $V_L = V_U + T_c D$ | Applying tax shield $T_c D$ when tax rate is zero ($V_L = V_U$ under MM no taxes). |
| $V_U$ | **Value of Unlevered Firm:** Firm financed 100% by equity | Currency ($ / ₹) | $V_U = \\text{EBIT}(1 - T_c) / r_0$ | Discounting unlevered cash flows at $WACC$ instead of unlevered cost of equity $r_0$. |
| $\\beta_L$ | **Levered Beta (Equity Beta):** Reflects business + financial risk | Unitless | $\\beta_L = \\beta_U [1 + (1 - T_c)(D/E)]$ | Forgetting the $(1 - T_c)$ term in the Hamada equation. |
| $\\beta_U$ | **Unlevered Beta (Asset Beta):** Pure business operational risk | Unitless | $\\beta_U = \\beta_L / [1 + (1 - T_c)(D/E)]$ | Assuming asset beta increases with debt; asset beta is independent of financing. |
| $S$ | **Synergy in M&A:** Incremental combined enterprise value | Currency ($ / ₹) | $S = V_{AB} - (V_A + V_B)$ | Including target standalone value in synergy; synergy is only the gain above sum of parts. |

---

## 2. Master Formulas by Module

### Module 1: Time Value of Money & Compounding
- **Future Value ($FV$):** $FV = PV \\times (1 + r)^t$
- **Present Value ($PV$):** $PV = \\frac{FV}{(1 + r)^t} = FV \\times (1 + r)^{-t}$
- **Effective Annual Rate ($EAR$):** $EAR = \\left(1 + \\frac{APR}{m}\\right)^m - 1$
- **Continuous Compounding:** $FV = PV \\times e^{r \\times t}, \\quad EAR = e^r - 1$
- **Rule of 72:** $t_{\\text{double}} \\approx \\frac{72}{r\\%}$

### Module 2: Annuities, Perpetuities & Amortization
- **Ordinary Annuity Present Value:** $PV = C \\times \\left[ \\frac{1 - (1 + r)^{-t}}{r} \\right]$
- **Ordinary Annuity Future Value:** $FV = C \\times \\left[ \\frac{(1 + r)^t - 1}{r} \\right]$
- **Annuity Due Adjustment:** $PV_{\\text{due}} = PV_{\\text{ordinary}} \\times (1 + r)$
- **Perpetuity:** $PV = \\frac{C}{r}$
- **Growing Perpetuity ($r > g$):** $PV = \\frac{C_1}{r - g} = \\frac{C_0(1+g)}{r - g}$
- **Loan Amortization Payment:** $PMT = \\frac{PV \\times r}{1 - (1 + r)^{-t}}$
  - Interest: $I_t = \\text{Balance}_{t-1} \\times r$
  - Principal: $PR_t = PMT - I_t$

### Module 3: Fixed Income (Bonds) & Stock Valuation
- **Bond Pricing Equation:** $P_0 = C \\times \\left[ \\frac{1 - (1 + y)^{-T}}{y} \\right] + \\frac{F}{(1 + y)^T}$
- **Semi-Annual Bond Adjustment:** $C/2$, $y/2$, and $2T$ periods.
- **Current Yield:** $CY = \\frac{\\text{Annual Coupon}}{P_0} = \\frac{C}{P_0}$
- **Clean vs Dirty Price:** $\\text{Dirty Price} = \\text{Clean Price} + \\text{Accrued Interest}$
- **Gordon Growth Model:** $P_0 = \\frac{D_1}{r - g} = \\frac{D_0(1+g)}{r - g} \\quad (r > g)$
- **Expected Return from Stock:** $r = \\frac{D_1}{P_0} + g = \\text{Dividend Yield} + \\text{Capital Gains Yield}$
- **Sustainable Growth Rate:** $g = b \\times ROE = (1 - \\text{Payout Ratio}) \\times ROE$

### Module 4: Capital Budgeting Decision Rules
- **Net Present Value ($NPV$):** $NPV = \\sum_{t=1}^n \\frac{CF_t}{(1 + r)^t} - I_0$  *(Accept if $NPV > 0$)*
- **Internal Rate of Return ($IRR$):** $\\sum_{t=1}^n \\frac{CF_t}{(1 + IRR)^t} - I_0 = 0$  *(Accept if $IRR > r$)*
- **Profitability Index ($PI$):** $PI = \\frac{PV(\\text{Inflows})}{I_0} = 1 + \\frac{NPV}{I_0}$  *(Accept if $PI > 1.0$)*
- **Equivalent Annual Annuity ($EAA$):** $EAA = \\frac{NPV \\times r}{1 - (1 + r)^{-t}}$

### Module 5: Risk, Return & Portfolio Theory
- **Expected Portfolio Return:** $E(R_p) = w_1 E(R_1) + w_2 E(R_2)$
- **Portfolio Variance (2 Assets):** $\\sigma_p^2 = w_1^2 \\sigma_1^2 + w_2^2 \\sigma_2^2 + 2 w_1 w_2 \\rho_{12} \\sigma_1 \\sigma_2$
- **Covariance Link:** $Cov(R_1, R_2) = \\rho_{12} \\sigma_1 \\sigma_2$
- **Asset Beta:** $\\beta_i = \\frac{Cov(R_i, R_m)}{\\sigma_m^2} = \\rho_{im} \\times \\frac{\\sigma_i}{\\sigma_m}$
- **Portfolio Beta:** $\\beta_p = \\sum w_i \\beta_i$

### Module 6: Capital Asset Pricing Model & Corporate Payouts
- **CAPM Formula:** $E(R_i) = R_f + \\beta_i [E(R_m) - R_f]$
- **Market Risk Premium:** $MRP = E(R_m) - R_f$
- **Sharpe Ratio:** $\\text{Sharpe} = \\frac{E(R_p) - R_f}{\\sigma_p}$
- **Treynor Ratio:** $\\text{Treynor} = \\frac{E(R_p) - R_f}{\\beta_p}$
- **Dividend Yield:** $DY = D_1 / P_0$
- **Dividend Payout Ratio:** $PR = \\text{Dividends} / \\text{Net Income}$

### Module 7: Cost of Capital & WACC
- **After-tax Cost of Debt:** $r_{d, \\text{after-tax}} = r_d \\times (1 - T_c)$
- **Cost of Preferred Stock:** $r_p = D_p / P_p$
- **Weighted Average Cost of Capital (WACC):**
  $$WACC = \\left(\\frac{E}{V}\\right) r_e + \\left(\\frac{D}{V}\\right) r_d (1 - T_c) + \\left(\\frac{P}{V}\\right) r_p$$
  *(Always use market values: $E = P_0 \\times \\text{Shares}$, $V = E + D + P$)*

### Module 8: Capital Structure, MM Propositions & M&A
- **MM Proposition I (No Tax):** $V_L = V_U$
- **MM Proposition II (No Tax):** $r_e = r_0 + \\frac{D}{E}(r_0 - r_d)$
- **MM Proposition I (With Tax):** $V_L = V_U + T_c D$
- **Interest Tax Shield:** $PV(ITS) = T_c \\times D$
- **MM Proposition II (With Tax):** $r_e = r_0 + \\frac{D}{E}(r_0 - r_d)(1 - T_c)$
- **Hamada Equation (Unlevering Beta):** $\\beta_U = \\frac{\\beta_L}{1 + (1 - T_c)(D/E)}$
- **Hamada Equation (Re-levering Beta):** $\\beta_L = \\beta_U [1 + (1 - T_c)(D/E)]$
- **M&A Net Synergy:** $S = V_{AB} - (V_A + V_B)$
- **Net Present Value of M&A:** $NPV_{M\\&A} = S - \\text{Premium Paid} = V_B + S - \\text{Cash Paid}$
"""

def get_corporate_finance_one_shot_notes() -> str:
    return """# Corporate Finance: High-Yield Revision Guide & Problem Solving Notes

> **Exam Revision Strategy:** Designed specifically for rapid last-minute cramming (1–2 hours before exams). Fluff and administrative content are removed. For every quantitative topic, this guide gives the **Formula Statement**, the **Input Checklist**, a **Step-by-Step Solving Algorithm**, a **Realistic Worked Numerical Example**, and the **Examiner Trap Radar**.

---

## Module 1: Foundations of Corporate Finance & Time Value Principle

### 1. The Core Objective of Corporate Finance
- **Shareholder Wealth Maximization (SWM):** The definitive normative goal of financial management is to maximize the intrinsic market value of the firm's equity (stock price).
- **Why Profit Maximization Fails:**
  1. Ignores the timing and duration of cash flows.
  2. Ignores risk and uncertainty.
  3. Subject to accounting manipulation and non-cash distortions.
- **Agency Theory in Corporations:** Conflict of interest between shareholders (principals) and corporate executives (agents).
  - *Direct Agency Costs:* Corporate jet purchases, excessive perquisites, external auditing expenses.
  - *Indirect Agency Costs:* Lost opportunities due to overly risk-averse managers fearing job loss.
  - *Mitigation Tools:* Executive stock options, independent board of directors, threat of hostile takeover.

---

## Module 2: Time Value of Money & Loan Amortization

### 1. Single Lump Sums & Compounding Mechanics
- **Core Principle:** A rupee today is worth more than a rupee in the future due to earning capacity and inflation.
- **Formula:** $FV = PV(1 + r)^t \\iff PV = \\frac{FV}{(1 + r)^t}$

#### 📐 Step-by-Step Solving Recipe
1. **Identify Given Variables:** Current principal ($PV$), annual rate ($r$), years ($t$), compounding frequency ($m$).
2. **Adjust for Periodicity:** Periodic rate $= r / m$; total periods $n = t \\times m$.
3. **Substitute & Solve:** $FV = PV \\times (1 + r/m)^n$.

> **Worked Numerical Example:**
> A student invests ₹50,000 in an account paying 8% per annum compounded quarterly ($m=4$) for 3 years.
> - $n = 3 \\times 4 = 12$ quarters.
> - Periodic rate $= 0.08 / 4 = 0.02$ (2% per quarter).
> - $FV = 50,000 \\times (1.02)^{12} = 50,000 \\times 1.26824 = \\mathbf{₹63,412.09}$.

- **⚠️ Examiner Trap:** Compounding frequency $m$ must adjust *both* the rate (divide by $m$) and the exponent (multiply by $m$).

---

### 2. Effective Annual Rate ($EAR$) vs Annual Percentage Rate ($APR$)
- **Formula:** $EAR = \\left(1 + \\frac{APR}{m}\\right)^m - 1$
- **Rule:** Whenever compounding occurs more frequently than once a year ($m > 1$), $EAR > APR$.

> **Worked Numerical Example:**
> Bank A offers 12% compounded monthly ($m=12$).
> - $EAR = (1 + 0.12/12)^{12} - 1 = (1.01)^{12} - 1 = 1.126825 - 1 = \\mathbf{12.68\\%}$.
> Bank B offers 12.2% compounded annually ($m=1$).
> - Decision: Choose Bank A for investments ($12.68\\% > 12.20\\%$); choose Bank B for borrowing.

---

### 3. Ordinary Annuities vs Annuities Due
- **Ordinary Annuity:** Cash flows occur at the **end** of each period.
  $$PV = C \\times \\left[ \\frac{1 - (1 + r)^{-t}}{r} \\right]$$
- **Annuity Due:** Cash flows occur at the **beginning** of each period.
  $$PV_{\\text{due}} = PV_{\\text{ordinary}} \\times (1 + r)$$

> **Worked Numerical Example:**
> You win a prize paying ₹100,000 at the end of each year for 5 years at an 8% discount rate.
> - $PV_{\\text{ord}} = 100,000 \\times \\left[ \\frac{1 - (1.08)^{-5}}{0.08} \\right] = 100,000 \\times 3.99271 = \\mathbf{₹399,271}$.
> If payments start immediately (Annuity Due):
> - $PV_{\\text{due}} = 399,271 \\times 1.08 = \\mathbf{₹431,213}$.

---

### 4. Perpetuities & Growing Perpetuities
- **Flat Perpetuity:** $PV = \\frac{C}{r}$
- **Gordon Growing Perpetuity ($r > g$):** $PV = \\frac{C_1}{r - g} = \\frac{C_0(1+g)}{r - g}$

> **Worked Numerical Example:**
> A commercial property generates net rental income of ₹1,200,000 next year ($C_1$), expected to grow at 3% annually forever. Required return is 11%.
> - $PV = \\frac{1,200,000}{0.11 - 0.03} = \\frac{1,200,000}{0.08} = \\mathbf{₹15,000,000}$.

- **⚠️ Examiner Trap:** If problem states "a cash flow *just paid* was ₹1,000,000 growing at 3%", that is $C_0$. You must multiply by $1.03$ to find $C_1 = ₹1,030,000$ before dividing by $(r - g)$!

---

## Module 3: Fixed Income (Bonds) & Stock Valuation

### 1. Bond Pricing Mechanics
- **Bond Valuation Formula:**
  $$P_0 = C \\times \\left[ \\frac{1 - (1 + y)^{-T}}{y} \\right] + \\frac{F}{(1 + y)^T}$$
- **Bond Pricing Theorems:**
  - If Coupon Rate $= YTM \\implies$ Bond sells at **Par** ($P_0 = F$).
  - If Coupon Rate $> YTM \\implies$ Bond sells at a **Premium** ($P_0 > F$).
  - If Coupon Rate $< YTM \\implies$ Bond sells at a **Discount** ($P_0 < F$).
  - *Inverse Relationship:* When interest rates (yields) rise, bond prices fall!

> **Worked Numerical Example (Semi-Annual Coupon):**
> A 10-year, ₹1,000 par bond has an 8% annual coupon paid semi-annually. Yield to maturity is 10%.
> - Periodic coupon $C = (0.08 \\times 1,000) / 2 = ₹40$.
> - Periodic yield $y = 0.10 / 2 = 0.05$ (5%).
> - Total periods $n = 10 \\times 2 = 20$.
> - $PV(\\text{Coupons}) = 40 \\times \\left[ \\frac{1 - (1.05)^{-20}}{0.05} \\right] = 40 \\times 12.4622 = ₹498.49$.
> - $PV(\\text{Par}) = \\frac{1,000}{(1.05)^{20}} = \\frac{1,000}{2.6533} = ₹376.89$.
> - $P_0 = 498.49 + 376.89 = \\mathbf{₹875.38}$ (Discount bond, since $8\\% < 10\\%$).

---

### 2. Common Stock Valuation: Dividend Discount Model
- **Gordon Growth Model:**
  $$P_0 = \\frac{D_1}{r - g} = \\frac{D_0(1 + g)}{r - g}$$
- **Required Return Implied by Stock Price:**
  $$r = \\frac{D_1}{P_0} + g = \\text{Dividend Yield} + \\text{Capital Gains Yield}$$
- **Sustainable Growth Formula:**
  $$g = b \\times ROE = (1 - \\text{Payout Ratio}) \\times ROE$$

> **Worked Numerical Example:**
> Company pays a ₹4.00 dividend just now ($D_0$). Payout ratio is 40%, and $ROE$ is 15%. Required return is 12%.
> 1. Retention ratio $b = 1 - 0.40 = 0.60$.
> 2. Growth rate $g = 0.60 \\times 0.15 = 0.09$ (9%).
> 3. Expected dividend $D_1 = 4.00 \\times (1 + 0.09) = ₹4.36$.
> 4. Stock price $P_0 = \\frac{4.36}{0.12 - 0.09} = \\frac{4.36}{0.03} = \\mathbf{₹145.33}$.

---

## Module 4: Capital Budgeting & Investment Criteria

### 1. Net Present Value ($NPV$) vs Internal Rate of Return ($IRR$)

| Dimension | Net Present Value ($NPV$) | Internal Rate of Return ($IRR$) |
| :--- | :--- | :--- |
| **Mathematical Definition** | $\\sum \\frac{CF_t}{(1+r)^t} - I_0$ | Rate $IRR$ where $NPV = 0$ |
| **Decision Rule** | Accept if $NPV > 0$ | Accept if $IRR > \\text{Hurdle Rate } r$ |
| **Reinvestment Assumption** | Cash flows reinvested at **Cost of Capital $r$** (Realistic) | Cash flows reinvested at **$IRR$** (Unrealistic) |
| **Mutually Exclusive Projects** | **Reliable:** Always selects project creating most wealth | **Unreliable:** Fails when project sizes or timings differ |
| **Sign Changes in Cash Flow** | Always produces a unique, correct answer | Produces multiple $IRRs$ or no real $IRR$ |

> **Worked Numerical Example (NPV & Profitability Index):**
> Project requires ₹500,000 initial outlay ($I_0$). Cash inflows: Yr 1 = ₹200,000; Yr 2 = ₹250,000; Yr 3 = ₹250,000. Cost of capital is 10%.
> - $PV(CF_1) = 200,000 / 1.10 = ₹181,818$
> - $PV(CF_2) = 250,000 / (1.10)^2 = ₹206,612$
> - $PV(CF_3) = 250,000 / (1.10)^3 = ₹187,829$
> - Total $PV(\\text{Inflows}) = 181,818 + 206,612 + 187,829 = ₹576,259$.
> - $NPV = 576,259 - 500,000 = \\mathbf{+₹76,259}$ $\\implies$ **Accept!**
> - $PI = \\frac{576,259}{500,000} = \\mathbf{1.15}$ $\\implies$ **Accept!**

---

## Module 5: Risk, Return & Portfolio Theory

### 1. Portfolio Expected Return & Variance
- **Expected Return:** $E(R_p) = w_1 E(R_1) + w_2 E(R_2)$, where $w_1 + w_2 = 1.0$.
- **Portfolio Variance (2 Assets):**
  $$\\sigma_p^2 = w_1^2 \\sigma_1^2 + w_2^2 \\sigma_2^2 + 2 w_1 w_2 \\rho_{12} \\sigma_1 \\sigma_2$$
- **The Diversification Theorem:**
  - If correlation $\\rho = +1.0 \\implies$ No risk reduction; $\\sigma_p$ is a straight weighted average.
  - If correlation $\\rho < +1.0 \\implies$ Portfolio risk is *strictly less* than weighted average risk.
  - If correlation $\\rho = -1.0 \\implies$ Perfect hedge; portfolio risk can be reduced to zero!

> **Worked Numerical Example:**
> Asset A: $E(R_A) = 14\\%$, $\\sigma_A = 20\\%$. Asset B: $E(R_B) = 8\\%$, $\\sigma_B = 10\\%$.
> Weights: $w_A = 0.60$, $w_B = 0.40$. Correlation $\\rho_{AB} = 0.20$.
> 1. $E(R_p) = (0.60 \\times 14) + (0.40 \\times 8) = 8.4 + 3.2 = \\mathbf{11.6\\%}$.
> 2. $\\sigma_p^2 = (0.6)^2(20)^2 + (0.4)^2(10)^2 + 2(0.6)(0.4)(0.20)(20)(10)$
>    $= 0.36(400) + 0.16(100) + 0.48(0.20)(200) = 144 + 16 + 19.2 = 179.2$.
> 3. $\\sigma_p = \\sqrt{179.2} = \\mathbf{13.39\\%}$.
> *Notice:* Weighted average standard deviation would be $(0.6 \\times 20) + (0.4 \\times 10) = 16.0\\%$. Diversification eliminated $2.61\\%$ of volatility!

---

## Module 6: Capital Asset Pricing Model (CAPM) & Payouts

### 1. Capital Asset Pricing Model (CAPM)
- **Security Market Line (SML):**
  $$E(R_i) = R_f + \\beta_i [E(R_m) - R_f]$$
- **Beta ($\\beta_i$):** Measures non-diversifiable systematic market risk.
  $$\\beta_i = \\frac{Cov(R_i, R_m)}{\\sigma_m^2} = \\rho_{im} \\times \\frac{\\sigma_i}{\\sigma_m}$$

> **Worked Numerical Example (Valuation via CAPM):**
> Risk-free rate $R_f = 6\\%$, expected market return $E(R_m) = 14\\%$. Stock X has $\\beta = 1.25$.
> - Market Risk Premium $MRP = 14\\% - 6\\% = 8\\%$.
> - Required Return $E(R_X) = 6\\% + 1.25(8\\%) = 6\\% + 10\\% = \\mathbf{16.0\\%}$.
> - If an analyst forecasts Stock X will return $18\\%$, Jensen's Alpha $\\alpha = 18\\% - 16\\% = +2\\%$ (Stock is **Undervalued**, BUY).

- **⚠️ Examiner Trap:** When the exam states "the *market risk premium* is 8%", do NOT subtract $R_f$ again! That is already $[E(R_m) - R_f]$.

---

## Module 7: Cost of Capital & WACC

### 1. Weighted Average Cost of Capital (WACC)
- **Master Formula:**
  $$WACC = \\left(\\frac{E}{V}\\right) r_e + \\left(\\frac{D}{V}\\right) r_d (1 - T_c) + \\left(\\frac{P}{V}\\right) r_p$$
- **Capital Weights Rule:** Must use **Market Values**, never book values.
  - $E = \\text{Market Price per Share} \\times \\text{Number of Shares}$
  - $D = \\text{Market Price per Bond} \\times \\text{Number of Bonds}$
  - $V = E + D + P$

> **Worked Numerical Example:**
> Company has:
> - Equity: 1,000,000 shares trading at ₹60 = $E = ₹60,000,000$. Cost of equity $r_e = 15\\%$.
> - Debt: Outstanding bonds with market value $D = ₹40,000,000$. Pre-tax cost of debt $r_d = 9\\%$.
> - Tax Rate $T_c = 30\\%$.
> 1. Total Firm Value $V = 60M + 40M = ₹100,000,000$.
> 2. Weights: $w_e = 60/100 = 0.60$; $w_d = 40/100 = 0.40$.
> 3. After-tax cost of debt $= 9\\% \\times (1 - 0.30) = 6.30\\%$.
> 4. $WACC = (0.60 \\times 15\\%) + (0.40 \\times 6.30\\%) = 9.0\\% + 2.52\\% = \\mathbf{11.52\\%}$.

---

## Module 8: Capital Structure, Modigliani-Miller & M&A

### 1. Modigliani-Miller Theorems & Debt Tax Shields
- **MM Proposition I (With Taxes):** Debt increases firm value due to the tax deductibility of interest payments:
  $$V_L = V_U + T_c D$$
- **Value of Interest Tax Shield ($PV(ITS)$):** $PV(ITS) = T_c \\times D$ (for perpetual debt).
- **MM Proposition II (With Taxes):**
  $$r_e = r_0 + \\frac{D}{E}(r_0 - r_d)(1 - T_c)$$

### 2. Hamada's Equation: Unlevering & Re-levering Beta
- **Unlevering Beta:** $\\beta_U = \\frac{\\beta_L}{1 + (1 - T_c)(D/E)}$
- **Re-levering Beta:** $\\beta_L = \\beta_U \\left[1 + (1 - T_c)(D/E)\\right]$

> **Worked Numerical Example:**
> A comparable listed peer has $\\beta_L = 1.40$, Debt/Equity ratio $D/E = 0.50$, tax rate $30\\%$.
> Your firm plans to operate with $D/E = 0.80$ and same tax rate.
> 1. **Unlever peer to isolate asset risk:**
>    $$\\beta_U = \\frac{1.40}{1 + (1 - 0.30)(0.50)} = \\frac{1.40}{1 + 0.35} = \\frac{1.40}{1.35} = \\mathbf{1.037}$$
> 2. **Re-lever to target structure:**
>    $$\\beta_L = 1.037 \\times [1 + (1 - 0.30)(0.80)] = 1.037 \\times [1 + 0.56] = 1.037 \\times 1.56 = \\mathbf{1.618}$$.

### 3. Mergers & Acquisitions Valuation
- **Synergy ($S$):** $S = V_{AB} - (V_A + V_B)$
- **Net Present Value to Acquirer:** $NPV_{M\\&A} = S - \\text{Premium Paid} = V_B + S - \\text{Cash Paid}$
- **Maximum Purchase Price:** $P_{\\text{max}} = V_B + S$
"""

# ==============================================================================
# COURSE 2: FAMILY BUSINESS STRATEGY (db945ff9)
# ==============================================================================

def get_family_business_one_shot_notes() -> str:
    return """# Family Business Strategy: 8-Module Master Revision Notes

> **Exam Revision Strategy:** Curated specifically for rapid last-minute cramming (1–2 hours before exams). All administrative intros, repetitive case-study filler, and generic conversational segments are omitted. Only the core frameworks, academic models, technical definitions, and exam gotchas are included.

---

## Module 1: Introduction to Family Businesses & Foundational Frameworks

### 1. Defining a Family Business (Chua, Chrisman, & Sharma Operational Definition)
- **A business is a Family Firm IF and ONLY IF:**
  1. **Ownership & Governance Control:** A family (or coalition of families) possesses sufficient voting equity to determine strategic direction.
  2. **Active Family Influence:** Family members actively participate in senior management or the Board of Directors.
  3. **Transgenerational Intent:** A clear, shared vision exists to preserve and transfer leadership and ownership to future generations.
- *Exam Gotcha:* A firm owned 100% by a founder who intends to sell it off upon retirement is an **entrepreneurial firm**, NOT a family business, because it lacks transgenerational intent.

---

### 2. Gersick's Three-Circle Model of Family Enterprise
- Conceptualizes the family business as three independent, overlapping subsystems:
  1. **Family Circle:** Driven by emotional bonds, unconditional love, equality, and inward focus.
  2. **Business Circle:** Driven by commercial competence, meritocracy, market performance, and profit.
  3. **Ownership Circle:** Driven by capital return, liquidity, voting control, and risk management.
- **The 7 Distinct Stakeholder Positions:**
  - *Zone 1 (Family only):* Non-working, non-owning relative (wants family unity, emotional harmony).
  - *Zone 2 (Business only):* Non-family employee (wants meritocratic promotion, fair compensation).
  - *Zone 3 (Ownership only):* External investor (wants dividends, ROI, share liquidity).
  - *Zone 4 (Family + Ownership):* Non-working family shareholder (wants high dividends, capital protection).
  - *Zone 5 (Business + Ownership):* Non-family executive with equity (wants company growth, stock appreciation).
  - *Zone 6 (Family + Business):* Working relative with no shares (wants career growth, equal recognition).
  - *Zone 7 (Center - All 3):* Family Owner-Manager (carries full emotional, financial, and strategic burden).

---

### 3. Theoretical Lenses: Agency Theory vs Stewardship Theory

| Analytical Dimension | Agency Theory (Jensen & Meckling) | Stewardship Theory (Davis, Schoorman, & Donaldson) |
| :--- | :--- | :--- |
| **View of Human Nature** | Self-serving, opportunistic, economic agent seeking personal utility | Pro-organizational, collectivist, intrinsically motivated partner |
| **Behavioral Motivation** | Extrinsic financial rewards, bonuses, threat of monitoring | Intrinsic satisfaction, company mission, legacy preservation |
| **Type I Agency Problem** | Conflict between Owners (Principals) and Managers (Agents). *Low in founder family firms!* | Assumes alignment; managers act in the best long-term interest of the firm |
| **Type II Agency Problem** | **High in Family Firms:** Majority family owners expropriating wealth from minority external shareholders | Replaced by collective pride and reputational preservation |
| **Governance Approach** | Tight monitoring, formal controls, auditing, board surveillance | Trust-based empowerment, shared cultural values, strategic mentoring |

---

### 4. Socioemotional Wealth (SEW) & The FIBER Framework
- **Socioemotional Wealth:** The non-financial utilities and emotional endowments that family owners derive from controlling the firm.
- **The FIBER Dimensions (Gómez-Mejía et al.):**
  - **F — Family Control & Influence:** Direct discretionary control over key executive appointments.
  - **I — Identification with the Firm:** The family's public identity and community reputation are inseparable from the business.
  - **B — Binding Social Ties:** Mutual commitment and loyalty extended to long-standing employees and local community.
  - **E — Emotional Attachment:** Psychological ownership, nostalgic memories, and pride embedded in company facilities.
  - **R — Renewal of Family Bonds:** Preserving the legacy to ensure future generations have a corporate home.
- **Strategic Implication (Loss Aversion):** Family owners will reject positive-NPV commercial decisions (like issuing new equity or selling a division) if it threatens to destroy their Socioemotional Wealth!

---

## Module 2: Dynamics of the Family Firm & The 5 Ownership Rights

### 1. The Five Fundamental Rights of Family Owners
Family owners possess five distinct property and strategic rights that must be clearly governed:
1. **Right to Design:** The authority to determine the legal and capital structure of the company (e.g. trusts, holding companies, dual-class shares).
2. **Right to Decide:** Voting power over fundamental company decisions (appointing directors, mergers, liquidations).
3. **Right to Value:** Defining what "success" means (balancing financial profit vs socioemotional dividends).
4. **Right to Information & Communication:** Receiving timely, transparent operational and financial disclosures.
5. **Right to Transfer:** The authority to sell, gift, or bequeath ownership shares according to agreed protocols.

---

### 2. The Four-Room Model of Family Enterprise Governance
To prevent chaotic role confusion, family enterprises structure governance into four distinct forums:
- **Room 1: The Family Room (Family Assembly / Council):** Focuses on family harmony, values, philanthropy, education, and family policies.
- **Room 2: The Board Room (Board of Directors):** Focuses on business strategy, CEO evaluation, capital allocation, and risk management.
- **Room 3: The Executive Suite (Management Team):** Focuses on day-to-day operations, sales, manufacturing, and profit delivery.
- **Room 4: The Owner's Room (Shareholders Assembly):** Focuses on capital structure, dividend policy, voting on board members, and share transfers.
- *Golden Rule:* Never debate "Family Room" emotional issues inside the "Board Room"!

---

## Module 3: Succession in Family Firms: Process, Pitfalls & Exit Archetypes

### 1. Succession as a Multi-Stage Evolutionary Process
Succession is not an isolated event (coronation); it is a multi-year evolutionary journey:
1. **Stage 1: Pre-Entry & Education:** Next-Gen completes university education and earns 3–5 years of verified outside work experience.
2. **Stage 2: Entry & Junior Operational Rotation:** Joining at an entry-level position; earning credibility among non-family peers.
3. **Stage 3: Functional Leadership:** Taking full P&L accountability for a division or subsidiary.
4. **Stage 4: Joint Leadership / Co-Piloting:** Working alongside the incumbent in strategic decision-making.
5. **Stage 5: Full Transfer:** Complete transfer of executive authority and voting equity.

---

### 2. Incumbent Exit Archetypes (Sonnenfeld's Model)
- **The Monarch:** Refuses to step down until death or physical incapacitation; believes they are indispensable.
- **The General:** Retires under pressure but hovers in the background, constantly plotting a comeback when crisis strikes.
- **The Ambassador:** Gracefully leaves executive power, serves as an elder statesman/advisor, and supports the successor.
- **The Governor:** Serves a strict, predetermined term, steps down cleanly, and transitions to outside interests.

---

### 3. Pruning the Family Tree
- As the family expands from siblings to cousins (Cousin Consortium), shareholding fragments into fractional owners with divergent financial goals.
- **Pruning Mechanics:** Buying out non-working or disinterested family branches via company share redemptions, debt-financed buyouts, or spin-offs to concentrate ownership among active, dedicated stewards.

---

## Module 4: Family Dynamics in Action & Employment Policies

### 1. Family Employment Policy (FEP)
To maintain meritocracy and prevent toxic nepotism, every multi-generational firm requires a formal FEP:
- **Minimum Criteria for Next-Gen Entry:**
  - Relevant academic degree from an accredited institution.
  - Mandatory 3–5 years of successful outside work experience with proven promotions.
  - Entry must fill an existing, budgeted vacancy; no jobs created purely for family members.
  - Compensation set strictly at prevailing market rates benchmarked by independent HR compensation consultants.

---

### 2. Related-Party Transactions (RPT)
- Purchasing goods, leasing real estate, or extending personal loans between family members and the business.
- **Governance Requirement:** All RPTs must be transacted at verified **arm's length fair market value** and approved by independent board directors to protect minority shareholders and prevent corporate asset stripping.

---

## Module 5: Management & Professionalisation

### 1. Defining Professionalisation in Family Firms
Professionalisation is NOT simply hiring non-family executives. It involves three fundamental shifts:
1. **Professional Management:** Instituting formal KPI performance evaluation, standardized operating procedures (SOPs), and meritocratic compensation.
2. **Professional Governance:** Establishing an active Board of Directors with qualified external independent directors.
3. **Professional Culture:** Transitioning from informal patriarchal decree to transparent, data-driven decision-making.

---

### 2. Retaining Non-Family Executives: The Glass Ceiling Trap
- Qualified non-family leaders often leave family businesses due to:
  - Exclusion from inner-circle informal family dinner decisions.
  - Glass ceilings where top leadership is reserved exclusively for bloodline successors regardless of talent.
  - Lack of long-term wealth creation (no equity incentives).
- **Remedies:** Long-term incentive plans (LTIP), Phantom Stock units, and clear operational autonomy.

---

## Module 6: Family Business Governance & The Family Constitution

### 1. The Three-Tiered Governance Architecture

```
[Family Circle]      --> Family Assembly (All members)  --> Family Council (Elected executive committee)
[Business Circle]    --> Board of Directors (Family + Independent Directors) --> Executive Management
[Ownership Circle]   --> Shareholder Assembly (Family Shareholders) --> Voting Trust / Holding Company
```

- **Family Assembly:** Broad gathering of the extended family to celebrate heritage and learn about business performance.
- **Family Council:** Executive committee (5–9 members) of the family that drafts family policies, resolves internal disputes, and coordinates with the Board of Directors.
- **Board of Directors:** Fiduciary body responsible for CEO evaluation, approving strategic plans, and monitoring financial risk.

---

### 2. The Family Constitution (Family Charter)
- A living, formal document articulating family values, legacy vision, and binding operating agreements:
  - **Core Contents:** Family mission statement, Family Employment Policy, Board selection criteria, Next-Gen education funding, Code of Conduct, and Dispute Resolution mechanisms.
  - **Share Transfer Protocols (Buy-Sell Agreements):**
    - *Right of First Refusal:* Shares must first be offered to active family owners or the company before external parties.
    - *Valuation Formula:* Predetermined formula (e.g. EBITDA multiple or third-party audit) to value shares upon exit, avoiding emotional price disputes.

---

## Module 7: Communities, External Stakeholders & Patient Capital

### 1. Patient Capital as a Competitive Moat
- Unlike publicly traded conglomerates pressured by quarterly earnings targets, family firms deploy **patient capital**:
  - Ability to make 10-to-20 year capital investments in R&D, brand trust, and capital equipment.
  - High resilience during economic downturns; lower debt leverage and higher survival rates.
- **Reputational Capital:** High social capital embedded in the local community; lower employee turnover due to paternalistic loyalty.

---

## Module 8: Institutional Contexts & Emerging Market Business Groups

### 1. Institutional Voids & Business Groups (Khanna & Palepu)
- In emerging markets (like India, Latin America, Southeast Asia), underdeveloped capital markets, ambiguous regulatory frameworks, and weak contract enforcement create **institutional voids**.
- **The Diversified Family Business Group (e.g. Tata, Reliance, Birla) acts as a private market:**
  - *Internal Capital Markets:* Profitable mature cash-cow subsidiaries fund risky new ventures without relying on external bank debt.
  - *Internal Talent Markets:* Rotating high-performing executives across group companies.
  - *Reputational Umbrella:* High consumer trust in the group's flagship brand reduces transaction costs across all business verticals.
"""

# ==============================================================================
# COURSE 3: DATA VISUALISATION FOR BUSINESS DECISIONS (deb83564)
# ==============================================================================

def get_data_viz_one_shot_notes() -> str:
    return """# Data Visualisation for Business Decisions: 3-Module Master Revision Notes

> **Exam Revision Strategy:** Hyper-condensed, high-yield cram notes covering visual encoding hierarchies, dashboard architecture, Gestalt perception laws, chart selection decision trees, and Power BI DAX modeling.

---

## Module 1: Understanding Business Data Visualisation & Visual Perception

### 1. The Core Purpose of Business Visualisation
- **Cognitive Offloading:** Visual representations shift the heavy computational burden from working memory (System 2) to the pre-attentive visual cortex (System 1), enabling instant pattern discovery.
- **Exploratory vs Explanatory Visualisation:**
  - *Exploratory:* Digging into unstructured data to uncover unknown correlations, anomalies, and outliers (internal data science).
  - *Explanatory:* Communicating a clear, pre-determined strategic insight to executive decision-makers to drive action.

---

### 2. Cleveland & McGill's Hierarchy of Visual Encodings
Ranked from **Most Accurate** (easiest for human eye to quantitatively compare) to **Least Accurate**:
1. **Position along a common scale:** (Bar charts, Scatter plots) — *Most accurate!*
2. **Position along non-aligned scales:** (Small multiples, multi-panel charts)
3. **Length:** (Standard bar / column charts)
4. **Direction / Slope:** (Line charts, slope charts)
5. **Angle:** (Pie charts, donut charts) — *Poor accuracy; humans misjudge angles!*
6. **Area:** (Bubble charts, treemaps) — *Humans consistently underestimate area differences!*
7. **Volume:** (3D spheres, 3D bars) — *Extreme cognitive distortion; banned in business analytics.*
8. **Color Saturation & Color Hue:** (Heatmaps) — *Good for categorical distinction, terrible for exact quantitative precision.*

---

### 3. Gestalt Principles in Dashboard Design
- **Proximity:** Objects placed close to one another are perceived as belonging to a single group.
- **Similarity:** Objects sharing color, shape, or size are perceived as functionally related.
- **Enclosure:** Drawing a border or shading a background box binds elements together into a conceptual unit.
- **Continuity:** The eye naturally follows smooth paths and lines rather than abrupt angle changes.
- **Connection:** Elements physically linked by a line are perceived as having a direct causal relationship.

---

### 4. Edward Tufte's Design Principles
- **Data-to-Ink Ratio:**
  $$\\text{Data-to-Ink Ratio} = \\frac{\\text{Ink dedicated to displaying data}}{\\text{Total ink used in graphic}}$$
  *Goal:* Maximize the ratio! Remove redundant 3D bevels, heavy background grids, decorative borders, and gradient shadows ("chartjunk").
- **Lie Factor Formula:**
  $$\\text{Lie Factor} = \\frac{\\text{Size of effect shown in graphic}}{\\text{Size of effect in underlying data}}$$
  *If Lie Factor $\\ne 1.0$, the chart is visually distorting reality.* Truncating the Y-axis to 0 on a bar chart artificially exaggerates minor differences!

---

### 5. Chart Selection Decision Matrix

| Analytical Objective | Primary Recommended Chart | Anti-Pattern (What to Avoid) |
| :--- | :--- | :--- |
| **Comparison across categories** | Horizontal Bar Chart or Column Chart | Pie Chart with $>3$ slices |
| **Trends over time** | Continuous Line Chart or Area Chart | Discrete Bar Chart with too many bars |
| **Part-to-whole breakdown** | 100% Stacked Bar or Waterfall Chart | 3D Pie Chart / Exploding Donut |
| **Correlation between 2 metrics** | Scatter Plot (with trendline) | Dual-Axis Line Chart (misleading scales) |
| **Hierarchical data distribution** | Treemap or Sunburst | Nested multi-level pie charts |
| **Geospatial variation** | Choropleth map (shaded by rate, not total) | Bubble map with overlapping opaque dots |

---

## Module 2: Designing Effective Business Dashboards

### 1. Dashboard Typology & User Segments
- **Strategic Dashboards (C-Suite / Executives):** High-level bird's-eye view; tracks core corporate KPIs against strategic targets; updated monthly/quarterly; minimal interactive filters.
- **Tactical Dashboards (Department Managers):** Monitors department performance, project milestones, resource allocation, and budget variance; updated weekly/daily.
- **Operational Dashboards (Frontline Staff):** Real-time monitoring of operational workflows, machine uptime, customer support queues; alerts and real-time triggers.

---

### 2. Dashboard Layout Architecture: The "Trend E" & F-Pattern
- **The 5-Second Rule:** A user must comprehend the overall health of the business within 5 seconds of glancing at the dashboard.
- **Z-Pattern / F-Pattern Reading Flow:**
  - *Top-Left Quadrant (Prime Real Estate):* Critical high-level KPIs, single-value cards with status indicators.
  - *Top-Right & Center:* Main trend over time (line charts) and primary categorical driver (bar charts).
  - *Bottom Half:* Diagnostic drill-downs, exception lists, and detailed transaction tables.

---

## Module 3: Building Visualisations with Power BI & Data Modeling

### 1. Data Modeling Architecture: Star Schema vs Snowflake Schema
- **Fact Table:** Central table storing quantitative numerical metrics (e.g. Sales Amount, Quantity, Revenue, Margin) with foreign keys. Large volume, narrow width.
- **Dimension Tables:** Surrounding tables storing descriptive context attributes (e.g. Customer, Date, Store, Product). Low volume, wide width.
- **Star Schema:** Dimensions are fully de-normalized; direct 1-to-many relationships to the fact table. *Best practice in Power BI for query performance and simpler DAX!*
- **Snowflake Schema:** Dimensions are normalized into sub-dimension tables. Increases join complexity and degrades report rendering speed.

---

### 2. Power BI DAX: Calculated Columns vs Measures

| Characteristic | Calculated Column | Measure (DAX) |
| :--- | :--- | :--- |
| **Evaluation Timing** | Computed during data refresh (Static) | Evaluated dynamically on the fly during user interaction |
| **Storage & RAM** | Stored in RAM / file memory (consumes space) | Consumes zero persistent memory; computed in CPU cache |
| **Evaluation Context** | **Row Context:** Evaluates row by row across table | **Filter Context:** Evaluates aggregated data based on slicers |
| **Appropriate Use** | Slicers, categories, matrix rows, age brackets | Totals, ratios, margins, year-over-year variances |

---

### 3. The `CALCULATE()` Engine in DAX
- `CALCULATE(<expression>, <filter1>, <filter2>...)` is the single most powerful function in DAX.
- **What it does:** Evaluates an expression while overriding, clearing, or modifying the existing visual filter context.
- **Example Pattern (Sales YoY Growth):**
  ```dax
  Sales LY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
  Sales YoY Growth = DIVIDE([Total Sales] - [Sales LY], [Sales LY], 0)
  ```
"""

# ==============================================================================
# COURSE 4: CRITICAL THINKING (d9173426)
# ==============================================================================

def get_critical_thinking_one_shot_notes() -> str:
    return """# Critical Thinking: 7-Module Master Revision Notes

> **Exam Revision Strategy:** High-yield conceptual review covering argumentation anatomy, deductive and inductive logic, informal fallacies, cognitive biases, the Toulmin model, and organizational de-biasing techniques.

---

## Module 1: Foundations of Critical Thinking & Epistemology

### 1. Truth, Validity, and Soundness
- **Deductive Argument:** An argument where the premises claim to guarantee the truth of the conclusion.
  - **Validity:** An argument is *valid* if and only if it takes a logical form that makes it impossible for the premises to be true and the conclusion nevertheless to be false.
  - **Soundness:** An argument is *sound* if and only if it is **valid AND all its premises are factually true**.
  - *Key Distinction:* An argument can be completely valid while being factually unsound!
- **Inductive Argument:** Premises provide probabilistic support, not absolute certainty. Evaluated as *Strong vs Weak* and *Cogent vs Uncogent*.

---

## Module 2: Argument Structure & Critical Reading

### 1. The Anatomy of an Argument
- **Claim / Conclusion:** The central assertion that the speaker wants you to accept.
- **Premises:** The factual claims or evidence advanced to support the conclusion.
- **Hidden / Unstated Assumptions:** Implicit beliefs that must be true for the argument to hold. Critical thinking primarily consists of surfacing and interrogating hidden assumptions!
- **Distinguishing Non-Arguments:**
  - *Explanations:* Account for *why* an already accepted fact occurred; they do not attempt to prove *that* it occurred.
  - *Assertions / Opinions:* Mere statements of belief without supporting evidence.

---

## Module 3: Constructing & Evaluating Arguments: The Toulmin Model

### 1. Stephen Toulmin's Model of Argumentation
Real-world arguments rarely fit simple syllogisms. The Toulmin Model provides a 6-part framework:
1. **Claim:** The final conclusion or viewpoint being advocated.
2. **Data / Grounds:** The observable facts, empirical evidence, or data.
3. **Warrant:** The underlying reasoning or principle that justifies connecting the Data to the Claim.
4. **Backing:** Additional evidence or authority that validates the Warrant.
5. **Qualifier:** The scope or degree of certainty (e.g. "presumably", "in most cases", "under standard conditions").
6. **Rebuttal / Exception:** Counter-conditions or circumstances where the warrant fails.

---

## Module 4: Logical Fallacies & Cognitive Biases

### 1. Formal Fallacies (Structural Errors)
- **Affirming the Consequent:** If $P \\implies Q$, and $Q$ is observed $\\implies$ falsely concluding $P$ is true. *(e.g. If it rains, the grass is wet. The grass is wet, therefore it rained. False: sprinkler could cause it).*
- **Denying the Antecedent:** If $P \\implies Q$, and not-$P$ $\\implies$ falsely concluding not-$Q$.

---

### 2. Major Informal Fallacies

| Fallacy Name | Mechanism / Trap | Real-World Business Example |
| :--- | :--- | :--- |
| **Ad Hominem** | Attacking the person's character, motive, or background instead of their argument | "We should reject Sarah's financial model because she joined from marketing." |
| **Straw Man** | Distorting or caricaturing an opponent's position to make it easy to knock down | "They want to build a safety net, which means they want complete corporate communism." |
| **Post Hoc Ergo Propter Hoc** | Assuming that because event B followed event A, A caused B | "We launched the new logo in June and sales rose in July; the logo drove sales." |
| **False Dilemma (Black/White)** | Forcing a complex scenario into only two extreme choices | "Either we cut R&D spending by 50% or the company goes bankrupt tomorrow." |
| **Begging the Question** | Circular reasoning; premise presupposes the truth of the conclusion | "Our enterprise software is the market leader because it outperforms all competitors." |
| **Sunk Cost Fallacy** | Continuing an unprofitable project because of non-recoverable past investments | "We already spent ₹10 crore on this failed ERP software, so we must invest another ₹5 crore." |

---

### 3. Cognitive Biases & Dual-Process Theory (Kahneman & Tversky)
- **System 1 (Intuitive):** Fast, automatic, effortless, emotional, prone to systematic cognitive illusions.
- **System 2 (Deliberative):** Slow, analytical, effortful, logical, computationally expensive.
- **Core Heuristics:**
  - *Availability Heuristic:* Estimating probability based on how easily vivid instances come to mind.
  - *Anchoring & Adjustment:* Over-relying on the first number presented when estimating value.
  - *Confirmation Bias:* Actively seeking data that supports preexisting beliefs while ignoring disconfirming facts.

---

## Modules 5–7: Expertise, Cultural Nuance & Strategic De-Biasing

### 1. Organizational De-Biasing Techniques
- **Red Teaming:** Designating an adversarial internal team whose sole mandate is to construct a rigorous attack plan against a proposed strategic initiative.
- **Devil's Advocacy:** Formally assigning a senior executive to challenge prevailing boardroom consensus to eliminate Groupthink.
- **Pre-Mortem Analysis (Gary Klein):** Before launching a project, assemble the team and say: *"Imagine we are 2 years in the future and this project has failed catastrophically. Write a 1-page report explaining exactly how and why it failed."* Surfacing hidden risks before capital is committed.
"""

# ==============================================================================
# COURSE 5: STARTUP DILEMMAS: FOUNDING OR JOINING (a846c0e5)
# ==============================================================================

def get_startup_dilemmas_one_shot_notes() -> str:
    return """# Startup Dilemmas: Founding or Joining: 4-Module Master Revision Notes

> **Exam Revision Strategy:** High-yield executive summary covering Noam Wasserman's founder dilemmas, co-founder dynamics, the 3 Rs, equity splitting frameworks, vesting cliffs, and startup offer evaluation.

---

## Module 1: Founding vs Joining & The Foundational Dilemma

### 1. Noam Wasserman's Founder's Dilemma: "Rich vs King"
Every entrepreneur faces an inescapable trade-off between **Wealth Maximization (Rich)** and **Autonomy / Decision Control (King)**:
- **The "King" Strategy:**
  - *Objective:* Retain absolute voting control, CEO title, and unilateral decision-making power.
  - *Trade-off:* Avoids taking external venture capital; relies on bootstrapping.
  - *Outcome:* Founder owns a massive slice (80–100%) of a small, resource-constrained pie.
- **The "Rich" Strategy:**
  - *Objective:* Maximize total enterprise valuation and personal financial payout.
  - *Trade-off:* Sells substantial equity to venture capitalists; yields board seats; accepts potential replacement as CEO.
  - *Outcome:* Founder owns a smaller slice (10–25%) of a gigantic, well-capitalized multi-billion dollar pie.
- *The Invariant Rule:* You can rarely have both! Founders who try to be both King and Rich end up with neither.

---

### 2. Career Capital & Founder Readiness
- **The Youth Advantage:** High energy, low opportunity cost, unencumbered by family obligations, blank-slate cognitive flexibility.
- **The Experience Advantage:** Deep domain knowledge, established executive network, customer empathy, management credibility.
- **Founding Readiness Audit:** Launching a startup requires three pillars:
  1. *Human Capital:* Technical, domain, or operational mastery.
  2. *Social Capital:* Network of talent, early customers, and angel capital.
  3. *Financial Runway:* Personal savings to survive 12–24 months without a corporate paycheck.

---

## Module 2: Co-Founder Dynamics & The 3 Rs Framework

### 1. Solo vs Team Foundings
- Empirical data reveals startups with 2–3 co-founders raise significantly more capital, build products faster, and scale larger than solo founders.
- **The Homophily Trap (Danger of Founding with Clones):**
  - Founders naturally gravitate toward people similar to themselves (college friends, same engineering background).
  - *Consequence:* Duplicate skills, overlapping operational desires, shared cognitive blind spots, and catastrophic lack of business/sales competence.
  - *Rule:* Teams must be built on **cognitive diversity and functional complementarity** (e.g., Hacker + Hustler).

---

### 2. The 3 Rs Framework
Co-founder agreements must systematically resolve:
- **Relationships:** Previous personal history vs professional boundaries.
- **Roles:** Clear operational boundaries, decision-making hierarchy, and designated final tie-breaker.
- **Rewards:** Splitting equity, founder compensation, and recognition.

---

### 3. Equity Splitting: The 50/50 Static Split Disaster
- **The Equal Split Trap:** Splitting equity 50/50 on day one without vesting is the single most common cause of early-stage corporate death.
- **Why Static Splits Fail:** Co-founder contributions, dedication, and life circumstances diverge dramatically over time. If a 50% co-founder quits after 6 months, they walk away with half the company's equity ("dead cap table"), making the firm uninvestable.
- **Mandatory Protections:**
  - **4-Year Time Vesting with a 1-Year Cliff:** No equity is earned for the first 12 months. At month 12, 25% vests; the remaining 75% vests monthly over the next 36 months.
  - **Section 83(b) Tax Election:** Filing within 30 days of stock grant to avoid crippling tax liabilities on unvested shares as valuation grows.

---

## Module 3: Evaluating Startups to Join

### 1. Assessing Startup Health from the Outside
Before joining an early-stage venture, analyze three vital signs:
1. **Net Runway & Burn Multiple:**
   $$\\text{Burn Multiple} = \\frac{\\text{Net Burn (Cash Spent)}}{\\text{Net New ARR (Revenue Added)}}$$
   *(A burn multiple $>2.0$ indicates inefficient growth; $<1.0$ is elite).*
2. **Gross Margin Health:** Differentiate between true high-margin software ($80\\%+$) and low-margin services or logistics ($15–30\\%$) masquerading as tech.
3. **Cap Table Dilution Trajectory:** Check how much equity the founders retain. If founders own $<30\\%$ by Series A, their long-term motivation is severely compromised.

---

### 2. Psychological Safety vs Accountability (Amy Edmondson)
- Startups operate in extreme uncertainty. The optimal workplace culture sits in the **Learning Zone**:
  - *High Psychological Safety + High Accountability:* Teams admit mistakes early, experiment fearlessly, and execute relentlessly.
  - *Low Psychological Safety + High Accountability (Anxiety Zone):* Toxic fear; employees hide bugs and flatter founders until catastrophe strikes.

---

## Module 4: Evaluating Startup Job Offers & Equity Packages

### 1. Deconstructing Startup Compensation
A candidate must evaluate the total package across three components:
- **Base Salary:** Discounted vs market rate (the "startup discount").
- **Stock Options (ESOP):** Incentive Stock Options (ISO) vs Non-Qualified Stock Options (NSO).
  - *Spread Value:* Market Price of Share - Strike Price (Exercise Price).
- **Dilution Expectations:** A 1.0% grant today will dilute to ~0.5% after subsequent Series B, C, and D funding rounds.

---

### 2. The Liquidation Preference Overhang
- Venture capital term sheets almost always carry **Liquidation Preferences**:
  - *1x Non-Participating Preferred:* Investors get their capital back first before common shareholders receive anything.
  - *Participating Preferred ("Double Dipping"):* Investors receive their initial investment back AND share pro-rata in the remaining proceeds.
- **The Common Stock Reality:** In a mediocre acquisition (e.g. company sells for ₹100M after raising ₹100M with 1x liquidation preference), **the common stockholders (employees) receive ZERO**, even if their options were "vested"!
"""

def run():
    print("Connecting to database...")
    conn = db.get_conn()

    courses = [
        ("2989cdfe", "Corporate Finance", get_corporate_finance_one_shot_notes(), get_corporate_finance_formula_sheet()),
        ("db945ff9", "Family Business Strategy", get_family_business_one_shot_notes(), ""),
        ("deb83564", "Data Visualisation for Business Decisions", get_data_viz_one_shot_notes(), ""),
        ("d9173426", "Critical Thinking", get_critical_thinking_one_shot_notes(), ""),
        ("a846c0e5", "Startup Dilemmas: Founding or Joining", get_startup_dilemmas_one_shot_notes(), "")
    ]

    for cid, cname, notes_md, formula_md in courses:
        print(f"\nProcessing {cname} ({cid})...")
        db.save_course_one_shot(cid, notes_md, formula_md)
        print(f"  Saved intelligent one-shot: Notes={len(notes_md)} chars, Formula Sheet={len(formula_md)} chars")

    print("\nExporting static data to study_data.js...")
    db.export_static_data()
    print("All 5 subjects successfully compiled into intelligent, curated one-shot master review sheets!")

if __name__ == "__main__":
    run()
