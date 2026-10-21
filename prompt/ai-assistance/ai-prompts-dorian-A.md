# TD 1 — Member A (Dorian Courcelle): AI-assistance prompts and disclosure

**Assigned model:** `groq:openai/gpt-oss-120b` (Groq Free plan)
**Session:** 21 October 2026 (TD 1, 14:00–18:30 Paris)
**Assistant:** Claude (Anthropic), used in a chat linked to my computer. It could read and write files in the kit folder and in my clone of this repository. It never received my API keys; I ran every model call and every git command myself.
**Scope:** personal use of an AI assistant to understand the kit, run batch A, analyse traces, document the work and review the repository. This file is **not** the prompt sent to the tested models: that prompt is the kit's `build_prompt()` output, unchanged, identical for the five models (see [`prompts-en.md`](../prompts-en.md) and the `prompt_sha256` column of the traces).

## 1. What the assistant did, and what I checked

| Task | Assistant's part | My check |
|---|---|---|
| Understanding the kit | Read the student pack and summarised the TD 1 steps, roles, deliverables and assessment sheet | Compared with the assignment and the instructor's briefing |
| References | Recomputed the 20 group values two ways: our SQL, run read-only on `boutique.sqlite`, and a separate Python script on the CSV files (completed age by month and day). Result: 20/20 identical | The references were written by the members; no assistant value was used as a reference |
| Batch A | Gave the command; read the Groq Free limits; diagnosed the Ctrl+C interruption after C01; proposed `--pause 8` from the tokens measured on C01 | I ran the batch myself: 20/20 correct, 1 attempt each |
| Explanations A | Read the 20 returned SQL queries and drafted [`explanations-A.csv`](../../explanation/explanations-A.csv) | Checked each row against `trace/traces-A.csv` |
| Group traces | Summarised batches B to E; checked one `prompt_sha256` per question across models; found the wrong agreements on C08, C09 and C10 | Cross-read with the operators' explanation files |
| Documentation | Drafted the model-prompt file with the fingerprint check, the root `.gitignore`, the README merge after a conflict, my [contribution note](../../reports/contribution-dorian-A.md) and the link and access-check fixes in [`td1.md`](../../reports/td1.md) | Reviewed before each commit |
| Repository review | Compared the repository with the assessment sheet and the hand-in page. Found an erroneous report draft and an Excel-corrupted trace merge; ran an offline `--replay` of the five state files (100/100 verdicts reproduced); audited the full git history for leaked secrets | Relayed to the group; corrections made and pushed |

## 2. Essential requests — reformulated for readability

The requests below are **reformulated in English** for an external reader and **reduced to the essential ones**. They are not verbatim. The original wording (French, complete list of 18 messages) is kept verbatim in [`reports/contribution-dorian-A.md`](../../reports/contribution-dorian-A.md), section 6. Each entry ends with the original message it reformulates.

### Understanding the task and organising the group

1. **Read the student pack and explain what I have to do for TD 1.**
   _Original: « lis le contenu de ce dossier et explique moi ce que je dois faire »_
2. **Here are the reference queries our group chose (`reference-td1.csv` attached). What is the next step, and how should the eight members split the work?**
   _Original: « d'accord voici les questions que nous avons choisi quelle est la suite ? Comment s'organiser en groupe chacun fait de son côté ? »_
3. **I am operator A (role table attached). Give me the exact steps to run my batch.**
   _Original: « je suis le rôle A »_
4. **We were told that only the reference values are assessed, not the model queries. Explain what the assessment sheet actually marks.**
   _Original: « les requêtes ne seront pas évaluées on sera évalulés sur les valeurs de référence explique »_

### Running batch A

5. **How can I check on the Groq console that my account has enough requests left for 20 calls plus a margin?**
   _Original: « […] vérifie qu'il te reste au moins 25 requêtes pour `openai/gpt-oss-120b` […] comment on sait ? »_
6. **My first run stopped with a `KeyboardInterrupt` after C01 (terminal output attached). What happened, and how do I resume without losing or repeating a call?**
   _Original: the terminal output, pasted without comment_
7. **I finished batch A with 20/20 correct. Should I run the 20 questions again to check that the result is stable?**
   _Original: « c'est fait, est ce intéressant de refaire les questions pour voir si j'ai encore 20/20 »_
   → Decision: **no second batch**. It is outside the TD 1 budget and protocol and is not assessed; answer stability at temperature 0 is recorded as a limit.

### Analysis and repository

8. **The merged traces and state files of the five operators are in the repository. What remains to be done?**
   _Original: « je t'ai mis en contexte le github avec la mise en commun de toutes nos traces et states quelle est la suite ? »_
9. **Write `explanations-A.csv` in the same format as the other operators' files.**
   _Original: « fais un fichier explantaions-A »_
10. **My push was rejected, then `git pull` reported a merge conflict in `README.md` (outputs attached). Resolve it.**
    _Original: the git outputs, pasted without comment_

### Review against the assessment sheet

11. **Review the current repository against the assessment sheet: what is missing for a perfect mark?** Then, after each round of corrections: **is the problem solved?**
    _Original: « lis le repo actuel que manque t il pour avoir une note parfaite ? », then « relis le repo et dis moi si ces problèmes sont résolus ? »_
12. **Check the repository and its history for security problems (leaked keys, personal data).**
    _Original: « c'est fait peux tu vérifier s'il y a des failles de sécurité »_
13. **Write a contribution note describing everything I did, then fix the broken links and complete the open items of the report.**
    _Original: « dans report fait un rapport qui explique ce que j'ai fait depuis le début », then « corrige le point2, le point 3 »_


## 3. Limits

- The assistant's answers are not reproduced; its contribution is summarised in section 1, and every file it drafted was reviewed before commit.
- Section 2 is a selection and a reformulation; the verbatim originals are kept in the contribution note.
- No API key, account identifier, e-mail address or local path is reproduced in this file.
