# Step 2 — part 3: delta query and independent check (Mehdy)

Case **C09**: revenue excl. VAT, in cents, of the customers who are exactly 25 years old on **2026-09-26** (all their orders).
Reference: **487980** (`TD1/reference-td1.csv`, identical to the official value). Cohere (`cohere/north-mini-code:free`) and Qwen (`qwen/qwen3.8-27b`) both return **0**.

## Delta query

File: [`delta-query.sql`](delta-query.sql), run read-only on the kit database, also in the repository as [`../data/boutique.sqlite`](../data/boutique.sqlite) (SHA-256 `0077e235…3398fec2`, same as the kit). Output: [`delta-output.csv`](delta-output.csv).

"Exactly 25 on 2026-09-26" means the 25th birthday is on or before that day and the 26th is after it, i.e. **2000-09-26 < birth_date ≤ 2001-09-26**. The query lists every customer in that window with the revenue of all their orders:

| customer_id | birth_date | order lines | revenue_cents |
|---|---|---:|---:|
| C007 | 2000-11-30 | 18 | 118740 |
| C009 | 2001-03-10 | 9 | 61330 |
| C008 | 2001-05-15 | 11 | 99090 |
| C002 | 2001-09-24 | 6 | 25920 |
| C001 | 2001-09-25 | 18 | 135000 |
| C003 | 2001-09-26 | 6 | 47900 |
| **Total** | | **68** | **487980** |

**Reading the delta.** Both faulty queries select no customer at all (they return 0). So the six customers above are all **missed**, none is wrongly **added**, and the gap is exactly **487980 − 0 = 487980 cents**: 118740 + 61330 + 99090 + 25920 + 135000 + 47900.

**Boundaries.** The window is decided by the birthdays around 26 September:
- C003, born 2001-09-26, turns 25 **on** the reference date → counted;
- C005, born 2000-09-26, turns 26 on the reference date → not counted;
- C004, born 2000-09-25, is already 26 → not counted.

No customer aged 25 on that date has zero orders, so the list is complete.

## Independent check

[`check_c09_csv.py`](check_c09_csv.py) recomputes C09 **without SQL**: it reads the three CSV files of the kit and computes completed age with year, month and day (`age = year diff − (birthday not reached yet)`).

```bash
python3 TD2/pair-b/C09/check_c09_csv.py TD2/pair-b/data
```

It returns the same six customers and the same total, **487980**. The delta query (date window) and this script (year/month-day arithmetic) use two different formulations of the same convention and agree with the reference query.

## Consequence for checking

- **A vote cannot catch this error.** In the fixed 2-of-3 panel, Cohere and Qwen agree on 0 and outvote gpt-oss-120b (487980): the quorum returns a **wrong consensus**. Agreement between models is not evidence of correctness when they share the same kind of mistake (here, an age computed without the month-day test).
- **Checks that would have detected it:**
  1. a **sanity rule**: an age question on a non-empty customer set that returns 0 is suspicious; count the selected customers (`COUNT(DISTINCT customer_id)`) and reject 0 when the window contains customers;
  2. a **deterministic recomputation** of the age filter (date window or the CSV script above) compared with the model's value;
  3. a **boundary test** on known birthdays (C003 must be in, C005 must be out).
- For the routing rule: age questions should not be accepted on a 2-of-3 vote alone; they need a deterministic check or a wider quorum that is allowed to abstain (the 3-of-5 quorum abstains on C09: 2 votes for 487980, 2 for 0, 1 for 369240; see [`part1-quorums.md`](part1-quorums.md)).
