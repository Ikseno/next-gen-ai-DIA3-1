# TD 2 — Pair B, part 2: SQL root cause of the wrong consensus on C09

Author: Marc Chen (role D in TD 1). Inputs: `TD1/trace/traces-C.csv`, `TD1/trace/traces-D.csv`, and `data/boutique.sqlite` from pack `2026-11-18-students-5` (opened read-only). Both faulty queries were re-run on the database and both still return 0.

**Source and nature.** The case comes from the team's stored TD 1 traces, final attempt per cell: `traces-C.csv` (Cohere, 1 attempt, 2026-10-21 12:15 UTC) and `traces-D.csv` (Qwen, 1 attempt, 2026-10-21 12:30 UTC). Both cells are `nature = real`, meaning real model outputs, not replayed or synthetic. A scan of the 100 final cells finds three shared wrong values: C08 (25 920; gpt-oss-20b and Dots), **C09 (0; Cohere and Qwen)** and C10 (119 410; Qwen and Dots). **C09 is the only one where the shared wrong value wins the fixed 2-of-3 panel.**

## The case in one line

**C09**: revenue from customers who are exactly 25 years old on 2026-09-26 (all their orders). The reference is **487 980** cents. Cohere (`cohere/north-mini-code:free`) and Qwen (`qwen/qwen3.8-27b`) both return **0**. They give the same wrong value, but their `WHERE` clauses are wrong for different reasons.

Correct filter: a customer has completed age 25 on 2026-09-26 when their birth date is in ]2000-09-26 ; 2001-09-26]. That gives 6 customers (C001, C002, C003, C007, C008, C009), 68 order lines and 487 980 cents.

## Cohere's query

Complete query, verbatim from `traces-C.csv`:

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
  -- Compute age on 2026-09-26
  (
    -- Age = 25 if birth_date's year + 25 <= 2026 and (birth_date's month, day) <= (09-26)
    -- and (birth_date's month, day) > (09-26) would be age 24, so we need to ensure the 25th anniversary has occurred on or before 2026-09-26
    -- Equivalent: date('2026-09-26', '-' || CAST((strftime('%Y-%m-%d', '2026-09-26') - c.birth_date) / 365 AS INTEGER) || ' days') >= c.birth_date
    -- Simpler: compute age using SQLite date functions
    CAST((strftime('%Y-%m-%d', '2026-09-26') - c.birth_date) / 365 AS INTEGER) = 25
    AND
    -- Ensure the 25th birthday has already occurred on or before 2026-09-26
    date(c.birth_date, '+' || (25 * 365) || ' days') <= '2026-09-26'
    AND
    -- Ensure the 26th birthday hasn't occurred yet
    date(c.birth_date, '+' || (26 * 365) || ' days') > '2026-09-26'
  );
```
In the table below, **P1**, **P2** and **P3** are the three conditions joined by `AND`, in order: the `CAST(... / 365 ...) = 25` test, the `25 * 365` days test and the `26 * 365` days test.

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

**Failure class (Lecture 2, slide 6).** Both cells are **wrong values**, not access failures and not invalid SQL. Each was answered on the first attempt (`attempts = 1`) with `http_status = 200` and no `error`, and each query runs on the database and returns a value. Both values come with their SQL stored in the trace, so under slide 7 both are allowed to vote. That is exactly why they can create a wrong consensus.

**Distinct families do not protect us (slide 21).** Cohere (north-mini-code, via OpenRouter) and Qwen (qwen3.8-27b, via Groq) come from different model families and different providers, and they wrote two different queries. They still agree on the same wrong value. Distinct families lower the risk of a shared error; they do not remove it.

**"A missing value is never zero" (slide 10).** Here the SQL itself breaks that rule: `COALESCE(SUM(...), 0)` turns "no row matched" into 0. In the answer format, a real 0 and an empty filter look identical, so neither the format check nor the vote can tell them apart.

**Lesson for checking:** a value of 0 should trigger a check that counts the matched lines and customers before the answer is delivered (see the next section).

## Reading the case with Lecture 2: format, meaning, correctness

**Canonical answers.** Each answer is put into the imposed format from Lecture 2, then hashed: SHA-256 of the JSON with sorted keys, first 8 hex characters shown. Here `date` holds the question's reference date; that is our choice for this field.

| Model | Canonical answer | Hash |
|---|---|---|
| gpt-oss-120b (Groq) | `{"currency":"EUR","date":"2026-09-26","tax":"excluded","unit":"cent","value":487980}` | `b7fc951a` |
| gpt-oss-20b (Groq) | `{"currency":"EUR","date":"2026-09-26","tax":"excluded","unit":"cent","value":487980}` | `b7fc951a` |
| north-mini-code (Cohere, OpenRouter) | `{"currency":"EUR","date":"2026-09-26","tax":"excluded","unit":"cent","value":0}` | `eb6e9907` |
| qwen3.8-27b (Groq) | `{"currency":"EUR","date":"2026-09-26","tax":"excluded","unit":"cent","value":0}` | `eb6e9907` |
| dots-3-note (OpenRouter) | `{"currency":"EUR","date":"2026-09-26","tax":"excluded","unit":"cent","value":369240}` | `1b00d5d6` |

**The three checks, in the lecture's order**

| Check | Cohere: 0 | Qwen: 0 | Does it catch C09? |
|---|---|---|---|
| 1. Format (schema) | integer, cent, EUR, excluded: valid | valid | **No.** 0 is a well-formed integer. |
| 2. Meaning (does it answer the question asked?) | amount for an age group: right type | right type | **No.** The type is right; only the filter is wrong. |
| 3. Correctness | 0 ≠ 487 980 | 0 ≠ 487 980 | **Yes**, but only because the lab has a reference value. |

**Vote on hashes**
- Cohere and Qwen share the hash `eb6e9907`.
- **2-of-3 panel** (gpt-oss-120b, Cohere, Qwen): `eb6e9907` gets 2 votes, and k = 2, so the panel reaches a consensus on **0**, which is wrong.
- **3-of-5 quorum**: `b7fc951a` gets 2, `eb6e9907` gets 2 and `1b00d5d6` gets 1. No hash reaches 3, so the quorum **abstains**. It avoids the wrong answer but delivers nothing.
- The panel and k were fixed before reading the answers (slide 18), and both votes were counted **without the reference**. The reference 487 980 is used only afterwards, to judge the decision (slide 23).
- These counts were made by hand. They still need checking with Pair A's `vote_k_sur_n` once it is delivered, as the assignment requires.

**A check that can see the cause (slides 19 and 22)**
- Checks that bring **no new information** (slide 22): asking Cohere or Qwen again (same model, temperature 0, same prompt), or asking a stronger model that reads the same question. Adding voters only adds votes: the 3-of-5 quorum avoids the error by abstaining, but it does not find the right value.
- A check that **does** bring new information: recompute in code what the SQL actually selected.
- Both bugs end the same way: the filter keeps no customer. The answer alone cannot show this, so the check has to look at what the SQL selected.
- In code, re-run the model's own `WHERE` with `COUNT(DISTINCT c.customer_id)` instead of the `SUM`. Cohere gives 0 and Qwen gives 0, yet the database has 6 customers aged 25 on 2026-09-26 (see Mohamed's delta, `part3-delta-mohamed.md`).
- **Proposed rule** for the type "amount for an age group": deliver a value of 0 only if a code check confirms that no customer falls in the age window. Otherwise, reject the answer, so it gets no vote.
- Log the check with its identifier and result, for example `check=age-window-nonempty result=fail` (slides 37 and 38).
- **Reaching the threshold is not the same as delivering (slide 19).** With this check, the 2-of-3 panel still reaches k = 2 on 0, but the required check fails. Nothing is delivered, so the wrong consensus never reaches the user.
- This count must come from code. The lecture says that a model's own statement that it checked something is not evidence.

## Appendix: DEMO-VOTE (synthetic teaching example, not a model output)

This is the assignment's one-row toy table, executed in SQLite in memory: `sales(sale_date, amount_cents)` = (`'2026-01-01'`, 100). The requested period runs from 1 January inclusive to 2 January exclusive.

| Variant | `WHERE` | Result |
|---|---|---|
| Proposals 1 and 2 | `sale_date > '2026-01-01' AND sale_date < '2026-01-02'` | **0** |
| Proposal 3 | `sale_date >= '2026-01-01' AND sale_date < '2026-01-02'` | **100** |

- **The boundary.** The start date is inclusive, so a sale made exactly on `2026-01-01` belongs to the period. A strict `>` drops it, so the sum is empty and `COALESCE` turns it into 0.
- **The quorum.** With proposals [0, 0, 100] and k = 2 of 3, the value 0 gets 2 votes: a wrong consensus against the independent reference of 100.
- **The link with C09.** It is the same mechanism: a filter that wrongly keeps nothing, turned into 0 by `COALESCE`, then outvoting the correct answer.

## Limits

- **One proven case, from a single batch.** Each cell was run once at temperature 0. Twenty questions do not give an error rate, and they do not guarantee how often a quorum is wrong (slide 23).
- **The 365-day shortcut** in Cohere's P2 and P3 happens to be harmless on this database (no customer is born in the 6 shifted days). The same query could fail differently on other data.
- **The hashes depend on our choice for the `date` field.** If the field changes, the hashes change. They would still be equal between the two 0 answers, because both answers are identical.
- **The proposed `age-window-nonempty` check** is a suggestion for this question type. It has not been implemented in the kit.

## How to reproduce the decomposition

From the repository root, open the database with `sqlite3 -readonly TD2/pair-b/data/boutique.sqlite` (same file as the kit's `data/boutique.sqlite`). Then, for each predicate (or combination), run:

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
