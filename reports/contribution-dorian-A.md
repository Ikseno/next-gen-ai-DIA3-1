# TD 1 contribution - Dorian Courcelle (role A)

Sub-group DIA3-1, session of 21 October 2026, pack `2026-10-14-students-1`.
Role: operator A, model `groq:openai/gpt-oss-120b`. All figures below come from
[`trace/traces-A.csv`](../trace/traces-A.csv) and [`state/state-A.jsonl`](../state/state-A.jsonl).

## 1. Preparation (before 14:00)

- Kit extracted to `esilv-student-2026-10-14/`, virtual environment `.venv` created in `kit-td1`.
- `check_access.py` run **once**, on 21 October at 09:05 (Paris), output saved in `ready-for-td1.txt` (not committed: it is listed in `.gitignore`):
  Python 3.14.8, database SHA-256 `0077e235...3398fec2` identical to `manifest.json`, SQLite 3.50.4, CSV fingerprints OK, **5/5 models OK**.
- This check cost 3 Groq calls and 2 OpenRouter calls, counted separately from the 100 base cells.

## 2. Step 1 - References

- Wrote references **C04, C08, C16** (see the members table in the [README](../README.md)).
- The 20 group references in [`reference-td1.csv`](../reference-td1.csv) were re-checked by an independent method: every SQL query was run read-only on `boutique.sqlite`, and every value was recomputed by a separate Python script that reads the three CSV files (no SQL) and computes completed age by month and day. **20/20 values identical** (including the two zero cases C06 and C14 and the one-day window C07). No customer is born on 29 February, so no leap-year ambiguity applies. This check was done with AI assistance (see section 6); no model answer was used as a reference value.
- - Cross-check in the group's circle: C04, C08 and C16 were checked by Mohamed; I checked Raphaël's references (C05, C09, C17).

## 3. Step 2 - Batch A (20 cells)

Command, run from `kit-td1` after copying the group's `reference-td1.csv` into it:

```powershell
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --state state-A.jsonl --out traces-A.csv
```

- **Allowance.** Groq Free limits for `openai/gpt-oss-120b` read on the console (Settings → Limits): 30 requests/min, 1,000 requests/day, 8,000 tokens/min, 200,000 tokens/day. About 1 request had been used on this model before the batch (the 09:05 check).
- **Interruption.** The first run was stopped by a keyboard interrupt (Ctrl+C) during the 3-second pause after C01. C01 was already recorded in `state-A.jsonl` (correct, 1 attempt), so **no call was lost or repeated**.
- **Resumption.** Same command and same state file, with `--pause 8`. C01 used about 740 tokens (638 prompt + 102 completion); 8 s between requests keeps the batch near 5,000 tokens/min, under the 8,000 tokens/min limit, to avoid HTTP 429s that would consume the single allowed retry.
- **Run time:** 12:46:20 to 12:50:43 UTC.

**Result: 20/20 correct**, every cell on attempt 1, HTTP 200, 0 retry, 0 access error, `model_returned = openai/gpt-oss-120b` on every line, `nature = real`.

| Measure | Value |
|---|---|
| Calls | 20 (20 initial, 0 retry) |
| Prompt tokens | 12,814 in total (619 to 666 per call) |
| Completion tokens | 5,175 in total (78 to 575 per call) |
| Latency | 446 to 1,951 ms, median 1,159 ms |
| `cost_native` | empty on every line: Groq returns no cost, so it is a **missing measurement, not zero** |

**Observation.** Reasoning tokens are low on period and product questions (about 20 to 70) and much higher on age questions (about 160 to 430, e.g. C02 317, C09 397, C17 427). The model spends visibly more effort on completed age, the family where every other model fails. This is relevant for TD 2 (routing by difficulty) and TD 3 (cost).

## 4. Step 3 - Reading the traces

- Wrote [`explanation/explanations-A.csv`](../explanation/explanations-A.csv): 20 rows, all `correct`, `cause_category = none`. As there is no failure to explain, each row states from the returned SQL how the convention was applied.
- Finding: gpt-oss-120b is correct on the 11 age questions with **three different, all valid, methods**:
  - anniversary window `date(birth_date,'+25 years') <= ref < date(birth_date,'+26 years')` (C02, C11, C16, C19);
  - year difference minus `(ref mm-dd < birth mm-dd)` (C08, C15);
  - birth-date interval `]ref - 26 years, ref - 25 years]` (C09, C17);
  - for age at the time of the order (C10, C18), the same window evaluated against `date(o.date)`.

  So it computes completed age to the day each time, which is exactly what the failing models miss.
- Read and checked the traces of B, C, D and E to support the group: identical `prompt_sha256` per question across the 5 models (106 lines), 6 HTTP 429 retries (B: C20; D: C16-C20) all recovered, and the wrong agreements to keep for TD 2: **C08** (B and E both 25,920, reference 605,580), **C10** (D and E both 119,410, reference 558,980) and C09 (C and D both 0, reference 487,980).

## 5. Repository work

- Pushed the raw files of batch A (`trace/traces-A.csv`, `state/state-A.jsonl`) and `explanations-A.csv`.
- Wrote the verbatim prompt file (now [`prompt/model-prompt-td1.md`](../prompt/model-prompt-td1.md)). The system message and user template are extracted from the kit's `build_prompt()`; the `prompt_sha256` of each question is recomputed from that text and matches every line of the five trace files (20/20 questions).
- Added the kit's `.gitignore` at the root (keys, `.env`, `.venv`, caches and `ready-for-td1.txt` stay out of the public repository).
- README: drafted a first version, then resolved the merge conflict with the teammate's README pushed at the same time (commit `0e07d97`). I kept their version as the base and added the database hash, my environment, the TD 1 status table and the wrong agreements.
- Reviewed the repository against the assessment sheet and the hand-in page, and reported to the group:
  - the first draft of the report described a different run (A 17/20, E 10/20, 123 attempts, HTTP 403s, a modified runner, broken `../td1/` links);
  - `trace/traces-td1.csv` had been re-saved by Excel with `;` separators (717 rows instead of 106);
  - missing items: `reports/` path, cross-check record, `traces-td1.jsonl`, AI-assistance files.

  The report was rewritten and the corrupted file deleted.

## 6. AI assistance (declared)

Assistant: **Claude** (Anthropic), in a chat linked to my computer. It could read and write files in the kit folder and in the repository clone; it never received my API keys. I ran every model call and every git command myself.

| Task | Assistant's part | My check |
|---|---|---|
| Understanding the kit | Read the pack and summarised the TD 1 workflow, roles and assessment | Compared with the assignment and the instructor's briefing |
| References | Independent recomputation of the 20 values (Python on CSV files + read-only SQL); copied the group file into `kit-td1` | References were written by the members; the 20 values match |
| Batch A | Gave the commands, explained the Groq limits, diagnosed the Ctrl+C interruption, suggested `--pause 8` from the measured tokens | I ran the batch and read the output (20/20) |
| Explanations A | Read the 20 returned SQL queries and drafted `explanations-A.csv` | Checked against the trace lines |
| Group traces | Summarised B to E, checked fingerprints, found the wrong agreements | Cross-read with the operators' explanation files |
| Documentation | Drafted the prompt file, `.gitignore`, README, the merge-conflict resolution and this contribution note | Reviewed before each commit |
| Review | Compared the repository with the assessment sheet and the hand-in page | Relayed to the group |

**Prompts sent to the assistant (verbatim, French).** Two screenshots of the group's role table were also shared.

1. « lis le contenu de ce dossier et explique moi ce que je dois faire »
2. « d'accord voici les questions que nous avons choisi quelle est la suite ? Comment s'organiser en groupe chacun fait de son côté ? » (with the group's `reference-td1.csv`)
3. « je suis le rôle A » (with the role table)
4. « Ouvre la console Groq (console.groq.com) et vérifie qu'il te reste au moins 25 requêtes pour `openai/gpt-oss-120b` : 20 pour les questions et 5 de marge. comment on sait ? »
5. « les requêtes ne seront pas évaluées on sera évalulés sur les valeurs de référence explique »
6. The terminal output of the interrupted first run (`KeyboardInterrupt`)
7. « j'ai finis les 3 premières étapes (j'ai lancé groq gpt oss 120 b et ai eu 20/20) »
8. « nous avons un github commun, je l'envoie à Maia ou je le met sur github »
9. « je t'ai mis en contexte le github avec la mise en commun de toutes nos traces et states quelle est la suite ? »
10. « j'ai pull les changements sur le repo, dis moi quelle est la suite ? »
11. « fais un fichier explantaions-A »
12. « c'est fait, est ce intéressant de refaire les questions pour voir si j'ai encore 20/20 »
13. « quelle est la suite ? »
14. The `git push` rejection output (non-fast-forward), then the `CONFLICT (content): Merge conflict in README.md` output
15. « lis le repo actuel que manque t il pour avoir une note parfaite ? »
16. « relis ya t il toujours ce problème »
17. « relis le repo et dis moi si ces problèmes sont résolus ? »
18. « dans report fait un rapport qui explique ce que j'ai fait depuis le début, »

Decision taken after prompt 12: **no second batch**. Repeating questions is outside the TD 1 budget and the protocol, and it is not assessed in this module. Answer stability at temperature 0 is recorded as a limit instead.

## 7. Limits and next steps

- One run per cell: the 20/20 of gpt-oss-120b supports a routing hypothesis for this task, not a general accuracy figure.
- The OpenRouter account was not used by A, so its allowance is not reported here.
- For TD 2: use C08, C09 and C10 to test the k-of-n vote; candidate routing rule: period and product questions to the cheapest model, age questions to gpt-oss-120b or to a vote.
