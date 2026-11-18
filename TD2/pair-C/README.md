# TD 2 — Pair C: routing rule

Draft for section 4 of [`../reports/td2.md`](../reports/td2.md).

| File | Content |
|---|---|
| [`routing-rule-C.md`](routing-rule-C.md) | One-page rule per family: TD 1 rates and cells, first model, check level per use, fallback |
| [`atelier-routage.py`](atelier-routage.py) | Kit simulator, unchanged |
| [`output-before.jsonl`](output-before.jsonl) | `python3 atelier-routage.py` (the 7 kit scenarios) |
| [`atelier-routage-adapted.py`](atelier-routage-adapted.py) | `RESOURCES` and `choose` adapted to our rule |
| [`output-after.jsonl`](output-after.jsonl) | `python3 atelier-routage-adapted.py` (the 7 kit scenarios + 2 of ours) |

## What we changed in the simulator

- **`RESOURCES`**: the three fictional resources are replaced by our five TD 1 models. There are eight resources: the free routes used in TD 1 (OpenRouter free for C and E, Groq free tier for A, B and D) and the documented Groq Developer paid route for A, B and D. Cash is the price of one request of 650 input + 300 output tokens at the 2026-10-05 Groq prices (the largest TD 1 cell was 1 333 tokens).
- **Eligibility levels from TD 1**: level 1 = F1 and F3 (all five models 10/10). Level 2 = F2b (C10, C18): only B and A are right. Level 3 = F2 (C02 C08 C09 C11 and C15 C16 C17 C19): only A is right on all of them. Each resource has an `evidence` string with its TD 1 cells, which is copied into every `reason`.
- **`choose`**: the priority order is unchanged. The request now gives a `family` and a `use` (`dashboard`, `customer`, `payout`) instead of `difficulty` and `high_impact`. The check comes from the rule table. A family not covered by C01–C20 is refused ("no eligibility evidence").
- **Policy v2 (after Lecture 2, final version)**: the check is no longer read from a family × use table. The use alone sets the starting rung (dashboard = format check by code, customer = 2-of-3 quorum, payout = reference + human review); the TD 1 evidence can only raise it (format only needs 100 % on at least 3 cells; on age families the quorum rung becomes the reference). Each step is logged in `checks.why`.
- **Policy v2.1 (after review C-by-B)**: paid-route and abstention reasons now cite the TD 1 cells; each check carries `status` (simulated) and `on_failure` (no delivery: dashboard recomputed, customer abstains, payout to human review); an abstention carries `handover` (deterministic reference template or a person, outside the simulator); F2b + F3 combinations are level 2; the two-gpt-oss F2b quorum is removed. See [`../reviews/review-C-by-B.md`](../reviews/review-C-by-B.md), section "Authors' answer".
- **Policy v2.2 (after review C-by-A)**: an unknown or missing `use` abstains to human review instead of raising `KeyError`; families are parsed in any order (`F1+F2` = `F2+F1`, level = strictest part); `cash` is always a float; the age reference is written as Pair B's predicate `date(ref,'-26 years') < birth_date <= date(ref,'-25 years')`, checked equal to the references of C02, C08, C09, C10 (at `order_date`) and C11 on `data/boutique.sqlite`. See [`../reviews/review-C-by-A.md`](../reviews/review-C-by-A.md).
- **Decision log**: every result now carries `policy` (`pairC-v2.2`), a check id (`pairC-v2.2-rung-N`) and `ruled_out`, the list of resources not chosen with the reason ("level 1 below level 3 (TD 1: 5/8)", "unavailable (quota exhausted), refill in 60 min"), as in the lecture's decision log.

## Before / after

| Scenario | Before (kit) | After (our rule) |
|---|---|---|
| simple | run `small-free` | run `dots-3-note-free`, check: format only (dots 10/10 on F1/F3) |
| complex | run `senior-subscription` | run `gpt-oss-120b-groq-free`, check: format only (120b 8/8 on F2) |
| deferrable | defer `senior-subscription`, 60 min | defer `gpt-oss-120b-groq-free`, 60 min (Groq free quota exhausted) |
| urgent | run `senior-api`, 0.30 USD | run `gpt-oss-120b-groq-dev`, 0.000278 USD |
| budget exhausted | abstain | abstain (no level-3 route at 0 USD) |
| high impact | run `senior-subscription` + source check and human review | run `gpt-oss-120b-groq-free` + age-window reference + human review |
| unknown capability | abstain | abstain: family F4 has no TD 1 evidence |
| *age at order, dashboard* | — | run `gpt-oss-20b-groq-free` + reference at `order_date` (20b 2/2: too thin for format only; no quorum on age) |
| *age at order, customer* | — | run `gpt-oss-20b-groq-free` + reference computed at `order_date` |
| *product, customer, OpenRouter down* | — | run `qwen3.8-27b-groq-free` + 2-of-3 quorum of available level-1 models |

`choose` takes the **least capable** eligible model among free resources (key `(allocation, level, id)`). That keeps gpt-oss-120b, the only level-3 model, free for F2 questions, and it is why qwen (level 1) comes before gpt-oss-20b (level 2) when OpenRouter is down.

## Why `choose` runs on an available subscription before deferring for an exhausted free resource

In the kit, `choose` first looks for **included** capacity: any eligible resource that is available with `cash == 0`. An available subscription (`cash == 0`, `allocation > 0`) is in that list. A free resource that is exhausted is not, because it is not `available`. So the subscription runs **before** the code even looks at the `waiting` list, even if the free resource refills before `deadline_minutes`. The reasons:

1. **The marginal cost is zero in both cases.** The subscription is already paid. Running on it now costs no new cash, and waiting saves no money, only some allocation.
2. **Waiting costs time and is not a guarantee.** The docstring says it: reaching a reset time does not prove capacity is back. A refill is only a chance to try again (in TD 1 our six HTTP 429 all recovered on attempt 2, but that is six cases on one day).
3. **Unused allocation is lost.** A subscription allocation that is not used before its period ends gives nothing back, so using it is the better use of money already spent.

**When the priority should be reversed:** when the subscription allocation is scarce and still needed later. For example, the allocation is close to its limit before the end of the period, and urgent or high-difficulty requests (level 3, can't wait) are expected that only it can serve, while the current request is deferrable and the free resource reliably refills before the deadline. Then spending the allocation now pushes a later urgent request to the paid API (`senior-api`, 0.30 USD) or to abstain. The same holds if the subscription has an overage charge, because its marginal cost is then no longer zero. In that case the rule should be "defer to the free refill first, keep the subscription for what cannot wait".

**Caveat:** our portfolio has no subscription. The Groq free tier plays the role of included capacity, and the Groq Developer route plays the role of the paid API. The rates come from twenty questions, one run each: a routing hypothesis for this batch, not a guarantee.
