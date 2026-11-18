# TD 2 report — The quorum, then the routing rule

**Class DIA 3, sub-group 1 (DIA3-1)** · Session of 18 November 2026 · Course pack `2026-11-18-students-5`
Inputs: TD 1 outputs in [`TD1/`](../../TD1/) — no new network batch. Work files: [`TD2/`](../).

## 1. What we attempted and what we completed

| Step | Pair | Status | Evidence |
|---|---|---|---|
| 1. k-of-n vote, 2-of-3 vs 3-of-5 on C01–C20 | A | _to complete by Pair A_ | |
| 2. Wrong consensus | B | Done: two real cases from the TD 1 traces, C09 (wrong consensus wins the fixed panel) and C08 (wins no quorum), each with SQL cause, delta query and independent check; vote counts re-checked with Pair A's `vote_k_sur_n` | [section 3](#3-step-2--wrong-consensus-pair-b) |
| 3. Routing rule and simulator | C | _to complete by Pair C_ | |
| Cross-review between pairs | all | _to complete_ (review of C by B: drafted) | [section 7](#7-cross-review-between-pairs) |

Inputs are the TD 1 outputs only ([`TD1/`](../../TD1/)); no new model call was made. The prompts are unchanged since TD 1 ([`TD1/prompt/prompts-en.md`](../../TD1/prompt/prompts-en.md)).

## 2. Step 1 — k-of-n vote (Pair A)

_Method, 2-of-3 vs 3-of-5 table for C01–C20, explanation of each changed decision._

## 3. Step 2 — Wrong consensus (Pair B)

Pair B found three shared wrong values in the 100 final cells of TD 1 (C08: 25 920, C09: 0, C10: 119 410) and analysed two of them, which show the two possible outcomes for a quorum.

### 3.1 Main case — C09: the shared wrong value wins the fixed panel

Files: [`../pair-b/C09/`](../pair-b/C09/) (Marc Chen, Mehdy). Question: customers **exactly 25 on 2026-09-26**, all their orders. Reference **487 980** cents.

| Model | Value | Verdict | | Quorum | Votes | Decision |
|---|---:|---|---|---|---|---|
| gpt-oss-120b (panel) | 487 980 | correct | | **2-of-3** (120b, Cohere, Qwen) | 0: 2 · 487 980: 1 | **consensus on 0 — wrong** |
| Cohere north-mini-code (panel) | **0** | incorrect | | **3-of-5** (all five) | 487 980: 2 · 0: 2 · 369 240: 1 | **abstention** |
| Qwen 3.8 27B (panel) | **0** | incorrect | | | | |
| gpt-oss-20b | 487 980 | correct | | | | |
| Dots 3 Note | 369 240 | incorrect | | | | |

Identification and votes: [`part1-quorums.md`](../pair-b/C09/part1-quorums.md).

**SQL root cause** ([`part2-sql-cause-marc.md`](../pair-b/C09/part2-sql-cause-marc.md)) — two different bugs that both produce an empty filter, which `COALESCE(SUM(...), 0)` turns into 0:
- **Cohere** computes `('2026-09-26' - birth_date) / 365`: SQLite subtracts the leading years of the two strings (25), then integer division gives 0, so `0 = 25` is false for every customer. (Its two other predicates alone would give 487 980, but only by luck: they use 365-day years, a window shifted by 6 days.)
- **Qwen** computes the age at the **order date** instead of 2026-09-26 (the C10 convention), and its two month-day conditions contradict each other (`x >= b AND x < b`), so no row matches.

**Delta query** ([`part3-delta-mehdy.md`](../pair-b/C09/part3-delta-mehdy.md), [`delta-query.sql`](../pair-b/C09/delta-query.sql)): the six customers born in ]2000-09-26 ; 2001-09-26] — C007 118 740, C009 61 330, C008 99 090, C002 25 920, C001 135 000, C003 47 900 — are all missed, none is wrongly added: **487 980 − 0 = 487 980 cents**. Boundary: C003 (born 2001-09-26) is in, C005 (born 2000-09-26, already 26) is out.

**Independent check:** [`check_c09_csv.py`](../pair-b/C09/check_c09_csv.py) recomputes C09 from the CSV files without SQL (completed age by year, month and day) and finds the same six customers and 487 980.

### 3.2 Second case — C08: the shared wrong value wins no quorum

Files: [`../pair-b/`](../pair-b/) (Yasmine Boukrouh). Question: customers **exactly 25 on 2026-09-24**. Reference **605 580** cents. gpt-oss-20b and Dots both return **25 920**: both filters keep only customers born **on 2001-09-24** (`>= '2001-09-24' AND < '2001-09-25'`, and `= '2001-09-24'`), instead of the whole window ]2000-09-24 ; 2001-09-24]. The delta query lists five omitted customers (C004, C005, C007, C008, C009) totalling **579 660 = 605 580 − 25 920** cents, none added. Both wrong models are **outside** the fixed panel: the 2-of-3 panel returns the correct 605 580 (gpt-oss-120b + Qwen), the 3-of-5 quorum abstains (605 580: 2 · 25 920: 2 · 1 188 090: 1). Reproduce everything with `python3 TD2/pair-b/analyse.py` (hash-checked data, independent Python/CSV check).

### 3.3 Reading with Lecture 2 (correlated errors)

| Lecture 2 notion | What our two cases show |
|---|---|
| **Diagnosis: access / invalid SQL / wrong value** | All four faulty answers are **wrong values**: HTTP 200, one attempt, SQL that runs. "A query that runs is not proof of a correct result." |
| **One model, one vote; failures do not shrink the panel** | One stored answer per model (last attempt), each with its stored SQL; no model failed on C08 or C09, so n = 3 and n = 5 throughout. |
| **Mix families** | The agreeing models come from **different families** (C09: Cohere and Qwen; C08: OpenAI gpt-oss-20b and Dots) and wrote **different SQL**, yet returned the same wrong value — like the lecture's pilot case C11 (two families, two queries, both 0). Distinct families lower the risk of a shared error; they do not remove it. |
| **Stricter k: more abstentions, not more truth** | Going from 2-of-3 to 3-of-5 turns the C09 wrong consensus into an abstention, not into the right value. Had a third model shared the 0, the error would have passed with k = 3 too: a shared mistake passes with any k. |
| **Three checks in order: format, meaning, correctness** | On the answers alone, all values pass the **format** check (integer euro cents, excl. VAT) and the **meaning** check (an amount for an age group); only **correctness** catches them, and only because the lab has a reference (detail in [`part2-sql-cause-marc.md`](../pair-b/C09/part2-sql-cause-marc.md)). Reading the SQL shows a hidden meaning error for Qwen on C09: it computes the age at the order date, i.e. the convention of another question (C10) — the value looks comparable but does not describe the same thing. |
| **Choose checks that see the cause** | Re-asking the same or a stronger model adds no new information. The checks that see the cause here are **deterministic, by code**: recomputing the age window (SQL date window or the CSV script), rejecting a 0 when the window contains customers, and a boundary test on known birthdays. |
| **Lab vs. real life** | We could prove the error only because the lab has an answer key. Without it, the evidence would be distinct families + a deterministic check + samples verified by an exact query, as above. Two cases measure the mechanism, not an error rate. |

### 3.4 Consequence for checking

- **Agreement is not correctness.** Whether a shared wrong value wins depends on **who sits in the panel** (C09: both wrong models in the fixed panel → wrong consensus; C08: both outside → no effect).
- **A wider quorum abstains instead of being wrong** (3-of-5 on C08 and C09): safer, but it gives no answer, and every launched call is still paid.
- **For age questions shown to a customer or paid out, the check runs after the vote and is deterministic** (age-window recomputation, `COUNT(DISTINCT customer_id)` sanity rule, boundary test). This is the check Pair C's routing rule requires for these uses (section 4). A check in error means no delivery.

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

**Errors are not independent on age questions.** Three age cells have a wrong value shared by two models: C08 (gpt-oss-20b and dots: 25,920, analysed by Pair B in section 3), C09 (north-mini-code and qwen: 0, see [`wrong-consensus-C09`](../pair-b/C09/part3-delta-mehdy.md)) and C10 (qwen and dots: 119,410). On C09, the team's fixed panel (gpt-oss-120b, north-mini-code, qwen) returns the wrong value 0 as a 2-of-3 consensus.

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

**Pair B (wrong consensus):**
- Two cases from one run per cell at temperature 0; they show the mechanism, not a probability that a quorum is wrong.
- The vote counts were computed by hand from the stored answers, then re-run with Pair A's completed `vote_k_sur_n` on C08 and C09: identical decisions ([`check-votes-with-pair-A.py`](../pair-b/check-votes-with-pair-A.py), output [`votes-pair-A-method.jsonl`](../pair-b/votes-pair-A-method.jsonl)). The script copies `TD2/skeleton-multi-llm-en.py` next to `pair-A/sandbox_sqlite.py` in a temporary folder, because the completed skeleton does not run from `TD2/` on its own.
- `TD2/pair-b/evidence.json` records SHA-256 hashes of the source files; they were recomputed on the repository's own files (LF line endings) — a checkout with CRLF line endings gives different text-file hashes, the database hash is unaffected.

_Pair A: to complete._

## 6. Who did what

| Pair | Members | Step |
|---|---|---|
| A | Alexandre, Maya | k-of-n vote |
| B | Yasmine Boukrouh, Marc Chen, Mehdy (Mohamed Diawara) | wrong consensus — C08 (Yasmine: identification, SQL cause, delta, `analyse.py`); C09 (Marc: SQL root cause; Mehdy: identification and quorums, delta query, independent CSV check, assembly of section 3). Prepared with AI assistance (Yasmine: Codex; Marc and Mehdy: Claude); every figure re-run on the database. |
| C | Raphael Delavictoire, Dorian Courcelle | routing rule; rule, simulator adaptation and analysis prepared with AI assistance (Claude); outputs reproduced by the pair; review of the rule pending |

## 7. Cross-review between pairs

Each pair is reviewed by the two other pairs (at least two reviewers each): six reviews in [`../reviews/`](../reviews/).

| Reviewed | by A | by B | by C |
|---|---|---|---|
| A — vote | — | [review](../reviews/review-A-by-B.md) | [review](../reviews/review-A-by-C.md) |
| B — wrong consensus | [review](../reviews/review-B-by-A.md) | — | [review](../reviews/review-B-by-C.md) |
| C — routing rule | [review](../reviews/review-C-by-A.md) | [review](../reviews/review-C-by-B.md) | — |
