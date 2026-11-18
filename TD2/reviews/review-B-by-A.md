# Review of Pair B by Pair A

**Reviewers:** Alexandre (tests executed; review to validate), Maya (validation pending)
**Reviewed:** Pair B — wrong consensus, cases C08 (Yasmine) and C09 (Marc, Mohamed)
**Date:** 18 November 2026
**Method:** Source inspection and offline reproduction using the committed TD1 traces and Pair B evidence. No new model calls.

## Files reviewed

- `TD2/pair-b/README.md`, `analyse.py`, `reference.sql`, `delta.sql`, `evidence.json`, `C08-models.csv` and `delta-customers.csv`
- `TD2/pair-b/faulty-gpt-oss-20b.sql` and `faulty-dots.sql`
- `TD2/pair-b/C09/README.md`, `part1-quorums.md`, `part2-sql-cause-marc.md` and `part3-delta-mohamed.md`
- `TD2/pair-b/C09/faulty-north-mini-code.sql`, `faulty-qwen.sql`, `delta-query.sql`, `empty-filter-check.sql` and their recorded outputs
- `TD2/pair-b/C09/check_c09_csv.py`
- `TD2/pair-b/check-votes-with-pair-A.py`
- `TD1/results/traces-td1.csv` and `TD1/reference-td1.csv`

## What we re-ran and the result

All commands were executed from the repository root using the stored data, without new LLM calls.

| Check | Command | Result |
|---|---|---|
| C08 reproduction | `python TD2/pair-b/analyse.py` | **PASS.** Seven committed evidence files reproduced successfully without being overwritten. |
| C08 SQL and independent calculation | Included in `analyse.py` | **PASS.** Reference: 605580 cents; GPT-OSS 20B and Dots: 25920 cents each; missing revenue: 579660 cents across five omitted customers. |
| C09 independent calculation | `python TD2/pair-b/C09/check_c09_csv.py TD2/pair-b/data` | **PASS.** Six eligible customers, with total revenue of 487980 cents. |
| C08/C09 quorum cross-check | `python TD2/pair-b/check-votes-with-pair-A.py` | **PASS.** Previously executed after consolidation of Pair A's voting implementation. Both cases reproduced the expected 2-of-3 and 3-of-5 decisions. |

The C09 SQL evidence and recorded outputs were inspected in the repository. The C09 SQL scripts were **not independently executed** as part of this review; the separate CSV calculation verifies the reference total.

## What is correct

**1. Pair B identifies a genuine wrong-consensus case.**

For C09, Cohere and Qwen both return 0 against the reference of 487980 cents. Their two votes form an incorrect 2-of-3 consensus. The 3-of-5 quorum abstains because no value receives three votes.

**2. The SQL explanations distinguish two different errors.**

Cohere performs invalid date-string arithmetic, while Qwen uses an unsuitable order-date age calculation with contradictory month-day conditions. Both produce empty selections, leading to the same incorrect numerical answer.

**3. C08 provides useful complementary evidence.**

GPT-OSS 20B and Dots both return 25920 cents rather than 605580. Their filters retain only a single birth date instead of the complete one-year age interval. The missing customers explain the entire 579660-cent discrepancy. Unlike C09, the shared wrong answer wins neither required quorum.

**4. The independent verification is reproducible.**

C08's script verifies the SQLite database, recorded traces, faulty queries, delta and independent CSV computation. Its default check mode does not rewrite committed evidence.

C09's CSV script independently confirms the six qualifying customers and the reference amount using completed-age arithmetic rather than the model-generated SQL.

**5. The conclusions respect the distinction between agreement and correctness.**

Pair B does not claim that two agreeing models establish a correct answer. Its proposed deterministic age-window check is a reasonable safeguard, and the documentation identifies it as a proposal rather than an implemented production guarantee.

## Issues found

| # | File / component | Issue | Severity | Suggested improvement |
|---|---|---|---|---|
| 1 | C09 verification workflow | Unlike C08's `analyse.py`, the C09 workflow does not provide a single automated, non-writing check that reruns its SQL evidence and compares all recorded outputs. The CSV reference calculation is separately reproducible. | Low | Add a read-only `--check` workflow for C09 that runs the faulty SQL, empty-filter query and delta query, then compares the results to the committed evidence. |
| 2 | `C09/check_c09_csv.py` | The script uses `sys.argv[1]` without validating its command-line arguments. Running it without the data-directory argument causes an `IndexError` instead of a useful usage message. | Low | Use `argparse` to require and validate the dataset path. |
| 3 | Pair B's proposed `age-window-nonempty` check | The proposed check is motivated by C09 but is not implemented or tested as an executable delivery gate. A nonempty age window alone also cannot verify that a nonzero revenue total is correct. | Low | Implement a deterministic test, include positive and negative cases, and distinguish a nonempty-window sanity check from full numerical verification. |

The earlier draft raised issues about missing faulty SQL clauses, `COALESCE` and the C09 folder's explanatory text. Pair B subsequently addressed those points in `delta-query.sql` and `C09/README.md`; they are not repeated as unresolved findings here.

## Questions to the authors

1. Could C09 have an automated check mode comparable to C08's, so an independent reviewer can verify all SQL evidence with one command?
2. Would the proposed `age-window-nonempty` check only reject suspicious zero results, or would it also verify the complete revenue calculation before delivery?
3. What would Pair B recommend for age-related questions when the deterministic reference is unavailable: abstention, a different panel or mandatory human review?

## Overall assessment

**The main analysis is supported by reproducible evidence.** The C08 checks passed, the C09 reference was independently recomputed, and the recorded quorum outcomes agree with Pair A's implementation.

The remaining findings concern additional automation, usability and the proposed production safeguard. They do not invalidate the two demonstrated cases.

**Review status:** Technical review drafted from inspected sources and executed tests. Final approval by both Pair A reviewers is pending.

## Authors' answer

_Answer by Pair B, written by Mohamed Diawara with AI assistance (Claude), to be validated by Marc Chen and Yasmine Boukrouh._

| # | Answer | Status |
|---|---|---|
| 1 | Accepted and fixed. New [`pair-b/C09/check_c09.py`](../pair-b/C09/check_c09.py): one command, **read-only** (it writes nothing). It checks the data against `manifest.json` (line endings normalised, so it also passes on Windows), re-runs `faulty-north-mini-code.sql` and `faulty-qwen.sql` (both 0), the delta query (compared with `delta-output.csv`) and the empty-filter check (compared with `empty-filter-check.csv`), and recomputes C09 without SQL. `python3 TD2/pair-b/C09/check_c09.py` → **16/16 checks OK**, exit code 0. | done |
| 2 | Accepted and fixed. `check_c09_csv.py` now uses `argparse`, defaults to `TD2/pair-b/data`, accepts `--data <folder>` (the old positional form still works) and stops with a clear message if a CSV file is missing, instead of an `IndexError`. | done |
| 3 | Accepted and fixed. The gate `age-window-nonempty` is now **executable and tested** in `check_c09.py`, on positive and negative cases: Cohere 0 → reject, Qwen 0 → reject (6 customers with orders in the window), a true 0 (age 80, empty window) → accept. As you point out, a non-empty window does not verify a non-zero total, so the two checks are kept separate: the gate only judges a 0, and a **full numerical check** (recompute the window's revenue by code, compare with the value) judges every value — gpt-oss-120b 487 980 → accept, Dots 369 240 → reject. | done |

**Answers to the questions**

1. Yes: `python3 TD2/pair-b/C09/check_c09.py` (C09) mirrors `python3 TD2/pair-b/analyse.py` (C08). Both are read-only by default.
2. The gate `age-window-nonempty` only rejects suspicious zeros (Lecture 2: a missing value is not zero — a 0 can hide an empty filter). The complete revenue is verified by the separate full numerical check, which recomputes the age window by code; it is the check required before delivery for customer-facing or paid-out age figures.
3. Without a deterministic reference, we would not deliver an age figure on a vote alone (C09 shows a 2-of-3 panel adopting a wrong value): **abstain** for a customer-facing figure, **mandatory human review** for a payout, and at most an unchecked value logged as such for an internal dashboard. A different panel lowers the risk (distinct families) but, as C09 shows with two families agreeing on 0, it does not remove it.
