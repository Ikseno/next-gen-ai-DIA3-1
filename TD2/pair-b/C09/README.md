# TD2 / pair-b / C09 (Pair B — Marc, Mohamed)

Main wrong-consensus case of Pair B: **C09** (customers exactly 25 on 2026-09-26). Cohere and Qwen both return 0 (reference 487980); the fixed 2-of-3 panel (gpt-oss-120b, Cohere, Qwen) **adopts the wrong value 0**, the 3-of-5 quorum abstains.

| File | Content |
|---|---|
| [`part1-quorums.md`](part1-quorums.md) | The five answers on C09 and the 2-of-3 / 3-of-5 decisions |
| [`part2-sql-cause-marc.md`](part2-sql-cause-marc.md) | SQL root cause of both faulty queries, predicate by predicate (Marc) |
| [`part3-delta-mohamed.md`](part3-delta-mohamed.md) | Delta query, exact gap and independent check (Mohamed) |
| [`faulty-north-mini-code.sql`](faulty-north-mini-code.sql), [`faulty-qwen.sql`](faulty-qwen.sql) | The two faulty queries, complete and verbatim from `TD1/results/traces-td1.csv` (last attempt); both return 0 |
| [`empty-filter-check.sql`](empty-filter-check.sql), [`empty-filter-check.csv`](empty-filter-check.csv) | Each model's own `WHERE` re-run with `COUNT(*)` and `COUNT(DISTINCT customer_id)`: both keep 0 lines and 0 customers, against 68 lines and 6 customers for the correct window |
| [`delta-query.sql`](delta-query.sql), [`delta-output.csv`](delta-output.csv) | Delta query and its output (6 customers, 487980 cents) |
| [`check_c09.py`](check_c09.py) | **One-command read-only check of all C09 evidence**, plus the tested delivery gate `age-window-nonempty` and the full numerical check: `python3 TD2/pair-b/C09/check_c09.py` (19/19 OK) |
| [`check_c09_csv.py`](check_c09_csv.py) | Independent recomputation without SQL: `python3 TD2/pair-b/C09/check_c09_csv.py TD2/pair-b/data` (from the repository root) |

**Takeaway.** Cohere and Qwen make two different SQL mistakes (text arithmetic divided by 365; age at the order date with contradictory month-day bounds) that both produce an empty filter, which `COALESCE(SUM(...), 0)` turns into the same value 0. Two wrong models inside a three-model panel are enough to outvote the correct one, so k-of-n voting alone cannot catch this error: age questions need a deterministic check after the vote, such as `age-window-nonempty` (a 0 is delivered only if the age window really holds no customer). This is the check Pair C's routing rule requires for customer and payout figures (section 3.4 of [`../../reports/td2.md`](../../reports/td2.md)).

The other case of Pair B (C08, Yasmine) is at the root of [`../`](../).
