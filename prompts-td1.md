# TD 1 — Exact model prompts

This document records the common prompts used by the TD 1 orchestration script (`skeleton-multi-llm-en.py`) for all five model evaluations. The prompt text below is transcribed from the Python definitions of `SYSTEM_PROMPT` and `USER_PROMPT_TEMPLATE`.

## 1. System message (exact text)

````text
You write SQLite queries for a small e-commerce database. Reply with exactly one SQLite SELECT statement and nothing else: no explanation, no comments, no markdown other than an optional ```sql fence.
````

## 2. User message template (exact text)

````text
Schema (SQLite):
{schema}

Conventions (binding):
- product.price is the unit price in euro cents, excluding VAT (an integer). Revenue excluding VAT is SUM(quantity_product * price), an integer number of cents.
- orders holds order lines: one row per (order_id, product_id). All lines of an order share the same customer_id and the same date.
- orders.date and customers.insert_date are UTC timestamps stored as text 'YYYY-MM-DD HH:MM:SS'. customers.birth_date is a date stored as text 'YYYY-MM-DD'. Compare them as text or with SQLite date functions.
- A period "from S to E" is closed on the left and open on the right: date >= S AND date < E.
- A customer's age on a day D is the number of completed years: someone born on B is N years old on D when the N-th anniversary of B is on or before D and the (N+1)-th anniversary is after D. "Exactly 25 years old" means completed age 25 on that day, computed from month and day, never from the year difference alone.
- Unless the question says "at the time of the order", ages are computed on the reference date given in the question.
- The query must return exactly one row and one column named revenue_cents. When no order line matches, return 0 (use COALESCE), not NULL.
- Use only the tables above. One SELECT statement, nothing else.

Question: {question}
````

## 3. How the template is populated

- `{schema}` is replaced by the SQLite database schema provided to the orchestration script.
- `{question}` is replaced by the text of the question being tested (C01–C20).
- The rendered user prompt differs from one question to another, but the **same system message and user template** apply to every model for a given question.
- `prompt_sha256` in `traces-td1.csv` records the prompt fingerprint for each call and can be used to verify that models received equivalent prompts for a given case.

## 4. Reproducibility evidence

- Orchestrator/source: `skeleton-multi-llm-en.py` (keep the exact version used to run the tests).
- Model configuration: `modeles-autorises.json` (or the exact configuration used during execution).
- Questions and schema: preserve the corresponding source files from the TD 1 kit.
- Raw API evidence: `traces-td1.csv` plus each model's individual trace CSV and JSONL state file.
- Reference answers: `reference-td1.csv`.

If the subgroup modified the prompt text during the experiment, document the exact modification here and retain the corresponding original trace files. Do not rewrite the source prompt after the experiment.
