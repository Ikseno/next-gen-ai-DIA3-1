# Step 3 — Routing rule (Pair C)

Source of every rate: [`../../TD1/results/pivot-td1.md`](../../TD1/results/pivot-td1.md) and [`../../TD1/results/traces-td1.csv`](../../TD1/results/traces-td1.csv) (final attempt of each cell, temperature 0, one run). Twenty questions give a **routing hypothesis for this batch**, not a general error rate, a permanent ranking, or a guarantee that a quorum is right.

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

**Ambiguous age questions (answer to review C-by-B, Q2):** if the question gives a reference date ("aged 25 on 2026-12-01"), it is F2; if the age is taken at the time of each order, it is F2b; if the text does not say which, the question is not routed to a model: it is sent back for clarification (abstain, "age reference date not specified"). An unseen combination (for example F2b + product list) takes the level of its strictest part, so F2b + F3 is level 2. Any family outside C01–C20 abstains: no TD 1 evidence.

**Policy v2 principle (Lecture 2: "Difficulty chooses the model. Stakes choose the check."):** the use alone sets the starting check: dashboard = format check by code, customer = 2-of-3 quorum, payout = deterministic reference + human review. The TD 1 evidence can only raise it, never lower it: format only needs the chosen model at 100 % on at least 3 cells of the family; on age families the quorum step is replaced by the deterministic reference (shared wrong values on C08, C09, C10). "No check" does not exist: every answer at least passes the format check (one integer, euro cents, excluding VAT).

| Family | First model | Internal dashboard | Figure shown to a customer | Amount paid out | Fallback if first model unavailable |
|---|---|---|---|---|---|
| **F1** period | E dots (free), 6/6 | **format check only**, by code (100 %, low stakes) | **2-of-3 quorum**: the three cheapest available among E, C, D (Groq free tier), B, all 6/6 | **deterministic reference + human review** (closed-open period SQL template) | C north → D qwen on the Groq free tier → B 20b → if all exhausted: wait for refill if deferrable, else abstain |
| **F3** product | E dots (free), 4/4 | **format check only**, by code (100 %, low stakes) | **2-of-3 quorum**: same panel as F1, all 4/4 | **deterministic reference + human review** (product `IN` list + period template) | Same as F1 |
| **F2** age at a date (incl. C15 C16 C17 C19) | A 120b, 4/4 and 4/4 combined | **format check only**, by code (A 8/8 on F2 and combined) | **deterministic reference**: age window `date(ref,'-26 years') < birth_date <= date(ref,'-25 years')` (same predicate as Pair B) | **deterministic reference + human review** | No other model is 100 % on F2 (D 3/4, E 2/4). If A is unavailable: wait for the Groq refill if deferrable (all 6 HTTP 429 in TD 1 recovered on attempt 2), else the Groq paid route of A within the budget, else abstain from the model route and hand over to the deterministic reference template or a person (outside the simulator) |
| **F2b** age at the order (incl. C18) | B 20b, 1/1 (A 1/1 as well); also covers F2b + F3, never seen in TD 1, by the strictest-part rule | **deterministic reference** (age at `order_date`): B is 2/2 only (C10, C18), too thin for format only, and no quorum on age | **deterministic reference**: age computed at `order_date` | **deterministic reference + human review** | A 120b → wait for refill if deferrable → Groq paid route (B, then A) within budget → abstain from the model route and hand over to the deterministic reference template or a person (outside the simulator) |

**What "deterministic reference" means here (answer to C3):** the reference query is run by code and **compared with** the model's value; it does not replace the model in the normal path. If the values differ, the answer is not delivered. The reference **replaces** the model only in the hand-over after an abstention, and only when a validated SQL template exists for that exact question type. This hand-over is outside the simulator: `choose` returns `abstain` with a `handover` field that says so.

**When a check fails (answer to C5):** in the simulator, checks are named, not executed (`checks.status` says so). The rule for delivery is: a failed check, or a check in error, means **no delivery**. Dashboard: the value is flagged and recomputed at the next run. Customer: the service answers "no verified figure yet" (abstention). Payout: the amount goes to human review. Each case is in `checks.on_failure`.

**Panel diversity (answer to C4):** the only quorum left in the rule is the F1/F3 customer quorum, drawn from dots (dots-studio), north (Cohere), qwen (Alibaba) and gpt-oss-20b (OpenAI): four different makers, so any three are three families. The former F2b dashboard quorum (gpt-oss-20b + gpt-oss-120b + qwen) put two OpenAI models together; it is removed and replaced by the deterministic reference.

**Why no quorum for customer or payout figures on F2/F2b:** the three shared wrong values above are all on age questions. In a 2-of-3 panel that contains B and E, C08 gives a consensus on the wrong value. A quorum only lowers the risk when the errors are independent, and on the age convention they are not.

**Why "format check only" is allowed on F1 and F3 (and F2 with A) for the dashboard only:** 10 out of 10 cells were correct for every model. That is a batch result, so a customer-facing figure still gets a cheap 2-of-3 check with free and very cheap models.
