# TD 1 — Individual contribution: Marc Chen (role D)

**Model operated:** `groq:qwen/qwen3.8-27b` (Qwen 3.8 27B, Groq Free plan)
**References assigned:** C06, C10, C18 (see the members table in the [README](../README.md))
**Cross-check:** _to complete (whose references I checked, and who checked mine)_

## 1. Preparation

- 16 October: kit of 14 October extracted (pack `2026-10-14-students-1`), `.venv` created in `kit-td1` with Python 3.13.9 (macOS), `requests` installed, `verify-data.py` → `"ok": true` (5 file hashes, SQLite integrity and foreign keys OK).
- Groq Free account (no payment method) and OpenRouter account (no credits bought, no per-key credit limit set) created; keys kept as environment variables only, never written in a file.
- Access check run on 16 October, **5/5 models OK**, saved in `ready-for-td1.txt` with a screenshot (not committed, listed in `.gitignore`).
- 21 October: the kit folder is stored in iCloud Drive and its files had been offloaded to the cloud; set to "keep downloaded" before the session. Local check `check_access.py --no-network` OK, then one more full check at about 14:20 (Paris), **5/5 models OK**. That second full check cost 3 Groq + 2 OpenRouter calls, counted outside the base batch.

## 2. Batch D

Command, run from `kit-td1` after copying the group's `reference-td1.csv` into it (a first attempt with the empty template was refused by the skeleton before any call: "Complete your reference values before calling models"):

```bash
python3 skeleton-multi-llm-en.py --run --models groq:qwen/qwen3.8-27b --state state-D.jsonl --out traces-D.csv
```

- **Run time:** 12:30:08 to 12:31:55 UTC (14:30–14:32 Paris), default 3-second pause.
- **25 recorded attempts:** 20 initial calls + 5 retries. HTTP 200 on 20 attempts, **HTTP 429 on 5** (first attempts of C16, C17, C18, C19, C20).
- **Cause of the 429s:** Groq limit on **output tokens per minute for this model: 1,000 OTPM** (error message: "Used 913–950, Requested 132–233"). Qwen produced 57 to 251 completion tokens per call; at one call every 3 to 4 seconds, the combined questions (longest SQL) pushed the batch over 1,000 output tokens per minute. Each 429 was retried once by the skeleton and the retry got HTTP 200. These five cells have now used both allowed attempts.
- **Measurements (successful attempts):** 12,598 prompt tokens and 2,761 completion tokens in total; latency 240 to 2,566 ms, median 507 ms; `model_returned = qwen/qwen3.8-27b`; `cost_native` empty on every line (Groq returns no cost: missing measurement, not zero); `nature = real` on all 25 lines.
- **Prompt:** the `prompt_sha256` of each question is identical to the other four models (see [`prompt/model-prompt-td1.md`](../prompt/model-prompt-td1.md)).
- Files: [`trace/traces-D.csv`](../trace/traces-D.csv), [`state/state-D.jsonl`](../state/state-D.jsonl).

## 3. Results and explanations

**15/20 correct** — period 6/6, product 4/4, age 3/5, combined 2/5. Every failure is a **completed-age** error; no invalid SQL, no rejected SQL, no unrecovered access failure.

| Question | Verdict | Cause read in the returned SQL |
|---|---|---|
| C09 | incorrect (0) | Reference date never used (age against `o.date`); window `mm-dd(order) >= mm-dd(birth)` AND `< mm-dd(birth + 26 years)` is always false: 6 customers missed |
| C10 | incorrect (too low) | Off-by-one: branch "year difference 24, birthday not reached" selects age 23; the case "difference 26, birthday not reached" is missing (C004, C005, C007, C022: −439,570 cents) |
| C15 | incorrect (0) | Birth year ignored; `mm-dd <= '09-25' AND mm-dd > '09-25'` is always false |
| C17 | incorrect (too low) | Birthday boundary inverted (`<` / `>=`): excludes C001 (born 2001-09-25, 25 that day), includes C004 (born 2000-09-25, 26 that day); net −9,690 cents |
| C19 | incorrect (too high) | Year string compared with a full date: `'2026' <= '2026-09-25'` is true as text, so the filter means "born in 2001 or earlier": 9 extra customers |

The 15 correct rows are also explained in [`explanation/explanations-D.csv`](../explanation/explanations-D.csv) (20 rows, one per question), each from the SQL actually returned: half-open periods, `COALESCE` giving 0 on C06 and C14, correct birthday boundary on C02, C08, C11 and C16, age at the order date on C18.

**Inconsistency within a family**, useful for TD 2:
- C16 correct but C17 wrong: same age rule, written with `<=` once and `<` once;
- C18 correct but C10 wrong: same "age at the time of the order" rule, applied correctly only once;
- Qwen hard-codes birth years (2001 / 2000) on C02, C08, C11, C16: correct here, but tied to the reference year.

**Wrong agreement noticed in the group traces:** on C10, Qwen (D) and Dots (E) both return 119,410 instead of 558,980.

**Reference check:** the 20 group references were recomputed by an independent Python script on the three CSV files (no SQL, completed age by month and day) and by re-running each reference SQL read-only: **20/20 identical**. So every Qwen failure is a model error, not a reference error (question raised by a teammate during the session).

## 4. Group work

- Ran batch D and uploaded `traces-D.csv`, `state-D.jsonl` and `explanations-D.csv` to the repository.
- Re-checked the 20 references after a teammate asked whether some reference queries might not match their question (result above), and detailed the explanations accordingly.

## 5. AI assistance

Claude (Anthropic) was used for setup guidance, running the batch, reading the traces, the reference re-check, the explanation file and this note. Prompts and the split between the assistant's work and my checks: [`prompt/ai-assistance/ai-prompts-marc-D.md`](../prompt/ai-assistance/ai-prompts-marc-D.md).

## 6. What I take from it, next steps

- Qwen 3.8 27B is reliable on this task for period and product filters (10/10) and unreliable on completed age (5/10, with inconsistent rules between similar questions): a candidate for the cheap route of simple questions, not for age questions.
- Rate limits matter as much as quotas: with Groq's 1,000 OTPM on this model, a 3-second pause is too short for long answers. For a future batch, a longer `--pause` (as role A did with 8 s) would avoid the 429s and keep the retry in reserve.
- One run per cell at temperature 0: this supports a routing hypothesis, not a general accuracy figure.
- For TD 2: C10 (wrong agreement D/E) and C09 are good test cases for the k-of-n vote.
