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
|---|---|---|---|---|
| 1 |[1] |NULL Safety on SUM | Low| COALESCE(SUM(o.quantity_product * p.price), 0) avoids returning NULL instead of 0|

## Questions to the authors

_To complete._

## Authors' answer

_To complete by Pair B._

