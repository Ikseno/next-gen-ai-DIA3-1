# Review of Pair C by Pair A

**Reviewers (at least two):** _names_
**Reviewed:** Pair C — routing rule: [`../pair-C/`](../pair-C/), section 4 of [`../reports/td2.md`](../reports/td2.md)
**Date:** 18 November 2026

## Files reviewed

[1] atelier-routage-adapted.py

## What we re-ran and the result

_Commands and outputs; do the figures match the TD 1 traces and `TD1/reference-td1.csv`?_

## What is correct

_To complete._

## Issues found

| # | File / cell | Issue | Severity | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | `TD2/pair-b/C09/README.md` (SQL script) | Missing the faulty SQL `WHERE` clause from `traces-td1.csv` explaining *why* both Cohere and Qwen returned `0`. | Minor | Add a 1–2 line comment quoting the shared faulty date filter from Cohere and Qwen so the shared-error root cause is self-contained. |
| 2 | `TD2/pair-b/C09/README.md` (Total `SELECT` query) | `SUM(o.quantity_product * p.price)` returns `NULL` instead of `0` if reused as a template on a query with zero matching rows. | Minor | Wrap the aggregation in `COALESCE(SUM(o.quantity_product * p.price), 0)`. |
| 3 | Pair C routing simulator (`choose()`) | Uncaught `KeyError` on `CHECKS[level][request["use"]]` if `request["use"]` is missing or unrecognized (unlike `family`, which gracefully abstains). | Medium | Validate `request.get("use") in CHECKS[level]` before indexing and return an `"abstain"` dictionary with `"human review"` on unknown uses. |
| 4 | Pair C routing simulator (`FAMILY_LEVEL` / `choose()`) | Combined family keys are order-sensitive (`"F2+F1"` is defined, but `"F1+F2"` or `"F3+F2"` will fail lookup and abstain). | Minor | Parse `request["family"].split("+")` and compute `max(FAMILY_LEVEL[f] for f in families)` so key order does not matter. |
| 5 | Pair C routing simulator (`choose()`) | Inconsistent `cash` return types: integer `0` for free/defer/abstain paths vs. `float` (e.g., `0.000278`) for paid routes. | Minor | Return `0.0` consistently across all return branches to keep the JSON output schema uniform. |
| 6 | Pair C routing simulator (`REF_AGE`) | Forward date shift (`date(birth,'+25 years') <= ref < date(birth,'+26 years')`) differs in notation from Pair B's backward shift (`date(ref,'-26 years') < birth_date <= date(ref,'-25 years')`), risking confusion on leap-year boundaries. | Minor | Align `REF_AGE` wording with Pair B's exact `date(ref, '-26 years') < birth_date <= date(ref, '-25 years')` predicate. |

## Questions to the authors

_To complete._

## Authors' answer

_To complete by Pair C._

