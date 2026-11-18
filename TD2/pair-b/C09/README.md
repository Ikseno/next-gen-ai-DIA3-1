# TD2 / pair-b / C09 (Pair B — Marc, Mehdy)

Main wrong-consensus case of Pair B: **C09** (customers exactly 25 on 2026-09-26). Cohere and Qwen both return 0 (reference 487980); the fixed 2-of-3 panel (gpt-oss-120b, Cohere, Qwen) **adopts the wrong value 0**, the 3-of-5 quorum abstains.

| File | Content |
|---|---|
| [`part1-quorums.md`](part1-quorums.md) | The five answers on C09 and the 2-of-3 / 3-of-5 decisions |
| [`part2-sql-cause-marc.md`](part2-sql-cause-marc.md) | SQL root cause of both faulty queries, predicate by predicate (Marc) |
| [`part3-delta-mehdy.md`](part3-delta-mehdy.md) | Delta query, exact gap and independent check (Mehdy) |
| [`delta-query.sql`](delta-query.sql), [`delta-output.csv`](delta-output.csv) | Delta query and its output (6 customers, 487980 cents) |
| [`check_c09_csv.py`](check_c09_csv.py) | Independent recomputation without SQL: `python3 TD2/pair-b/C09/check_c09_csv.py TD2/pair-b/data` (from the repository root) |

The other case of Pair B (C08, Yasmine) is at the root of [`../`](../).
