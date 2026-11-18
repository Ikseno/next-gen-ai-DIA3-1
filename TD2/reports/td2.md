# TD 2 report — The quorum, then the routing rule

**Class DIA 3, sub-group 1 (DIA3-1)** · Session of 18 November 2026 · Course pack `2026-11-18-students-5`
Inputs: TD 1 outputs in [`TD1/`](../../TD1/) — no new network batch. Work files: [`TD2/`](../).

## 1. What we attempted and what we completed

_To complete._

## 2. Step 1 — k-of-n vote (Pair A)

_Method, 2-of-3 vs 3-of-5 table for C01–C20, explanation of each changed decision._

## 3. Step 2 — Wrong consensus (Pair B)

Pair B analyses **C08**, a real shared wrong answer in the team's stored TD1 traces. GPT-OSS 20B and Dots both return **25,920 cents**, whereas the independently checked reference is **605,580 cents**. Both faulty queries select only customers born on `2001-09-24`, rather than all customers aged 25 on `2026-09-24` (birth dates strictly after `2000-09-24` and on or before `2001-09-24`).

The executed delta query identifies five omitted customers whose revenue totals **579,660 cents**, exactly `605,580 - 25,920`. The fixed **2-of-3** panel returns the correct value with two votes; the **3-of-5** quorum abstains (two correct votes, two votes for 25,920, one for 1,188,090). The shared wrong value wins neither quorum.

Full diagnosis, complete SQL queries, customer-level evidence, source hashes and independent CSV checking: **[Pair B analysis](../pair-b/README.md)**. Reproduce offline with `python TD2/pair-b/analyse.py` from the repository root. SQLite execution and the independent Python/CSV calculation agree. **Pending:** verify the vote counts with Pair A's completed method and complete the internal team cross-review.

## 4. Step 3 — Routing rule (Pair C)

Work files: [`TD2/pair-C/`](../pair-C/). The full rule is in [`routing-rule-C.md`](../pair-C/routing-rule-C.md) and the simulator work in [`pair-C/README.md`](../pair-C/README.md). Every rate below comes from [`TD1/results/pivot-td1.md`](../../TD1/results/pivot-td1.md) and [`traces-td1.csv`](../../TD1/results/traces-td1.csv): one run per cell at temperature 0, final attempt. Twenty questions give a **routing hypothesis for this batch**, not a general error rate, a permanent ranking, or a guarantee that a quorum is right.

### 4.1 TD 1 rates by family (correct / cases)

| Family | Cells | north-mini-code (free) | dots-3-note (free) | gpt-oss-20b | gpt-oss-120b | qwen3.8-27b |
|---|---|---|---|---|---|---|
| **F1** period | C01 C04 C05 C06 C07 C20 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| **F3** product list | C03 C12 C13 C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| **F2** completed age at a date | C02 C08 C09 C11 | 0/4 | 2/4 | 1/4 | **4/4** | 3/4 |
| **F2b** age at the order | C10 | 0/1 | 0/1 | **1/1** | **1/1** | 0/1 |
| F2 combined with F1/F3 | C15 C16 C17 C19 | 2/4 (C19 by chance) | 3/4 | 4/4 | **4/4** | 1/4 |
| F2b combined with F1 | C18 | 0/1 | 0/1 | 1/1 | **1/1** | 1/1 |

Portfolio, cheapest first: north-mini-code and dots-3-note (OpenRouter free, no paid route), then gpt-oss-20b (0.075 / 0.30 USD per million tokens), gpt-oss-120b (0.15 / 0.60) and qwen3.8-27b (0.80 / 4.00) on Groq.

**Errors are not independent on age questions.** Three age cells have a wrong value shared by two models: C08 (gpt-oss-20b and dots: 25,920, analysed by Pair B in section 3), C09 (north-mini-code and qwen: 0, see [`wrong-consensus-C09`](../wrong-consensus-C09/part3-delta-mehdy.md)) and C10 (qwen and dots: 119,410). On C09, the team's fixed panel (gpt-oss-120b, north-mini-code, qwen) returns the wrong value 0 as a 2-of-3 consensus.

### 4.2 The rule

A question with an age condition is routed as F2 or F2b, whatever else it contains. A combination takes the rule of its strictest part.

| Family | First model | Internal dashboard | Figure shown to a customer | Amount paid out | Fallback |
|---|---|---|---|---|---|
| **F1**, **F3** | dots-3-note (free), 10/10 | none (every model 10/10) | 2-of-3 quorum of the three cheapest available models among dots, north, qwen, gpt-oss-20b (all 10/10) | deterministic reference (period / product SQL template) | north → qwen (Groq free) → gpt-oss-20b → wait for refill if deferrable → abstain |
| **F2** | gpt-oss-120b, 4/4 (and 4/4 combined) | none (100 % in TD 1), value logged as unchecked | deterministic reference: age window `date(birth,'+25 years') <= ref < date(birth,'+26 years')` | deterministic reference + human review | No other model is 100 % on F2. Wait for the Groq refill if deferrable (the six HTTP 429 of TD 1 all recovered on attempt 2), else paid Groq route, else deterministic reference alone, else abstain |
| **F2b** | gpt-oss-20b, 1/1 (gpt-oss-120b 1/1 too) | 2-of-3 quorum gpt-oss-20b + gpt-oss-120b + qwen ("none" refused: one case only) | deterministic reference, age computed at `order_date` | deterministic reference + human review | gpt-oss-120b → wait for refill → deterministic reference alone → abstain |

dots-3-note goes before north-mini-code for F1/F3 (both free) because north produced the only invalid SQL of TD 1 (C11) and a value correct by chance (C19). No quorum is accepted for customer or payout figures on age questions, because of the shared wrong values above.

### 4.3 Simulator: before and after adaptation

`python3 TD2/pair-C/atelier-routage.py` gives [`output-before.jsonl`](../pair-C/output-before.jsonl). In [`atelier-routage-adapted.py`](../pair-C/atelier-routage-adapted.py), `RESOURCES` holds our five models: the free routes used in TD 1, plus the Groq paid route for gpt-oss-20b, gpt-oss-120b and qwen. The cash for one request assumes 650 input + 300 output tokens; the largest TD 1 cell used 1,333 tokens. Eligibility levels come from 4.1: level 1 = F1/F3, level 2 = F2b, level 3 = F2, and each model gets the highest level it passed entirely. Each `reason` cites the TD 1 cells. `choose` keeps the kit's priority order, but the request now gives a family and a use, and the check comes from the rule table. Output: [`output-after.jsonl`](../pair-C/output-after.jsonl), reproduced identically on Windows by the pair.

| Scenario | Before (kit) | After (our rule) |
|---|---|---|
| simple | run `small-free` | run dots-3-note (free), no check (F1 6/6) |
| complex | run `senior-subscription` | run gpt-oss-120b (Groq free), no check, logged as unchecked |
| deferrable | defer `senior-subscription`, 60 min | defer gpt-oss-120b (Groq free quota exhausted), 60 min |
| urgent | run `senior-api`, 0.30 USD | run gpt-oss-120b on the paid route, 0.000278 USD |
| budget exhausted | abstain | abstain: no level-3 route at 0 USD |
| high impact | run `senior-subscription`, source check and human review | run gpt-oss-120b, age-window reference and human review |
| unknown capability | abstain | abstain: family F4 has no TD 1 evidence |
| *age at order, customer* (added) | — | run gpt-oss-20b (Groq free), reference computed at `order_date` |
| *product, customer, OpenRouter down* (added) | — | run qwen (Groq free), 2-of-3 quorum of available level-1 models |

Among free resources, `choose` picks the least capable eligible one (key `(allocation, level, id)`). This keeps gpt-oss-120b, the only level-3 model, free for F2 questions.

### 4.4 Why `choose` runs on an available subscription before deferring for an exhausted free resource

`choose` first builds the list of **included** capacity: eligible resources that are available with `cash == 0`. An available subscription (`allocation > 0`) is in it. An exhausted free resource is not, since it is not available. So the subscription runs before `choose` even looks at resources to wait for, even when the free one refills before `deadline_minutes`. This is the right default for three reasons:

1. **No new spending either way.** The subscription is already paid, so waiting saves no cash.
2. **Waiting costs time and guarantees nothing.** A reset time is only a chance to retry. The docstring requires availability to be measured again at wake-up.
3. **Unused allocation is lost** at the end of its period.

**When to reverse it:** when the subscription allocation is scarce and still needed. For example, it is close to its limit before the end of the period, and urgent or level-3 requests that only it can serve are expected, while the current request can wait for a reliable free refill. Spending the allocation now would push those later requests to the paid API (0.30 USD in the kit) or to abstention. The same holds if the subscription charges for overage, since its marginal cost is then no longer zero. Our own portfolio has no subscription: in our version, the Groq free tier plays the role of included capacity and the Groq paid route the role of the API.

## 5. Limits, decisions and next steps

**Pair C (routing rule):**
- The rates come from twenty questions with one run each, and F2b rests on a single case (C10). The rule is a hypothesis for this batch; it should be re-measured on a new batch before it governs a customer figure or a payout.
- The deterministic references (period, product and age-window SQL templates) cover only the families seen in TD 1. A question outside F1–F3 is refused rather than routed.
- Prices and quotas in the simulator are scenario inputs (Groq prices of 2026-10-05, fixed token envelope), not measurements.
- Decision for TD 3: no free model answers F2 or F2b alone, so the checking cost of age questions is the cost of the deterministic reference, not of a quorum.

_Other pairs: to complete._

## 6. Who did what

| Pair | Members | Step |
|---|---|---|
| A | Alexandre, Maya | k-of-n vote |
| B | Yasmine Boukrouh, Marc, Mehdy | wrong consensus; C08 analysis and evidence prepared with AI assistance; team review pending |
| C | Raphael Delavictoire, Dorian Courcelle | routing rule; rule, simulator adaptation and analysis prepared with AI assistance (Claude); outputs reproduced by the pair; review of the rule pending |
