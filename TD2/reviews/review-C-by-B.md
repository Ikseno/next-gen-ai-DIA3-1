# Review of Pair C by Pair B

**Status:** Technical review.
**Reviewers:** Yasmine Boukrouh ; Marc and Mohamed.
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

**From Pair C (Raphaël Delavictoire, Dorian Courcelle).** Thank you: every point is accepted. The simulator is now policy `pairC-v2.1`; `output-after.jsonl` was regenerated (10 scenarios: one was added for the F2b dashboard case, so the re-run should expect 10 decisions, not 9). Later changes after the review by Pair A are in version `pairC-v2.2`.

| ID | Answer | Where |
|---|---|---|
| C1 | Fixed: both links now use `../../TD1/`. | `routing-rule-C.md`, line 3 |
| C2 | Fixed: the paid resources carry the full TD 1 evidence of their model (no more alias), and the abstention reason lists the cells of the level and the eligible models with their rates, e.g. "level-3 cells C02 C08 C09 C11 C15 C16 C17 C19: eligible in TD 1 = gpt-oss-120b-groq-free 8/8, gpt-oss-120b-groq-dev 8/8". | `RESOURCES`, last branch of `choose` |
| C3 | Aligned: the deterministic-reference-only fallback is **outside** the simulator. `choose` abstains from the model route and returns a `handover` field ("the deterministic reference query if a template exists for this exact question, otherwise a person"). The rule now says that the reference is **compared with** the model's value in the normal path and **replaces** it only in this hand-over. | `routing-rule-C.md` ("What deterministic reference means here"), `choose` |
| C4 | Revised: the F2b dashboard quorum with two gpt-oss models is removed. On age families the quorum rung is replaced by the deterministic reference (shared wrong values C08, C09, C10), and gpt-oss-20b has only 2 F2b cells, too few for format only. The only remaining quorum (F1/F3, customer) draws from four different makers. | `check_for`, `routing-rule-C.md` ("Panel diversity") |
| C5 | Specified: each `checks` record now has `status` ("simulated: named here, executed by code before delivery") and `on_failure`: a failed or erroring check means no delivery; dashboard recomputed at the next run, customer abstains ("no verified figure yet"), payout goes to human review. | `ON_FAILURE`, `check_for` |

**Q1:** see C3: intentionally excluded from the simulation, now stated in the rule and in every abstention record.
**Q2:** a reference date in the question means F2; age at the time of each order means F2b; if the text does not say which, the question is sent back for clarification (no model call). Unseen combinations take their strictest part: `F2b+F3` and `F2b+F1+F3` are now level 2 in `FAMILY_LEVEL`; anything outside C01–C20 still abstains.
**Q3:** yes for the reasons (C2); the two-gpt-oss quorum is removed (C4).

Other change made at the same time, after Lecture 2 (final version): "none" is replaced by "format check by code", the use alone sets the starting check and the TD 1 evidence can only raise it, and each decision logs `policy`, the check id and `ruled_out` (every resource not chosen, with why).

## Review conclusion

The published simulations reproduce and all family rates match the team's traces. Request clarification/correction of the evidence in reasons, deterministic fallback scope and F2b family diversity before final approval.

## Technical follow-up — fixes verified on Windows

18 November 2026, verification follow-up on Yasmine's Windows machine (with Codex assistance), based on `8156c0e`. The original findings above refer to the earlier snapshot; the current routing policy is `pairC-v2.2`.

- **C1 resolved:** the rule's two TD1 links now resolve through `../../TD1/`.
- **C2 resolved:** urgent paid-route and budget-abstention reasons cite the family evidence and exact case IDs.
- **C3 resolved:** the rule explicitly distinguishes normal comparison from deterministic-only handover outside the simulator; the budget-exhausted decision records the handover.
- **C4 resolved:** the former two-GPT-OSS F2b quorum is replaced by a deterministic reference. The new F2b dashboard scenario records that reference.
- **C5 resolved for this simulator:** supported-family decisions name the simulated check and no-delivery failure behaviour. Unknown families abstain explicitly; no execution of the named checks by the simulator is claimed.

Reran both published simulators and compared parsed JSON with the committed outputs: **7/7 original and 10/10 adapted scenarios match**. Additional assertions check C2 evidence, C3 handover, C4's deterministic age reference and C5 failure records. All passed; no saved output was regenerated. The earlier nine-scenario result remains historical.

**Technical conclusion:** C1–C5 are addressed in the current files. This closes the technical change requests from this review; it does not fabricate human signatures or claim that simulated delivery checks have run against a live request.
