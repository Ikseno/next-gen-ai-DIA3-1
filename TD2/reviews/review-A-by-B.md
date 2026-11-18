# Review of Pair A by Pair B

**Reviewers (at least two):** Marc Chen (Pair B); second Pair B reviewer Yasmine Boukrouh and Mohamed Diawara 
**Reviewed:** Pair A (Alexandre, Maya) — k-of-n vote: `vote_k_sur_n` in [`../pair-A/skeleton-multi-llm-en.py`](../pair-A/skeleton-multi-llm-en.py), [`../pair-A/td2_compare_votes.py`](../pair-A/td2_compare_votes.py), [`../reports/td2-task-A-report.md`](../reports/td2-task-A-report.md), [`../reports/td2-task-A-comparison.csv`](../reports/td2-task-A-comparison.csv), sections 1 and 2 of [`../reports/td2.md`](../reports/td2.md)
**Date:** 18 November 2026 (state of `main` at commit `26ff494`)
. Every check below was re-run on a clean copy of the repository; it must be read and validated by both reviewers before signing._

Reference for the checks: Lecture 2 ([cm2](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/diaporama/cm2-en.html), quorum slides 15–19, evidence slide 7, comparable answers slides 9–14, wrong agreement slides 20–23) and the TD 2 assignment (Step 1 and "What is expected").

## Files reviewed

- `TD2/pair-A/skeleton-multi-llm-en.py`: compared with `TD1/skeleton-multi-llm-en.py`. The only change is the body of `vote_k_sur_n` (lines 627–673).
- `TD2/skeleton-multi-llm-en.py`: a second, different implementation of `vote_k_sur_n` (uploaded in `7967fcd`), compared with the `pair-A/` one.
- `TD2/pair-A/atelier-vote.py`, `TD2/pair-A/sandbox_sqlite.py`, `TD2/pair-A/td2_compare_votes.py`, in full.
- `TD2/reports/td2-task-A-report.md`, `td2-task-A-comparison.csv`, `td2-vote-real.jsonl`, `td2-vote-synthetic.jsonl`.
- `TD2/reports/td2.md`, section 2 and the Pair A row of section 1.

## What we re-ran and the result

All runs were made on a clean copy of `main` at `26ff494` (Linux, Python 3.13), so that no committed file could be changed.

| Check | Command | Result |
|---|---|---|
| Synthetic examples | `python3 TD2/pair-A/atelier-vote.py` | ✅ agreement → consensus 100 (2 votes) · disagreement → abstention (1) · unavailable → abstention (1) · wrong consensus → consensus 0, `matches_reference: false`. Same as `td2-vote-synthetic.jsonl`. |
| 20-question comparison | `python3 TD2/pair-A/td2_compare_votes.py` | ✅ Runs from the repository root. 2-of-3: 16 correct, 1 wrong (C09), 3 abstentions. 3-of-5: 17 correct, 0 wrong, 3 abstentions. Same content as the committed CSV (only the line endings differ, see issue 6). |
| Commands documented in the report | `python atelier-vote.py`, `python td2_compare_votes.py` "from the repository root" | ❌ `can't open file`: neither script is at the root (see issue 4). |
| Independent recomputation of the 20 rows | the TD 2 kit's `TD2/atelier-vote.py` (`proposals_for`, last attempt per member) + Pair A's `vote_k_sur_n` | ✅ **20/20 rows identical** to `td2-task-A-comparison.csv` (consensus, value and votes, for both quorums). |
| Contract of `vote_k_sur_n` (`pair-A/` version) | 12 edge cases | ✅ k = 0, 1, 4 and `True` → `ValueError`; k = 2 → consensus; k = 3 → abstention with `votes: 2`; duplicate `(provider, model)` → `ValueError`; errors stay in n and cast no vote; a value of 0 votes; empty panel → `ValueError`. ⚠️ k = `2.0` is accepted (see issue 3). |
| Cross-check with Pair B | C08 and C09 rows | ✅ Same as `pair-b/votes-pair-A-method.jsonl` and `pair-b/C09/part1-quorums.md`. C08: 2-of-3 605 580 (2 votes), 3-of-5 abstains (2). C09: 2-of-3 **0** (2 votes), 3-of-5 abstains (2). |

The four questions where the decision changes, with the exact values and verdicts from `TD1/results/traces-td1.csv` (last attempt):

| Case | Reference | 120b | north | qwen | 20b | dots | 2-of-3 | 3-of-5 |
|---|---:|---:|---:|---:|---:|---:|---|---|
| C08 | 605 580 | 605 580 ✅ | 1 188 090 ❌ | 605 580 ✅ | 25 920 ❌ | 25 920 ❌ | ✅ 605 580 (2) | abstain (605 580: 2 · 25 920: 2 · 1 188 090: 1) |
| C09 | 487 980 | 487 980 ✅ | 0 ❌ | 0 ❌ | 487 980 ✅ | 369 240 ❌ | ❌ **0** (2) | abstain (487 980: 2 · 0: 2 · 369 240: 1) |
| C15 | 168 680 | 168 680 ✅ | 314 020 ❌ | 0 ❌ | 168 680 ✅ | 168 680 ✅ | abstain (three different values) | ✅ 168 680 (3) |
| C17 | 258 180 | 258 180 ✅ | 0 ❌ | 248 490 ❌ (2nd attempt, after HTTP 429) | 258 180 ✅ | 258 180 ✅ | abstain (three different values) | ✅ 258 180 (3) |

C10 abstains in both quorums, but for two different reasons. In 2-of-3, the three values are all different (558 980, 0, 119 410). In 3-of-5, it is a tie: 558 980 has 2 votes (120b, 20b), and the shared wrong value 119 410 also has 2 (qwen, dots). The other 15 cases give the same correct value in both quorums.

## What is correct

- **`vote_k_sur_n` meets the five points of the contract** (assignment, Step 1) and the Lecture 2 voting rules:
  - strict majority enforced with `ValueError` (slide 15);
  - a duplicate panel member is refused (slide 17);
  - a failed member stays in n and does not vote (slide 16);
  - with no value at k, it returns `value: None` and never invents one (slide 5);
  - it never receives the reference (slide 23).
- **A value without its stored SQL does not vote** (slide 7). `td2_compare_votes.py` excludes such a proposal before the vote (`accepted = ... and bool(sql)`). This closes issue 3 of [`review-A-by-C.md`](review-A-by-C.md).
- **One vote per model, last attempt kept** (slide 17). C17 shows this: Qwen's HTTP 429 retry counts once, with its second attempt (248 490).
- **The abstention policy is written before the vote** (slide 16), in section 1 of the report: no lowering of k, no change of panel afterwards, abstention logged and sent to review.
- **0 is a value, not a missing answer** (slide 10): C06 and C14 (reference 0) give a correct consensus.
- **The output is traceable:** the CSV lists the models of the winning group for each decision. This closes issue 6 of `review-A-by-C.md`.
- **The conclusions are honest:** "this does not establish a general error rate", the reference is used only after the vote, and C09 is read the same way as Pair B (two models do not need the same SQL bug to agree on the same wrong value).

## Issues found

| # | File / cell | Issue | Severity | Suggested fix |
|---|---|---|---|---|
| 1 | `td2.md`, section 2 and section 1 (Pair A row) | **The deliverable is not in the report.** The assignment asks for the 20-question table "in `reports/td2.md`". Section 2 still holds the placeholder, and the Pair A row of section 1 says "to complete". The work exists, but only in `td2-task-A-report.md`. | **high** | Copy the summary table and the four changed decisions into section 2, with a link to the CSV and to `td2-task-A-report.md`. Fill in the Pair A row of section 1. |
| 2 | `td2-task-A-report.md`, "Four decisions that change" | The assignment asks for an explanation "citing the exact values and verdicts from your traces". The explanations name only the winning value. They do not give the other models' values, and do not mention the HTTP 429 retry behind Qwen's C17 answer. | medium | Use the table above: give each model's value and verdict, and say for C17 that Qwen's value comes from its second attempt after an HTTP 429. |
| 3 | `TD2/skeleton-multi-llm-en.py` and `TD2/pair-A/skeleton-multi-llm-en.py` | **There are two different implementations of `vote_k_sur_n`.** The `TD2/` one rejects a non-integer k (`bool`, `float`). The `pair-A/` one, used by `td2_compare_votes.py`, accepts `k = 2.0`. Both give the same 20 decisions, but the reader cannot tell which one is the deliverable. The `TD2/` copy cannot run where it is, because `sandbox_sqlite.py` is in `pair-A/`. | medium | Keep a single implementation, in `pair-A/`, with the type check on k. Remove `TD2/skeleton-multi-llm-en.py`. |
| 4 | `td2-task-A-report.md` section 5; `td2_compare_votes.py` docstring | The reproduction commands do not work as written. They say "from the repository root: `python atelier-vote.py`, `python td2_compare_votes.py`", but the scripts are in `TD2/pair-A/`. | medium | Document `python3 TD2/pair-A/atelier-vote.py` and `python3 TD2/pair-A/td2_compare_votes.py`, which we checked from the root. |
| 5 | `td2-vote-synthetic.jsonl`; `td2-vote-real.jsonl`, `td2_compare_votes.py` | The synthetic output is saved in **UTF-16 LE with CRLF**, so GitHub shows it as a binary file and `json.loads` cannot read it line by line. Two other files start with a UTF-8 BOM. These look like PowerShell redirection artefacts. | low | Re-save as UTF-8 without BOM, for example `python3 TD2/pair-A/atelier-vote.py > TD2/reports/td2-vote-synthetic.jsonl` from a POSIX shell, or `Out-File -Encoding utf8NoBOM`. |
| 6 | `td2_compare_votes.py`, `OUTPUT` | **Re-running the check rewrites the committed evidence.** The script overwrites `td2-task-A-comparison.csv`. The content is identical, but on Linux the line endings change, so a replay shows a modified file. Pair C raised the same point for Pair B: a replay should test the code without changing the stored inputs or outputs (slide 39). | low | Write to a temporary file and compare it with the committed CSV, or add a `--check` option. |
| 7 | Report, section 3 and limits | The 2-of-3 **correct** consensus on **C19** rests on north-mini-code, whose value is correct by chance: its age test is wrong (see `TD1/results/pivot-td1.md`). The 3-of-5 quorum also contains two gpt-oss models, so it is not five independent families (slide 21). Neither point is stated. | low | Flag C19 as "correct by chance" in the table. Add one line to the limits about the two gpt-oss models. |
| 8 | `vote_k_sur_n` | The vote does not normalise values. The integer 100 and the text `"100"` count as two different values, so the vote abstains. There is no effect in TD 2, because `td2_compare_votes.py` converts every value with `int()` first. Lecture 2 puts normalisation before the vote (slides 10–12). | low | State in the report that values are normalised to integer cents **before** the call, or check the type inside the function. |
| 9 | CSV and report | No policy version is recorded. Lecture 2 versions policies (for example `p2`), so that a decision can be traced back to the rule in force. | low | Add a `policy` column, for example `2of3-fixed-v1` and `3of5-all-v1`. |

### Follow-up after Pair A's updates (state of `main` at `f4b68e0`)

Pair A then wrote section 2 of `td2.md` (commit `59e7e37`) consolidated its implementation (commit `1eeaf76`), and normalised its evidence with a safe replay mode (commit `1ba9621`). We re-checked each issue against that version:

| # | Status | Detail |
|---|---|---|
| 1 | ✅ fixed | Section 2 now gives the method, the results table (16/1/3 against 17/0/3), the four changed decisions and the limits. The Pair A row of section 1 says "Done". |
| 2 | ⏳ open | The explanations in section 2.2 still give only the winning value. They do not give the other models' values and verdicts, or Qwen's HTTP 429 retry on C17 (see the table above). |
| 3 | ✅ fixed | Only `pair-A/skeleton-multi-llm-en.py` remains, and it now rejects a non-integer k: re-run, `k = 2.0` and `k = True` → `ValueError`, `k = 2` → consensus. `td2_compare_votes.py` still reproduces the committed CSV exactly. |
| 4 | ✅ fixed | `td2.md` section 2.4, `td2-task-A-report.md` and the docstring of `td2_compare_votes.py` now give `python TD2/pair-A/...`, which we checked from the repository root. |
| 5 | ✅ fixed | `td2-vote-synthetic.jsonl` and `td2-vote-real.jsonl` are now UTF-8 JSON lines without BOM. Re-running `python TD2/pair-A/atelier-vote.py` reproduces the synthetic file exactly. |
| 6 | ✅ fixed | `td2_compare_votes.py --check` verifies the committed CSV without modifying it. Re-run: the working tree stays clean. |
| 7 | ◐ partly fixed | Section 2.3 now says the two gpt-oss models are not independent. C19 is still not flagged as correct by chance. |
| 8, 9 | ⏳ open | Low severity: no change needed for the TD 2 results. |

## Questions to the authors

1. Which implementation is the deliverable, `TD2/skeleton-multi-llm-en.py` or `TD2/pair-A/skeleton-multi-llm-en.py`? Who wrote each one?
2. On C15 and C17, the 3-of-5 quorum answers where 2-of-3 abstains, but it costs two more calls per question. On C08, it abstains where 2-of-3 was right. For a figure shown to a customer, which panel would you keep, and what does each abstention cost (slide 19: every launched call is paid)?
3. On C10, the 3-of-5 quorum avoids a wrong answer only because of a tie (558 980: 2, 119 410: 2). If one more model had shared 119 410, it would have won with k = 3. Would you add this case to the limits?
4. Where is the AI assistance used for Step 1 declared? The report says "used AI assistance" but gives no tool or prompt log, as in `TD1/prompt/`.

## Authors' answer

_To complete by Pair A._
