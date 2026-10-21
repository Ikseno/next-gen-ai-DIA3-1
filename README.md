# next-gen-ai-DIA3-1

ESILV, A4 Data & AI, module **Next-Generation AI / Trustworthy Generative AI** (Didier Parisot).
Shared repository of sub-group **DIA3-1**, kept from TD 1 to TD 3.

- Course pack: **2026-10-14-students-1** (kit `kit-td1` dated 14 October 2026, `modeles-autorises.json` dated 2026-10-14)
- Database: `data/boutique.sqlite`, seed 20260925, SHA-256 checked against `data/manifest.json` by `check_access.py`

## Members and TD 1 roles

| Member | References (step 1) | Role (step 2) | Model run |
|---|---|---|---|
| Dorian Courcelle | C04, C08, C16 | A | `groq:openai/gpt-oss-120b` |
| Raphaël de la Victoire | C05, C09, C17 | B | `groq:openai/gpt-oss-20b` |
| Mohamed Diawara | C01, C02, C15 | C | `openrouter:cohere/north-mini-code:free` |
| Marc Chen | C06, C10, C18 | D | `groq:qwen/qwen3.8-27b` |
| Alexandre Flavigny | C07, C11, C20 | E | `openrouter:dots-studio/dots-3-note-preview:free` |
| Maya Bourrey | C03, C12, C13 | F + G | cross-check of references, merge of traces |
| Yasmine | C14, C19 | H | summaries and pivot |

Seven members for eight roles: F and G are held by the same person. Roles rotate in TD 2 and TD 3.

## Environment

- Python 3.10 or later (run with Python 3.13 on macOS), virtual environment `.venv`, package `requests` (only for `check_access.py`; the skeleton uses the standard library).
- Personal free accounts: Groq Free plan and OpenRouter (no credits bought, `:free` models only, zero-price routes).
- API keys are environment variables `GROQ_API_KEY` and `OPENROUTER_API_KEY`, never written in this repository (see `.gitignore`).
- Call settings from the kit: temperature 0, capped output, 45 s timeout, 3 s between requests, one request in flight per sub-group, at most one retry per cell.

## Repository layout

| Path | Content |
|---|---|
| `reference-td1.csv` | The 20 reference queries and values, computed with SQL on the database and cross-checked |
| `trace/traces-X.csv` | Raw traces of operator X (A to E), every attempt |
| `state/state-X.jsonl` | State files of the runs (one line per attempt) |
| `traces-td1.csv` | All raw traces merged under one header (106 lines, retries included) |
| `explanation/` | Per-model explanation of every final result, written by each operator |
| `model-question-comparison-en.csv` | One final row per model and question (100 rows) |
| `pivot-td1.md` | Models x questions view of the comparison |
| `reports/td1.md` | Session report |

## Reproduce

From the extracted `kit-td1` folder of the 14 October kit, with this repository next to it:

```bash
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
python3 -m pip install requests
python3 verify-data.py                                    # data integrity, last object "ok": true
cp ../next-gen-ai-DIA3-1/reference-td1.csv .              # our checked references

# Replay the stored SQL offline (no key, no network): re-executes each model's SQL and recomputes the verdicts
python3 skeleton-multi-llm-en.py --replay ../next-gen-ai-DIA3-1/state/state-C.jsonl --state replay-C.jsonl --out replay-C.csv

# Re-run a model for real (needs the keys exported in the shell; counts against the account allowance)
export GROQ_API_KEY="..."; export OPENROUTER_API_KEY="..."
python3 check_access.py --no-network                      # local checks only, no call
python3 skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --state state-A.jsonl --out traces-A.csv
```

Model identifiers per operator are in the table above. A changed prompt or reference starts a new experiment: new `--state` and `--out` files, old ones kept.
