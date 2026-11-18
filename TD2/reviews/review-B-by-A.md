# Review of Pair B by Pair A

**Reviewers (at least two):** Alexandre (technical review and tests completed), Maya (validation pending)

**Reviewed:** Pair B — wrong consensus: C08 in [`../pair-b/`](../pair-b/) (Yasmine Boukrouh), C09 in [`../pair-b/C09/`](../pair-b/C09/) (Marc Chen, Mohamed Diawara), section 3 of [`../reports/td2.md`](../reports/td2.md)

**Date:** 18 November 2026

**Status:** Technical review completed; awaiting validation by both Pair A reviewers.

Reference for the checks: Lecture 2 (quorum voting, independent verification, evidence and reproducibility, wrong agreement) and the TD2 assignment, Step 2.

All analyses use the recorded TD1 answers. No new LLM calls were made.

## Files reviewed

- **`TD2/pair-b/` (C08):** `README.md`, `analyse.py`, `reference.sql`, `faulty-gpt-oss-20b.sql`, `faulty-dots.sql`, `delta.sql`, `delta-customers.csv`, `C08-models.csv`, `evidence.json` and `data/manifest.json`.
- **`TD2/pair-b/C09/`:** `README.md`, `part1-quorums.md`, `part2-sql-cause-marc.md`, `part3-delta-mohamed.md`, `faulty-north-mini-code.sql`, `faulty-qwen.sql`, `delta-query.sql`, `delta-output.csv`, `empty-filter-check.sql`, `empty-filter-check.csv` and `check_c09_csv.py`.
- **Cross-check:** `TD2/pair-b/check-votes-with-pair-A.py` and `votes-pair-A-method.jsonl`.
- **Original data:** `TD1/results/traces-td1.csv`, `TD1/reference-td1.csv` and the distributed SQLite/CSV dataset.

## What we re-ran and the result

Tests were run from the repository root on Windows using the committed data. The scripts did not make network requests.

| Check | Command | Result |
|---|---|---|
| C08 evidence reproduction | `python TD2/pair-b/analyse.py` | ✅ **PASS.** All seven generated evidence files matched the committed versions: `reference.sql`, both faulty SQL files, `delta.sql`, `delta-customers.csv`, `C08-models.csv`, `evidence.json`. No files were rewritten. |
| C08 reference and faulty values | Included in `analyse.py` | ✅ Reference **605580** cents; GPT-OSS 20B and Dots each return **25920** cents. |
| C08 independent delta | Included in `analyse.py` | ✅ Five omitted customers, total **579660** cents. The difference is exactly 605580 − 25920. |
| C09 independent CSV verification | `python TD2/pair-b/C09/check_c09_csv.py TD2/pair-b/data` | ✅ **PASS.** Six eligible customers, total **487980** cents. |
| C08/C09 quorum integration | `python TD2/pair-b/check-votes-with-pair-A.py` | ✅ Previously re-run successfully after Pair A's implementation was consolidated. Decisions match both cases' documented quorums. |
| C09 SQL evidence | Inspection of `delta-query.sql`, `empty-filter-check.sql` and stored outputs | ⚠️ Evidence present and internally consistent with the independent CSV check; these SQL scripts were not separately executed during this review. |

### Verification of the quorum results

The final recorded answers are:

| Model | C08 (reference 605580) | C09 (reference 487980) |
|---|---|---|
| GPT-OSS 120B | 605580 ✅ | 487980 ✅ |
| GPT-OSS 20B | **25920 ❌** | 487980 ✅ |
| Cohere North Mini Code | 1188090 ❌ | **0 ❌** |
| Qwen 27B | 605580 ✅ | **0 ❌** |
| Dots 3 Note | **25920 ❌** | 369240 ❌ |

The quorum decisions are:

| Case | Fixed 2-of-3 panel | All five, k=3 |
|---|---|---|
| C08 | Correct consensus on **605580**, 2 votes | Abstention; maximum 2 votes |
| C09 | **Wrong consensus on 0**, 2 votes | Abstention; maximum 2 votes |

These results agree with Pair A's `vote_k_sur_n` implementation and the original TD1 references.

**Independent C09 CSV result:**

| Customer | Birth date | Revenue (cents) |
|---|---|---:|
| C007 | 2000-11-30 | 118740 |
| C009 | 2001-03-10 | 61330 |
| C008 | 2001-05-15 | 99090 |
| C002 | 2001-09-24 | 25920 |
| C001 | 2001-09-25 | 135000 |
| C003 | 2001-09-26 | 47900 |
| **Total** | | **487980** |

This confirms the reference independently of either faulty model query.

## What is correct

- **Two complementary cases of shared incorrect answers.** C09 demonstrates a wrong consensus actually adopted by the fixed panel, whereas C08 demonstrates a shared wrong answer that fails to reach either required quorum. This distinction is important: the outcome depends on panel composition, not only on how many models agree.

- **The SQL root causes are identified precisely.** On C08, GPT-OSS 20B and Dots both select customers born on a single date instead of the full interval corresponding to age 25. On C09, Cohere performs inappropriate arithmetic on date strings while Qwen calculates age using the order date with contradictory conditions. These different errors produce the same numerical result of zero.

- **The delta queries explain the complete discrepancies.** For C08, five omitted customers contribute 579660 cents. For C09, the faulty filters exclude all six eligible customers, explaining the entire 487980-cent difference. The analysis also discusses boundary dates to justify inclusion and exclusion.

- **The reference is independent of the model-generated SQL.** Both cases are checked using Python calculations on the original CSV data, with completed-age arithmetic. Agreement between SQL replay and an independently written calculation provides stronger evidence than simply comparing two LLM answers.

- **The voting decisions are evaluated correctly.** The quorum is computed before consulting the reference. The reference is used afterwards to classify a retained answer as correct or incorrect. A zero is treated as a numerical value, while missing answers are excluded from voting.

- **C08 is reproducible without changing the repository.** `analyse.py` verifies the SQLite and CSV evidence against hashes, executes the stored SQL and compares newly calculated results with committed files. Its default mode is read-only with respect to evidence generation, and the Windows run completed successfully.

- **The conclusions avoid unjustified generalisation.** Pair B uses these cases to demonstrate a failure mechanism, not to estimate a general probability that quorum voting is wrong. The proposed deterministic `age-window-nonempty` check is described as a safeguard rather than an already validated production system.

## Issues found

| # | File / component | Issue | Severity | Suggested fix |
|---|---|---|---|---|
| 1 | `pair-b/C09/` — SQL verification workflow | **C09 does not provide a single automated, non-writing replay equivalent to C08's `analyse.py`.** The SQL delta, empty-filter results and independent CSV calculation exist, but their agreement must be checked using separate commands and manual comparisons. | **medium** | Add a C09 verification script that executes the stored SQL read-only, compares the results to `delta-output.csv` and `empty-filter-check.csv`, then verifies the independent CSV total. It should exit with a nonzero status if any comparison fails. |
| 2 | `pair-b/check-votes-with-pair-A.py` | **The cross-check prints decisions without asserting the expected values.** If a future change breaks the voting algorithm and changes C08/C09 outcomes, the script can still finish successfully, leaving the reviewer to detect the discrepancy manually. | **medium** | Add assertions for the four expected case/panel decisions, consensus values and vote counts, or compare the generated records programmatically against the committed `votes-pair-A-method.jsonl`. |
| 3 | `pair-b/C09/check_c09_csv.py` | **The independent check prints the total but does not verify it against the expected reference automatically.** A different total would still result in a successful process exit. | low | Accept an expected total as an optional argument or compare with `TD1/reference-td1.csv`; fail explicitly when the values differ. |
| 4 | `pair-b/C09/check_c09_csv.py` | **Command-line arguments are not validated.** The script accesses `sys.argv[1]` directly, so omitting the data path produces an exception rather than a documented usage error. | low | Use `argparse` with a required directory argument and check the existence of the expected CSV files. |
| 5 | Proposed `age-window-nonempty` safeguard | **The proposed delivery check is not yet an executable, tested component.** Detecting an empty age filter would catch C09, but verifying that customers exist does not establish that the revenue aggregation is correct for nonzero results. | low | Implement the check and test it against C08, C09, a genuinely empty age window and a deliberately incorrect nonzero result. Specify when full deterministic recomputation is required. |

**Previously reported issues already resolved:** The earlier draft identified missing faulty SQL excerpts, absent `COALESCE`, and missing explanatory text in the C09 folder. Pair B subsequently addressed these issues by updating `delta-query.sql`, preserving both faulty queries and adding the explanatory takeaway in `C09/README.md`. They are therefore not counted as unresolved findings.

These issues concern verification automation and robustness. They do not invalidate the numerical evidence established by the reproduced cases.

## Questions to the authors

1. **Automated verification:** Could the C09 analysis be consolidated into a read-only verification command, equivalent to `analyse.py` for C08, so that all its SQL results and the independent reference are tested automatically?

2. **Quorum testing:** Would Pair B consider turning `check-votes-with-pair-A.py` into a regression test that fails when a previously verified voting decision changes?

3. **Production safeguards:** Is the proposed `age-window-nonempty` test intended as a preliminary sanity check or as a sufficient condition for delivering a revenue figure? How should the system verify incorrect but nonzero aggregates?

4. **Fallback decision:** Since C09 produces a wrong 2-of-3 consensus while C08 produces a correct 2-of-3 consensus but a 3-of-5 abstention, which quorum and independent-check policy would Pair B recommend for customer-facing age queries?

5. **Reproducibility:** Would Pair B prefer a single verification command for both C08 and C09, producing a summary that records the input hashes, expected outputs and whether each check passed?

## Authors' answer

_Answer by Pair B to the revised review (5 issues, 5 questions), written by Mohamed Diawara with AI assistance (Claude), to be validated by Marc Chen and Yasmine Boukrouh. All commands run from the repository root, read-only._

| # | Answer | Status |
|---|---|---|
| 1 | Accepted and fixed. New [`pair-b/C09/check_c09.py`](../pair-b/C09/check_c09.py): one read-only command. It checks the data against `manifest.json` (line endings normalised, so it passes on Windows), re-runs `faulty-north-mini-code.sql` and `faulty-qwen.sql` (both 0), the delta query (compared with `delta-output.csv`), the empty-filter check (compared with `empty-filter-check.csv`), recomputes C09 without SQL, and exits with status 1 if any comparison fails. Result: **19/19 checks OK**. | done |
| 2 | Accepted and fixed. [`check-votes-with-pair-A.py`](../pair-b/check-votes-with-pair-A.py) is now a **regression test**: each of the four decisions (C08/C09 × 2-of-3/3-of-5) is compared with the committed `votes-pair-A-method.jsonl` (consensus, value, votes, models); it prints `OK`/`DIFF` and exits with status 1 if one changed. Result: 4/4 decisions unchanged. | done |
| 3 | Accepted and fixed. `check_c09_csv.py` compares its total with the expected value (by default C09 in `TD1/reference-td1.csv`, or `--expected <cents>`) and exits with an explicit `FAIL` when they differ (tested with `--expected 1`). | done |
| 4 | Accepted and fixed. `check_c09_csv.py` now uses `argparse` (`--data`, default `TD2/pair-b/data`; the old positional form still works) and stops with a clear message if a CSV file is missing. | done |
| 5 | Accepted and fixed. The gate `age-window-nonempty` is executable and tested in `check_c09.py`, **separately** from a full numerical check (recompute the age window's revenue by code and compare). Tested on C09 (Cohere 0 and Qwen 0 → gate reject; gpt-oss-120b 487 980 → full check accept; Dots 369 240 → full check reject), on **C08** (gpt-oss-20b/Dots 25 920 and Cohere 1 188 090 → full check reject; gpt-oss-120b/Qwen 605 580 → accept) and on a **genuinely empty window** (age 80 → a 0 is accepted). | done |

**Answers to the questions**

1. Yes: `python3 TD2/pair-b/C09/check_c09.py` is the C09 equivalent of `analyse.py`.
2. Yes, done (issue 2).
3. `age-window-nonempty` is only a **preliminary sanity check** on zeros (Lecture 2: a missing value is not zero; a 0 can hide an empty filter). It is never sufficient to deliver a figure. Non-zero aggregates, wrong or right, are verified by the **full numerical check**, which recomputes the age window's revenue by code; that check is what decides delivery.
4. For customer-facing age queries, no quorum is enough on its own: 2-of-3 adopted a wrong 0 on C09, and 3-of-5 abstained on both cases (and would let a shared error through if a third model shared it). We recommend: first model gpt-oss-120b (4/4 on F2 in TD 1), then the **full numerical check after the vote**, whatever k is; on disagreement, **abstain** (customer) or **human review** (payout). This is consistent with Pair C's rule (section 4 of `td2.md`).
5. Yes: [`pair-b/check_all.py`](../pair-b/check_all.py) runs the four checks above, prints the SHA-256 of the inputs (traces, references, database, Pair A's skeleton) and one PASS/FAIL line per step, and exits with status 1 if one fails. Result: **4/4 steps passed**.

Windows verification follow-up (18 November 2026, Codex on Yasmine's machine): after integrating the team's concurrent fixes at `af7f935`, `python TD2/pair-b/check_all.py` passes **4/4 steps**. This includes all seven C08 evidence comparisons, C09's **19/19 checks**, the independent C09 CSV total against the reference, and the four vote regression comparisons. No evidence was regenerated. These results confirm the technical fixes in the authors' answer above; remaining human reviewer validation is not represented as completed by this automated check.
