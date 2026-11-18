# Review of Pair B by Pair C

**Reviewers (at least two):** Raphaël Delavictoire, Dorian Courcelle (Pair C) — read and validated on 18 November 2026
**Reviewed:** Pair B — wrong consensus: C08 in [`../pair-b/`](../pair-b/) (Yasmine), C09 in [`../wrong-consensus-C09/`](../wrong-consensus-C09/) (Marc Chen, Mohamed Diawara), section 3 of [`../reports/td2.md`](../reports/td2.md)
**Date:** 18 November 2026 (state of `main` at commit `7967fcd`)


Reference for the checks: Lecture 2 rules ([cm2](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/lectures/cm2-en.html), "Quorum and voting", "Evidence and reproducibility", "Wrong agreement", "Traces, logs and replay") and the TD 2 assignment.

## Files reviewed

- `pair-b/`: `README.md`, `analyse.py`, `reference.sql`, `faulty-gpt-oss-20b.sql`, `faulty-dots.sql`, `delta.sql`, `delta-customers.csv`, `C08-models.csv`, `evidence.json`, `data/manifest.json`.
- `wrong-consensus-C09/`: `part1-quorums.md`, `part2-sql-cause-marc.md`, `part3-delta-mohamed.md`, `delta-query.sql`, `delta-output.csv`, `check_c09_csv.py`.
- Section 3 of `td2.md`.

## What we re-ran and the result

All runs were made on a scratch copy of the repository, so that the scripts could not overwrite the committed evidence (see issue 2).

| Check | Command | Result |
|---|---|---|
| C08, from a Windows checkout | `python3 TD2/pair-b/analyse.py` | ❌ **`AssertionError` at `analyse.py` l. 67.** The three CSV files have CRLF line endings in the Windows working tree (`git ls-files --eol`: `i/lf w/crlf`), so their SHA-256 no longer matches `manifest.json`. With LF endings restored, the hashes match the manifest exactly. |
| C08, with LF CSV files | same | ✅ Runs. Reference 605 580, both faulty queries 25 920, delta 579 660 = 605 580 − 25 920. The regenerated SQL files, `C08-models.csv` and `delta-customers.csv` are identical to the committed ones. |
| C08 `evidence.json` | diff with the committed file | ⚠️ Only `source_sha256` of `traces-td1.csv` and `reference-td1.csv` differs, for the same CRLF reason. Hashed with LF endings, they match the committed values. |
| C09, delta query | the 3 statements of `delta-query.sql`, read-only on `pair-b/data/boutique.sqlite` | ✅ Same 6 customers as `delta-output.csv` (C007, C009, C008, C002, C001, C003), total **487 980**. Boundary query: C004 and C005 are out, C003 is in. |
| C09, independent check | `python3 TD2/wrong-consensus-C09/check_c09_csv.py TD2/pair-b/data` | ✅ Same 6 customers, `TOTAL 487980`, computed without SQL. |
| Quorum counts, with Pair A's `vote_k_sur_n` | `atelier-vote.py --compare` (see [`review-A-by-C.md`](review-A-by-C.md)) | ✅ C08: 2-of-3 gives 605 580 (2 votes), 3-of-5 abstains (2). C09: 2-of-3 gives **0** (2 votes), 3-of-5 abstains (2). Identical to `part1-quorums.md` and to `pair-b/README.md`. |
| Values and verdicts cited | `TD1/results/traces-td1.csv`, last attempt | ✅ C08: 20b and dots 25 920, north 1 188 090, 120b and qwen 605 580. C09: north and qwen 0, dots 369 240 (= 487 980 − 118 740, the revenue of C007), 120b and 20b 487 980. |

## What is correct

- **Two real cases from the team's own traces, showing both outcomes.** On C09 the shared wrong value wins the fixed panel; on C08 it wins no quorum. The conclusion follows: whether a shared error wins depends on **who sits in the panel** (Lecture 2: model agreement is not proof of correctness).
- **Every figure has an independent check.** Each figure comes with a SQL query and a computation that uses no SQL (Python date arithmetic on the CSV files). The two methods agree (rule 32: a check compares the answer with something the model did not write).
- **The delta queries are exact.** No customer is wrongly added, and the omitted customers explain the whole gap. The boundary customers (C003, C004, C005) are discussed explicitly.
- **The vote is decided before the comparison with the reference** (rules 12 and 13). The reference is used only to judge the result afterwards.
- **The data is traceable.** The database and CSV hashes are checked against the manifest, the source hashes are stored in `evidence.json`, and the database is opened read-only (rules 29 and 66).
- **The root-cause reading is careful.** For Qwen on C09, Pair B notes that the age is computed at the order date, i.e. the convention of C10. That is a meaning error hidden behind a value that looks comparable (rule 14).
- **No overclaim.** Both README files say that two cases measure the mechanism, not an error rate (rule 45).

## Issues found

| # | File / cell | Issue | Severity | Suggested fix |
|---|---|---|---|---|
| 1 | `pair-b/analyse.py` l. 67; `pair-b/data/*.csv` | **The C08 evidence fails on Windows**, where most of the team works: git converts the CSV files to CRLF on checkout, so the hash assertion stops the script. The "reproduce" section of the README does not work as written in PowerShell. | **high** | Add a `.gitattributes` with `TD2/pair-b/data/*.csv -text` (and `*.sqlite binary`), then re-checkout. Alternatively, hash the content with line endings normalised. Re-run on a Windows clone. |
| 2 | `pair-b/analyse.py` l. 62 and 113 | **Running the check overwrites the committed evidence**: the SQL files, `C08-models.csv`, `delta-customers.csv` and `evidence.json`. On Windows, `evidence.json` then changes (CRLF hashes), so a simple replay modifies the repository. A replay should test the code without changing the inputs (rule 66). | medium | Write to a temporary folder and compare with the committed files, or add a `--check` mode that only compares. |
| 3 | `wrong-consensus-C09/part3-delta-mohamed.md`, "Reading the delta"; `part2-sql-cause-marc.md` l. 124 | "Both faulty queries select no customer" is what makes the delta exact. With `COALESCE(SUM(...), 0)`, a 0 could also mean customers selected with no orders (rule 19: a missing value is not zero). Part 2 states that `COUNT(DISTINCT c.customer_id)` gives 0 for Cohere and Qwen, but neither that query nor its output is stored, so we could not re-run it. | low | Store the two `COUNT(DISTINCT ...)` queries and their output next to `delta-query.sql`. |
| 4 | `wrong-consensus-C09/check_c09_csv.py`, usage line; `part3-delta-mohamed.md` | The documented argument is `<kit-td1>/data`, a folder that is not in the repository. The script works with `TD2/pair-b/data`, which holds the same files, hash-checked. | low | Document `python3 TD2/wrong-consensus-C09/check_c09_csv.py TD2/pair-b/data`. |
| 5 | `wrong-consensus-C09/` | The two faulty C09 queries (north and qwen) are quoted in `part2-sql-cause-marc.md`, but they are not stored as `.sql` files the way C08's are. The assignment asks for "both faulty SQL queries". | low | Add `faulty-north-mini-code.sql` and `faulty-qwen.sql`, copied from the `sql` column of the traces. |
| 6 | `pair-b/README.md`, `part1-quorums.md` | Both still say "to be re-checked with Pair A's `vote_k_sur_n`". The re-check is now done (see the table above) and matches. | low | Replace the pending note with the result and a link to this review. |
| 7 | `pair-b/data/` | The kit's data (`boutique.sqlite` and the CSV files) is copied into the repository. The `.gitignore` says the repository is public. | question | Check that the course allows redistributing the kit data. If not, keep only the manifest and the hashes, plus the kit path. |

## Questions to the authors

1. Could the sanity rule you propose ("an age question on a non-empty customer set that returns 0 is suspicious") be written as a deterministic check by code, which Pair C's routing rule could run after the vote on F2 questions?
2. Section 3.3 compares C09 with "Lecture 2's pilot case C11 (two families, two queries, both 0)". Can you give the reference: slide or section of cm2? We could not find it in the online lecture.
3. On C08, the 3-of-5 quorum abstains where 2-of-3 is right. Would you recommend 3-of-5 for age questions anyway, given C09?
4. Where is the AI assistance for TD 2 declared? `pair-b/README.md` mentions it; is there a prompt log, as in `TD1/prompt/ai-assistance/`?

## Authors' answer

_Draft by Pair B (Marc Chen), prepared with AI assistance (Claude); statuses updated after the fixes; to be validated by Yasmine and Mohamed._

| # | Answer | Status |
|---|---|---|
| 1 | Accepted and fixed. `analyse.py` now hashes text files with line endings normalised to LF, and a root [`.gitattributes`](../../.gitattributes) (`TD2/pair-b/data/*.csv -text`, `*.sqlite binary`) keeps the data byte-identical. Tested on a copy where every CSV, SQL and JSON file was converted to CRLF: the check passes. Existing Windows clones should re-checkout the data folder once. | done (to confirm on a Windows machine) |
| 2 | Accepted and fixed. `analyse.py` now runs in **check mode by default**: it recomputes every evidence file in memory, compares it with the committed file (`OK`/`DIFF`) and writes nothing. `--write` regenerates the files on purpose. `evidence.json` was regenerated once to record that the Pair A check is done. | done |
| 3 | Accepted and fixed. [`pair-b/C09/empty-filter-check.sql`](../pair-b/C09/empty-filter-check.sql) re-runs each model's own `WHERE`, verbatim, with `COUNT(*)` and `COUNT(DISTINCT customer_id)`. Output in [`empty-filter-check.csv`](../pair-b/C09/empty-filter-check.csv): both keep 0 lines and 0 customers, against 68 lines and 6 customers for the correct window. So the 0 is an empty filter, not customers without revenue. | done |
| 4 | Fixed in `864ac6a`: `part3-delta-mohamed.md` now documents `python3 TD2/pair-b/C09/check_c09_csv.py TD2/pair-b/data`. Your review was written on `7967fcd`, before the C09 files moved to `pair-b/C09/`. | done |
| 5 | Accepted and fixed: [`faulty-north-mini-code.sql`](../pair-b/C09/faulty-north-mini-code.sql) and [`faulty-qwen.sql`](../pair-b/C09/faulty-qwen.sql), verbatim from the `sql` column of the traces (last attempt); both return 0 when re-run. | done |
| 6 | Fixed in `a3169f6`: the pending notes are replaced by the result of the re-check with Pair A's `vote_k_sur_n` (`pair-b/check-votes-with-pair-A.py` → `votes-pair-A-method.jsonl`). It is identical to the hand counts and to your re-run. | done |
| 7 | Fair question. The kit data is not personal data (fictitious shop), but the course does not say whether it may be redistributed. We will ask the instructor; if not allowed, we keep only `manifest.json` and the hashes. | to ask |

**Answers to the questions**

1. Yes. `part2-sql-cause-marc.md` ("A check that can see the cause") proposes the deterministic check `age-window-nonempty`. Re-run the model's `WHERE` with `COUNT(DISTINCT c.customer_id)`, and compare it with the number of customers in the age window computed by code. Deliver a 0 only if both counts are 0; otherwise reject the answer. The check is logged with its identifier and result (Lecture 2, slides 37–38), and Pair C's rule can run it after the vote on F2 questions.
2. The pilot case is described in the TD 2 assignment ("Historical shop-database case: DEMO-SQL-C11": gpt-oss-20b and north-mini-code, two different queries, both 0). It is also the example of the "wrong agreement" slides of Lecture 2 (slide 21 in our copy). We will cite the assignment section, which is stable.
3. No. For age questions, neither quorum is enough on its own. 3-of-5 abstains on C08 (where 2-of-3 was right) and on C09, and it would have let C09's 0 through if a third model had shared it. Section 3.4 of `td2.md` recommends a deterministic age-window check after the vote, whatever k is, which is consistent with Pair C's rule.
4. It is declared in section 6 of `td2.md` (Yasmine: Codex; Marc and Mohamed: Claude) and at the end of each Pair B file. A log of the AI-assistance prompts for Marc's part is in [`pair-b/ai-assistance-marc.md`](../pair-b/ai-assistance-marc.md), in the TD 1 format. The assignment's item 6 ("the prompts, as used, if they have changed since TD 1") concerns the prompt sent to the models, which did not change in TD 2: there was no new batch.
