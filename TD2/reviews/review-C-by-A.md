# Review of Pair C by Pair A

**Reviewers (at least two):** Alexandre Flavigny, Maya Bourrey (Pair A)

**Reviewed:** Pair C — routing rule by Raphaël Delavictoire and Dorian Courcelle: [`../pair-C/`](../pair-C/), section 4 of [`../reports/td2.md`](../reports/td2.md)

**Date:** 18 November 2026

**Status:** Technical review completed on policy `pairC-v2.2`.

Reference for the checks: Lecture 2 (routing priorities, eligibility, checking according to stakes, evidence and reproducibility) and the TD2 assignment, Step 3.

## Files reviewed

- `TD2/pair-C/atelier-routage.py` — original routing simulator.
- `TD2/pair-C/atelier-routage-adapted.py` — adapted simulator, policy `pairC-v2.2`.
- `TD2/pair-C/routing-rule-C.md` — family-level eligibility, checks and fallbacks.
- `TD2/pair-C/README.md` — reproduction instructions and rationale.
- `TD2/pair-C/output-before.jsonl` and `output-after.jsonl` — committed simulation results.
- Section 4 of `TD2/reports/td2.md`.
- TD1 family rates and references as recorded in the team's reports.
- Previous reviews `review-C-by-B.md` and `review-C-by-A.md`, including Pair C's responses.

## What we re-ran and the result

All tests were executed offline from the repository root on Windows, using the existing Python implementation. No API calls were made, and no committed files were modified.

### 1. Reproduction of the committed simulations

| Check | Command / method | Result |
|---|---|---|
| Original simulator | Execute `python TD2/pair-C/atelier-routage.py`; parse JSON lines and compare with `output-before.jsonl` | ✅ PASS — all **7 scenarios** match exactly. |
| Adapted simulator | Execute `python TD2/pair-C/atelier-routage-adapted.py`; parse JSON lines and compare with `output-after.jsonl` | ✅ PASS — all **10 scenarios** match exactly. |
| Evidence integrity | Compare parsed JSON records, including routing decisions, checks, resources and reasons | ✅ PASS — no difference in any of the 17 records. |

Both scripts reproduced the committed evidence exactly.

### 2. Independent targeted tests

Pair A imported `atelier-routage-adapted.py` and called `family_level()` and `choose()` with additional requests. These tests were separate from the ten predefined scenarios.

| Category | Verified behaviour | Result |
|---|---|---|
| Combined families | `F1+F2` and `F2+F1` both map to level 3 | ✅ PASS |
| Combined families | `F3+F2b` maps to level 2 | ✅ PASS |
| Unsupported input | Unknown family `F4` abstains | ✅ PASS |
| Unsupported input | Unknown use `marketing` abstains | ✅ PASS |
| Unsupported input | Missing `use` abstains | ✅ PASS |
| Dashboard checks | F1 dashboard selects format-check rung 0 | ✅ PASS |
| Customer checks | F1 customer selects quorum rung 1 | ✅ PASS |
| Age checks | F2 customer selects deterministic-reference rung 2 | ✅ PASS |
| Age checks | F2b dashboard selects deterministic-reference rung 2 | ✅ PASS |
| High-stakes checks | Payout selects reference and human-review rung 3 | ✅ PASS |
| Quota management | Deferrable F2 request waits for refill | ✅ PASS |
| Paid fallback | Urgent F2 request selects `gpt-oss-120b-groq-dev` | ✅ PASS |
| Budget management | Zero-budget F2 request with no waiting abstains | ✅ PASS |
| Traceability | All ten scenarios record `pairC-v2.2` | ✅ PASS |
| Output consistency | All ten scenarios use floating-point `cash` values | ✅ PASS |
| Explanations | Every scenario identifies excluded resources | ✅ PASS |

**Result: 16/16 targeted checks passed.**

### 3. Additional robustness probe

A separate test removed the `family` field from an otherwise valid request.

**Observed result:**

```text
MISSING FAMILY LIMITATION: KeyError 'family'
```

The simulator correctly handles unknown family values and missing `use`, but a missing `family` causes an exception.

This is a new finding in version `pairC-v2.2`, distinct from the missing-`use` issue previously reported and fixed.

### 4. Routing decisions and cost

| Scenario | Observed adapted decision | Result |
|---|---|---|
| Simple F1 dashboard | Run Dots free, format check | ✅ |
| Complex F2 dashboard | Run GPT-OSS 120B free, format check | ✅ |
| Deferrable F2 | Defer GPT-OSS 120B free for 60 minutes | ✅ |
| Urgent F2 | Run GPT-OSS 120B paid, **$0.000278** | ✅ |
| Zero-budget urgent F2 | Abstain | ✅ |
| High-impact F2 payout | GPT-OSS 120B free, deterministic reference and human review | ✅ |
| Unknown F4 | Abstain | ✅ |
| F2b dashboard | GPT-OSS 20B free, deterministic reference | ✅ |
| F2b customer | GPT-OSS 20B free, deterministic reference | ✅ |
| F3 customer, OpenRouter unavailable | Qwen free, 2-of-3 quorum specified | ✅ |

The paid-route estimate is consistent with the stated token envelope:

\[
\frac{650(0.15)+300(0.60)}{10^6}
=0.0002775\text{ USD}
\]

Rounded to six decimals, this is **$0.000278**.

These are simulated prices and availability states, not measured provider costs.

## What is correct

- **The adapted simulation reproduces exactly.** All ten recorded scenarios match the implementation, and the original seven scenarios also reproduce. This makes the before/after comparison inspectable.

- **The original routing priority is preserved.** The implementation considers available included capacity first, then waiting for a refill, then eligible paid resources within budget, and finally abstention.

- **Eligibility reflects the observed TD1 evidence.** The rule separates F1/F3 (level 1), F2b (level 2) and F2 (level 3). The policy treats these rates as evidence from a limited batch, not as guarantees of future performance.

- **Family combinations are handled consistently.** The order of components no longer affects the chosen capability level. Unknown family values are refused rather than assigned unsupported eligibility.

- **Difficulty and stakes are separated.** Family difficulty determines eligible models, while intended use determines the starting verification level. Additional evidence requirements can increase the verification level.

- **The verification policy recognises correlated errors.** Age-related queries use deterministic references instead of relying solely on agreement between models. This is justified by the shared wrong values observed in TD1 cases C08, C09 and C10.

- **The F1/F3 quorum policy uses distinct model families.** Pair C removed the earlier F2b quorum containing two GPT-OSS models. Its documented F1/F3 customer panel draws from different model providers.

- **The decision logs are substantially improved.** Records include the policy version, check identifier, check rationale, failure policy, selected resource and excluded-resource reasons.

- **Failure handling is explicitly described.** The written policy states that a failed or unavailable check prevents delivery. Customer figures lead to abstention, while payout questions go to human review.

- **Previously identified defects have been corrected.** Pair A's tests confirm the missing-`use`, combined-family-order and floating-point consistency fixes. Inspection also confirms that the reference-age predicate was aligned with Pair B's formulation.

## Issues found

The following findings apply to the current `pairC-v2.2` implementation. Previously resolved issues are not counted as open defects.

| # | File / component | Issue | Severity | Suggested fix |
|---|---|---|---|---|
| 1 | `atelier-routage-adapted.py`, `choose()` | **Missing `family` raises `KeyError`.** The function initially uses `request.get("family")`, but the unknown-family branch subsequently accesses `request["family"]`. Pair A reproduced the exception with an otherwise valid request. | **medium** | Replace the direct access with `request.get("family")`, so a missing family follows the existing abstention path. Add a regression test for missing, unknown and malformed family values. |
| 2 | `atelier-routage-adapted.py`, `choose()` and `check_for()` | **Quorum feasibility is described but not checked by the simulator.** For F1/F3 customer requests, the decision names a 2-of-3 check without assembling an actual panel or verifying that three distinct models are available. The simulator's scope is documented, but availability-dependent quorum feasibility remains an execution requirement. | **clarification** | Specify that an executing service must verify three distinct eligible models before launching the quorum. If fewer than three are available, it should defer, use an authorised deterministic check or abstain. A simulation-only guard would also make this requirement visible. |
| 3 | `atelier-routage-adapted.py`, unsupported-input branches | **Abstention records have different structures.** Unknown-family and unknown-use paths omit `checks.status` and `checks.on_failure`, which are present on ordinary decisions. A downstream reader expecting a uniform schema could fail. | low | Use a common decision-record schema, including an explicit check status and a consistent failure or handover policy for unsupported inputs. |
| 4 | `pair-C/README.md`, file overview | **The scenario count is outdated.** The description of `output-after.jsonl` still says “the 7 kit scenarios + 2 of ours”, although the latest simulator and committed evidence contain **10 scenarios**, including three additional cases. | low | Update the file overview to say “7 kit scenarios + 3 additional scenarios”. |

**Scope distinction:** Issue 1 was directly reproduced. Issues 2–4 follow from inspection of the current code and documentation. Issue 2 is a question about integration beyond the routing simulator, not a claim that a promised execution-time quorum check failed.

### Follow-up on the previous Pair A review

| Previous finding | Current status | Verification |
|---|---|---|
| Missing or unknown `use` caused `KeyError` | ✅ Fixed | Both cases now abstain in independent tests. |
| Combined family ordering was inconsistent | ✅ Fixed | `F1+F2`, `F2+F1` and `F3+F2b` tested successfully. |
| `cash` type varied across branches | ✅ Fixed | All ten recorded scenarios use floats. |
| Age-reference notation differed from Pair B | ✅ Fixed in documentation | Predicate now uses the backward date window. Pair C reports having verified equivalent results on the SQLite data; Pair A did not independently rerun those database queries in this round. |
| Two findings involving `pair-b/C09/README.md` | Not applicable | They concern Pair B, not Pair C, as the authors correctly pointed out. |

## Questions to the authors

1. **Input validation:** Would Pair C accept a regression test requiring missing `family` to produce an abstention rather than a `KeyError`, consistent with how missing `use` is handled?

2. **Quorum feasibility:** If an F1/F3 customer request has fewer than three distinct eligible models available, which fallback should be used? Could the simulator explicitly report that a quorum cannot currently be formed?

3. **Uniform output schema:** Should unsupported-family and unsupported-use results carry the same `checks.status` and `checks.on_failure` fields as ordinary decisions to simplify downstream processing?

4. **Age-reference verification:** Pair C reports that its corrected age predicates match the TD1 reference values on the supplied database. Would an automated regression test for boundary dates, including leap-day births on synthetic data, be useful before extending this policy beyond the TD1 dataset?

5. **Policy limits:** The F2b eligibility evidence comes from only C10 and C18. What additional validation would Pair C require before using this routing policy for customer-facing figures outside the course's 20-question batch?

## Authors' answer

**Existing response from Pair C (Raphaël Delavictoire, Dorian Courcelle) to the earlier Pair A review, preserved here.** The answers below concern the original findings, not the new follow-up issues above.

Pair C accepted and addressed points 3–6 in policy `pairC-v2.2`. Points 1 and 2 of the original draft concerned Pair B's C09 files and were correctly identified as outside Pair C's responsibility.

| Previous issue | Pair C's response |
|---|---|
| 3 — Unknown `use` | Fixed. `CHECKS[level][use]` was removed. The current `choose()` checks `request.get("use")` and abstains with human review for unknown or missing uses. |
| 4 — Family order | Fixed. `family_level()` splits the string on `+` and takes the maximum required level across components. Unknown components still cause abstention. |
| 5 — Inconsistent `cash` type | Fixed. Decision branches return floating-point cash values; the ten committed records were regenerated. |
| 6 — Age predicate | Fixed in the rule. `REF_AGE` now uses `date(ref,'-26 years') < birth_date <= date(ref,'-25 years')`, with the corresponding order-date predicate for F2b. Pair C reports that both formulations matched TD1 references on the supplied database; no leap-day births were present. |

**New follow-up findings (current review):**

**From Pair C (Raphaël Delavictoire, Dorian Courcelle).** Answers checked against the current `atelier-routage-adapted.py` (policy `pairC-v2.2`, commit `a38500d`); `python3 TD2/pair-C/atelier-routage-adapted.py` still reproduces `output-after.jsonl` exactly.

| # | Answer | Status |
|---|---|---|
| 1 | Yes. It is already the behaviour of the current code: `family_level()` returns `None` for a missing, empty or unknown family, and `choose()` then **abstains** with human review, exactly like a missing `use`. Re-tested with no `family` key, `family=None` and `family=""`: all three give `abstain`, check `pairC-v2.2-human`, no `KeyError`. | done |
| 2 | Accepted as a limit. The simulator **names** the 2-of-3 quorum but does not count how many distinct eligible models are available: with a single available model it still returns `run` with the quorum text. The intended fallback is the use's `on_failure` (customer: abstain, "no verified figure yet"; payout: human review), since a quorum that cannot be formed is a check that cannot pass. Reporting "quorum not formable" explicitly is the next change to the simulator. | open (documented) |
| 3 | Already uniform. Every record, including unsupported family and unsupported use, carries the same `checks` fields: `id`, `check`, `why`, `status`, `on_failure`. | done |
| 4 | Yes, useful. Today the age predicates are only checked against the TD 1 references (C02, C08, C09, C10, C11) on the supplied database, which has no 29 February birth. A test on synthetic data with births on the boundary days (exactly 25 and 26 years, and 29 February) is needed before any use outside TD 1. | open (documented) |
| 5 | Two cells (C10, C18) are not enough to rely on the model. That is why the rule never uses a quorum on age families: the **deterministic reference** stays mandatory before delivery. Before customer-facing use outside the 20 questions, we would require more F2/F2b cases with known references, the boundary test of question 4, and the deterministic reference for every age figure. Without a reference, the answer stays abstain (customer) or human review (payout). | answered |

## Review conclusion

**The implemented routing policy passes all reproduced scenarios and 16 additional targeted tests.** The main routing logic, verification levels, fallbacks and decision records are consistent with the stated TD2 design.

The missing-family `KeyError` is no longer reproducible in `pairC-v2.2` (see the authors' answer, question 1). The quorum-feasibility and schema observations concern robustness and integration beyond the predefined scenarios; they do not invalidate the reported simulation results.

**Assessment:** Technically satisfactory for the TD2 routing-simulation scope, with minor follow-up corrections recommended before final sign-off.

## Technical follow-up after the final corrections

The findings from this review were revisited after additional corrections to the routing simulator.

| Finding | Final technical status | Resolution |
|---|---|---|
| 1. Missing `family` raises `KeyError` | Fixed | The simulator now uses `request.get("family")`, allowing missing and unsupported families to produce an abstention rather than an exception. |
| 2. Quorum feasibility | Clarified | The README now explicitly states that the simulator selects and describes checks but does not execute them. An executing system must verify that three distinct eligible models are available before performing a 2-of-3 quorum. If the quorum cannot be assembled, it must not deliver an unverified result. |
| 3. Inconsistent abstention schema | Fixed | Unsupported-family and unsupported-use results now contain `checks.status` and `checks.on_failure`, consistent with the regular decision records. |
| 4. Incorrect scenario count | Fixed | The README now correctly identifies seven original scenarios and three additional scenarios. |

### Regression verification

The updated simulator was checked against the ten committed simulation scenarios. The routing decisions remain unchanged. The only recorded evidence difference is the addition of check metadata for the unsupported-family scenario.

Additional tests confirm that missing or unsupported family and use fields produce abstentions with consistent check metadata.

**Final technical assessment:** The reproducible implementation defects identified in this review have been corrected. Quorum execution remains outside the simulator's scope and is documented as an integration requirement. The TD2 routing simulations remain reproducible.

This follow-up records the technical corrections; it does not constitute a separate absent team member's approval.