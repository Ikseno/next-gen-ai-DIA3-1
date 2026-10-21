# TD 1 — Member D (Marc Chen): AI-assistance prompts and disclosure

**Assigned model:** `groq:qwen/qwen3.8-27b`
**Session:** 16 October (preparation) and 21 October 2026 (TD 1)
**Assistant:** Claude (Anthropic), in a chat linked to my computer: it could read and write files in my kit folder and read our public repository; it never received my API keys.
**Scope:** personal use of an AI assistant to set up, run, analyse and document TD 1. This file is **not** the prompt sent to the tested models: that prompt is the kit's `build_prompt()` output, unchanged, identical for the five models (see [`prompt/model-prompt-td1.md`](../model-prompt-td1.md) and the `prompt_sha256` column of the traces).

## 1. What the assistant did, and what I checked

| Task | Assistant's part | My check |
|---|---|---|
| Understanding the module | Read the course site (Before TD 1, environment guide, TD 1 assignment, protocol, syllabus, hand-in page) and summarised the steps, deadlines and group organisation; wrote a plain-language TD 1 guide (`td1-explication.md`) | Compared with the instructors' emails and the schedule shown in the room |
| Machine setup (16 Oct) | Gave the macOS commands step by step (venv, `requests`, `verify-data.py`, `export` of the keys, `check_access.py`); explained the Groq Free plan and the optional OpenRouter per-key credit limit | I ran every command and created the accounts and keys myself; `ready-for-td1.txt` shows 5/5 models OK |
| iCloud issue (21 Oct) | Detected that the kit files had been offloaded to iCloud and could not be read | I set the folder to "keep downloaded" |
| Reference file | Did **not** write any reference. Found the group's completed `reference-td1.csv` in the repository and gave the command to copy it into `kit-td1` | I copied it myself; 20 rows with values |
| Batch D | Explained the skeleton (demo mode, `--run`, `--state`, `--out`), and why not to run before references exist (unscored traces cannot be rescored in the same state file) | I ran the demo and the batch myself: 15/20 correct, 25 attempts |
| Protocol check | Checked the run against the protocol: one retry max, same prompt fingerprints as model C, same references, real traces only | Points left to the group: instructor validation of the references, one caller at a time |
| Reference re-check | Recomputed the 20 references with a separate Python script on the CSV files (no SQL) and re-ran the reference SQL read-only: 20/20 identical | Reported to the group after a teammate questioned the references |
| Explanations for model D | Read the SQL returned by Qwen for the 20 cells, compared the customers kept by Qwen and by the reference (customer by customer), drafted `explanation/explanations-D.csv` (5 failures, then the 15 correct rows on request) | Read each row before uploading; an overstatement on C19 ("filters nothing") was corrected to "born in 2001 or earlier" |
| Documentation | Drafted this file and `reports/contribution-marc-D.md` from the traces and the conversation | Reviewed before uploading; uploads to GitHub done by me (the assistant had no write access) |

## 2. Prompts sent to the assistant (verbatim, original French)

### Preparation (16 October)

> J'ai un module en école d'ingénieur qui va commencer et je dois préparer des trucs mais les explications ne sont pas assez synthétiques, j'aimerais que tu me guides :  *(with the instructor's email)*

> adapte le guide en prenant compte du fait que je suis sur macos

> Procédons étape par étape, je suis à l'étape 2 avec python, je te dirais quand passer à l'étape suivant. J'ai fais python3 --version et j'ai 3.13.L9

> je le laisse dans icloud, l'étape 2 est elle fini ?

> étape 3

> 3a comment je sais si c'est bien gratuit ? j'ai pas mis de carte

> pour open router ca me demande d'tablir une limite pour la clé

> étape 4

> De quel preuve tu parles ?

> je dois lui envoyer ou montrer au debut du td ?

> ah donc je vais devoir remettre mes clés api ?

> j'ai fini du coup ?

> ils sont dans le zip ou je dois aller les chercher sur le site de l'école ?

> un ami a fait ca , verifie que j'ai tout fait :  *(with a classmate's summary)*

> c'est des grp de cb ?

> est ce que les groupes sont par groupe de td ou toute la promo ?

*(Terminal outputs of `ls`, the venv setup, `verify-data.py` and `ready-for-td1.txt` were also pasted; keys were masked.)*

### Session start (21 October)

> As tu accès aux documents ?

> Je souhaite réaliser le TD1

> comment relancer le check ?

> Je viens de faire le checkin, guide moi pour la suite  *(with a photo of the session schedule)*

> commence par faire une explication de ce qu'on va faire

> explique de maniere plus simple et dans son entiereté

> faire un md

> du coup le code est à faire ou ? dans un nouveau fichier ou un fichier est déjà pret pour etre rempli

### Batch D

> ok du coup je vais faire ma partie D, donne ce que je dois faire  *(with the group's role table)*

> j'aimerais accelerer et faire ma partie

> je ne comprends rien à ce que je dois faire là, comment je seutp le modele, une fois que je l'ai appelé c'est un chatbot ?, comment je lui pose les questions ? depuis ou ?, comment et ou enregistrer les questions?

> repo https://github.com/Ikseno/next-gen-ai-DIA3-1.git

*(The output of the demo run, of the refused run with the empty template, and of the full batch were pasted.)*

> vérifie que tu as bien respecté les consignes

### Repository and explanations

> du coup je dois mettre quoi sur github

> c'est quoi state d ?

> comment ajouter manuellement des fichiers

> est ce que les explications sont sous le meme format que celui de Mohamed

> alors, alexandre nous dit que nos explications doivent être plus détaillé, en particulier certianes réponses peuvent etre mauvaises parce que les requetes sql de base ne correspondait pas à ce qui était demandé donc fais une verification

> oui explique bien pourquoi c'est vrai en plus des faux

> pour l'oral je dois utiliser quoi pour expliquer

> fais en plus un fichier prompt et report sur le modèle de celui de mehdy

## 3. Limits

- Every explanation is a reading of the trace (returned SQL, value, error field), checked on the database (customer-by-customer comparison with the reference set); causes are stated as observed in the SQL, not as a claim about the model in general.
- The assistant could not push to GitHub: every upload to the repository was done by me.
