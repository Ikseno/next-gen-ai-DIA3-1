# TD 1 reference calculations — review draft

The 20 SQLite queries in `reference-td1.csv` were executed against the supplied database in read-only mode. All 20 results agree with a separate Python iteration over the supplied CSV files. The two implementations share the case definitions, so agreement does not replace review of the question interpretation.

## Conventions to explain

- Revenue is the sum of each order line's quantity multiplied by its product price, in integer euro cents excluding VAT. Do not count orders instead of lines, and do not divide by 100 in the submitted reference.
- Periods include the start timestamp and exclude the end timestamp. C05 includes 1 June only; C07 includes 31 May only.
- Completed age subtracts one from the year difference if the birthday has not yet occurred. C02, C08, C09 and C11 use different reference dates and include all orders of the matching customers.
- C10 and C18 calculate age on each order date. They do not use the fixed reference date from C02.
- Product filters apply to individual lines. A mixed order contributes only its matching products.
- An empty selection returns integer zero through COALESCE. C06 and C14 both returned zero.

## Validation status

- SQLite execution: complete.
- CSV computational cross-check: complete, 20/20 agree.
- Another group member's independent review: pending.
- Instructor comparison with the answer key: pending.
- Model experiments: all five batches attempted; comparison and summary drafts prepared. Qwen C18 exhausted its two attempts with HTTP 429.


