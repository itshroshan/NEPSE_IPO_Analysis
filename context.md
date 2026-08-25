# CONTEXT.md — NEPSE IPO Quantitative Data Collection Context

## Purpose

This file is the working context for an AI agent that will collect and organize the real historical data required for a quantitative study of Nepal's "10-Kitta" IPO lottery system.

The goal at this stage is **data collection only**. Do not redesign the mathematical model, change the research objective, or start the Monte Carlo simulation unless explicitly instructed.

The underlying project studies:

- Expected value (EV) of participating in Nepal's IPO lottery system.
- The effect of using multiple family Demat accounts.
- The equilibrium point where additional accounts become economically unattractive.
- The relationship between IPO quality/prestige, demand, and listing returns.
- A later 10,000-run Monte Carlo simulation comparing a naive strategy with a quality-filtered strategy.

The original proposal recommends collecting historical data for roughly 30–50 recent NEPSE IPOs. For a stronger final model, our working target is **100–150 comparable IPOs**, subject to data availability and quality.

---

# 1. Core Mathematical Definitions

## Lottery probability

For an IPO with general-public shares `S`:

`L = S / 10`

where `L` is the number of 10-share winning lots.

The single-account probability of winning is:

`P_win = min(1, L / A)`

where:

- `A` = number of valid applicants participating in the relevant lottery.

## Listing return

The study defines:

`R_listing = (P_listing - P_issue) / P_issue`

where:

- `P_issue` = IPO issue price.
- `P_listing` = secondary-market listing price.

For this project, the preferred operational definition is:

**P_listing = the official closing price on the first actual trading day.**

Do NOT substitute:
- opening price,
- intraday high,
- intraday low,
- allowed opening-price range,
- or an arbitrary later LTP.

If the source uses a field named `LTP`, verify whether it is actually the market close/closing price before using it as `P_listing`.

## Single-account EV

`EV_single = P_win * (K * R_listing) - C_ASBA - (C_annual / M) - (K * r * t / 365)`

where:

- `K` = application capital, normally NPR 1,000 for a 10-share application at NPR 100/share.
- `C_ASBA` = application fee.
- `C_annual` = annual account maintenance overhead.
- `M` = number of IPOs/issues in the modeled annual horizon.
- `r` = annual risk-free rate.
- `t` = number of days capital is economically locked.

## Multi-account model

For `n` distinct family accounts:

`X ~ Binomial(n, P_win)`

and under the model's simplifying assumption:

`EV(n) = n * EV_single`

## Critical market-demand threshold

`A* = [L * (K * R_listing)] / [C_ASBA + (C_annual / M) + (K * r * t / 365)]`

---

# 2. Main Data-Collection Principle

Build the dataset at the **IPO level**.

Target approximately **100–150 comparable Nepalese IPOs**, preferably from a reasonably consistent regulatory/market regime (initial working window: approximately 2019–2026, subject to review).

Do not blindly mix fundamentally different issue structures.

For each IPO, collect the **general-public lottery pool**, not merely the total company IPO size.

For example, if an issue allocates shares separately to:
- Nepalese citizens working abroad,
- employees,
- mutual funds,
- other reserved categories,
- general public,

then `S` for the core lottery model should represent the shares actually available to the relevant general-public lottery pool.

---

# 3. Required Master IPO Dataset

Create one master row per IPO.

## Identification and dates

- `ipo_id`
- `company_name`
- `symbol`
- `sector`
- `issue_open_date`
- `issue_close_date`
- `allotment_date`
- `listing_date`
- `first_trading_date`

## IPO size and price

- `total_issue_shares`
- `general_public_shares`  ← use this as `S` for the lottery model
- `issue_price`
- `face_value`
- `issue_premium` (if applicable)

## Demand / lottery inputs

- `valid_applications`  ← use as `A`
- `applied_shares`
- `oversubscription`

Calculate:

`winning_lots = general_public_shares / 10`

`p_win = min(1, winning_lots / valid_applications)`

`oversubscription = applied_shares / general_public_shares`

## First-day market data

Collect first actual trading-day:

- `first_day_open`
- `first_day_high`
- `first_day_low`
- `first_day_close`
- `first_day_ltp`
- `first_day_quantity` (recommended)
- `first_day_turnover` (recommended)

Use:

`P_listing = first_day_close`

for the baseline listing-return model.

Calculate:

`R_listing = (first_day_close - issue_price) / issue_price`

---

# 4. Transaction / Opportunity-Cost Data

Collect or reconstruct:

- `casba_fee`
- `annual_account_cost`
- `risk_free_rate`
- `capital_lock_days`

Do not automatically hard-code the proposal's baseline values if historical values can be obtained.

The proposal uses:

- `K = NPR 1,000`
- `C_ASBA` baseline/range = NPR 5–25
- `C_annual = NPR 150/account`
- `r = 6% p.a.`
- `t = 10–14 days`

These are baseline assumptions, not necessarily historically exact values.

## Better treatment

### C-ASBA

Prefer actual historical applicable fees. If bank-specific historical reconstruction is impossible, preserve the uncertainty and later run sensitivity analysis over a reasonable range rather than falsely assigning one universal historical fee.

### Annual cost

Track the relevant Demat/MeroShare/account-maintenance cost for the period. Keep the exact definition of the cost clear.

### Risk-free rate

Prefer a historical rate tied to the IPO period rather than a constant 6%.

A strong proxy is the Nepal Rastra Bank Treasury Bill rate (e.g. 91-day T-bill), subject to methodological decision later.

### Capital lock period

Do not automatically assume 10–14 days.

Collect:
- issue open date,
- issue close date,
- allotment date,
- refund/unblocking date (where available).

Then define and calculate the lock period consistently with the economic interpretation of `t`.

---

# 5. Fundamental / Prestige-Score Dataset

The proposal introduces a composite issuer Prestige Score:

`Q_i ∈ [0,1]`

It states that the score is based on fundamental/structural characteristics such as:

- Net worth per share
- Sector
- Promoter lock-in

However, the proposal does **not** specify a complete mathematical formula for `Q`.

Therefore, at the data-collection stage:

**Do not invent the final Q formula.**

Instead, collect enough raw variables to allow a later calibrated score/model.

Recommended variables:

## Core fundamentals

- `net_worth_per_share`
- `eps`
- `book_value_per_share`
- `roe`
- `roa`
- `debt_equity`
- `revenue_growth`
- `profit_growth`
- `operating_margin`
- `dividend_history` (if applicable)

## Company / governance structure

- `sector`
- `promoter_holding`
- `promoter_lockin`
- `public_float`
- `company_age`
- `paid_up_capital`
- `credit_rating` (if applicable)

## IPO-specific fundamentals

- `issue_size`
- `general_public_issue_size`
- `issue_price`
- `face_value`
- `issue_premium`
- `institutional_or_reserved_allocation` (where relevant)

Whenever possible, use values from the IPO prospectus or contemporaneous official financial documents so that the measurements correspond to information available around the IPO, rather than later restatements.

---

# 6. Optional but Strongly Recommended Market-Context Dataset

To avoid attributing broad market movements entirely to IPO-specific quality, collect:

- `nepse_index_at_issue`
- `nepse_index_at_listing`
- `nepse_return_between_issue_and_listing`
- `market_volatility_around_listing`
- `sector_index_at_issue` (if available)
- `sector_return_between_issue_and_listing` (if available)

These are not explicitly required by the original equations, but they are highly useful as controls when analyzing listing returns.

---

# 7. Preferred Data Sources

Use a source hierarchy.

## Tier 1 — Official / primary sources

### SEBON — Securities Board of Nepal

Use primarily for:
- IPO approvals
- issue information
- prospectuses
- issue size
- public allocation
- financial/fundamental information contained in prospectuses

Source:
https://www.sebon.gov.np/

Prospectus archive:
https://www.sebon.gov.np/prospectus

Public issues data:
https://sebon.gov.np/public-issues-data

### CDSC — CDS and Clearing Limited

Use primarily for:
- C-ASBA-related information
- allotment information
- applicant/allotment-related records where available
- relevant regulatory/fee information

Source:
https://cdsc.com.np/

### NEPSE — Nepal Stock Exchange

Use primarily for:
- listing/trading dates
- official historical market prices
- first trading-day OHLC
- closing price
- quantity/turnover where available

Source:
https://www.nepalstock.com/

### Nepal Rastra Bank (NRB)

Use primarily for:
- Treasury Bill / government security rates
- deposit/savings rates if needed
- macroeconomic/market-rate data

Source:
https://www.nrb.org.np/

## Tier 2 — High-value secondary sources

### ShareSansar

Useful for:
- IPO application counts
- applied shares
- allotment results
- issue/listing announcements
- historical IPO news

Source:
https://www.sharesansar.com/

### MeroLagani

Useful for:
- historical company/price information
- price history
- company information

Source:
https://merolagani.com/

Secondary sources may accelerate collection, but **critical values should be verified against primary/official sources wherever possible**.

---

# 8. Source Selection Rules for Every Value

For every collected value, store:

- `source_name`
- `source_url`
- `source_type` (`official`, `secondary`)
- `source_document_title` if applicable
- `source_date`
- `retrieval_date`
- `page_number` or section if the source is a PDF
- `raw_value`
- `normalized_value`
- `notes`
- `verification_status`

Do not silently combine numbers from two conflicting sources.

If two sources disagree:

1. Preserve both raw values.
2. Prefer the official/primary source.
3. Record the discrepancy in `notes`.
4. Do not overwrite the original evidence.
5. Flag the row for manual verification.

---

# 9. Data Quality Rules

## Do not guess

If a value is not found:
- use `NA` / blank,
- record why it is missing,
- try another authoritative source,
- flag it for review.

Never fabricate historical values.

## Dates

Normalize all dates to:

`YYYY-MM-DD`

## Currency

Normalize monetary values to:

`NPR`

## Percentages

Store percentage rates consistently.

Recommended raw numeric convention:
- 6% = `0.06`
- 150% = `1.50`

If useful, also store a display percentage separately.

## Shares

Store as integer counts.

## Price

Use numeric NPR price per share.

---

# 10. Important Distinctions

## General-public shares vs total IPO size

For the lottery model:

`S = general-public lottery allocation`

not necessarily total shares issued by the company.

## Applicants vs applied shares

Keep both:

`A = valid applicant count`

and

`D = total applied shares`

Do not substitute one for the other.

## Listing price vs listing range

The permitted first-trading/opening range is not the same thing as the first-day closing price.

For the baseline return calculation:

`P_listing = first-day official close`

## LTP vs Close

The source may provide both `LTP` and `Close`.

Do not assume they are interchangeable without checking the source definition for the relevant historical record.

## Issue price vs face value

Store them separately.

For a standard NPR 100-per-share issue:

- face value = NPR 100/share
- 10 shares = NPR 1,000 application capital

The NPR 1,000 is the typical capital amount for a 10-share application, not NPR 1,000 face value per share.

---

# 11. Derived Variables to Calculate After Raw Collection

Once raw data are collected, calculate:

- `winning_lots`
- `p_win`
- `oversubscription`
- `listing_return`
- `capital_gain_per_won_application`
- `capital_lock_days`
- `opportunity_cost`
- `expected_gross_return`
- `EV_single`
- `A_star`

Core formulas:

`winning_lots = general_public_shares / 10`

`p_win = min(1, winning_lots / valid_applications)`

`oversubscription = applied_shares / general_public_shares`

`listing_return = (first_day_close - issue_price) / issue_price`

`expected_gross_return = p_win * (K * listing_return)`

`opportunity_cost = K * risk_free_rate * capital_lock_days / 365`

`EV_single = p_win * (K * listing_return) - casba_fee - (annual_account_cost / M) - opportunity_cost`

`A_star = winning_lots * (K * listing_return) / (casba_fee + annual_account_cost/M + opportunity_cost)`

Keep raw and derived fields separate.

---

# 12. Recommended Sample Size

Historical real data:

- Minimum prototype: ~30 IPOs
- Good: ~75 IPOs
- Strong target: ~100–150 IPOs
- If quality and consistency allow: up to ~150–200

The project should prioritize **data consistency and completeness over simply increasing the number of IPOs**.

The model may eventually fit:
- demand vs quality,
- listing return vs quality,
- dependence structure / copula.

These statistical components are more credible with substantially more than 30 observations.

## Monte Carlo distinction

The proposal specifies:

`N_sim = 10,000`

This is the number of **simulated scenarios**, not the number of real IPO observations.

Do not confuse historical sample size with Monte Carlo iteration count.

---

# 13. Suggested Working Time Window

Start with approximately:

**2019–2026**

but verify comparability before final modeling.

Do not automatically merge every IPO from every historical year because:
- market participation changes,
- regulations can change,
- IPO allocation rules can change,
- C-ASBA infrastructure/fees can change,
- market regimes differ.

Store the year and relevant regulatory regime information so later analysis can control for structural changes.

---

# 14. Recommended Data-Collection Workflow

For each IPO:

### Step 1 — Identify the issue

Find:
- company
- symbol
- issue period
- listing date

### Step 2 — Obtain the prospectus

Extract:
- issue price
- face value
- total issue size
- general-public allocation
- reserved allocations
- financial/fundamental variables
- promoter/governance information

### Step 3 — Obtain application/allotment data

Extract:
- valid applicants
- total applied shares
- successful/winning applicants if available
- allotment date

### Step 4 — Obtain first trading-day data

Extract:
- first actual trading date
- open
- high
- low
- close
- LTP
- quantity
- turnover

Use official close for `P_listing`.

### Step 5 — Obtain transaction/rate inputs

Extract:
- historical C-ASBA fee
- relevant annual account cost
- appropriate historical risk-free rate

### Step 6 — Record evidence

For every important value, record:
- source
- URL
- source date
- page/section
- raw value
- normalized value
- notes
- verification status

### Step 7 — Calculate derived variables

Run the formulas only after raw fields have been collected and verified.

---

# 15. Do Not Do These Things

Do not:

- invent missing data,
- estimate historical applicant counts from oversubscription alone if actual applicant counts are available,
- use total IPO size when the relevant lottery pool is smaller,
- use a random post-listing price for `P_listing`,
- assume LTP always equals close,
- hard-code 6% risk-free rate if historical data can be obtained,
- hard-code 10–14 lock-up days if actual dates are available,
- fabricate a Prestige Score `Q` before the raw fundamental variables are collected,
- drop missing observations silently,
- overwrite conflicting source values,
- mix data from incompatible regulatory periods without recording the regime,
- treat 10,000 Monte Carlo simulations as 10,000 historical observations.

---

# 16. Output Required From the Data-Collection Agent

The collection agent should ultimately produce:

## A. Raw dataset

`nepse_ipo_raw.csv`

One row per IPO with all raw fields and source evidence.

## B. Clean dataset

`nepse_ipo_clean.csv`

Normalized dates, prices, shares, rates, and standardized categorical values.

## C. Derived dataset

`nepse_ipo_model.csv`

Includes:
- winning_lots
- p_win
- oversubscription
- listing_return
- lock_days
- opportunity_cost
- EV_single
- A_star

## D. Source log

`source_log.csv`

At minimum:

`ipo_id, variable_name, source_name, source_url, document/page, source_date, raw_value, normalized_value, verification_status, notes`

## E. Missing-data report

A list of:
- missing fields,
- unresolved conflicts,
- rows requiring manual verification.

---

# 17. Final Research Objective for This Data Stage

The final dataset must support these later model stages:

1. Calculate historical `P_win`.
2. Calculate historical `R_listing`.
3. Calculate single-account EV.
4. Analyze multi-account EV.
5. Estimate demand relationships.
6. Construct/calibrate a Prestige Score `Q`.
7. Model the relationship between `Q`, demand, and listing return.
8. Fit the dependence structure / Gaussian copula.
9. Run 10,000 Monte Carlo simulations.
10. Compare:
   - naive participation in all IPOs,
   - quality-filtered participation where `Q > threshold`.
11. Evaluate:
   - expected return,
   - Sharpe ratio,
   - VaR 95%,
   - maximum drawdown.

At the current stage, **focus only on collecting high-quality historical data that makes those later calculations possible.**
