#!/usr/bin/env python3
"""
Master One-Shot Revision Notes & Corporate Finance Formula Sheet Generator.
Compiles hyper-condensed, exam-optimized one-shot review sheets for all 5 subjects
and the master formula sheet + variable index for Corporate Finance.
"""

import sys
import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import db

def build_corporate_finance_formula_sheet() -> str:
    # Exhaustive formula sheet with complete variable index
    return """# Corporate Finance: Master Formula Sheet & Comprehensive Variable Index

> **Exam Revision Purpose:** This formula sheet covers all mathematical models across Modules 1 through 8. Every single symbol, variable, and subscript is defined in the index with units, boundary conditions, and common calculation traps.

---

## 1. Alphabetical Variable Legend & Symbol Index

| Symbol | Mathematical & Economic Meaning | Standard Unit | Key Constraints / Boundaries | Common Exam Pitfalls & Traps |
| :--- | :--- | :--- | :--- | :--- |
| $PV$ | **Present Value:** Discounted value today of future cash flows | Currency ($ / ₹) | $PV \\le FV$ when discount rate $r > 0$ | Discounting with wrong periodic rate or incorrect exponent $t$. |
| $FV$ | **Future Value:** Compounded value at horizon date $t$ | Currency ($ / ₹) | $FV = PV(1+r)^t$ | Confusing simple interest with compounding interest. |
| $C$ or $CF_t$ | **Cash Flow:** Periodic payment or net inflow at time $t$ | Currency ($ / ₹) | Constant for annuities; variable for projects | Missing period 0 initial cash outlay ($I_0$). |
| $r$ | **Discount Rate / Required Return / Cost of Capital** | % per annum or period | Decimal in formulas (e.g. 10% = $0.10$) | Using annual $r$ when compounding is semi-annual or monthly. |
| $t$ or $n$ | **Number of Periods / Time Horizon** | Years or compounding periods | Must match periodicity of rate $r$ | Forgetting to multiply years by $m$ (e.g., 5 years semi-annual = 10 periods). |
| $m$ | **Compounding Frequency per Year** | Periods per year | $m=1$ (annual), $m=2$ (semi), $m=12$ (monthly) | Omitting $m$ in exponent when computing $EAR$. |
| $EAR$ | **Effective Annual Rate:** True annualized interest earned | % per annum | $EAR \\ge APR$; $EAR = (1 + APR/m)^m - 1$ | Using nominal $APR$ directly in multi-year $PV$ formulas. |
| $APR$ | **Annual Percentage Rate:** Quoted nominal interest rate | % per annum | Quoted rate without inter-year compounding | Assuming $APR = EAR$; valid only when $m = 1$. |
| $g$ | **Constant Growth Rate:** Perpetual dividend/cash flow growth | % per annum | **Strictly $r > g$**; if $g \\ge r$, model breaks | Using $g$ larger than overall GDP growth or greater than discount rate $r$. |
| $D_0$ | **Current Dividend:** Most recently paid historical dividend | Currency per share | Paid in past ($t=0$); not discounted directly | Plugging $D_0$ into numerator instead of expected $D_1 = D_0(1+g)$. |
| $D_1$ | **Expected Dividend:** Dividend to be received at end of year 1 | Currency per share | $D_1 = D_0(1+g)$ | Confusing "just paid dividend" ($D_0$) with "next dividend" ($D_1$). |
| $P_0$ | **Current Stock / Bond Price:** Intrinsic market price at $t=0$ | Currency per share / bond | $P_0 = PV(\\text{Future Cash Inflows})$ | Comparing clean price with dirty price without adding accrued interest. |
| $F$ | **Face Value (Par Value) of Bond** | Currency (usually $1,000) | Constant principal repaid at maturity $T$ | Forgetting that face value is repaid at end alongside last coupon. |
| $y$ or $YTM$ | **Yield to Maturity:** Internal rate of return of a bond | % per annum | Rate where $PV(\\text{coupons} + \\text{face value}) = P_0$ | Halving annual $YTM$ for semi-annual bonds but forgetting to double periodic $y$ back to annual. |
| $b$ | **Retention Ratio (Plowback Ratio)** | Unitless ratio ($0$ to $1$) | $b = 1 - \\text{Dividend Payout Ratio}$ | Subtracting $b$ from 100 instead of 1.0 when expressed as a decimal. |
| $ROE$ | **Return on Equity:** Net Income / Total Equity | % per annum | Drives sustainable growth rate $g = b \\times ROE$ | Using total assets instead of shareholder equity in denominator. |
| $NPV$ | **Net Present Value:** Incremental wealth created by project | Currency ($ / ₹) | **Decision Rule:** Accept project if $NPV > 0$ | Forgetting to subtract initial investment $I_0$ at time 0. |
| $IRR$ | **Internal Rate of Return:** Discount rate that yields $NPV = 0$ | % per annum | Accept if $IRR > r$; fails for non-normal cash flows | Relying on $IRR$ over $NPV$ for mutually exclusive projects of different sizes. |
| $PI$ | **Profitability Index:** Ratio of $PV$ of inflows to initial outlay | Unitless ratio | $PI = PV(\\text{Inflows}) / I_0 = 1 + (NPV / I_0)$ | Choosing projects by highest $PI$ without checking total capital constraint. |
| $E(R)$ | **Expected Return of Asset or Portfolio** | % per annum | Probability-weighted average return | Failing to verify that portfolio weights $\\sum w_i = 1.0$. |
| $\\sigma$ | **Standard Deviation:** Total volatility / total risk | % per annum | $\\sigma = \\sqrt{\\text{Variance}}$; $\\sigma \\ge 0$ | Assuming portfolio risk is simply the weighted average of individual standard deviations. |
| $\\rho_{ij}$ | **Correlation Coefficient:** Co-movement between two assets | Unitless ratio | **Strict Range:** $-1.0 \\le \\rho_{ij} \\le +1.0$ | Believing diversification benefits require $\\rho < 0$; any $\\rho < 1.0$ diversifies risk. |
| $Cov(i,j)$ | **Covariance:** Unscaled directional co-movement | Variance units | $Cov(i,j) = \\rho_{ij} \\sigma_i \\sigma_j$ | Mixing up covariance with correlation coefficient. |
| $\\beta_i$ | **Beta (Systematic Risk):** Sensitivity to market movements | Unitless sensitivity | Market Beta $\\beta_m = 1.0$; Risk-free Beta $\\beta_f = 0$ | Thinking Beta measures total risk; Beta measures only non-diversifiable systematic risk. |
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

## 2. Module 1: Time Value of Money & Compounding Mechanics

### 2.1 Single Lump Sum Formulas
- **Future Value ($FV$):**
  $$FV = PV \\times (1 + r)^t$$
- **Present Value ($PV$):**
  $$PV = \\frac{FV}{(1 + r)^t} = FV \\times (1 + r)^{-t}$$
- **Simple Interest Total:**
  $$FV_{\\text{simple}} = PV \\times (1 + r \\times t)$$
- **Compounding Frequency Adjustment ($m$ times per year):**
  $$FV = PV \\times \\left(1 + \\frac{r_{\\text{nominal}}}{m}\\right)^{m \\times t}$$

### 2.2 Effective Annual Rate ($EAR$) vs Annual Percentage Rate ($APR$)
- **Effective Annual Rate Formula:**
  $$EAR = \\left(1 + \\frac{APR}{m}\\right)^m - 1$$
- **Continuous Compounding Limit ($m \\to \\infty$):**
  $$FV = PV \\times e^{r \\times t}, \\quad EAR = e^r - 1$$
- **Rule of 72 (Doubling Period Approximation):**
  $$t_{\\text{double}} \\approx \\frac{72}{r\\%}$$

---

## 3. Module 2: Annuities, Perpetuities & Loan Amortization

### 3.1 Ordinary Annuities (Cash flows at End of Period)
- **Present Value of Ordinary Annuity ($PV$):**
  $$PV = C \\times \\left[ \\frac{1 - (1 + r)^{-t}}{r} \\right]$$
- **Future Value of Ordinary Annuity ($FV$):**
  $$FV = C \\times \\left[ \\frac{(1 + r)^t - 1}{r} \\right]$$

### 3.2 Annuity Due (Cash flows at Beginning of Period)
- **Relationship Rule:** Multiply ordinary annuity value by $(1 + r)$:
  $$PV_{\\text{due}} = PV_{\\text{ordinary}} \\times (1 + r)$$
  $$FV_{\\text{due}} = FV_{\\text{ordinary}} \\times (1 + r)$$

### 3.3 Perpetuities
- **Constant Perpetuity:**
  $$PV = \\frac{C}{r}$$
- **Growing Perpetuity (Constant growth rate $g$, where $r > g$):**
  $$PV = \\frac{C_1}{r - g}$$
  *Note:* $C_1 = C_0 \\times (1 + g)$. If current payment $C_0$ is given, advance it by one period.
- **Growing Annuity ($t$ periods, $r \\ne g$):**
  $$PV = \\frac{C_1}{r - g} \\left[ 1 - \\left(\\frac{1 + g}{1 + r}\\right)^t \\right]$$

### 3.4 Loan Amortization Mechanics
- **Equated Periodic Payment ($PMT$):**
  $$PMT = \\frac{PV \\times r}{1 - (1 + r)^{-t}}$$
- **Periodic Interest Component ($I_t$):**
  $$I_t = \\text{Beginning Principal Balance}_t \\times r$$
- **Periodic Principal Repayment Component ($PR_t$):**
  $$PR_t = PMT - I_t$$
- **Ending Principal Balance:**
  $$\\text{Ending Balance}_t = \\text{Beginning Balance}_t - PR_t$$

---

## 4. Module 3: Fixed Income (Bonds) & Equity (Stocks) Valuation

### 4.1 Bond Valuation Formulas
- **Standard Bond Pricing Equation:**
  $$P_0 = \\sum_{t=1}^T \\frac{C}{(1 + y)^t} + \\frac{F}{(1 + y)^T} = C \\times \\left[ \\frac{1 - (1 + y)^{-T}}{y} \\right] + \\frac{F}{(1 + y)^T}$$
- **Semi-Annual Coupon Adjustment:**
  $$C_{\\text{semi}} = \\frac{C_{\\text{annual}}}{2}, \\quad y_{\\text{semi}} = \\frac{YTM}{2}, \\quad n = 2 \\times T$$
  $$P_0 = \\frac{C}{2} \\times \\left[ \\frac{1 - (1 + y/2)^{-2T}}{y/2} \\right] + \\frac{F}{(1 + y/2)^{-2T}}$$
- **Current Yield ($CY$):**
  $$CY = \\frac{\\text{Annual Coupon Payment}}{P_0} = \\frac{C}{P_0}$$
- **Clean Price vs Dirty Price:**
  $$\\text{Dirty Price} = \\text{Clean Price} + \\text{Accrued Interest}$$
  $$\\text{Accrued Interest} = C \\times \\left( \\frac{\\text{Days since last coupon payment}}{\\text{Total days in coupon period}} \\right)$$
- **Zero-Coupon Bond Pricing:**
  $$P_0 = \\frac{F}{(1 + y)^T}$$

### 4.2 Common Stock Valuation
- **Zero-Growth Dividend Model:**
  $$P_0 = \\frac{D}{r}$$
- **Constant Growth Model (Gordon Growth Model):**
  $$P_0 = \\frac{D_1}{r - g} = \\frac{D_0 \\times (1 + g)}{r - g} \\quad (r > g)$$
- **Implied Expected Return on Stock:**
  $$r = \\frac{D_1}{P_0} + g = \\text{Dividend Yield} + \\text{Capital Gains Yield}$$
- **Sustainable Growth Rate Formula:**
  $$g = b \\times ROE = (1 - \\text{Dividend Payout Ratio}) \\times ROE$$
- **Two-Stage (Non-Constant) Dividend Growth Model:**
  $$P_0 = \\sum_{t=1}^N \\frac{D_t}{(1 + r)^t} + \\frac{P_N}{(1 + r)^N}, \\quad \\text{where } P_N = \\frac{D_{N+1}}{r - g_{\\text{stable}}}$$
- **Price-Earnings Multiple Valuation:**
  $$\\frac{P_0}{E_1} = \\frac{1 - b}{r - g}$$

---

## 5. Module 4: Capital Budgeting & Investment Decision Criteria

### 5.1 Net Present Value ($NPV$)
$$NPV = \\sum_{t=1}^n \\frac{CF_t}{(1 + r)^t} - I_0$$
- **Decision Rule:** Accept if $NPV > 0$. If comparing mutually exclusive projects, select the highest positive $NPV$.

### 5.2 Internal Rate of Return ($IRR$)
$$0 = \\sum_{t=1}^n \\frac{CF_t}{(1 + IRR)^t} - I_0$$
- **Decision Rule:** Accept if $IRR > \\text{Hurdle Rate } r$.
- **Limitations:** Multiple $IRRs$ if cash flows change signs more than once; scale problem on mutually exclusive projects.

### 5.3 Profitability Index ($PI$)
$$PI = \\frac{PV(\\text{Future Cash Inflows})}{I_0} = \\frac{\\sum_{t=1}^n \\frac{CF_t}{(1 + r)^t}}{I_0} = 1 + \\frac{NPV}{I_0}$$
- **Decision Rule:** Accept if $PI > 1.0$.

### 5.4 Payback & Discounted Payback Period
$$\\text{Payback Period} = A + \\frac{B}{C}$$
- Where $A$ = Last full period with negative cumulative cash flow.
- $B$ = Absolute unrecovered cost at the start of period $A+1$.
- $C$ = Total cash flow received in period $A+1$.
- **Discounted Payback:** Same formula, but replacing nominal cash flows with discounted cash flows $\\frac{CF_t}{(1+r)^t}$.

### 5.5 Equivalent Annual Annuity ($EAA$) — Unequal Life Projects
$$EAA = \\frac{NPV}{\\text{PVIFA}_{r, t}} = \\frac{NPV \\times r}{1 - (1 + r)^{-t}}$$

---

## 6. Module 5: Risk, Return & Portfolio Theory

### 6.1 Individual Asset Risk & Return
- **Expected Return ($E(R)$):**
  $$E(R) = \\sum_{i=1}^k p_i R_i$$
- **Variance ($\\sigma^2$) and Standard Deviation ($\\sigma$):**
  $$\\sigma^2 = \\sum_{i=1}^k p_i [R_i - E(R)]^2, \\quad \\sigma = \\sqrt{\\sigma^2}$$

### 6.2 Two-Asset Portfolio Mathematics
- **Portfolio Expected Return ($E(R_p)$):**
  $$E(R_p) = w_1 E(R_1) + w_2 E(R_2), \\quad \\text{where } w_1 + w_2 = 1$$
- **Portfolio Variance ($\\sigma_p^2$):**
  $$\\sigma_p^2 = w_1^2 \\sigma_1^2 + w_2^2 \\sigma_2^2 + 2 w_1 w_2 Cov(R_1, R_2)$$
  $$\\sigma_p^2 = w_1^2 \\sigma_1^2 + w_2^2 \\sigma_2^2 + 2 w_1 w_2 \\rho_{12} \\sigma_1 \\sigma_2$$
- **Covariance and Correlation Link:**
  $$Cov(R_1, R_2) = \\rho_{12} \\sigma_1 \\sigma_2, \\quad \\rho_{12} = \\frac{Cov(R_1, R_2)}{\\sigma_1 \\sigma_2}$$

### 6.3 Systematic Risk (Beta $\\beta$)
- **Beta of Asset $i$:**
  $$\\beta_i = \\frac{Cov(R_i, R_m)}{\\sigma_m^2} = \\rho_{im} \\times \\frac{\\sigma_i}{\\sigma_m}$$
- **Portfolio Beta:**
  $$\\beta_p = \\sum_{i=1}^N w_i \\beta_i$$

---

## 7. Module 6: Capital Asset Pricing Model & Corporate Payouts

### 7.1 Capital Asset Pricing Model (CAPM)
$$E(R_i) = R_f + \\beta_i [E(R_m) - R_f]$$
- **Market Risk Premium ($MRP$):**
  $$MRP = E(R_m) - R_f$$
- **Jensen's Alpha (Abnormal Performance):**
  $$\\alpha_i = R_{i, \\text{actual}} - \\left( R_f + \\beta_i [R_m - R_f] \\right)$$

### 7.2 Portfolio Performance Metrics
- **Sharpe Ratio (Total Risk Reward):**
  $$\\text{Sharpe Ratio} = \\frac{E(R_p) - R_f}{\\sigma_p}$$
- **Treynor Ratio (Systematic Risk Reward):**
  $$\\text{Treynor Ratio} = \\frac{E(R_p) - R_f}{\\beta_p}$$

### 7.3 Corporate Payout Mechanics
- **Dividend Yield ($DY$):**
  $$DY = \\frac{D_1}{P_0}$$
- **Dividend Payout Ratio ($PR$):**
  $$PR = \\frac{\\text{Total Dividends Paid}}{\\text{Net Income}}$$
- **Share Repurchase Post-Price (Neutral Market):**
  $$P_{\\text{post}} = \\frac{\\text{Equity Value} - \\text{Cash Spent on Repurchase}}{\\text{Initial Shares} - \\text{Shares Repurchased}} = P_{\\text{pre}}$$

---

## 8. Module 7: Cost of Capital & WACC

### 8.1 Component Costs of Capital
- **Cost of Equity ($r_e$):**
  $$\\text{Via CAPM: } r_e = R_f + \\beta_e [E(R_m) - R_f]$$
  $$\\text{Via DDM: } r_e = \\frac{D_1}{P_0} + g$$
- **After-Tax Cost of Debt ($r_d$):**
  $$r_{d, \\text{after-tax}} = r_d \\times (1 - T_c)$$
- **Cost of Preferred Stock ($r_p$):**
  $$r_p = \\frac{D_p}{P_p}$$

### 8.2 Weighted Average Cost of Capital (WACC)
$$WACC = \\left(\\frac{E}{V}\\right) r_e + \\left(\\frac{D}{V}\\right) r_d (1 - T_c) + \\left(\\frac{P}{V}\\right) r_p$$
- **Capital Weights Constraint:**
  $$V = E + D + P, \\quad \\frac{E}{V} + \\frac{D}{V} + \\frac{P}{V} = 1.0$$
  *Always calculate weights using market values ($E = \\text{Shares} \\times \\text{Price}$), never accounting book values.*

---

## 9. Module 8: Capital Structure, MM Propositions & M&A Decisions

### 9.1 Modigliani-Miller Theorem (No Taxes)
- **Proposition I (Value Invariance):**
  $$V_L = V_U$$
- **Proposition II (Cost of Equity Leverage Penalty):**
  $$r_e = r_0 + \\frac{D}{E}(r_0 - r_d)$$
  Where $r_0$ is the cost of capital for an all-equity firm.

### 9.2 Modigliani-Miller Theorem (With Corporate Taxes $T_c$)
- **Proposition I (Debt Creates Value via Interest Tax Shield):**
  $$V_L = V_U + T_c D$$
- **Present Value of Interest Tax Shield ($ITS$ for Perpetual Debt):**
  $$PV(ITS) = T_c \\times D$$
- **Proposition II (Cost of Equity with Tax Shield Relief):**
  $$r_e = r_0 + \\frac{D}{E}(r_0 - r_d)(1 - T_c)$$

### 9.3 Hamada Equation (Unlevering & Re-levering Beta)
- **Unlevering Beta (Finding Business Risk $\\beta_U$):**
  $$\\beta_U = \\frac{\\beta_L}{1 + (1 - T_c)\\left(\\frac{D}{E}\\right)}$$
- **Re-levering Beta (Target Debt-to-Equity Ratio):**
  $$\\beta_L = \\beta_U \\left[ 1 + (1 - T_c)\\left(\\frac{D}{E}\\right) \\right]$$

### 9.4 Mergers & Acquisitions (M&A) Valuation
- **Total Combined Enterprise Value with Synergy ($V_{AB}$):**
  $$V_{AB} = V_A + V_B + S$$
- **Net Synergy Gain ($S$):**
  $$S = \\Delta CF / r = V_{AB} - (V_A + V_B)$$
- **Net Present Value of Acquisition to Acquirer ($NPV_{M\\&A}$):**
  $$NPV_{M\\&A} = S - \\text{Premium Paid} = V_B + S - \\text{Cash Paid}$$
- **Maximum Purchase Price ($P_{\\text{max}}$):**
  $$P_{\\text{max}} = V_B + S$$
"""

def distill_topic_to_oneshot(topic_title: str, mod_num: int, video_idx: int, notes_raw: str, is_cf: bool = False) -> str:
    """
    Distills raw topic notes into a punchy, hyper-condensed one-shot format.
    Preserves formulas, worked problems, versus matrices, definitions, and gotchas.
    Omit generic filler and repetitions.
    """
    clean_title = topic_title.replace("CF ", "").strip()
    clean_title = re.sub(r"^M\d+\s*C\d+\s*", "", clean_title).strip()
    if not clean_title or clean_title.lower() == "video":
        clean_title = topic_title

    lines = [f"### Module {mod_num} Video {video_idx}: {clean_title}\n"]

    # 1. Extract Core Takeaway if present
    takeaway_match = re.search(r"> \*\*Core Takeaway:\*\*\s*(.+)", notes_raw)
    if takeaway_match:
        lines.append(f"> **Core Principle:** {takeaway_match.group(1).strip()}\n")

    # 2. Extract bullet points / definitions from main section
    # Find bullets that define terms or give key mechanics
    bullet_matches = re.findall(r"^[*-]\s+\*\*([^:]+):\*\*\s*(.+)", notes_raw, re.MULTILINE)
    if bullet_matches:
        lines.append("**Essential Definitions & Mechanics:**")
        # Keep up to 6 high-yield bullets
        count = 0
        for term, desc in bullet_matches:
            # Skip generic intro bullets
            if any(w in term.lower() for w in ["overview", "introduction", "welcome", "agenda"]):
                continue
            lines.append(f"- **{term}:** {desc.strip()}")
            count += 1
            if count >= 6:
                break
        lines.append("")

    # 3. Extract Formulas & Worked Numericals (Crucial for Corporate Finance)
    formula_section_match = re.search(r"### (?:Key )?Formulas?.*?\n([\s\S]*?)(?=###|\Z)", notes_raw, re.IGNORECASE)
    if formula_section_match:
        f_text = formula_section_match.group(1).strip()
        if f_text:
            lines.append("#### 📐 Mathematical Formula & Numerical Application")
            lines.append(f_text)
            lines.append("")

    # 4. Extract Versus / Differentiation tables if present
    table_match = re.search(r"(\|.+?\|\n\|[-:\s|]+\|\n(?:\|.+?\|\n)+)", notes_raw)
    if table_match:
        lines.append("#### ⚖️ Conceptual Matrix & Differentiation")
        lines.append(table_match.group(1).strip())
        lines.append("")

    # 5. Extract MCQ Trap Radar & Gotchas
    traps = re.findall(r"\*\*Trap:\*\*\s*(.+?)\s*→\s*\*\*Reality:\*\*\s*(.+)", notes_raw)
    if traps:
        lines.append("**⚠️ Examiner Trap Radar:**")
        for trap, reality in traps[:2]:
            lines.append(f"- **Trap:** {trap.strip()} $\\to$ **Reality:** {reality.strip()}")
        lines.append("")

    lines.append("---\n")
    return "\n".join(lines)

def generate_course_one_shot(course_id: str, course_name: str, conn) -> str:
    """
    Generates a continuous, scrollable 8-module master revision sheet for a given course.
    """
    modules = conn.execute("""
        SELECT id, number, name 
        FROM modules 
        WHERE course_id = ? 
        ORDER BY number ASC
    """, (course_id,)).fetchall()

    content = [f"# {course_name}: 8-Module Master One-Shot Revision Notes\n"]
    content.append("> **Quick-Cram Architecture:** Continuous scrollable revision sheet covering all modules video-by-video. Optimized for last-minute review 1–2 hours before exams. Filtered to definitions, formulas, distinction matrices, and gotchas.\n\n---\n")

    # Table of Contents
    content.append("## Quick Module Navigation\n")
    for m in modules:
        content.append(f"- [Module {m['number']}: {m['name']}](#module-{m['number']})")
    content.append("\n---\n")

    for m in modules:
        mod_num = m['number']
        mod_name = m['name']
        content.append(f"<a id=\"module-{mod_num}\"></a>")
        content.append(f"## Module {mod_num}: {mod_name}\n")

        topics = conn.execute("""
            SELECT id, title, notes_markdown 
            FROM topics 
            WHERE module_id = ? 
            ORDER BY rowid ASC
        """, (m['id'],)).fetchall()

        if not topics:
            content.append("*No lecture videos in this module.*\n\n---\n")
            continue

        for v_idx, t in enumerate(topics, 1):
            notes_raw = t['notes_markdown'] or ""
            topic_str = distill_topic_to_oneshot(
                t['title'], 
                mod_num, 
                v_idx, 
                notes_raw, 
                is_cf=(course_id == "2989cdfe")
            )
            content.append(topic_str)

    return "\n".join(content)

def run():
    print("Connecting to database...")
    conn = db.get_conn()

    courses = conn.execute("SELECT id, name FROM courses ORDER BY rowid ASC").fetchall()
    print(f"Found {len(courses)} courses.")

    for c in courses:
        cid = c['id']
        cname = c['name']
        print(f"\nProcessing course: {cname} ({cid})...")

        one_shot_md = generate_course_one_shot(cid, cname, conn)
        formula_sheet_md = ""

        if cid == "2989cdfe":  # Corporate Finance
            print("  Building Master Formula Sheet & Variable Index for Corporate Finance...")
            formula_sheet_md = build_corporate_finance_formula_sheet()

        db.save_course_one_shot(cid, one_shot_md, formula_sheet_md)
        print(f"  Saved one-shot for {cname} (Length: {len(one_shot_md)} chars, Formula Sheet: {len(formula_sheet_md)} chars)")

    print("\nExporting static data to study_data.js...")
    db.export_static_data()
    print("Static data exported successfully.")

if __name__ == "__main__":
    run()
