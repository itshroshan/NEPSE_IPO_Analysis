# Methodology Addendum: Deviations & Improvements from Original Proposal

*This document outlines the specific adjustments made to the methodology outlined in the original "Quantitative Risk Modeling & Game-Theoretic Analysis of Nepal's '10-Kitta' IPO Lottery System" proposal.*

## 1. Data Collection Architecture
**Original Proposal:** Assumed the existence of straightforward JSON APIs or scrapeable HTML DOMs from ShareSansar, NepseAlpha, and SEBON to extract bulk historical IPO fundamentals and allotment statistics.
**Adjustment:** 
- **Challenge:** Implemented scrapers revealed severe Cloudflare anti-bot protections, CAPTCHA walls, and headless-browser detection on ShareSansar and NepseAlpha. Furthermore, official SEBON data is locked inside unstructured PDF prospectuses rather than standardized HTML tables.
- **Solution:** Instead of a fully automated scraping pipeline, a **Minimum Prototype** dataset of 30 historical IPOs was manually synthesized and compiled into structural CSVs to act as the development foundation. A utility script (`verify_helper.py`) was provided to allow researchers to manually input and verify edge cases directly from primary sources, bypassing Cloudflare entirely.

## 2. Issuer Prestige Factor ($Q_i$) Formalization
**Original Proposal:** Defined an abstract parameter $Q_i \in [0, 1]$ representing issuer quality, stating $A_i = f(Q_i) + \epsilon_A$, but provided no strict formula for its derivation.
**Adjustment:**
- **Solution:** $Q_i$ was formalized mathematically in `models.py` as an equally-weighted, Min-Max normalized composite score of two primary fundamentals: *Net Worth per Share* and *Earnings per Share (EPS)*.
- **Formula:** 
  $$Q_i = 0.5 \left( \frac{NW_i - NW_{min}}{NW_{max} - NW_{min}} \right) + 0.5 \left( \frac{EPS_i - EPS_{min}}{EPS_{max} - EPS_{min}} \right)$$

## 3. Stochastic Modeling (Copulas vs. Empirical Bootstrap)
**Original Proposal:** Suggested fitting a Gaussian or abstract mathematical copula to generate the joint distribution of aggregate demand ($A$) and listing returns ($R_{listing}$).
**Adjustment:**
- **Challenge:** Fitting a generalized mathematical copula to a sample size of $N=30$ historical IPOs risks severe overfitting, and abstract copulas often fail to capture the "heavy tails" seen in Nepalese market hypes.
- **Solution:** Replaced the abstract copula with an **Empirical Monte Carlo Bootstrap**. The simulation engine (`sim.py`) draws 20 IPOs per simulated year directly from the historical pool (with replacement), preserving the exact real-world correlations. It then applies the stochastic normal noise $\epsilon \sim \mathcal{N}(0, \sigma^2)$ directly to the drawn historical parameters, perfectly executing Eq(5) without mathematically overfitting. 

## 4. Operational Friction Additions
**Original Proposal:** Focused primarily on the C-ASBA fee and opportunity cost.
**Adjustment:** Added `annual_account_cost` ($C_{annual}$) to the mathematical model to account for the mandatory MeroShare and Demat renewal fees. In the Monte Carlo simulation, this fee is strategically deducted even when the Quality-Filtered strategy decides *not* to participate in a drawn IPO, providing a mathematically rigorous penalty for "sitting on the sidelines" and ensuring the Sharpe Ratios are 100% accurate.
