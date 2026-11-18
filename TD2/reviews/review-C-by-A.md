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

**From Pair C (Raphaël Delavictoire, Dorian Courcelle).** Thank you. Points 1 and 2 concern Pair B's C09 files, not Pair C; we leave them to Pair B. Points 3 to 6 are accepted and fixed in policy `pairC-v2.2` of [`atelier-routage-adapted.py`](../pair-C/atelier-routage-adapted.py); [`output-after.jsonl`](../pair-C/output-after.jsonl) was regenerated (10 scenarios): running `python3 TD2/pair-C/atelier-routage-adapted.py` reproduces it exactly.

| # | Answer |
|---|---|
| 3 | Fixed. `CHECKS[level][use]` no longer exists (since v2 the use sets the check rung). `choose` now checks `request.get("use")` first: a missing or unknown use returns `abstain`, check `human review`, reason "use ... is not one of ['customer', 'dashboard', 'payout']". Tested with `use="marketing"` and with no `use`. |
| 4 | Fixed. `FAMILY_LEVEL` is replaced by `family_level()`: the family string is split on `+`, each part is looked up in `PART_LEVEL` (`F1`, `F3` = 1, `F2b` = 2, `F2` = 3) and the level is the maximum, so `F1+F2`, `F3+F2b` and `F2+F1` all work. An unknown part (`F1+F5`) still abstains. |
| 5 | Fixed. Every branch returns `cash` as a float (`0.0` or the paid price); all ten records in `output-after.jsonl` have a float. |
| 6 | Fixed. `REF_AGE` now uses Pair B's predicate `date(ref,'-26 years') < birth_date <= date(ref,'-25 years')`, and the order-date version uses `date(o.date, ...)`. We ran both forms read-only on `data/boutique.sqlite`: they give the same totals, equal to the references (C02 590 320, C08 605 580, C09 487 980, C11 446 690, C10 558 980). The base has no customer born on 29 February, so the leap-year edge is not exercised by this data. |

