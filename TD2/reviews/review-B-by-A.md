# Review of Pair B by Pair A

**Reviewers (at least two):** _names_
**Reviewed:** Pair B — wrong consensus: C08 in [`../pair-b/`](../pair-b/) (Yasmine), C09 in [`../pair-b/C09/`](../pair-b/C09/) (Marc, Mohamed)
**Date:** 18 November 2026

## Files reviewed

[1] chech_c09_csv.py

## What we re-ran and the result

_Commands and outputs; do the figures match the TD 1 traces and `TD1/reference-td1.csv`?_

## What is correct

_To complete._

## Issues found

| # | File / cell | Issue | Severity | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | `TD2/pair-b/C09/README.md` (Total `SELECT` query) | `SUM(o.quantity_product * p.price)` evaluates to `NULL` rather than `0` if reused as a diagnostic template on a question with zero matching rows. | Minor | Wrap the aggregation in `COALESCE(SUM(o.quantity_product * p.price), 0)`. |

| # | File / cell | Issue | Severity | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | `TD2/pair-b/C09/README.md` (Header comments) | Omits the exact faulty SQL `WHERE` clauses from `traces-td1.csv` that caused both Cohere and Qwen to return `0`. | Minor | Add a 1–2 line comment quoting the faulty SQLite date-filter snippets from Cohere and Qwen so the shared-error root cause is self-contained. |
| 2 | `TD2/pair-b/C09/README.md` (Total `SELECT` query) | `SUM(o.quantity_product * p.price)` evaluates to `NULL` rather than `0` if reused as a diagnostic template on a question with zero matching rows. | Minor | Wrap the aggregation in `COALESCE(SUM(o.quantity_product * p.price), 0)`. |
| 3 | `TD2/pair-b/C09/README.md` (Scope / Deliverable) | File is pure `.sql` code inside `README.md` without Markdown prose summarizing the systemic takeaway for Pair C (`reports/td2.md`). | Minor | Add a brief Markdown summary explaining why correlated SQLite date-arithmetic errors defeat $k$-of-$n$ voting and require schema/template grounding or deterministic routing. |

## Questions to the authors

_To complete._

## Authors' answer

_Answer by Pair B, written by Marc Chen with AI assistance (see [`ai-assistance-marc.md`](../pair-b/ai-assistance-marc.md)) and validated by Yasmine Boukrouh and Mohamed Diawara._

All three points concern [`pair-b/C09/delta-query.sql`](../pair-b/C09/delta-query.sql). `C09/README.md` is the Markdown index of the folder and contains no SQL, and `check_c09_csv.py` contains no SQL either: its Python `sum()` already returns 0 on an empty set.

| # (second table) | Answer | Status |
|---|---|---|
| 1 | Accepted and fixed. The header of `delta-query.sql` now quotes both faulty `WHERE` clauses and says why each one keeps nothing. The complete queries are stored verbatim in [`faulty-north-mini-code.sql`](../pair-b/C09/faulty-north-mini-code.sql) and [`faulty-qwen.sql`](../pair-b/C09/faulty-qwen.sql). | done |
| 2 | Accepted and fixed. The total query of `delta-query.sql` now uses `COALESCE(SUM(o.quantity_product * p.price), 0)`. Re-run: 487 980, unchanged. The first table repeated the same point. | done |
| 3 | Accepted and fixed. [`C09/README.md`](../pair-b/C09/README.md) now ends with a "Takeaway" paragraph. It explains that two different SQL mistakes produce the same empty filter, that two wrong models inside a 3-model panel outvote the correct one, and that age questions therefore need a deterministic check after the vote (`age-window-nonempty`). This is consistent with section 3.4 of `td2.md` and with Pair C's rule. The empty-filter evidence is stored in [`empty-filter-check.sql`](../pair-b/C09/empty-filter-check.sql) → [`empty-filter-check.csv`](../pair-b/C09/empty-filter-check.csv). | done |

The review does not yet list reviewers, what was re-run, or what is correct. We will answer those sections once Pair A completes them.

