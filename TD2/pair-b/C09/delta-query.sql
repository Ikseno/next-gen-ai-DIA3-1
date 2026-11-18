-- TD 2, Step 2 (Pair B) - Wrong consensus on C09
-- Question C09: revenue excl. VAT (cents) of customers exactly 25 years old on 2026-09-26 (all their orders).
-- Reference (TD1/reference-td1.csv, official value): 487980. Cohere and Qwen both return 0.
-- Faulty WHERE clauses (complete queries in faulty-north-mini-code.sql and faulty-qwen.sql):
--   Cohere: CAST((strftime('%Y-%m-%d', '2026-09-26') - c.birth_date) / 365 AS INTEGER) = 25 AND ...
--           (text minus text = 25 years, then 25 / 365 = 0 in integer division: always false)
--   Qwen:   (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 25
--           AND strftime('%m-%d', o.date) >= strftime('%m-%d', c.birth_date)
--           AND strftime('%m-%d', o.date) <  strftime('%m-%d', date(c.birth_date, '+26 years'))
--           (age at the order date, not on 2026-09-26, and the two month-day conditions contradict each other)
-- empty-filter-check.sql shows that both filters keep 0 order lines and 0 customers.
--
-- Delta query: every customer the reference counts, with the revenue of all their orders.
-- Both faulty queries select no customer (they return 0), so every row below is a row they miss,
-- and the sum of the rows is the exact gap 487980 - 0.
-- Completed age 25 on 2026-09-26  <=>  2000-09-26 < birth_date <= 2001-09-26
-- (formulated as a date window, independently of the year/month-day formula of the reference query).
SELECT c.customer_id, c.birth_date,
       COUNT(*)                          AS order_lines,
       SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers AS c
JOIN orders  AS o ON o.customer_id = c.customer_id
JOIN product AS p ON p.product_id  = o.product_id
WHERE c.birth_date >  date('2026-09-26', '-26 years')   -- born after 2000-09-26 (not yet 26)
  AND c.birth_date <= date('2026-09-26', '-25 years')   -- born on or before 2001-09-26 (already 25)
GROUP BY c.customer_id, c.birth_date
ORDER BY c.birth_date;

-- Total, to compare with the reference and with the faulty value 0
-- (COALESCE so that an empty window would give 0, not NULL):
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers AS c
JOIN orders  AS o ON o.customer_id = c.customer_id
JOIN product AS p ON p.product_id  = o.product_id
WHERE c.birth_date >  date('2026-09-26', '-26 years')
  AND c.birth_date <= date('2026-09-26', '-25 years');

-- Boundary customers (why the window is exactly this one):
SELECT customer_id, birth_date FROM customers
WHERE birth_date BETWEEN '2000-09-24' AND '2000-09-27'
   OR birth_date BETWEEN '2001-09-24' AND '2001-09-27'
ORDER BY birth_date;
