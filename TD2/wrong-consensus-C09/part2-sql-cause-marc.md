# TD 2 — Pair B, part 2: SQL root cause of the wrong consensus on C09

Author: Marc Chen (role D in TD 1). Inputs: `TD1/trace/traces-C.csv`, `TD1/trace/traces-D.csv`, and `data/boutique.sqlite` from pack `2026-11-18-students-5` (opened read-only). Both faulty queries were re-run on the database and both still return 0.

## The case in one line

**C09**: revenue from customers who are exactly 25 years old on 2026-09-26 (all their orders). The reference is **487 980** cents. Cohere (`cohere/north-mini-code:free`) and Qwen (`qwen/qwen3.8-27b`) both return **0**. They give the same wrong value, but their `WHERE` clauses are wrong for different reasons.

Correct filter: a customer has completed age 25 on 2026-09-26 when their birth date is in ]2000-09-26 ; 2001-09-26]. That gives 6 customers (C001, C002, C003, C007, C008, C009), 68 order lines and 487 980 cents.

## Cohere's query

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (
    CAST((strftime('%Y-%m-%d', '2026-09-26') - c.birth_date) / 365 AS INTEGER) = 25     -- P1
    AND date(c.birth_date, '+' || (25 * 365) || ' days') <= '2026-09-26'                -- P2
    AND date(c.birth_date, '+' || (26 * 365) || ' days') >  '2026-09-26'                -- P3
);
```
(The SQL comments from the trace are removed and P1/P2/P3 labels added. The logic is unchanged.)

| Predicate | What the model meant | What SQLite actually computes | Lines kept | Revenue (cents) |
|---|---|---|---|---|
| P1 | age = 25, from a difference in days | `'2026-09-26' - '2001-09-25'` subtracts two **text** values. SQLite keeps only the leading number of each string (2026 and 2001), so the result is **25 years** (an integer), not a number of days. `25 / 365` then gives **0** with integer division. P1 becomes `0 = 25` and is false for every customer. | 0 | 0 |
| P2 | 25th birthday reached | 25 × 365 days misses the 6 leap days, so the test becomes birth ≤ 2001-10-02 (instead of ≤ 2001-09-26) | 348 | 2 426 640 |
| P3 | 26th birthday not reached | same 365-day shortcut, so the test becomes birth > 2000-10-02 (instead of > 2000-09-26) | 117 | 887 590 |
| P2 AND P3 | | | 68 | 487 980 |
| **P1 AND P2 AND P3** | | | **0** | **0** |

**Root cause: P1.** Cohere assumed that subtracting two date strings gives a number of days. In SQLite it gives the difference between the leading year numbers. Dividing that by 365 turns 25 into 0, so the condition can never be true. With no rows left, `COALESCE(SUM(...), 0)` returns 0.

Side note: P2 AND P3 alone would have returned 487 980, but only **by luck**. Their window is shifted by 6 days, and no customer is born between 2000-09-27 and 2000-10-02 or between 2001-09-27 and 2001-10-02. With this filter, a customer born on 2001-09-30 (aged 24) would be counted, and one born on 2000-09-30 (aged 25) would be missed.

## Qwen's query

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 25                       -- Q1
  AND (strftime('%m-%d', o.date) >= strftime('%m-%d', c.birth_date))                     -- Q2
  AND (strftime('%m-%d', o.date) <  strftime('%m-%d', date(c.birth_date, '+26 years'))); -- Q3
```
(Q1/Q2/Q3 labels added. The query is otherwise verbatim from the trace.)

| Predicate | What the model meant | What SQLite actually computes | Lines kept | Revenue (cents) |
|---|---|---|---|---|
| Q1 | year difference = 25 | It uses the **order date** `o.date`, not the reference date 2026-09-26. All orders are in 2026, so Q1 keeps everyone born in 2001: C001, C002, C003, C006, C008, C009 and C014. C006 and C014 are only 24 on the reference date, and C007 (born in 2000, aged 25) is missed. | 72 | 548 920 |
| Q2 | birthday already passed on the order date | mm-dd(order) ≥ mm-dd(birth) | 129 | 907 310 |
| Q3 | 26th birthday not yet passed | birth + 26 years has the **same month-day** as the birth date (checked: no customer is an exception), so Q3 is mm-dd(order) < mm-dd(birth) | 268 | 1 918 940 |
| Q2 AND Q3 | | x ≥ b AND x < b cannot both be true | 0 | 0 |
| **Q1 AND Q2 AND Q3** | | | **0** | **0** |

**Root cause: two errors stacked.**
1. **Wrong date.** Qwen computes the age at each order, which is the C10 convention, but C09 asks for the age at a fixed reference date. The reference date 2026-09-26 never appears in the query.
2. **Contradictory window.** Q2 and Q3 cancel each other out, so no row can match and the result is 0.

Removing Q3 would not fix the query: Q1 AND Q2 gives 119 410 (only C008 and C009), still far from 487 980.

## Why the two models agree on 0

Their reasoning is not the same. Cohere makes a **type error**: it does arithmetic on text and expects days. Qwen makes a **convention error** (the wrong date) and adds a **logical contradiction**. The only thing they share is the outcome: a filter that keeps no row, which `COALESCE(SUM(...), 0)` turns into 0.

So **0 is the value any empty filter produces**, and two independent bugs naturally land on it. Their agreement is not evidence that the answer is right. In the fixed 2-of-3 panel (gpt-oss-120b: 487 980, Cohere: 0, Qwen: 0), the two wrong answers outvote the correct one.

**Lesson for the routing rule:** a value of 0 should trigger a check, such as counting the matched lines and customers, before it is allowed into a vote.

## How to reproduce the decomposition

Open the database with `sqlite3 -readonly data/boutique.sqlite`. Then, for each predicate (or combination), run:

```sql
SELECT COUNT(*) AS lines, COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE <predicate>;
```

To see the P1 type problem directly:

```sql
SELECT customer_id, birth_date,
       strftime('%Y-%m-%d', '2026-09-26') - birth_date          AS diff,         -- 25 for C001: years, not days
       (strftime('%Y-%m-%d', '2026-09-26') - birth_date) / 365  AS diff_div_365  -- 0
FROM customers WHERE customer_id IN ('C001', 'C007');
```

*AI assistance: the decomposition and this write-up were prepared with Claude (Anthropic). Every figure was re-run on the database (read-only) and checked against the reference 487 980.*
