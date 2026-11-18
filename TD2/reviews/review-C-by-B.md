# Review of Pair C by Pair B

**Status:** Technical review.
**Reviewers:** Yasmine Boukrouh ; Marc and Mehdy.
**Reviewed:** Pair C — Dorian Courcelle and Raphaël Delavictoire.

## Files reviewed

`TD2/pair-C/{README.md,routing-rule-C.md,atelier-routage.py,atelier-routage-adapted.py,output-before.jsonl,output-after.jsonl}`, section 4 of `TD2/reports/td2.md`, and the team's TD1 merged traces and references. The assignment's Step 3 consistency constraint is the acceptance criterion; optional suggestions below are distinguished from failures.

## What was re-run

The checks below were run offline from the repository root: both simulators (`python TD2/pair-C/atelier-routage.py`, `python TD2/pair-C/atelier-routage-adapted.py`), compared with the committed outputs, and the family rates recomputed from the final attempt per cell of `TD1/results/traces-td1.csv`.

| Check | Result |
|---|---|
| Original routing simulator | All 7 decisions exactly match `output-before.jsonl`, after parsing JSON. |
| Adapted routing simulator | All 9 decisions exactly match `output-after.jsonl`, after parsing JSON. |
| Family rates | All 30 cells match independent recomputation from the final attempt per provider/model/question in the 106-row merged CSV (100 final cells). |
| Retry handling | Rates are final-attempt rates, not first-attempt reliability. They do not establish future quota recovery. |
| Urgent paid route | 650 input and 300 output tokens at 0.15/0.60 USD per million = 0.0002775 USD, rounded to 0.000278. This is a simulated budget estimate, not a measured provider cost. |
| Unknown family | F4 explicitly abstains rather than borrowing unsupported eligibility. |

Recomputed rates, in the same model order as the rule:

| Family | North | Dots | GPT-OSS 20B | GPT-OSS 120B | Qwen |
|---|---|---|---|---|---|
| F1 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| F3 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| F2 | 0/4 | 2/4 | 1/4 | 4/4 | 3/4 |
| F2b | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| F2 + F1/F3 | 2/4 | 3/4 | 4/4 | 4/4 | 1/4 |
| F2b + F1 | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 |

## What is correct

- The rule limits unchecked single-model answers to low-stakes dashboards and families where the chosen model scored 100% on the observed batch. Customer and payout uses require a quorum or deterministic check, as the assignment requires.
- The exact family cells and rates support the proposed eligibility. Keeping C19's correct-by-chance caveat is useful; the observed verdict should not be silently changed when calculating the empirical rate.
- Availability is synthetic scenario input and the script makes no provider calls. Free and paid routes are distinguished.
- The original priority is correctly explained: available included capacity precedes waiting for an exhausted free route; a concrete reversal condition is preserving scarce allocation for later urgent or high-difficulty requests.
- The OpenRouter-down product scenario chooses Qwen because all free routes have zero immediate cash cost and the tie-breaker selects the lowest eligible capability level before GPT-OSS 20B. This is explained in `pair-C/README.md`; the earlier review's question on this point is answered by the existing code and README.

## Issues and requested clarifications

| ID | File / line or cell | Finding | Severity | Suggested action |
|---|---|---|---|---|
| C1 | `routing-rule-C.md:3` | Both source links use `../TD1/`, which resolves inside TD2 and is broken. | low | Use `../../TD1/`. |
| C2 | `atelier-routage-adapted.py:54–62,112,114`; urgent and budget-exhausted scenarios | Paid-route reasons identify only a model alias (`A, same model ...`), and the abstention reason contains no TD1 cells. Step 3 explicitly asks for the justifying cells in every decision's reason. | medium | Carry the family/case evidence into paid-route and abstention reasons, rather than relying on readers following an alias. |
| C3 | `routing-rule-C.md:38–39`; adapted `choose:108–114` | The written age fallback includes running the deterministic reference alone. The simulator has no deterministic resource or branch: the budget-exhausted F2 scenario abstains although the rule offers this fallback. | medium | State that deterministic fallback is outside this simulator, or model it explicitly and regenerate outputs. Clarify whether the reference replaces the model or compares against it. |
| C4 | `routing-rule-C.md:39`; `atelier-routage-adapted.py:67` | The F2b dashboard panel contains both GPT-OSS 20B and 120B, which are the same family. This weakens the distinct-family principle and makes two agreeing votes potentially correlated. | medium | Prefer distinct families, or explicitly justify this exception and retain a deterministic check. Do not claim independence of the two GPT-OSS votes. |
| C5 | Rule's customer/payout checks; simulator `checks` field | Checks are described as strings, not executed; disagreement, check failure and unavailable checker behaviour are not specified. This is acceptable for a routing simulator, but not evidence that a delivered amount was checked. | clarification | Define no delivery on unresolved check failure; state the customer abstention / payout review path and label simulated checks clearly. |

## Questions to Pair C

1. Is the deterministic-reference-only fallback implemented elsewhere, or intentionally excluded from this simulation? Please align the written rule and the simulated scope.
2. What is the rule for an ambiguous F2 versus F2b question, or an unseen F2b + product combination? The simulator abstains for unrecognised strings; specify whether this is the intended classification policy.
3. Can the paid/abstention reasons cite the actual family cases, and can you justify or revise the two-GPT-OSS F2b quorum?

## Corrections to the earlier draft review

A 2-of-3 customer check on F1/F3 is **not itself an assignment violation**: Step 3 permits a quorum or a deterministic check; it does not mandate 3-of-5 plus deterministic checking for every customer figure. The earlier concern may be a conservative policy suggestion, not a compliance defect. The Qwen-versus-20B free-route choice is already explained in the README. No claim of checking extra Lecture 2 material is made in this revision.

## Authors' answer

Pending — to be completed by Pair C. The existing explanation of the Qwen tie-breaker is acknowledged above; no new author reply is invented.

## Review conclusion

The published simulations reproduce and all family rates match the team's traces. Request clarification/correction of the evidence in reasons, deterministic fallback scope and F2b family diversity before final approval.
