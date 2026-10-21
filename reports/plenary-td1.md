# TD 1 plenary - sub-group DIA3-1

Same database, same 20 questions, same prompt (one `prompt_sha256` per question across the five models, see `prompt/model-prompt-td1.md`), temperature 0. Real calls only, no replay, no credits bought.

## 1. Results (final attempt per cell)

| Model (operator, access) | Score | Failed questions |
|---|---|---|
| openai/gpt-oss-120b (A, Groq Free) | **20/20** | none |
| openai/gpt-oss-20b (B, Groq Free) | 17/20 | C02, C08, C11 |
| qwen/qwen3.8-27b (D, Groq Free) | 15/20 | C09, C10, C15, C17, C19 |
| dots-studio/dots-3-note-preview:free (E, OpenRouter) | 15/20 | C08, C09, C10, C16, C18 |
| cohere/north-mini-code:free (C, OpenRouter) | 12/20 | C02, C08, C09, C10, C11, C15, C17, C18 |

Full models x questions view: `results/pivot-td1.md`. Rows and causes: `results/model-question-comparison-en.csv`.

## 2. By question family

| Family (questions) | gpt-oss-120b | gpt-oss-20b | qwen3.8-27b | dots-3-note | north-mini-code |
|---|---|---|---|---|---|
| Period (6) | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| Product list (4) | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Age (5) | 5/5 | 2/5 | 3/5 | 2/5 | 0/5 |
| Combined (5) | 5/5 | 5/5 | 2/5 | 3/5 | 2/5 |

**Every failure involves the completed-age convention.** No model misses a period or product question.

## 3. Questions most models miss

- **C08, C09, C10**: missed by 3 of 5 models each.
- C08 and C09 move the reference date one day before / after C02 (2026-09-24, 2026-09-26): customers born around 25 September flip in or out.
- C10 computes the age at the time of each order, not on a fixed date.

Recurring causes read in the SQL: age window too wide (0 to 25 instead of exactly 25), a single birth date or birth year instead of a one-year window, year difference without the month-day test, wrong `substr` positions, and one syntax error (`? :` is not SQLite).

## 4. A correct value is not a correct query

C19 (product d, September 2026, age 25 on 2026-09-25) is marked correct for Cohere, but its age test compares month-year strings: it keeps C003 (born 2001-09-26, aged 24) and drops C005 (born 2000-09-26, aged 25). Neither bought product d in September, so the value happens to match. Dots also gets C19 with an incomplete age predicate (it misses customers born late 2000).

## 5. Traces to explain

- **Access, recovered**: `groq:qwen/qwen3.8-27b:C16`, attempt 1 = HTTP 429, Groq limit on *output tokens per minute* (limit 1000, used 913, requested 132), `not_executed`, no tokens recorded; attempt 2 three seconds later = HTTP 200, 620 prompt + 175 completion tokens, correct. Same prompt fingerprint on both lines. 6 such 429s in total (1 for B, 5 for D), each recovered by its single allowed retry.
- **Invalid SQL, not an access failure**: `openrouter:cohere/north-mini-code:free:C11`, HTTP 200, 551 + 165 tokens, native cost 0, verdict `sql_invalid` (`syntax error near "?"`).
- **Missing measurement**: Groq returns no native cost; `cost_native` stays empty, not 0.

## 6. Portfolio and routing hypothesis

| Model | Public index (28/09) | Paid route, same model (USD / M tokens in-out, 05/10) |
|---|---|---|
| gpt-oss-120b | 11.6 | Groq Developer 0.15 / 0.60 |
| gpt-oss-20b | 9 | Groq Developer 0.075 / 0.30 |
| qwen3.8-27b | 33.7 | Groq Developer 0.80 / 4.00 |
| north-mini-code:free | N/A | N/A (no documented paid route) |
| dots-3-note-preview:free | N/A | N/A (no documented paid route) |

The highest public index (Qwen) is not the best on our task, and the best model here (gpt-oss-120b) is cheaper than Qwen.

**Hypothesis for TD 2, from this batch only:** period and product questions can go to the cheapest model; age questions need gpt-oss-120b or a vote between models, and a disagreement should be reported rather than resolved by picking a value. Twenty questions, one run per cell at temperature 0: not a general ranking.
