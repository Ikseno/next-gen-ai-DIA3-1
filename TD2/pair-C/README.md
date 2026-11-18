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

## Before / after

| Scenario | Before (kit) | After (our rule) |
|---|---|---|
| simple | run `small-free` | run `dots-3-note-free`, check: none (F1 6/6) |
| complex | run `senior-subscription` | run `gpt-oss-120b-groq-free`, check: none, logged as unchecked (F2 4/4) |
| deferrable | defer `senior-subscription`, 60 min | defer `gpt-oss-120b-groq-free`, 60 min (Groq free quota exhausted) |
| urgent | run `senior-api`, 0.30 USD | run `gpt-oss-120b-groq-dev`, 0.000278 USD |
| budget exhausted | abstain | abstain (no level-3 route at 0 USD) |
| high impact | run `senior-subscription` + source check and human review | run `gpt-oss-120b-groq-free` + age-window reference + human review |
| unknown capability | abstain | abstain: family F4 has no TD 1 evidence |
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
