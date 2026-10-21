# TD 1 — Models × questions

Final attempt of each cell (100 cells, all real calls). Source: [`model-question-comparison-en.csv`](model-question-comparison-en.csv); every cell points to its line in [`traces-td1.csv`](traces-td1.csv).

**Legend:** ✓ correct · ✗ wrong value · SQL✗ invalid SQL · ↻ answered on the 2nd attempt after an HTTP 429 · ✓* correct value with a wrong age rule (correct by chance)

| Model | C01 | C04 | C05 | C06 | C07 | C20 | C03 | C12 | C13 | C14 | C02 | C08 | C09 | C10 | C11 | C15 | C16 | C17 | C18 | C19 | Correct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| *Family* | period | period | period | period | period | period | product | product | product | product | age | age | age | age | age | combined | combined | combined | combined | combined | |
| **gpt-oss-120b** (A, Groq) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **20/20** |
| **gpt-oss-20b** (B, Groq) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ ↻ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | **17/20** |
| **north-mini-code** (C, OpenRouter) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | SQL✗ | ✗ | ✓ | ✗ | ✗ | ✓* | **12/20** |
| **qwen3.8-27b** (D, Groq) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ ↻ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ ↻ | ✗ ↻ | ✓ ↻ | ✗ ↻ | **15/20** |
| **dots-3-note-preview** (E, OpenRouter) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | **15/20** |
| *Models failing* | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 3 | 3 | 2 | 2 | 1 | 2 | 2 | 1 | |

## By family

| Model | Period (6) | Product (4) | Age (5) | Combined (5) |
|---|---|---|---|---|
| gpt-oss-120b | 6/6 | 4/4 | 5/5 | 5/5 |
| gpt-oss-20b | 6/6 | 4/4 | 2/5 | 5/5 |
| north-mini-code | 6/6 | 4/4 | 0/5 | 2/5 |
| qwen3.8-27b | 6/6 | 4/4 | 3/5 | 2/5 |
| dots-3-note-preview | 6/6 | 4/4 | 2/5 | 3/5 |

## Reading

- **Every failure is on the completed-age convention.** All five models get the 10 period and product questions right.
- **Most missed: C08, C09, C10** (3 models of 5 each). C08 and C09 move the reference date one day around C02; C10 takes the age at the time of each order.
- **✓\* C19 for north-mini-code:** the value matches, but the age test compares month-year strings: it keeps C003 (aged 24) and drops C005 (aged 25), neither of whom bought product d in September. A correct value is not a correct query.
- **↻ 6 retries, all recovered:** gpt-oss-20b C20 (Groq tokens-per-minute limit) and qwen3.8-27b C16–C20 (Groq output-tokens-per-minute limit, 1000). An HTTP 429 is a refused access, not a wrong answer; the only invalid answer is north-mini-code C11 (HTTP 200, `? :` is not SQLite).
- Twenty questions, one run per cell at temperature 0: a routing hypothesis for this task, not a general ranking.
