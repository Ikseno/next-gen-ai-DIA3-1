-- Customers aged 25 on 2026-09-24 omitted by BOTH faulty queries.
SELECT c.customer_id, c.birth_date,
       SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id = o.product_id
WHERE c.birth_date > '2000-09-24'
  AND c.birth_date <= '2001-09-24'
  AND NOT (c.birth_date >= '2001-09-24' AND c.birth_date < '2001-09-25')
  AND NOT (c.birth_date = '2001-09-24')
GROUP BY c.customer_id, c.birth_date
ORDER BY c.customer_id;
