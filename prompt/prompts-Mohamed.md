# TD 1 — Member C (Mohamed Diawara): AI-assistance prompts and disclosure

**Assigned model:** `openrouter:cohere/north-mini-code:free`  
**Session:** 16 October (preparation) and 21 October 2026 (TD 1)  
**Assistant:** Claude (Anthropic), used in a chat linked to my computer (it could read and write files in my project folders; it never received my API keys).  
**Scope:** personal use of an AI assistant to set up, run, analyse and document TD 1. This file is **not** the prompt sent to the tested models: that prompt is the kit's `build_prompt()` output, unchanged, identical for the five models (see the sub-group prompt file and the `prompt_sha256` column of the traces).

## 1. What the assistant did, and what I checked

| Task | Assistant's part | My check |
|---|---|---|
| Machine setup (16 Oct) | Wrote `setup-td1.sh` (venv, `requests`, `verify-data.py`, masked key entry, `check_access.py`); copied the extracted kit into my project folder | I entered my own keys and ran the script; `ready-for-td1.txt` shows 5/5 models OK |
| Reference file | Did **not** compute any reference. Re-ran the 20 SQL queries of the group's `reference-td1.csv` to confirm each query returns its recorded value (consistency only) | References written and cross-checked by the members, validated in session |
| Batch C | Gave the commands; I ran them myself (test on C01, then C02–C20) | Output: 12/20 correct, 7 incorrect, 1 `sql_invalid` |
| Explanations for model C | Read the SQL returned by Cohere for each of the 20 cells, compared it with our reference SQL, ran small SQLite checks (e.g. `substr` positions, text subtraction, `||` vs `+` precedence), drafted `explanation/explanations-C.csv` | I went through the cells one by one and approved each explanation before it was recorded |
| C19 "correct by chance" | Compared the customers kept by Cohere's age test with the reference set (keeps C003 aged 24, drops C005 aged 25) | Added to the C row of `five-model-summary-en.csv` after review |
| Merged outputs | Built `traces-td1.csv` (5 trace files, 106 lines, all attempts), `model-question-comparison-en.csv` (100 rows, final attempt + operator explanations) and `pivot-td1.md`; checked one `prompt_sha256` per question across models | Totals per model match the run outputs |
| Repository | Wrote `README.md`, copied the kit `.gitignore`, wrote `plenary-td1.md`; checked consistency of the other members' explanation files, `five-model-summary-en.csv` and the prompt file against the traces and the kit | Reviewed before each commit; git commands run by me |

## 2. Prompts sent to the assistant (verbatim, original French)

### Setup and access check

> je dois faire ca avant le prochain td aide moi a setup

> fais le setup pour moi

> relance le check pour voir si ca marche

> j'ai ce probleme comment je le regle  *(check reporting `missing GROQ_API_KEY`: the zsh `read` syntax was wrong)*

### Organising the session

> ok mtn commencons le TD1 dis moi toutes les etapes

> ok avant doit on se repartir les questions avec le groupe non?

> mets des noms :y'a mohamed dorian rapahel marc alexandre maya yasmine

> comment je pose la question à open router

### Explaining the failures of model C

> j'ai aps compris dis moi ,je comprends que je dois expliquer chaque erreur mais comment mtn

> quand je lit la colonne sql comment je sais ce qu'il mal fait

> ok note celui on passe au suivant

> mets les questions correct aussi dans le fichier explanation et explique pk elle sont corrects

### Repository, checks and plenary

> clone le repo pour que je travaille

> j'arrive pas pull

> regarde les fichier si ils sont bien

> occupe toi de 2 et 3  *(copy the kit `.gitignore`, write the README)*

> regarde si le five model summary est correct

> prompt.md est il correct

> fok fait la pleniere

## 3. Limits

- Every explanation is a reading of the trace (returned SQL, value, error field), checked with small SQLite queries; causes are stated as observed in the SQL, not as a claim about the model in general.
- The assistant's network access could not reach the course site or GitHub: downloads, `git pull` and `git push` were done by me.
