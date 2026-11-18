# TD 2 report — The quorum, then the routing rule

**Class DIA 3, sub-group 1 (DIA3-1)** · Session of 18 November 2026 · Course pack `2026-11-18-students-5`
Inputs: TD 1 outputs in [`TD1/`](../../TD1/) — no new network batch. Work files: [`TD2/`](../).

## 1. What we attempted and what we completed

| Step | Pair | Status | Evidence |
|---|---|---|---|
| 1. k-of-n vote, 2-of-3 vs 3-of-5 on C01–C20 | A | Done: implementation, tests and 20-case comparison completed | [section 2](#2-step-1--k-of-n-vote-pair-a) |
| 2. Wrong consensus | B | Done: two real cases from the TD 1 traces, C09 (wrong consensus wins the fixed panel) and C08 (wins no quorum), each with SQL cause, delta query and independent check; vote counts re-checked with Pair A's `vote_k_sur_n` | [section 3](#3-step-2--wrong-consensus-pair-b) |
| 3. Routing rule and simulator | C | Done: routing policy and simulations completed; 7 original and 10 adapted scenarios reproduced | [section 4](#4-step-3--routing-rule-pair-c) |
| Cross-review between pairs | all | All six reviews written and answered | [section 7](#7-cross-review-between-pairs) |

Inputs are the TD 1 outputs only ([`TD1/`](../../TD1/)); no new model call was made. The prompts are unchanged since TD 1 ([`TD1/prompt/prompts-en.md`](../../TD1/prompt/prompts-en.md)).

## 2. Step 1 — k-of-n vote (Pair A)

### 2.1 Implementation and experimental protocol

Pair A (Alexandre and Maya) implemented `Orchestrateur.vote_k_sur_n` and compared two predefined voting configurations using the recorded TD1 traces for C01–C20, without making new model calls.

- **2-of-3:** GPT-OSS 120B, Cohere North Mini Code and Qwen 27B, with `k = 2`.
- **3-of-5:** all five TD1 models (GPT-OSS 120B, GPT-OSS 20B, Cohere North Mini Code, Qwen 27B and Dots 3 Note), with `k = 3`.

The voting algorithm applies a strict-majority threshold (`n // 2 < k <= n`), with one vote per distinct `(provider, model_requested)` pair. Duplicate model identities are rejected. Failed or unavailable models remain part of the original panel size but do not vote. Missing values are never interpreted as zero.

The offline comparison uses the final recorded attempt for each model and question. Only successful answers with an integer value and an associated SQL query are eligible to vote. Reference values are used **only after the vote** to determine whether the accepted result is correct.

If no value reaches the fixed quorum, the system abstains. It never lowers the threshold retrospectively or invents an answer. Abstentions require independent verification or human review before any result can be delivered.

### 2.2 Experimental results

| Outcome | 2-of-3 | 3-of-5 |
|---|---:|---:|
| Correct consensus | 16 | 17 |
| Incorrect consensus | 1 | 0 |
| Abstention | 3 | 3 |
| **Total** | **20** | **20** |

**Complete C01?C20 comparison (values in euro cents).** For abstentions, the vote count is the largest group of agreeing proposals, below the required threshold. Correctness is assessed against the reference only after voting.

| Case | Reference | 2-of-3 decision | Votes | Correct? | 3-of-5 decision | Votes | Correct? |
|---|---:|---:|---:|---|---:|---:|---|
| C01 | 792,800 | 792,800 | 3 | Correct | 792,800 | 5 | Correct |
| C02 | 590,320 | 590,320 | 2 | Correct | 590,320 | 3 | Correct |
| C03 | 936,350 | 936,350 | 3 | Correct | 936,350 | 5 | Correct |
| C04 | 2,826,250 | 2,826,250 | 3 | Correct | 2,826,250 | 5 | Correct |
| C05 | 38,480 | 38,480 | 3 | Correct | 38,480 | 5 | Correct |
| C06 | 0 | 0 | 3 | Correct | 0 | 5 | Correct |
| C07 | 13,970 | 13,970 | 3 | Correct | 13,970 | 5 | Correct |
| C08 | 605,580 | 605,580 | 2 | Correct | Abstain | 2 | ? |
| C09 | 487,980 | 0 | 2 | Wrong | Abstain | 2 | ? |
| C10 | 558,980 | Abstain | 1 | ? | Abstain | 2 | ? |
| C11 | 446,690 | 446,690 | 2 | Correct | 446,690 | 3 | Correct |
| C12 | 1,666,490 | 1,666,490 | 3 | Correct | 1,666,490 | 5 | Correct |
| C13 | 107,740 | 107,740 | 3 | Correct | 107,740 | 5 | Correct |
| C14 | 0 | 0 | 3 | Correct | 0 | 5 | Correct |
| C15 | 168,680 | Abstain | 1 | ? | 168,680 | 3 | Correct |
| C16 | 376,740 | 376,740 | 3 | Correct | 376,740 | 4 | Correct |
| C17 | 258,180 | Abstain | 1 | ? | 258,180 | 3 | Correct |
| C18 | 62,480 | 62,480 | 2 | Correct | 62,480 | 3 | Correct |
| C19 | 1,990 | 1,990 | 2 | Correct | 1,990 | 4 | Correct |
| C20 | 1,106,090 | 1,106,090 | 3 | Correct | 1,106,090 | 5 | Correct |

The [detailed comparison CSV](td2-task-A-comparison.csv) also records the supporting model identities and changed-decision explanations.

Four decisions changed between the two configurations:

| Case | 2-of-3 | 3-of-5 | Explanation |
|---|---|---|---|
| C08 | Correct: 605,580 | Abstention | Two votes support the correct value, but three are required in the larger panel. |
| C09 | Incorrect: 0 | Abstention | Cohere and Qwen agree on the wrong value, while the reference is 487,980. Their two votes do not reach the larger quorum. |
| C15 | Abstention | Correct: 168,680 | Three models agree in the larger panel, reaching the quorum. |
| C17 | Abstention | Correct: 258,180 | Three models agree in the larger panel, reaching the quorum. |

The remaining 16 cases produced unchanged decisions.

The table below gives the exact final-attempt values (integer euro cents) and verdicts from the stored TD1 traces for the four changed cases:

| Case | Reference | GPT-OSS 120B | North | Qwen | GPT-OSS 20B | Dots |
|---|---:|---|---|---|---|---|
| C08 | 605580 | 605580 correct | 1188090 wrong | 605580 correct | 25920 wrong | 25920 wrong |
| C09 | 487980 | 487980 correct | 0 wrong | 0 wrong | 487980 correct | 369240 wrong |
| C15 | 168680 | 168680 correct | 314020 wrong | 0 wrong | 168680 correct | 168680 correct |
| C17 | 258180 | 258180 correct | 0 wrong | 248490 wrong | 258180 correct | 258180 correct |

For C17, Qwen's value of 248490 is its second attempt, following an HTTP 429 response. Only the final attempt counts, so retries never create additional votes.

### 2.3 Interpretation and limitations

The 3-of-5 configuration avoids the incorrect C09 consensus and recovers correct answers for C15 and C17, but loses the correct C08 consensus. Increasing both the panel size and the threshold therefore changes the balance between accepted answers, errors and abstentions.

A quorum establishes agreement, **not correctness**. C09 demonstrates that different model families can produce the same incorrect value through different SQL mistakes, as analysed by Pair B in Section 3.

The five-model panel also contains two GPT-OSS models from the same family, so its votes are not fully independent. Furthermore, the experiment changes both panel composition and quorum threshold; it cannot isolate the effect of changing `k` alone.

C10 provides another warning: the 3-of-5 panel abstains on a two-versus-two tie between the correct value 558980 and the shared wrong value 119410. If a third model had returned 119410, the quorum would have accepted a wrong result.

On C19, North Mini Code matches the reference by chance despite using an incorrect age condition. A numerically correct answer therefore does not establish that the underlying SQL reasoning is valid.

These results describe only 20 recorded TD1 questions and do not establish general error rates. Accepted answers still require appropriate independent checks before delivery.

### 2.4 Reproducibility

The experiments use `TD1/results/traces-td1.csv` and `TD1/reference-td1.csv`. No new model calls were made.

Run from the repository root:

```powershell
python TD2/pair-A/atelier-vote.py
python TD2/pair-A/td2_compare_votes.py
```

Evidence:

- [`../pair-A/td2_compare_votes.py`](../pair-A/td2_compare_votes.py) — comparison script.
- [`td2-task-A-comparison.csv`](td2-task-A-comparison.csv) — detailed 20-case results.
- [`td2-vote-synthetic.jsonl`](td2-vote-synthetic.jsonl) — synthetic voting tests.
- [`td2-vote-real.jsonl`](td2-vote-real.jsonl) — real-trace tests.
- [`td2-task-A-report.md`](td2-task-A-report.md) — supplementary Pair A report.

The experimental results were obtained by running the offline scripts against the recorded TD1 traces.

## 3. Step 2 — Wrong consensus (Pair B)

Pair B found three shared wrong values in the 100 final cells of TD 1 (C08: 25 920, C09: 0, C10: 119 410) and analysed two of them, which show the two possible outcomes for a quorum.

### 3.1 Main case — C09: the shared wrong value wins the fixed panel

Files: [`../pair-b/C09/`](../pair-b/C09/) (Marc Chen, Mohamed). Question: customers **exactly 25 on 2026-09-26**, all their orders. Reference **487 980** cents.

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

**Delta query** ([`part3-delta-mohamed.md`](../pair-b/C09/part3-delta-mohamed.md), [`delta-query.sql`](../pair-b/C09/delta-query.sql)): the six customers born in ]2000-09-26 ; 2001-09-26] — C007 118 740, C009 61 330, C008 99 090, C002 25 920, C001 135 000, C003 47 900 — are all missed, none is wrongly added: **487 980 − 0 = 487 980 cents**. Boundary: C003 (born 2001-09-26) is in, C005 (born 2000-09-26, already 26) is out.

**Independent check:** [`check_c09_csv.py`](../pair-b/C09/check_c09_csv.py) recomputes C09 from the CSV files without SQL (completed age by year, month and day) and finds the same six customers and 487 980.

**Empty-filter check:** [`empty-filter-check.sql`](../pair-b/C09/empty-filter-check.sql) re-runs the two faulty `WHERE` clauses, stored verbatim in [`faulty-north-mini-code.sql`](../pair-b/C09/faulty-north-mini-code.sql) and [`faulty-qwen.sql`](../pair-b/C09/faulty-qwen.sql), with `COUNT(DISTINCT customer_id)`. Both keep **0 lines and 0 customers**, against 68 lines and 6 customers for the correct window ([output](../pair-b/C09/empty-filter-check.csv)), so their 0 is an empty filter.

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

**Errors are not independent on age questions.** Three age cells have a wrong value shared by two models: C08 (gpt-oss-20b and dots: 25,920, analysed by Pair B in section 3), C09 (north-mini-code and qwen: 0, see [`pair-b/C09`](../pair-b/C09/part3-delta-mohamed.md)) and C10 (qwen and dots: 119,410). On C09, the team's fixed panel (gpt-oss-120b, north-mini-code, qwen) returns the wrong value 0 as a 2-of-3 consensus.

### 4.2 The rule

A question with an age condition is routed as F2 or F2b, whatever else it contains. A combination takes the rule of its strictest part. If the age reference (a given date or the order date) is not stated, the question is sent back for clarification.

**Principle (policy `pairC-v2.2`, after Lecture 2 and the reviews by Pairs B and A):** difficulty chooses the model, stakes choose the check. The use alone sets the starting check (dashboard: format check by code; customer: 2-of-3 quorum of distinct families; payout: deterministic reference + human review). The TD 1 evidence can only raise it: format only needs the chosen model at 100 % on at least 3 cells, and on age families the quorum is replaced by the deterministic reference. The reference is compared with the model's value; a failed or erroring check means no delivery (dashboard recomputed, customer abstains, payout to human review).

| Family | First model | Internal dashboard | Figure shown to a customer | Amount paid out | Fallback |
|---|---|---|---|---|---|
| **F1**, **F3** | dots-3-note (free), 10/10 | format check only, by code (every model 10/10) | 2-of-3 quorum of the three cheapest available models among dots, north, qwen, gpt-oss-20b (all 10/10) | deterministic reference + human review (period / product SQL template) | north → qwen (Groq free) → gpt-oss-20b → wait for refill if deferrable → abstain |
| **F2** | gpt-oss-120b, 4/4 (and 4/4 combined) | format check only, by code (gpt-oss-120b 8/8 on F2 and combined) | deterministic reference: age window `date(ref,'-26 years') < birth_date <= date(ref,'-25 years')` (same predicate as Pair B) | deterministic reference + human review | No other model is 100 % on F2. Wait for the Groq refill if deferrable (the six HTTP 429 of TD 1 all recovered on attempt 2), else paid Groq route within budget, else abstain from the model route and hand over to the deterministic reference template or a person (outside the simulator) |
| **F2b** (also F2b + F3) | gpt-oss-20b, 1/1 (gpt-oss-120b 1/1 too) | deterministic reference, age at `order_date` (gpt-oss-20b 2/2 only: too thin for format only; no quorum on age) | deterministic reference, age computed at `order_date` | deterministic reference + human review | gpt-oss-120b → wait for refill if deferrable → paid Groq route → abstain and hand over (outside the simulator) |

dots-3-note goes before north-mini-code for F1/F3 (both free) because north produced the only invalid SQL of TD 1 (C11) and a value correct by chance (C19). No quorum is accepted for customer or payout figures on age questions, because of the shared wrong values above.

### 4.3 Simulator: before and after adaptation

`python3 TD2/pair-C/atelier-routage.py` gives [`output-before.jsonl`](../pair-C/output-before.jsonl). In [`atelier-routage-adapted.py`](../pair-C/atelier-routage-adapted.py), `RESOURCES` holds our five models: the free routes used in TD 1, plus the Groq paid route for gpt-oss-20b, gpt-oss-120b and qwen. The cash for one request assumes 650 input + 300 output tokens; the largest TD 1 cell used 1,333 tokens. Eligibility levels come from 4.1: level 1 = F1/F3, level 2 = F2b, level 3 = F2, and each model gets the highest level it passed entirely. Each `reason` cites the TD 1 cells. `choose` keeps the kit's priority order, but the request now gives a family and a use, and the check follows the principle above. Each decision logs `policy`, a check id with `status` and `on_failure`, the `reason` with its TD 1 cells (paid route and abstention included), and `ruled_out`: every resource not chosen, with why (for example "level 1 below level 3 (TD 1: 5/8)"). An abstention adds `handover`. Output: [`output-after.jsonl`](../pair-C/output-after.jsonl), reproduced identically on Windows by the pair.

| Scenario | Before (kit) | After (our rule) |
|---|---|---|
| simple | run `small-free` | run dots-3-note (free), format check only (10/10) |
| complex | run `senior-subscription` | run gpt-oss-120b (Groq free), format check only (8/8) |
| deferrable | defer `senior-subscription`, 60 min | defer gpt-oss-120b (Groq free quota exhausted), 60 min |
| urgent | run `senior-api`, 0.30 USD | run gpt-oss-120b on the paid route, 0.000278 USD |
| budget exhausted | abstain | abstain: no level-3 route at 0 USD |
| high impact | run `senior-subscription`, source check and human review | run gpt-oss-120b, age-window reference and human review |
| unknown capability | abstain | abstain: family F4 has no TD 1 evidence |
| *age at order, dashboard* (added) | — | run gpt-oss-20b (Groq free), deterministic reference at `order_date` (2/2 too thin for format only) |
| *age at order, customer* (added) | — | run gpt-oss-20b (Groq free), reference computed at `order_date` |
| *product, customer, OpenRouter down* (added) | — | run qwen (Groq free), 2-of-3 quorum of available level-1 models |

Among free resources, `choose` picks the least capable eligible one (key `(allocation, level, id)`). This keeps gpt-oss-120b, the only level-3 model, free for F2 questions.

The cross-review by Pair B (C1 to C5, [`review-C-by-B.md`](../reviews/review-C-by-B.md)) led to version `pairC-v2.1`; the review by Pair A (unknown use, family order, cash type, age predicate, [`review-C-by-A.md`](../reviews/review-C-by-A.md)) to `pairC-v2.2`. The answers are in those files.

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
- The vote counts were computed by hand from the stored answers, then re-run with Pair A's completed `vote_k_sur_n` on C08 and C09: identical decisions ([`check-votes-with-pair-A.py`](../pair-b/check-votes-with-pair-A.py), output [`votes-pair-A-method.jsonl`](../pair-b/votes-pair-A-method.jsonl)). The cross-check now uses the authoritative implementation and supporting files from `TD2/pair-A/`.
- `TD2/pair-b/evidence.json` records SHA-256 hashes of the source files. Text files are hashed with line endings normalised to LF and `.gitattributes` keeps the data files byte-identical, so `analyse.py` gives the same result on Windows (CRLF) and macOS/Linux (LF). `analyse.py` only checks by default and writes nothing (`--write` regenerates the evidence).
- Next steps for TD 3:
  - integrate the already implemented and tested `age-window-nonempty` check into the end-to-end post-vote workflow for age questions (F2, F2b). A 0 is delivered only if the age window really holds no customer, and the check identifier and result are logged.
  - pass any value that the check rejects to the deterministic reference or to human review, as section 4 requires for customer and payout figures. The check could be extended to other filters where `COALESCE(SUM(...), 0)` can hide an empty selection (period, product list).

**Pair A:** Implementation and 20-case comparison completed; see Section 2.

## 6. Who did what

| Pair | Members | Step |
|---|---|---|
| A | Alexandre, Maya | k-of-n vote |
| B | Yasmine Boukrouh, Marc Chen, Mohamed Diawara | wrong consensus — C08 (Yasmine: identification, SQL cause, delta, `analyse.py`); C09 (Marc: SQL root cause; Mohamed: identification and quorums, delta query, independent CSV check, assembly of section 3). Every figure was re-run on the database. |
| C | Raphaël Delavictoire, Dorian Courcelle | routing rule; Raphaël and Dorian developed the rule, adapted the simulator and prepared the analysis; they reproduced the outputs and answered the cross-reviews |

## 7. Cross-review between pairs

Each pair is reviewed by the two other pairs (at least two reviewers each): six reviews in [`../reviews/`](../reviews/).

| Reviewed | by A | by B | by C |
|---|---|---|---|
| A — vote | — | [review](../reviews/review-A-by-B.md) | [review](../reviews/review-A-by-C.md) |
| B — wrong consensus | [review](../reviews/review-B-by-A.md) | — | [review](../reviews/review-B-by-C.md) |
| C — routing rule | [review](../reviews/review-C-by-A.md) | [review](../reviews/review-C-by-B.md) | — |

## 8. AI assistance (declared)

AI-assisted work is accepted in this module when it is declared and the decisions are explained (see [`TD1/prompt/README.md`](../../TD1/prompt/README.md)). This section is the single place where the AI assistance used in TD 2 is declared; the other TD 2 files do not repeat it.

| Who | Assistant | Used for | How it was checked |
|---|---|---|---|
| Pair A — Alexandre Flavigny, Maya Bourrey | AI tools (coding and drafting support) | `vote_k_sur_n`, comparison script, Pair A report | Offline test outputs and the course's voting contract; review by Pairs B and C |
| Pair B — Yasmine Boukrouh | Codex | C08 analysis and `analyse.py`; Windows re-runs of `analyse.py` and `check_all.py` recorded in the reviews | `analyse.py` compares every evidence file; 7/7 OK on Windows |
| Pair B — Marc Chen | Claude (Anthropic) | C09 SQL root cause, `check-votes-with-pair-A.py`, Pair B's answer to review B-by-C, draft of review A-by-B | Every query re-run read-only on the database |
| Pair B — Mohamed Diawara | Claude (Anthropic) | C09 quorums and delta, `check_c09_csv.py`, `check_c09.py`, `check_all.py`, assembly of section 3, Pair B's answer to review B-by-A, internal re-run of `analyse.py` | `python3 TD2/pair-b/check_all.py`: 4/4 steps (C09 19/19) |
| Pair C — Raphaël Delavictoire, Dorian Courcelle | Claude (Anthropic) | Routing rule and adapted simulator, Pair C's answers to reviews C-by-A and C-by-B | `atelier-routage-adapted.py` reproduces `output-after.jsonl` exactly |

No model or assistant answer was used as a reference value: every figure comes from the database, the TD 1 traces or the deterministic reference queries. The prompts sent to the models are unchanged since TD 1.

