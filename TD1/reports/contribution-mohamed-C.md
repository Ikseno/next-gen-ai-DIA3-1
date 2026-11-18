# TD 1 — Individual contribution: Mohamed Diawara (role C)

**Model operated:** `openrouter:cohere/north-mini-code:free` (Cohere North Mini Code, OpenRouter free route)
**References assigned:** C01, C02, C15 (in the group's [`reference-td1.csv`](../reference-td1.csv))
**Cross-check:** I re-ran and checked Dorian's references (C04, C08, C16); mine were checked by Yasmine.

## 1. Preparation

- Kit of 14 October extracted, `.venv` with `requests`, `verify-data.py` → `"ok": true`.
- Access check run twice (16 and 21 October), both **5/5 models OK**, saved in `ready-for-td1.txt` and `check-21oct.txt`. Each check = 3 Groq + 2 OpenRouter calls, counted outside the base batch.
- Allowances recorded on 21 October at 11:12 (Paris): Groq Free organisation limits 30 RPM, 1K RPD, 8K TPM, 200K TPD for each of the three Groq models; OpenRouter free requests 2 used, 48 remaining out of 50.

## 2. Batch C

- One test call on C01 (12:13 Paris, correct), then C02–C20 with the same `--state` file (12:14–12:17 UTC).
- **20 initial calls, 0 retry, 0 HTTP error.** Median latency 2.9 s; 11,194 prompt tokens and 2,848 completion tokens in total; native cost 0 on every line (free route).
- OpenRouter allowance after the batch: 22 used, **28 remaining** out of 50 (14:19 Paris).
- Files: [`trace/traces-C.csv`](../trace/traces-C.csv), [`state/state-C.jsonl`](../state/state-C.jsonl).

## 3. Results and explanations

**12/20 correct** — all period (6/6) and product (4/4) questions; 0/5 age; 2/5 combined.

| Question | Verdict | Cause read in the returned SQL |
|---|---|---|
| C02 | incorrect (0) | Month-day compared without the birth year; contradictory conditions, no customer kept |
| C08 | incorrect (too high) | Window `birth_date > date(ref, '-26 years')`: customers aged 0 to 25, not exactly 25 |
| C09 | incorrect (0) | `('2026-09-26' - birth_date)/365`: SQLite keeps the leading year (25), then 25/365 = 0 |
| C10 | incorrect (0) | No `= 25` condition; `'+' \|\| N + 1 \|\| ' years'` gives a number, `strftime` returns NULL |
| C11 | sql_invalid | `? :` operator does not exist in SQLite: `syntax error near "?"` (HTTP 200, not an access failure) |
| C15 | incorrect (too high) | Period correct; same 0-to-25 age window as C08 |
| C17 | incorrect (0) | `substr(birth_date,7,4)` gives `'9-25'`: computed age about 2017 |
| C18 | incorrect (too high) | No upper age bound (older customers kept); day extracted as `'9-'` |
| C19 | correct **by chance** | Month-year compared instead of month-day: keeps C003 (24), drops C005 (25); neither bought product d in September |

Each cause was checked with small SQLite queries (e.g. `substr` positions, text subtraction, `||` precedence) before being recorded in [`explanation/explanations-C.csv`](../explanation/explanations-C.csv), one row for each of the 20 questions.

## 4. Group work

- Proposed the split of the 20 references and of the roles A–H for seven members.
- Merged the five trace files into [`results/traces-td1.csv`](../results/traces-td1.csv) and [`results/traces-td1.jsonl`](../results/traces-td1.jsonl) (106 lines; Maya made a parallel merge, same rows), built [`results/model-question-comparison-en.csv`](../results/model-question-comparison-en.csv) (100 rows) and [`results/pivot-td1.md`](../results/pivot-td1.md); checked that every question has one prompt fingerprint across the five models.
- Checked the other explanation files, the five-model summary and the prompt file against the traces; added the C19 limit to the summary.
- Repository: README, kit `.gitignore`, layout (`results/`, `reports/`, `prompt/`), merge conflicts, consolidation of the group report [`td1.md`](td1.md).

## 5. AI assistance

Claude was used for setup, trace reading, explanation drafts, file merging, checks and documentation. Prompts and the split between the assistant's work and my checks: [`prompt/ai-assistance/ai-prompts-mohamed-C.md`](../prompt/ai-assistance/ai-prompts-mohamed-C.md).

## 6. What I take from it, next steps

- A correct value does not prove a correct query (C19): for TD 2, the vote should be read together with the SQL, not only the values.
- Cohere handles period and product filters reliably on this task but not date arithmetic in SQLite; it is a candidate for the "cheap route" of simple questions, not for age questions.
- Help needed: none for now.
