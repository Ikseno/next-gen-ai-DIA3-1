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
