# Review of Pair B by Pair A

**Reviewers (at least two):** _names_
**Reviewed:** Pair B — wrong consensus: C08 in [`../pair-b/`](../pair-b/) (Yasmine), C09 in [`../pair-b/C09/`](../pair-b/C09/) (Marc, Mehdy)
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

_To complete by Pair B._

