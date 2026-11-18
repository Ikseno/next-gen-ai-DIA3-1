SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders AS o
JOIN product AS p ON p.product_id = o.product_id
JOIN customers AS c ON c.customer_id = o.customer_id
WHERE (CAST(strftime('%Y', '2026-09-24') AS INTEGER) - CAST(substr(c.birth_date, 1, 4) AS INTEGER) - (strftime('%m-%d', '2026-09-24') < substr(c.birth_date, 6, 5))) = 25;
