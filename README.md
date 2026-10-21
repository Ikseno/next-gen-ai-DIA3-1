# next-gen-ai-DIA3-1

ESILV, A4 Data & AI, module **Next-Generation AI / Trustworthy Generative AI** (Didier Parisot).
Shared repository of **class DIA 3, sub-group 1 (DIA3-1)**, seven members, kept from TD 1 to TD 3.

- Course pack: **2026-10-14-students-1** (kit `kit-td1` dated 14 October 2026, `modeles-autorises.json` dated 2026-10-14)
- Database: `data/boutique.sqlite`, seed 20260925, SHA-256 `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2`, checked against `data/manifest.json` by `check_access.py`

## Members and TD 1 roles

| Member | References (step 1) | Role (step 2) | Model run |
|---|---|---|---|
| Dorian Courcelle | C04, C08, C16 | A | `groq:openai/gpt-oss-120b` |
| Raphaël Delavictoire | C05, C09, C17 | B | `groq:openai/gpt-oss-20b` |
| Mohamed Diawara | C01, C02, C15 | C | `openrouter:cohere/north-mini-code:free` |
| Marc Chen | C06, C10, C18 | D | `groq:qwen/qwen3.8-27b` |
| Alexandre Flavigny | C07, C11, C20 | E | `openrouter:dots-studio/dots-3-note-preview:free` |
| Maya Bourrey | C03, C12, C13 | F + G | cross-check of references, merge of traces |
| Yasmine Boukrouh | C14, C19 | H | summaries and pivot |

Seven members for eight roles: F and G are held by the same person. Roles rotate in TD 2 and TD 3.

## Environment

- Python 3.10 or later (runs used Python 3.13 on macOS and Python 3.14.8 / SQLite 3.50.4 on Windows PowerShell), virtual environment `.venv`, package `requests` (only for `check_access.py`; the skeleton uses the standard library).
- Personal free accounts: Groq Free plan and OpenRouter (no credits bought, `:free` models only, zero-price routes).
- API keys are environment variables `GROQ_API_KEY` and `OPENROUTER_API_KEY`, never written in this repository (see `.gitignore`).
- Call settings from the kit: temperature 0, capped output, 45 s timeout, 3 s between requests, one request in flight per sub-group, at most one retry per cell.

## Repository layout

| Path | Content |
|---|---|
| `reference-td1.csv` | **Deliverable 1.** The 20 reference queries and integer values, with the member who wrote each query (`author`) and the member who checked it (`checked_by`) |
| `results/traces-td1.csv`, `results/traces-td1.jsonl` | **Deliverable 2.** Every attempt of the five batches, errors and retries included, with the original measurements (106 lines; the JSONL is the five state files concatenated) |
| `results/model-question-comparison-en.csv` | **Deliverable 3.** One final row per model and question (100 rows) with the explanation of each result |
| `results/five-model-summary-en.csv` | **Deliverable 4.** The five models: public index, dated prices, access used, results by question family, limits |
| `prompt/prompts-en.md` | **Deliverable 5.** The prompt sent to the models (system message and user template), verbatim, with the fingerprint of each question |
| `results/pivot-td1.md` | Models x questions view of the comparison |
| `trace/traces-X.csv` | Raw traces of operator X (A to E), as produced by the skeleton |
| `state/state-X.jsonl` | State files of the runs (one line per attempt) |
| `explanation/explanations-X.csv` | Explanation of every final result of model X, written by its operator |
| `prompt/ai-assistance/` | AI-assistance disclosure: prompts each member sent to an AI assistant, and what was checked |
| `reports/td1.md` | Session report of the sub-group |
| `reports/contribution-*.md` | Individual contribution of each of the seven members |
| `skeleton-multi-llm-en.py` | The kit's orchestrator, unchanged (identical to the 14 October kit) |

## AI assistance (declared)

AI-assisted work is accepted in this module when it is declared, the prompts are kept and the decisions are explained. Every value and explanation was checked by the member responsible against the traces and the database; no model or assistant answer was used as a reference value.

| Member | Assistant | Where it is declared |
|---|---|---|
| Dorian Courcelle (A) | Claude | [`prompt/ai-assistance/ai-prompts-dorian-A.md`](prompt/ai-assistance/ai-prompts-dorian-A.md) (verbatim originals in [`reports/contribution-dorian-A.md`](reports/contribution-dorian-A.md), section 6) |
| Raphaël Delavictoire (B) | Claude | [`prompt/ai-assistance/ai-prompts-Raphael-B.md`](prompt/ai-assistance/ai-prompts-Raphael-B.md) |
| Mohamed Diawara (C) | Claude | [`prompt/ai-assistance/ai-prompts-mohamed-C.md`](prompt/ai-assistance/ai-prompts-mohamed-C.md) |
| Marc Chen (D) | Claude | [`prompt/ai-assistance/ai-prompts-marc-D.md`](prompt/ai-assistance/ai-prompts-marc-D.md) |
| Alexandre Flavigny (E) | ChatGPT (and Codex, Claude for references) | [`prompt/ai-assistance/ai-prompts-alexandre-E.md`](prompt/ai-assistance/ai-prompts-alexandre-E.md) |
| Maya Bourrey (F + G) | **No AI assistant used** | — |
| Yasmine Boukrouh (H) | Codex | [`reports/contribution-yasmine-boukrouh.md`](reports/contribution-yasmine-boukrouh.md), section *AI assistance disclosure* |

## Reproduce

From the extracted `kit-td1` folder of the 14 October kit, with this repository next to it:

```bash
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
python3 -m pip install requests
python3 verify-data.py                                    # data integrity, last object "ok": true
cp ../next-gen-ai-DIA3-1/reference-td1.csv .              # our checked references

# Replay the stored SQL offline (no key, no network): re-executes each model's SQL and recomputes the verdicts
python3 skeleton-multi-llm-en.py --replay ../next-gen-ai-DIA3-1/results/traces-td1.jsonl --state replay-td1.jsonl --out replay-td1.csv

# Re-run a model for real (needs the keys exported in the shell; counts against the account allowance)
export GROQ_API_KEY="..."; export OPENROUTER_API_KEY="..."
python3 check_access.py --no-network                      # local checks only, no call
python3 skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --state state-A.jsonl --out traces-A.csv
```

Model identifiers per operator are in the table above. A changed prompt or reference starts a new experiment: new `--state` and `--out` files, old ones kept.

Operator A resumed after a manual interruption (Ctrl+C after C01, no extra call) with `--pause 8` to stay under the Groq Free limit of 8,000 tokens per minute. Operators B, C, D and E used the default 3-second pause (median gap between successive calls in the traces: 3 to 6 s, i.e. 3 s + latency).

## TD 1 status

Completed: 20 references; 100 base cells (60 Groq, 40 OpenRouter), all executed; 6 retries after HTTP 429 (B: C20; D: C16 to C20), all succeeded on the second attempt. 106 trace lines in total.

| Model | Correct / 20 |
|---|---|
| A, gpt-oss-120b (Groq) | 20 |
| B, gpt-oss-20b (Groq) | 17 |
| C, cohere north-mini-code (OpenRouter) | 12 (7 incorrect, 1 invalid SQL) |
| D, qwen3.8-27b (Groq) | 15 |
| E, dots-3-note-preview (OpenRouter) | 15 |

Every failure is on an age question; all period and product-only questions are correct for all five models.

Replay check: re-executing the stored SQL of `results/traces-td1.jsonl` offline against `reference-td1.csv` (command above) gives the same scores (20, 17, 12, 15, 15).

**Open blocks:** comparison of the references with the instructor's answer key (end of session); member preparing TD 2 to be designated; access-check count and OpenRouter allowance of operator E not recorded (missing measurement).
Wrong agreements kept for TD 2: C08 (B and E both 25920, reference 605580), C10 (D and E both 119410, reference 558980), C09 (C and D both 0, reference 487980).

