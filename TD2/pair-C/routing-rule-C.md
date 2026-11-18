# Step 3 — Routing rule (Pair C)

Source of every rate: [`../TD1/results/pivot-td1.md`](../TD1/results/pivot-td1.md) and [`../TD1/results/traces-td1.csv`](../TD1/results/traces-td1.csv) (final attempt of each cell, temperature 0, one run). Twenty questions give a **routing hypothesis for this batch**, not a general error rate, a permanent ranking, or a guarantee that a quorum is right.

## Portfolio, cheapest first

| Rank | Model | Route used in TD 1 | Paid price (in / out, USD per M tokens) |
|---|---|---|---|
| 1 | `cohere/north-mini-code:free` (C) | OpenRouter free | 0 (free only, no paid route) |
| 1 | `dots-studio/dots-3-note-preview:free` (E) | OpenRouter free | 0 (free only, no paid route) |
| 3 | `openai/gpt-oss-20b` (B) | Groq | 0.075 / 0.30 |
| 4 | `openai/gpt-oss-120b` (A) | Groq | 0.15 / 0.60 |
| 5 | `qwen/qwen3.8-27b` (D) | Groq | 0.80 / 4.00 |

Tie between the two free models: E goes first (15/20 overall against 12/20 for C, and C produced the only invalid SQL, C11).

## Families and TD 1 rates (correct / cases)

| Family | Cells | C north | E dots | B 20b | A 120b | D qwen |
|---|---|---|---|---|---|---|
| **F1** period | C01 C04 C05 C06 C07 C20 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| **F3** product list (with or without period) | C03 C12 C13 C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| **F2** completed age at a date | C02 C08 C09 C11 | 0/4 | 2/4 | 1/4 | **4/4** | 3/4 |
| **F2b** age at the order | C10 | 0/1 | 0/1 | **1/1** | **1/1** | 0/1 |
| F2 + F1/F3 combined | C15 C16 C17 C19 | 2/4 (C19 by chance) | 3/4 | 4/4 | **4/4** | 1/4 |
| F2b + F1 combined | C18 | 0/1 | 0/1 | 1/1 | **1/1** | 1/1 |

**Shared wrong values seen in TD 1 (why a quorum is not enough on age):** C08, B and E both return 25 920 (ref. 605 580). C10, D and E both return 119 410 (ref. 558 980). C09, C and D both return 0 (ref. 487 980).

## The rule

**Classification first:** a question that contains an age condition is routed as F2 or F2b, whatever else it contains. A combination takes the rule of its strictest component.

| Family | First model | Internal dashboard | Figure shown to a customer | Amount paid out | Fallback if first model unavailable |
|---|---|---|---|---|---|
| **F1** period | E dots (free), 6/6 | **none** (100 %, low stakes) | **2-of-3 quorum**: the three cheapest available among E, C, D (Groq free tier), B, all 6/6 | **deterministic reference** (closed-open period SQL template) | C north → D qwen on the Groq free tier → B 20b → if all exhausted: wait for refill if deferrable, else abstain |
| **F3** product | E dots (free), 4/4 | **none** (100 %, low stakes) | **2-of-3 quorum**: same panel as F1, all 4/4 | **deterministic reference** (product `IN` list + period template) | Same as F1 |
| **F2** age at a date (incl. C15 C16 C17 C19) | A 120b, 4/4 and 4/4 combined | **none** allowed (A 100 %); we still log the value as "unchecked" | **deterministic reference**: age window `date(birth,'+25 years') <= ref < date(birth,'+26 years')` | **deterministic reference + human review** | No other model is 100 % on F2 (D 3/4, E 2/4). If A is unavailable: wait for the Groq refill if deferrable (all 6 HTTP 429 in TD 1 recovered on attempt 2), else run the deterministic reference alone, else abstain |
| **F2b** age at the order (incl. C18) | B 20b, 1/1 (A 1/1 as well) | **2-of-3 quorum** B + A + D: one case only (C10), so we do not grant "none" | **deterministic reference**: age computed at `order_date` | **deterministic reference + human review** | A 120b → wait for refill → deterministic reference alone → abstain |

**Why no quorum for customer or payout figures on F2/F2b:** the three shared wrong values above are all on age questions. In a 2-of-3 panel that contains B and E, C08 gives a consensus on the wrong value. A quorum only lowers the risk when the errors are independent, and on the age convention they are not.

**Why "none" is allowed on F1 and F3 for the dashboard only:** 10 out of 10 cells were correct for every model. That is a batch result, so a customer-facing figure still gets a cheap 2-of-3 check with free and very cheap models.
