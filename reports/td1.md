# TD 1 report — Comparing five free models on the same 20 questions

**Class DIA 3, sub-group 1 (DIA3-1)** · Session of 21 October 2026 · Course pack `2026-10-14-students-1` (kit of 14 October 2026)
Members: Dorian Courcelle (A), Raphaël Delavictoire (B), Mohamed Diawara (C), Marc Chen (D), Alexandre Flavigny (E), Maya Bourrey (F + G), Yasmine Boukrouh (H).

All figures below are computed from the files of this repository. Every model call counted here is a real call (`nature = real`); no replayed or simulated line is used.

## 1. What we attempted and what we completed

| Step | Status | Evidence |
|---|---|---|
| Machine preparation and access check | Done before the session | `check_access.py` output kept by each member (5/5 models OK for C on 16 and 21 October) |
| 1. Twenty reference queries | Done: 20/20 queries written and run on `data/boutique.sqlite`, cross-checked by a second member, values recomputed independently twice (see section 5) | [`reference-td1.csv`](../reference-td1.csv) |
| 2. Five model batches (100 base cells) | Done: 100/100 cells with a final answer, 6 retries | [`trace/`](../trace/), [`state/`](../state/), merged in [`results/traces-td1.csv`](../results/traces-td1.csv) and [`results/traces-td1.jsonl`](../results/traces-td1.jsonl) |
| 3. Trace reading and explanations | Done for the 100 cells | [`explanation/`](../explanation/), [`results/model-question-comparison-en.csv`](../results/model-question-comparison-en.csv) |
| 3. Five-model summary | Done | [`results/five-model-summary-en.csv`](../results/five-model-summary-en.csv) |
| Prompt as used | Done, verified against the traces | [`prompt/prompts-en.md`](../prompt/prompts-en.md) |
| 4. Plenary | No oral presentation this session; models x questions view ready | [`results/pivot-td1.md`](../results/pivot-td1.md) |

## 2. What worked

**Same prompt for every model.** For each of the 20 questions, the `prompt_sha256` is identical on every line of the five trace files, retries included. The prompt is the kit's `build_prompt()` output, unchanged; `skeleton-multi-llm-en.py` in this repository is byte-identical to the kit's.

**Results (final attempt per cell):**

| Model | Operator, access | Correct | Failed questions |
|---|---|---|---|
| `openai/gpt-oss-120b` | A, Groq Free | **20/20** | — |
| `openai/gpt-oss-20b` | B, Groq Free | 17/20 | C02, C08, C11 |
| `qwen/qwen3.8-27b` | D, Groq Free | 15/20 | C09, C10, C15, C17, C19 |
| `dots-studio/dots-3-note-preview:free` | E, OpenRouter | 15/20 | C08, C09, C10, C16, C18 |
| `cohere/north-mini-code:free` | C, OpenRouter | 12/20 | C02, C08, C09, C10, C11 (invalid SQL), C15, C17, C18 |

Final verdicts over the 100 cells: 79 correct, 20 incorrect value, 1 invalid SQL, 0 access failure.

**By question family** (6 period, 4 product list, 5 age, 5 combined):

| Family | gpt-oss-120b | gpt-oss-20b | qwen3.8-27b | dots-3-note | north-mini-code |
|---|---|---|---|---|---|
| Period | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| Product list | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Age | 5/5 | 2/5 | 3/5 | 2/5 | 0/5 |
| Combined | 5/5 | 5/5 | 2/5 | 3/5 | 2/5 |

## 3. What failed, and why

**Observation.** All 21 failed cells involve the completed-age convention ("exactly 25 years old"). No model fails a period-only or product-only question. C08, C09 and C10 are each missed by 3 of the 5 models.

**Causes read in the returned SQL** (one cause per cell, detailed in `explanation/explanations-X.csv`):

- age window too wide: customers aged 0 to 25 kept instead of exactly 25 (e.g. Cohere C08, C15);
- one birth date or one birth year instead of a one-year window (e.g. gpt-oss-20b C02, C08; Dots C08, C09);
- year difference without the month-day test, or the month-day test inverted (e.g. Qwen C10, C17; Dots C10, C18);
- string handling errors in SQLite: wrong `substr` positions (Cohere C17, C18), text subtraction of dates (Cohere C09), `||` evaluated before `+` making `strftime` return NULL (Cohere C10), comparison of a year string with a full date (Qwen C19);
- one syntax error: the `? :` operator does not exist in SQLite (Cohere C11, HTTP 200, `syntax error near "?"`). This is a wrong answer, not an access failure.

**A correct value is not always a correct query.** Cohere's C19 matches the reference, but its age test compares month-year strings: it keeps C003 (born 2001-09-26, aged 24) and drops C005 (born 2000-09-26, aged 25). Neither bought product d in September 2026, so the value is unaffected. Dots' C19 is also correct with an incomplete age predicate (customers born late 2000 are missed). Both are recorded as correct, with this limit stated.

**Hypotheses (not verified here).** The age convention is written in the prompt, yet four of five models still apply a simpler rule; this suggests the difficulty is in translating "completed age" into SQLite string/date functions rather than in understanding the question. Testing this would need a variant prompt, i.e. a separate experiment.

## 4. Access, attempts and missing measurements

| Operator | Initial calls | Retries | HTTP 429 (all recovered) |
|---|---|---|---|
| A | 20 | 0 | 0 |
| B | 20 | 1 | 1 — C20, Groq tokens per minute (limit 8000) |
| C | 20 | 0 | 0 |
| D | 20 | 5 | 5 — C16 to C20, Groq **output** tokens per minute (limit 1000) |
| E | 20 | 0 | 0 |
| **Total** | **100** | **6** | **6** |

- Each 429 cell was retried once, about three seconds later, and answered with HTTP 200; no cell exceeded two attempts.
- Qwen's 429s come from an output-tokens-per-minute limit of 1000 that is not shown in the limits table of the Groq console (which lists 8K tokens per minute); the limit and usage are in the error message of the trace.
- Access checks are counted separately from the 100 base cells: member C ran two full checks (16 and 21 October, 3 Groq + 2 OpenRouter calls each); OpenRouter allowance of C after the batch: 28 of 50 free requests left (21 October, 14:19 Paris). Other operators, from their contribution notes:
  - A: one full check on 21 October, 09:05 Paris (3 Groq + 2 OpenRouter calls); Groq Free limits read on the console for `openai/gpt-oss-120b` (30 RPM, 1K RPD, 8K TPM, 200K TPD); about 1 request used on this model before the batch, about 21 after. Remaining count after the batch not read on the console.
  - B: one full check on 16 October, 01:31 Paris (3 Groq + 2 OpenRouter calls); Groq allowance before and after the batch **not recorded** (missing measurement).
  - D: one full check on 16 October and one on 21 October at about 14:20 Paris (2 × (3 Groq + 2 OpenRouter) calls), plus a `--no-network` local check; allowance before and after the batch not recorded.
  - E: one test call on C01 before the batch (counted in the 20 base calls); access-check count and OpenRouter allowance before and after the batch not recorded (missing measurement).
  - Pause between requests: A used `--pause 8` after C01; B, C, D and E used the default 3 s. The trace timestamps agree: median gap between successive calls of 9 s for A and 3 to 6 s for B to E (3 s pause + latency).
- Native cost: empty for every Groq line (Groq returns no cost: missing measurement, not zero); 0 for every OpenRouter line (free route). No credit was bought, no paid plan was enabled.

## 5. Decisions, limits and uncertainty

- **References.** Each value comes from SQL run read-only on the database; no model answer was used as a reference. Each member's queries were re-run and checked by another member, in a circle so that nobody checks their own work:

  | Author | Questions | Checked by |
  |---|---|---|
  | Mohamed Diawara | C01, C02, C15 | Yasmine Boukrouh |
  | Dorian Courcelle | C04, C08, C16 | Mohamed Diawara |
  | Raphaël Delavictoire | C05, C09, C17 | Dorian Courcelle |
  | Marc Chen | C06, C10, C18 | Raphaël Delavictoire |
  | Alexandre Flavigny | C07, C11, C20 | Marc Chen |
  | Maya Bourrey | C03, C12, C13 | Alexandre Flavigny |
  | Yasmine Boukrouh | C14, C19 | Maya Bourrey |

  In addition, two independent recomputations agree with all 20 values of [`reference-td1.csv`](../reference-td1.csv): Dorian recomputed every value with a Python script reading the three CSV files without SQL (completed age by month and day), see [`contribution-dorian-A.md`](contribution-dorian-A.md); Yasmine wrote her own 20 SQL queries and a CSV-based check in a separate local run, and her 20 values are identical to ours ([her reference file](https://github.com/Ikseno/next-gen-ai-DIA3-1/blob/3b0a4894b6e778a91ceee3df4d93f43680e10069/td1-local-run/td1/reference-td1.csv), [cross-check record](https://github.com/Ikseno/next-gen-ai-DIA3-1/blob/3b0a4894b6e778a91ceee3df4d93f43680e10069/td1-local-run/td1/reference-crosscheck.json)). Comparison with the instructor's answer key: to be recorded at the end of the session.
- Final verdict = last attempt of each cell; every attempt is kept in the raw traces.
- Index and prices come from the kit (portfolio snapshot of 28 September, Groq Developer prices of 5 October). Cohere and Dots have no documented paid route for the exact same model: N/A, not $0.
- One run per cell at temperature 0, on 20 questions: this supports a routing hypothesis for this task, not a general ranking. The highest public index (Qwen, 33.7) is not the best model here; gpt-oss-120b (index 11.6) is, and its paid route is cheaper than Qwen's.
- **Protocol deviation.** The timestamps show that batches B (12:28–12:32 UTC), D (12:30–12:31) and E (12:27–12:39) overlapped, although the protocol asks for one request in flight per sub-group. They used different accounts, and the 429s are reported per Groq organisation, so we do not attribute the 429s to the overlap; we record it as a deviation.
- **A second, separate experiment.** Yasmine also ran all five batches herself, from her own accounts, before the group batches were consolidated (files kept in the repository history at commit [`3b0a489`](https://github.com/Ikseno/next-gen-ai-DIA3-1/tree/3b0a4894b6e778a91ceee3df4d93f43680e10069/td1-local-run), folder `td1-local-run/`, removed from the current tree so that the deliverables describe one experiment). It is **not** used in the figures of this report, because it differs from the protocol on three points: the runner was modified with Codex (`--retry-access` to re-run cells that had failed with HTTP 401/403, `--stop-on-access-error`); the two OpenRouter batches (C and E) used the same personal account; and batch A first met 17 HTTP 403 and 2 HTTP 401 before its cells were recovered. That run recorded 123 attempts and 71/100 correct final cells (A 17, B 17, C 12, D 15, E 10; Qwen C18 left `not_executed` after two 429s).
- **Observation from the two runs (hypothesis to test in TD 2).** With the same prompt, the same model identifiers and temperature 0, the two runs do not give the same answers: gpt-oss-120b is 20/20 here and 17/20 there (exact-birthday conditions on C15, C17, C19), Dots 15/20 here and 10/20 there. Temperature 0 does not make these hosted models deterministic; a single run per cell is therefore a weak basis for ranking, which supports a vote over several answers.

## 6. Who did what

| Member | References written / checked | Batch and analysis | Group work |
|---|---|---|---|
| Dorian Courcelle | C04, C08, C16 / checked Raphaël's | A (gpt-oss-120b), explanations A | Independent recomputation of the 20 references (Python on the CSV files, no SQL); `prompts-en.md` with fingerprint check; README merge; repository review against the assessment sheet ([note](contribution-dorian-A.md)) |
| Raphaël Delavictoire | C05, C09, C17 / checked Marc's | B (gpt-oss-20b, 1 retry), explanations B | — ([note](contribution-raphael-B.md)) |
| Mohamed Diawara | C01, C02, C15 / checked Dorian's | C (north-mini-code), explanations C | Merged traces kept in `results/` (CSV and JSONL), the 100-row comparison CSV and the pivot; README, `.gitignore` and repository layout; consolidation of this report ([note](contribution-mohamed-C.md)) |
| Marc Chen | C06, C10, C18 / checked Alexandre's | D (qwen3.8-27b, 5 retries), explanations D | — ([note](contribution-marc-D.md)) |
| Alexandre Flavigny | C07, C11, C20 / checked Maya's | E (dots-3-note), explanations E | Created the shared repository; compiled and uploaded the group's `reference-td1.csv`; uploaded the five-model summary prepared by Yasmine ([note](contribution-alexandre-E.md)) |
| Maya Bourrey | C03, C12, C13 / checked Yasmine's | — (roles F + G) | Cross-check of the references; her own merge of the five trace files (uploaded in `trace/` at 15:24, Excel export, superseded by the version in `results/` with the same rows); help with the comparison CSV and the five-model summary ([note](contribution-maya-FG.md)) |
| Yasmine Boukrouh | C14, C19 / checked Mohamed's | — (role H) | Five-model summary (index, prices, access, results by family); separate local run used as an independent reference check, see section 5 ([note](contribution-yasmine-boukrouh.md)) |

Several consolidation files were built in parallel by more than one member (merged traces, comparison CSV); the versions kept in `results/` were checked against the five raw trace files (see the README replay check). The git history records who uploaded each file.

**AI assistance.** Declared per member in the README (section *AI assistance*), in [`prompt/ai-assistance/`](../prompt/ai-assistance/) and in the contribution notes: Dorian, Raphaël, Mohamed and Marc used Claude; Alexandre used ChatGPT (and Codex, Claude for references); Yasmine used Codex (queries, cross-check, runner changes, consolidation and her report, see her contribution note); **Maya used no AI assistant**. Every value and explanation kept in the deliverables was checked against the traces and the database by the member responsible.

## 7. Next steps and help needed

- TD 2: the k-of-n vote on these five models. Questions C08, C09 and C10 are the natural test cases for a wrong or split consensus.
- Routing hypothesis to test: period and product questions to the cheapest model; age questions to gpt-oss-120b or to a vote, reporting disagreement instead of picking a value.
- Member preparing TD 2 (`atelier-vote.py`): _to be designated_.
- Still open: the comparison of our 20 references with the instructor's answer key, the member preparing TD 2, and the access-check count and OpenRouter allowance of operator E (recorded as missing).
