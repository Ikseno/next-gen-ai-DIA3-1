-- TD 2, Step 2 (Pair B) - C09: what each filter actually selects (empty-filter check).
-- A value of 0 from COALESCE(SUM(...), 0) can mean "customers found but no revenue" or "no row at all".
-- This query re-runs each model's own WHERE clause (verbatim, from faulty-north-mini-code.sql and
-- faulty-qwen.sql) and counts the order lines and distinct customers it keeps, next to the correct
-- age window (2000-09-26 < birth_date <= 2001-09-26). Run read-only:
--   sqlite3 -readonly TD2/pair-b/data/boutique.sqlite < TD2/pair-b/C09/empty-filter-check.sql
-- Output: empty-filter-check.csv. Deterministic check proposed in part2-sql-cause-marc.md: age-window-nonempty.
SELECT 'reference window' AS filter,
       COUNT(*) AS order_lines,
       COUNT(DISTINCT c.customer_id) AS customers,
       COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders  o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id  = o.product_id
  WHERE c.birth_date >  date('2026-09-26', '-26 years')
    AND c.birth_date <= date('2026-09-26', '-25 years')
UNION ALL
SELECT 'Cohere (north-mini-code)' AS filter,
       COUNT(*) AS order_lines,
       COUNT(DISTINCT c.customer_id) AS customers,
       COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders  o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id  = o.product_id
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
    )
UNION ALL
SELECT 'Qwen (qwen3.8-27b)' AS filter,
       COUNT(*) AS order_lines,
       COUNT(DISTINCT c.customer_id) AS customers,
       COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders  o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id  = o.product_id
  WHERE (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 25
    AND (strftime('%m-%d', o.date) >= strftime('%m-%d', c.birth_date))
    AND (strftime('%m-%d', o.date) < strftime('%m-%d', date(c.birth_date, '+26 years')));
