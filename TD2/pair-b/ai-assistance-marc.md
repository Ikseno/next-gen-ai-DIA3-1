# TD 2 — Pair B (Marc Chen): AI-assistance prompts and disclosure

**Session:** 18 November 2026 (TD 2)
**Assistant:** Claude (Anthropic), in a chat linked to my computer. It could read the kit and my local clone of the repository, run read-only queries on `data/boutique.sqlite`, and write files in my folder. It had no write access to GitHub: every commit was pushed by me.
**Scope:** my personal use of an AI assistant for Pair B (C09 SQL root cause), the related fixes and the Pair B reviews. This file is **not** the prompt sent to the tested models. That prompt is unchanged since TD 1, and no new batch was run in TD 2.

## 1. What the assistant did, and what remains my responsibility

| Task | Assistant's part | My part |
|---|---|---|
| C09 SQL root cause ([`C09/part2-sql-cause-marc.md`](C09/part2-sql-cause-marc.md)) | Read the two faulty queries in the traces; re-ran each `WHERE` predicate separately on the database (lines kept, revenue); explained Cohere's text arithmetic and Qwen's order-date age and contradictory month-day window; drafted the file | Task split decided within Pair B (Yasmine, Mohamed, me); I read the explanation before pushing |
| Lecture 2 reading of C09 | Read the Lecture 2 slides and the TD 2 assignment, listed the requirements, and added the "format → meaning → correctness" table, the canonical answers with their hashes, and the `age-window-nonempty` check | Asked for the alignment with Lecture 2, and read the result |
| Vote check with Pair A's method | Wrote [`check-votes-with-pair-A.py`](check-votes-with-pair-A.py) and ran it: C08 and C09 decisions identical to the hand counts | Pushed |
| Fixes asked by the reviews | Stored the two faulty C09 queries and the empty-filter check; added `COALESCE` to the total query; added a check-only mode to `analyse.py` (no overwrite, line endings normalised) and `.gitattributes` | Pushed; Yasmine to confirm the changes to her `analyse.py` |
| Reviews | Drafted [`../reviews/review-A-by-B.md`](../reviews/review-A-by-B.md) and Pair B's answers to the reviews by A and C, after re-running Pair A's and Pair B's scripts | To read and sign with a second Pair B member |

## 2. Key prompts, verbatim (French)

Only the prompts that shaped a deliverable are listed. A name in brackets was normalised (we use "Mohamed" throughout the repository).

> vasy fais ma partie, [Mohamed] a fini la sienne

> Voici le cours 2 qui explicite un format d'écriture de code que j'aimerais appliquer à ce td : https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/diaporama/cm2-en.html

> modifie ma partie en conséquences

> il nous reste que les reviews pour la partie B nous qu'on va faire, corrige les autres erreurs (1 et 2)

> Fais les reviews selon le format de reponse des review deja faite

> finis tout ce qui reste à faire pour la partie B

## 3. Limits

Every figure produced with the assistant was re-run on `data/boutique.sqlite` (read-only) or recomputed from the CSV files. The assistant's statements are not evidence in themselves (Lecture 2): the evidence is the stored queries, their outputs and the scripts above.
