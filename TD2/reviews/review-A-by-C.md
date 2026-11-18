# Review of Pair A by Pair C

**Reviewers (at least two):** Raphaël Delavictoire, Dorian Courcelle (Pair C) — read and validated on 18 November 2026
**Reviewed:** Pair A (Alexandre, Maya) — k-of-n vote: `vote_k_sur_n` in [`../skeleton-multi-llm-en.py`](../skeleton-multi-llm-en.py), [`../atelier-vote.py`](../atelier-vote.py), 2-of-3 vs 3-of-5 table for C01–C20, section 2 of [`../reports/td2.md`](../reports/td2.md)
**Date:** 18 November 2026 (state of `main` at commit `7967fcd`)
_Prepared with AI assistance (Claude). Every check below was re-run on the repository, then read and validated by both reviewers._

Reference for the checks: Lecture 2 rules ([cm2](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/lectures/cm2-en.html), "Quorum and voting", "Evidence and reproducibility", "Traces, logs and replay") and the TD 2 assignment.

## Files reviewed

- `TD2/skeleton-multi-llm-en.py`: compared with `TD1/skeleton-multi-llm-en.py`. The only change is the body of `vote_k_sur_n` (lines 627–650).
- `TD2/atelier-vote.py`, in full.
- `TD2/reports/td2.md`, section 2 and section 1 (Pair A row).
- `TD2/README.md`, which lists the files expected from Pair A.

## What we re-ran and the result

| Check | Command | Result |
|---|---|---|
| Synthetic examples, from the repository | `python3 TD2/atelier-vote.py` | ❌ **Fails at import:** `FileNotFoundError: sandbox: none of [...]/TD2/sandbox_sqlite.py ...` (skeleton line 97). |
| 2-of-3 vs 3-of-5, from the repository | `python3 TD2/atelier-vote.py --traces TD1/results/traces-td1.csv --compare` | ❌ Same error. `questions-td1.json`, required by `compare_panels` (line 80), is not in the repository either. |
| Synthetic examples, in a scratch copy with a stub `sandbox_sqlite.py` (the vote does not use it) | `python3 atelier-vote.py` | ✅ agreement → consensus 100 (2 votes) · disagreement → abstention (1) · unavailable → abstention (1) · wrong consensus → consensus 0, `matches_reference: false` |
| Contract of `vote_k_sur_n`, in the scratch copy | 12 edge cases: k = 0, 1, 2, 3, 4, `True`, `2.0`; duplicate member; errors staying in n; value 0 | ✅ `ValueError` for every k outside `n//2 < k <= n` (including `True` and `2.0`). Duplicate `(provider, model)` → `ValueError`. Errors stay in n and cast no vote. 0 is counted as a value, not as missing. |
| 2-of-3 vs 3-of-5 on C01–C20, in the scratch copy with `questions-td1.json` rebuilt from the traces | `--compare` | ✅ Runs. 2-of-3: 17 consensus, **16 correct**, 3 abstentions. 3-of-5: 17 consensus, **17 correct**, 3 abstentions. |
| Cross-check with Pair B | C08 and C09 lines of the comparison | ✅ Same counts as Pair B (C08: 2-of-3 605 580 with 2 votes, 3-of-5 abstains with 2; C09: 2-of-3 **0** with 2 votes, 3-of-5 abstains with 2). This closes the "Pair A integration pending" item in Pair B's files. |

Questions where the decision changes between the fixed 2-of-3 panel (gpt-oss-120b, north-mini-code, qwen) and the 3-of-5 quorum (all five), from our re-run:

| Case | Reference | 2-of-3 | 3-of-5 | Why |
|---|---:|---|---|---|
| C08 | 605 580 | ✅ 605 580 (120b + qwen) | abstain (605 580: 2 · 25 920: 2 · 1 188 090: 1) | gpt-oss-20b and dots share the wrong 25 920 |
| C09 | 487 980 | ❌ **0** (north + qwen) | abstain (487 980: 2 · 0: 2 · 369 240: 1) | wrong consensus inside the fixed panel |
| C15 | 168 680 | abstain (three different values) | ✅ 168 680 (120b + 20b + dots) | the two extra models agree with 120b |
| C17 | 258 180 | abstain | ✅ 258 180 (120b + 20b + dots) | same |

C10 abstains in both quorums. The other 16 cases give the same correct value in both.

## What is correct

- **`vote_k_sur_n` meets the five points of the contract and the Lecture 2 voting rules.**
  - Strict majority enforced with `ValueError` (rules 5 and 11). The check also rejects `bool` and `float` values of k.
  - Duplicate panel member refused (rule 10).
  - A failed member stays in n and does not vote (rule 7).
  - When no value reaches k, the function returns `value: None` and never invents a value (rule 6).
  - The function never receives the reference (rule 13). `evaluate` and `compare_panels` compare with the reference only **after** the decision.
- **The panels are fixed in code before any answer is read** (rule 4): `PANEL` and `PANEL_FIVE`, lines 22–34.
- **One vote per model, last attempt kept** (rule 9). `proposals_for` keeps the last CSV row per member, so the HTTP 429 retries (gpt-oss-20b C20, qwen C16–C20) count once.
- **0 is treated as a value, not as a missing answer** (rule 19). For example, C06 and C14 have the reference 0 and both give a correct consensus.
- **The docstring of `atelier-vote.py` is honest about families.** It says the five-model quorum contains two gpt-oss variants, so it is "not five independent model families" (rule 43).

## Issues found

| # | File / cell | Issue | Severity | Suggested fix |
|---|---|---|---|---|
| 1 | `skeleton-multi-llm-en.py` l. 97; `atelier-vote.py` l. 80 | **Pair A's results cannot be reproduced from the repository.** The skeleton imports `sandbox_sqlite` at load time, and `--compare` needs `questions-td1.json`. Neither file is committed, so both commands fail (see the re-run table). Rule 66 asks to replay from stored inputs. | **high** | Commit the kit's `sandbox_sqlite.py` and `questions-td1.json` next to `atelier-vote.py`, or document the exact kit path. Then re-run both commands on a clean clone. |
| 2 | `TD2/` and section 2 of `td2.md` | **Expected deliverables are missing:** no `atelier-vote.py` outputs, no 2-of-3 vs 3-of-5 table, no explanation of each changed decision. Section 2 and the Pair A row of section 1 are empty. | **high** | Commit the synthetic output, `vote-comparison.csv` and the JSON summary. Write section 2 with the four changed cases above (C08, C09, C15, C17) and the reason for each. |
| 3 | `atelier-vote.py` l. 60 | Rule 26: "a value without its stored query does not vote". `proposals_for` accepts any row with a verdict and a value, without checking the `sql` column. There is no effect on TD 1 (0 rows have a value without SQL), but the rule is not enforced. | medium | Add `and (row.get("sql") or "").strip()` to `valid`. |
| 4 | `skeleton-multi-llm-en.py` l. 642 | One executed answer whose value is not an integer raises `ValueError` and aborts the vote for the **whole question**. Rule 18 says such an answer is rejected and does not vote; the rest of the panel should still vote. | low | Treat it like an error: `continue`, and log it, instead of raising. Or say in the report why aborting is preferred. |
| 5 | `--compare` summary | `accuracy_given_consensus = 1.0` for 3-of-5 (17/17) reads like a guarantee. Rules 15 and 45: a unique accepted value is not proof, and twenty questions measure the method, not an error rate. Also, the 2-of-3 consensus on **C19** relies on north-mini-code, whose value is correct **by chance** (wrong age test, see `TD1/results/pivot-td1.md`). | medium | Report every figure with its denominator (17 decisions out of 20, 3 abstentions; rule 75), state that it holds for this batch only, and flag C19. |
| 6 | `vote-comparison.csv` columns (l. 115–121) | The CSV keeps value, votes and correct, but drops `models`, so we cannot see which members were retained by the winning group (rule 63). There is no policy version in the output either (rule 65). | low | Add a `{name}_models` column and a `policy` field, for example `2of3-fixed-v1`. |
| 7 | `atelier-vote.py` l. 68 | `evaluate` always votes with k = 2, whatever the panel. This is correct for the 3-member panel used today, but wrong if `PANEL` changes. | low | Pass k as a parameter, or compute it from `len(panel)`. |

## Questions to the authors

1. Did you write `compare_panels` and the `--compare` option, or do they come from the kit? The commit `7967fcd` ("Add files via upload") adds both files at once, so we cannot tell your changes from the kit's.
2. Is the 3-of-5 quorum, with two gpt-oss models, the panel you would recommend for production, or only the one the assignment asks you to compare? Lecture 2 asks for distinct families.
3. On C15 and C17, the 3-of-5 quorum answers where 2-of-3 abstains. What does each abstention cost (rule 75: "an abstention is not free"), and which panel would you keep for a customer-facing figure?
4. Is the AI assistance used for this step declared somewhere, as in TD 1 (`TD1/prompt/ai-assistance/`)?

## Authors' answer

_To complete by Pair A._
