# Next Generation AI – TD 1 – sub-group DIA3-1

ESILV, module *Trustworthy Generative AI* (MESIIN475926), lab session 1 of 21 October 2026.
Student pack `2026-10-14-students-1` (14 October 2026).

## Sub-group and roles (TD 1)

| Member | Role | TD 1 task |
|---|---|---|
| Dorian | A | `groq:openai/gpt-oss-120b`, 20 cells, explanations |
| Raphaël | B | `groq:openai/gpt-oss-20b`, 20 cells, explanations |
| Mohamed | C | `openrouter:cohere/north-mini-code:free`, 20 cells, explanations (personal OpenRouter account) |
| Marc | D | `groq:qwen/qwen3.8-27b`, 20 cells, explanations |
| Alexandre | E | `openrouter:dots-studio/dots-3-note-preview:free`, 20 cells, explanations (second, distinct OpenRouter account) |
| Maya | F + G | reference cross-check, merge of the traces |
| Yasmine | H | comparison CSV, five-model summary, pivot for the plenary |
| _TODO_ | | _8th member, if any_ |

All members wrote and cross-checked part of the twenty reference queries (see `reference-td1.csv`).

## Data and environment

- Database: `data/boutique.sqlite` from the kit, seed 20260925, never modified.
  SHA-256 `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2` (identical to the kit's `manifest.json`).
- Python 3.14.8, SQLite 3.50.4, Windows / PowerShell, virtual environment `.venv` with `requests` (not committed).
- Keys: `GROQ_API_KEY` and `OPENROUTER_API_KEY` set as environment variables on each operator's machine only. No key, `.env` file or virtual environment is committed (see `.gitignore`).

## Repository contents

| Path | Content |
|---|---|
| `reference-td1.csv` | C01–C20: reference SQL and `revenue_cents`, computed on the database and independently checked |
| `trace/traces-A.csv` … `traces-E.csv` | raw CSV traces per operator, every attempt kept (106 lines: 100 first attempts + 6 retries after HTTP 429) |
| `state/state-A.jsonl` … `state-E.jsonl` | raw JSONL state files of the skeleton (source of the CSV traces) |
| `explanation/` | per-model explanation of every failure (and of every cell for A) |
| `prompts-en.md` | system message and user template, verbatim, with the prompt fingerprint per question |
| `reports/td1.md` | session report |
| `traces-td1.csv` | merge of the five operators' CSV traces, one header, all 106 attempts |
| _TODO_ `traces-td1.jsonl` | merge of the five JSONL state files |
| `model-question-comparison-en.csv` | one final row per model × question (100 rows) |
| `pivot-td1.md` | models × questions pivot of the comparison CSV, for the plenary |
| _TODO_ `five-model-summary-en.csv` | five models: index, dated prices, access, results by family |

## Commands

Run from the kit folder `kit-td1` (PowerShell: `python`, bash: `python3`):

```bash
python check_access.py                    # environment, database hash, one probe per model
# one operator at a time, each with their own state/out files:
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --state state-A.jsonl --out traces-A.csv --pause 8
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-20b --state state-B.jsonl --out traces-B.csv
python skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --state state-C.jsonl --out traces-C.csv
python skeleton-multi-llm-en.py --run --models groq:qwen/qwen3.8-27b --state state-D.jsonl --out traces-D.csv
python skeleton-multi-llm-en.py --run --models openrouter:dots-studio/dots-3-note-preview:free --state state-E.jsonl --out traces-E.csv
python skeleton-multi-llm-en.py --rates --state state-A.jsonl   # rates per model
```

_TODO: each operator checks the `--pause` value actually used (A: default 3 s for C01, then `--pause 8`)._
To replay offline from a fresh clone: copy `reference-td1.csv` into `kit-td1`, then
`python skeleton-multi-llm-en.py --replay ../trace/traces-A.csv` (no key, no network).

## TD 1 status

Completed: 20 references; 100 base cells (60 Groq, 40 OpenRouter), all executed, 6 retries after HTTP 429 (B: C20; D: C16–C20), all succeeded on the second attempt.

| Model | Correct / 20 |
|---|---|
| A – gpt-oss-120b (Groq) | 20 |
| B – gpt-oss-20b (Groq) | 17 |
| C – cohere north-mini-code (OpenRouter) | 12 (7 incorrect, 1 invalid SQL) |
| D – qwen3.8-27b (Groq) | 15 |
| E – dots-3-note-preview (OpenRouter) | 15 |

Every failure is on an age question; all period and product-only questions are correct for all five models.
Wrong agreements noted for TD 2: C08 (B and E both 25920, reference 605580), C10 (D and E both 119410, reference 558980), C09 (C and D both 0, reference 487980).

Open items: see the _TODO_ lines above.
