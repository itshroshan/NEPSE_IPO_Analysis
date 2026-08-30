# Quantitative Risk Modeling & Game-Theoretic Analysis of Nepal's "10-Kitta" IPO Lottery System

An end-to-end quantitative trading, game theory, and risk analysis framework built to model, simulate, and evaluate retail bidding strategies in the Nepal Stock Exchange (NEPSE) Initial Public Offering (IPO) lottery system.

---

## 1. Executive Summary & Core Motivation

In Nepal's primary equity market, oversubscribed retail IPOs are distributed via a uniform lottery in fixed 10-share lots (10 Kitta, par value NPR 1,000). To maximize win probability, retail participants deploy multi-account strategies across family Demat accounts.

This project answers three fundamental quantitative questions:

1. **Is multi-account participation positive-EV?** Does account-splitting generate net alpha after deducting bank fees ($C_{\text{ASBA}}$), annual Demat maintenance costs ($C_{\text{annual}}$), and capital lockup opportunity costs ($r$)?
2. **What is the game-theoretic equilibrium ($A^*$)?** At what total aggregate applicant threshold does market account dilution force the marginal expected value of an additional account to zero?
3. **How do we defeat the winner's curse?** Low-quality issuers offer high win probabilities on value-destroying stocks, while high-quality issuers suffer extreme dilution ($P_{\text{win}} \to 0$). Can a fundamental prestige filter ($Q$) outperform naive participation?

---

## 2. Theoretical & Mathematical Framework

### 2.1 Single-Account Expected Value ($EV_{\text{single}}$)

For an IPO issuing $S$ general-public shares ($L = S/10$ total winning lots) with aggregate applicant demand $A$, single-account win probability $P_{\text{win}}$ is:

$$P_{\text{win}} = \min\left(1, \frac{L}{A}\right)$$

Factoring in application fees ($C_{\text{ASBA}}$), prorated annual account upkeep ($C_{\text{annual}} / M$ across $M$ annual issues), and opportunity costs ($K \cdot r \cdot \frac{t}{365}$), net single-account expected value is:

$$EV_{\text{single}} = P_{\text{win}} \cdot \left( K \cdot R_{\text{listing}} \right) - C_{\text{ASBA}} - \left(\frac{C_{\text{annual}}}{M}\right) - \left( K \cdot r \cdot \frac{t}{365} \right)$$

Where $K = \text{NPR } 1,000$, $R_{\text{listing}} = \frac{P_{\text{listing}} - P_{\text{issue}}}{P_{\text{issue}}}$, $r$ is the annual risk-free rate, and $t$ is lockup duration in days.

### 2.2 Multi-Account Portfolio Dynamics & Scaling

For an investor deploying $n$ distinct family accounts, allocation outcomes follow a binomial distribution $X \sim \text{Binomial}(n, P_{\text{win}})$. Assuming $n \ll A$, expected return scales linearly:

$$EV(n) = n \cdot EV_{\text{single}}$$

### 2.3 Critical Market Demand Nash Equilibrium ($A^*$)

Setting $EV_{\text{single}} = 0$ yields the aggregate applicant threshold $A^*$ past which retail lottery participation becomes unviable:

$$A^* = \frac{L \cdot \left( K \cdot R_{\text{listing}} \right)}{C_{\text{ASBA}} + \left(\frac{C_{\text{annual}}}{M}\right) + \left( K \cdot r \cdot \frac{t}{365} \right)}$$

The system reaches Nash equilibrium when aggregate market expansion forces $A \ge A^*$, driving the marginal expected value of deploying the $(n+1)$-th account below zero.

### 2.4 Issuer Prestige Score ($Q_i$) & Winner's Curse

To model adverse selection, issuer quality $Q_i \in [0, 1]$ is calculated as an equally weighted, min-max normalized composite score of fundamental metrics:

$$Q_i = 0.5 \left( \frac{\text{NW}_i - \text{NW}_{\min}}{\text{NW}_{\max} - \text{NW}_{\min}} \right) + 0.5 \left( \frac{\text{EPS}_i - \text{EPS}_{\min}}{\text{EPS}_{\max} - \text{EPS}_{\min}} \right)$$

---

## 3. System Architecture & Methodology Pivots

**Data architecture & execution pipeline:**

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│  Primary Filings Data   │ ──► │    Data Processing ETL   │ ──► │    Derived Features     │
│  (SEBON, CDSC, NEPSE)   │     │    (process_data.py)     │     │ (EV_single, A*, p_win)  │
└─────────────────────────┘     └─────────────────────────┘     └───────────┬─────────────┘
                                                                              │
                                                                              ▼
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│  Visualizations & Plots │ ◄── │    Monte Carlo Engine    │ ◄── │   Empirical Bootstrap   │
│  (return_dist, scaling) │     │    (10,000 iterations)   │     │  (noise injection)      │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

To optimize quantitative accuracy while handling real-world market constraints, three key engineering pivots were made:

1. **Scraper anti-bot bypass.** Web scrapers encountered Cloudflare anti-bot blocks and CAPTCHA barriers on financial portals. Data collection was pivoted to a structured ETL pipeline (`process_data.py`) acting on verified primary historical filings (`nepse_ipo_raw.csv`), validated via helper scripts (`check_github.py`).
2. **Empirical bootstrap vs. abstract copulas.** Abstract copulas can overfit small historical datasets and fail on heavy-tailed demand spikes. The simulation engine instead uses an empirical Monte Carlo bootstrap, sampling historical IPO horizons with replacement and injecting Gaussian noise $\epsilon \sim \mathcal{N}(0, \sigma^2)$.
3. **Strict sideline penalty.** Maintenance fees ($C_{\text{annual}}$) are deducted even when the quality-filtered strategy skips an IPO. This ensures zero survivorship bias and realistic Sharpe ratio calculations.

---

## 4. Master Data Schema & Parameters

### Global fixed constants

| Parameter | Value |
| :--- | :--- |
| Application capital per lot ($K$) | NPR 1,000 |
| C-ASBA application fee ($C_{\text{ASBA}}$) | NPR 10.00 |
| Annual Demat / MeroShare maintenance cost ($C_{\text{annual}}$) | NPR 150.00 |
| Capital lockup window ($t$) | 10–14 days |
| Risk-free rate ($r$) | 6.00% p.a. |
| Annual modeled horizon ($M$) | 20 IPOs |

### Core input table layout (`nepse_ipo_raw.csv`)

| Ticker | Sector | Public Shares ($S$) | Valid Applicants ($A$) | Issue Price ($P_{\text{issue}}$) | Listing Price ($P_{\text{listing}}$) | Net Worth / Share | EPS |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| CHCL | Hydro | 1,500,000 | 1,250,000 | 100 | 320 | 145.20 | 18.50 |
| SHIVM | Manufacturing | 2,000,000 | 980,000 | 100 | 280 | 180.50 | 22.10 |
| UNHPL | Hydro | 800,000 | 1,420,000 | 100 | 115 | 92.10 | 3.20 |

---

## 5. Monte Carlo Simulation Engine & Results

The simulation engine (`sim.py`) ran 10,000 stochastic iterations comparing two strategies across account sizes $n \in [1, 10]$:

1. **Unfiltered naive strategy** — bid on all $M$ IPOs using $n$ accounts.
2. **Quality-filtered strategy** — bid only when $Q_i > 0.50$.

### Portfolio risk & return performance ($n = 1$)

| Metric | Unfiltered Naive Strategy | Quality-Filtered Strategy ($Q > 0.5$) | Interpretation |
| :--- | ---: | ---: | :--- |
| Expected annual net return | **NPR 8,500** | NPR 450 | Naive captures raw gain volume during market bull cycles. |
| 95% Value-at-Risk (VaR) | **NPR 4,623** | −NPR 127 | High-Q issues dilute win rates ($P_{\text{win}} \to 0$), leaving fixed fees unrecovered. |
| Maximum drawdown | Minimal | Moderate | Filtered strategy suffers fee drag from sitting on the sidelines. |
| Sharpe ratio | High (in bull market) | Low (dilution drag) | Demonstrates severe dilution on prime assets. |

### Return distribution & tail risk analysis (10,000 iterations)

The plot below shows the empirical net return distributions. The red dashed line marks the 95% VaR cutoff for the naive approach versus the filtered model.

![Return Distribution](return_distribution.png)

### Multi-account EV scaling dynamics ($n = 1 \dots 10$)

Expected net return scales linearly with family account expansion ($n$), showing that account splitting is a valid alpha generator under current NEPSE fee structures.

![Expected Return Scaling](expected_return_scaling.png)

---
## 6. Conclusion & Market Inefficiency

The findings of this quantitative simulation reveal significant structural inefficiencies within the NEPSE 10-kitta lottery system, presenting a clear alpha-generation opportunity for retail participants.

* **The $A^*$ Equilibrium Gap:** The model proves that the NEPSE primary market is currently operating far below its theoretical Nash Equilibrium. For an average mid-sized IPO, the break-even applicant threshold ($A^*$) approaches **15 to 17 million applicants** before fixed frictions drain the expected value to zero. Because actual market participation currently caps at around **1.5 to 2.5 million applicants**, the lottery remains a highly profitable, positive-EV structural arbitrage.
* **The Quality Filter Paradox (Winner's Curse):** Applying fundamental analysis to filter IPOs ($Q > 0.5$) actively destroys portfolio returns. High-prestige issues attract such extreme oversubscription that the win probability approaches zero ($P_{\text{win}} \to 0$). The filtered strategy fails to secure enough winning lots to cover the fixed annual Demat and MeroShare maintenance drag, resulting in a negative 95% VaR.
* **The Optimal Bidding Strategy:** The mathematically optimal approach is the **Unfiltered Naive Strategy** deployed across maximum available family accounts ($n$). By bidding on all issues indiscriminately, the strategy captures asymmetric listing-day returns (+100% to +300%) that effortlessly offset the trivial C-ASBA fees (NPR 10) lost on the occasional underperforming stock.

---
## 7. Repository Structure

```
.
├── CONTEXT.md                    # Research rules, math definitions, & data requirements
├── METHODOLOGY_ADDENDUM.md       # Technical deviations (bootstrap, scraper pivot, penalties)
├── check_github.py               # Repository API checker & verification script
├── process_data.py               # Data pipeline: raw CSV -> clean CSV & model feature CSV
├── sim.py                        # Monte Carlo bootstrap simulation engine (10,000 runs)
├── plots.py                      # Visualization generator for distributions & EV scaling
├── nepse_ipo_raw.csv             # Raw input dataset
├── nepse_ipo_clean.csv           # Cleaned dataset (normalized dates & types)
├── nepse_ipo_model.csv           # Model output dataset (EV_single, A*, p_win, returns)
├── return_distribution.png       # Generated plot: distribution of returns & 95% VaR
└── expected_return_scaling.png   # Generated plot: EV vs. number of family accounts (n)
```

---

## 8. Quickstart Guide

### Prerequisites

- Python 3.9+
- Required packages: `pandas`, `numpy`, `matplotlib`, `seaborn`, `requests`

```bash
pip install pandas numpy matplotlib seaborn requests
```

### Execution steps

1. **Verify source connection & environment**

   ```bash
   python check_github.py
   ```

2. **Run the data processing pipeline** — calculates single-account EV, equilibrium bounds ($A^*$), and win probabilities:

   ```bash
   python process_data.py
   ```

3. **Execute the Monte Carlo simulation & generate plots** — runs 10,000 bootstrap iterations and outputs visualization charts:

   ```bash
   python plots.py
   ```
