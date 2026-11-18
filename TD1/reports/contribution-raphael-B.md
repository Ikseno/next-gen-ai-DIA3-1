# TD 1 contribution - Raphaël Delavictoire (role B)

Sub-group DIA3-1, session of 21 October 2026, pack `2026-10-14-students-1`.
Role: operator B, model `groq:openai/gpt-oss-20b`. All figures below come from
[`trace/traces-B.csv`](../trace/traces-B.csv) and [`state/state-B.jsonl`](../state/state-B.jsonl).

## 1. Preparation (before 14:00)

- Kit of 14 October extracted to `Next Gen IA/esilv-student-2026-10-14/kit-td1`.
- `check_access.py` run once on 16 October (01:31 Paris), output saved in `ready-for-td1.txt` (not committed, listed in `.gitignore`). It costs 3 Groq and 2 OpenRouter calls, counted outside the 100 base cells. _To confirm from the saved file: 5/5 models OK._
- Groq allowance before and after the batch: **not recorded** (to state as a missing measurement, not to reconstruct).

## 2. Step 1 - References

- Wrote references **C05, C09, C17** (see the members table in [`td1.md`](td1.md)). They were cross-checked by Dorian; I checked Marc's references (C06, C10, C18).
- Before the batch, the copy of `reference-td1.csv` in my `kit-td1` folder was still the empty kit template (146 bytes, no value), and the skeleton refused to run (`Complete your reference values before calling models`). The group file in the repository had a double extension (`reference-td1.csv.csv` at that time); I copied it into `kit-td1` as `reference-td1.csv` and checked its 20 values before calling the model. No reference value came from a model answer.

## 3. Step 2 - Batch B (20 cells)

Commands, run from `kit-td1` (PowerShell, inside VS Code):

```powershell
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-20b --cases C01,C02 --state state-B.jsonl --out traces-B.csv
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-20b --cases C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20 --state state-B.jsonl --out traces-B.csv
```

- **Test first.** C01 and C02 were run alone to check the setup; the second command reused the same state file, so C01 and C02 were not called again.
- **Setup issue fixed.** The first test stopped with `missing environment variable(s): GROQ_API_KEY`: the key was not loaded in the VS Code terminal. It was reloaded in that terminal only; the key never appears in a file or in the repository.
- **Run time:** 12:28:43 to 12:32:10 UTC.

**Result: 17/20 correct**, 20 initial calls + 1 retry = **21 attempts**, 0 invalid SQL, 0 rejected query, `model_returned = openai/gpt-oss-20b` on every answered line, `nature = real`.

| Measure | Value |
|---|---|
| Calls | 21 (20 initial, 1 retry) |
| Prompt tokens | 12,814 in total (619 to 666 per call) |
| Completion tokens | 5,530 in total (92 to 701 per call) |
| Latency | 399 to 20,229 ms, median 702 ms (C01, the first call, took 20 s; all others under 1.4 s) |
| `cost_native` | empty on every line: Groq returns no cost, so it is a **missing measurement, not zero** |

**Retry (C20).** Attempt 1 returned HTTP 429: Groq Free tokens-per-minute limit for `openai/gpt-oss-20b` (limit 8,000 TPM, 7,036 used, 1,110 requested). No SQL, no value, verdict `not_executed`: an access failure, not a wrong answer. The skeleton retried once, as the protocol allows; attempt 2 returned HTTP 200 with the correct value. Both attempts are kept in the trace (21 lines for 20 cells); the final verdict is the last attempt.

## 4. Step 3 - Reading the traces

Wrote [`explanation/explanations-B.csv`](../explanation/explanations-B.csv): 20 rows, one per question, each cause read from the returned SQL or the HTTP status.

| Family | Result |
|---|---|
| Period (C01, C04, C05, C06, C07, C20) | 6/6 |
| Product list (C03, C12, C13, C14) | 4/4 |
| Age at the time of the order (C10, C18) | 2/2 |
| Age on a reference date, combined with period or products (C15, C16, C17, C19) | 4/4 |
| Age on a reference date, alone (C02, C08, C09, C11) | **1/4** |

The three failures are all valid SQL with the wrong birth-date window:

| Question | Value / reference | Cause read in the returned SQL |
|---|---|---|
| C02 | 135,000 / 590,320 | `birth_date = '2001-09-25'`: only customers whose 25th birthday is the reference date, instead of everyone born from 2000-09-26 to 2001-09-25 |
| C08 | 25,920 / 605,580 | `birth_date >= '2001-09-24' AND birth_date < '2001-09-25'`: same one-day window, same misreading of "exactly 25" |
| C11 | 322,160 / 446,690 | `birth_date > '2001-12-01' AND birth_date <= '2006-12-01'`: bounds 20 and 25 years before the date, so customers aged 20 to 24 are kept and those aged 25 excluded |

**Observations.**

- The age logic is not stable: the model gets C09 right with an exact one-year window (`BETWEEN '2000-09-27' AND '2001-09-26'`), and C15, C16, C17, C19 right with the same reference date as C02, yet fails C02 itself. The prompt states the completed-age rule explicitly, so the failure is the model's, not the wording's.
- Reasoning effort does not predict success: reasoning tokens are low on period and product questions (17 to 64) and high on age questions, but C09 (617 reasoning tokens) is correct while C02 (521) is wrong.
- **Wrong agreement for TD 2:** on C08, B and E (Dots) return the same wrong value, 25,920, against a reference of 605,580. A 2-of-n vote including both would keep a wrong value.

**Independent check of the correct answers.** With AI assistance (section 6), each of the 20 B queries was run against the group's reference query on dense synthetic test databases (one customer per birth date from 1999 to 2008, orders on the period boundaries), and the 20 reference queries were compared with a separate Python computation of each question (no SQL). Result: the 20 references match the questions, the 17 correct B queries are equivalent to their reference, the 3 failures are not. None of the 17 correct values is correct by chance. This check uses test data, not `boutique.sqlite`; the reference values remain those validated in session.

## 5. Repository work

- Pushed `trace/traces-B.csv`, `state/state-B.jsonl` and `explanation/explanations-B.csv` (first version, then a detailed version covering the 20 questions after the instructors asked for more detailed explanations).
- Wrote [`prompt/ai-assistance/ai-prompts-Raphael-B.md`](../prompt/ai-assistance/ai-prompts-Raphael-B.md) (AI-assistance prompts, verbatim).
- Reviewed the repository and reported to the group that the first draft of `td1.md` did not match the traces (A 17/20 instead of 20/20, E 10/20 instead of 15/20, 71 instead of 79 correct, 123 attempts and HTTP 403/401 instead of 106 attempts and six 429s, B's 429 missing, broken `../td1/` links, `report/` instead of `reports/`).

## 6. AI assistance (declared)

Assistant: **Claude** (Anthropic), in a chat conversation. It read the course site and our public repository; it never received my API key and had no access to `boutique.sqlite`. I ran every model call and every upload myself.

| Task | Assistant's part | My check |
|---|---|---|
| Lecture 1 and TD 1 | Summarised the lecture, the assignment and the protocol; wrote a practice quiz | Read against the course site |
| Setup | PowerShell commands to check Python, the key (without displaying it) and to find the kit and the reference file | Ran them myself |
| Batch B | Gave the commands; diagnosed the empty reference template and the missing key | I ran the batch and read the output (17/20) |
| Explanations B | Read the 20 returned SQL queries and drafted `explanations-B.csv` | Checked values and references against my trace |
| Independent check | Synthetic-database equivalence test and Python recomputation (section 4) | Results reported with their limit |
| Documentation | Drafted the prompts file and this contribution note | Reviewed before upload |

Verbatim prompts: [`prompt/ai-assistance/ai-prompts-Raphael-B.md`](../prompt/ai-assistance/ai-prompts-Raphael-B.md).

## 7. Limits and next steps

- One run per cell at temperature 0: 17/20 supports a routing hypothesis for this task, not a general accuracy figure.
- **Protocol deviation:** batch B (12:28 to 12:32 UTC) overlapped with batches D and E, although the protocol asks for one request in flight per sub-group. The 429 on C20 is a per-organisation limit of my own Groq account, so it is not attributed to the overlap.
- Groq allowance before and after the batch was not recorded.
- For TD 2: gpt-oss-20b is enough for period, product and age-at-order questions; age on a reference date should go to gpt-oss-120b or to a vote, and C08 (B and E agree on a wrong value) is a test case for the wrong consensus.
