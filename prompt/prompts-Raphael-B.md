# TD 1 — Member B (Raphaël Delavictoire): AI-assistance prompts and disclosure

**Assigned model:** `groq:openai/gpt-oss-20b` (Groq Free plan)
**Session:** 21 October 2026 (lecture in the morning, TD 1 in the afternoon)
**Assistant:** Claude (Anthropic), in a chat conversation. It never received my API keys; it read our public repository and the course site, and could not access `data/boutique.sqlite`.
**Scope:** personal use of an AI assistant to understand the lecture, run batch B, analyse its traces and document the results. This file is **not** the prompt sent to the tested models.

## 1\. Prompt used for the five-model experiment

Model B received exactly the prompt built by `build\_prompt()` in `skeleton-multi-llm-en.py`, unchanged: the system message and user template documented verbatim in [`prompt-yasmine.md`](./prompt-yasmine.md) and [`prompts-Dorian.md`](./prompts-Dorian.md). The `prompt\_sha256` of the 21 lines of `trace/traces-B.csv` (retry included) equals the per-question fingerprint listed in `prompts-Dorian.md` for all 20 questions.

Call parameters for B: temperature 0, `reasoning\_effort: low`, `max\_completion\_tokens: 1024`, 45 s timeout, at most one retry per cell, one request at a time per sub-group.

Commands I ran myself, from the `kit-td1` folder:

```
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-20b --cases C01,C02 --state state-B.jsonl --out traces-B.csv
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-20b --cases C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20 --state state-B.jsonl --out traces-B.csv
```

The second run reused the same state file, so C01 and C02 were not called again.

## 2\. What the assistant did, and what I checked

|Task|Assistant's part|My check|
|-|-|-|
|Lecture 1 and TD 1 preparation|Summarised Lecture 1, the TD 1 assignment and the protocol; wrote a practice quiz (its own questions, not the Moodle quiz)|Read against the course site|
|Environment|Gave PowerShell commands to check Python, the Groq key (without displaying it) and to locate the kit and the group's `reference-td1.csv`|Ran them myself; my key never left my machine|
|Reference file|Did **not** compute any reference value. Found that the kit copy of `reference-td1.csv` was the empty template and that the repository copy was named `reference-td1.csv.csv`; told me to copy the group's file|Copied it myself, checked 20 rows with values|
|Batch B|Gave the commands; I ran them myself (test on C01, C02, then the 20 questions)|Output: 17/20 correct, 0 invalid, 0 rejected, 21 attempts|
|Reading the traces|Gave commands to list failures; read the SQL returned for every cell from `trace/traces-B.csv`|Compared with the terminal output of my run|
|Explanations for model B|Drafted `explanation/explanations-B.csv`, one row per question, causes read from the returned SQL and the HTTP status|Checked each value and reference against my trace|
|Independent check|Compared the group's 20 reference queries with a separate Python computation of each question (no SQL), and ran each model-B query and its reference query on dense synthetic test databases (one customer per birth date 1999 to 2008, orders on the period boundaries). Result: the 20 references match the questions; the 17 correct B queries are equivalent to the references, the 3 failures (C02, C08, C11) are not|The real `boutique.sqlite` was not available to the assistant: this check is on test data, the reference values themselves remain those validated in session|

## 3\. My prompts to the assistant (verbatim, original French wording and typos kept)

### Understanding the lecture and preparing TD 1

> https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/index.html
> tu peux me faire un resumé de la lecon 1 avec ce que je dois retenir et savoir pour le td 1

### Environment and kit

> je crois que j ai deja les clés api sur mon pc je veux juste verifier



### Running batch B

> on est au td qql a finis la partie sql on doit faire quoi ensuite et est ce que je dois ouvrir vsscode

> c est bon donne moi juste ce que je dois taper pour avoir faire mon travail apres je t envoie les reponses 

> c est bon tu peux me donner les test c01 et c02 et apres tu me dis la trace

### Analysing failures and documenting

> tu peux faire un resumé de ou il a les bonnes reponse et ou il a eu faux et pourquoi

> https://github.com/Ikseno/next-gen-ai-DIA3-1
> peut tu faire un fichier csv explanation B

> alors on nous a demandez que nos explications doivent etre plus detaillé en particulier certaines réponses peuvent etre mauvais parce que les requetes sql de base ne correspondait pas a ce qui etait demandé donc fais une verifications

> lit le github et donne notre prompt pour le B

> passe a l etape b et le nomme le prompte B

Short messages in between (screenshots of the terminal, "ok", file-upload questions) are not listed.

## 4\. Results of batch B (from `trace/traces-B.csv`)

* 17/20 correct. Period 6/6, product list 4/4, age at the time of the order 2/2 (C10, C18), combined with an age on a reference date 4/4 (C15, C16, C17, C19), age on a reference date alone 1/4 (C09 correct; C02, C08, C11 incorrect).
* C02, C08, C11: valid SQL with the wrong birth-date window (exact birthday or a window shifted by five years), although the prompt states the completed-age rule explicitly.
* C20: attempt 1 HTTP 429 (Groq Free tokens-per-minute limit), `not\_executed`; attempt 2 HTTP 200, correct. Access failure, not a wrong answer.

## 5\. Evidence and limitations

* Model B was queried only through the provided skeleton and the Groq API; its inputs and outputs are in `trace/traces-B.csv` and `state/state-B.jsonl`. My conversation with the assistant is not a model evaluation and is not counted among the 100 cells.
* The assistant's explanations were checked against the raw traces before submission; the group remains responsible for every line.
* No API key or secret appears in this file.

