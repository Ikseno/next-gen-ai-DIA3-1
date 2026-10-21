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

## 2. AI-assistance requests — clarified technical formulations

The following prompts are **retrospective, technically clarified summaries** of the requests made during TD 1. They preserve the objectives of the original exchanges but are **not verbatim chat messages** or a complete transcript.

### Interpreting the assignment and designing the workflow

> Analyse le kit étudiant et les consignes officielles du TD 1 pour identifier les livrables évalués, les contraintes expérimentales et les preuves attendues. Propose une procédure reproductible allant de l'établissement des références SQL à l'analyse des traces, en distinguant ce qui relève du protocole obligatoire des bonnes pratiques supplémentaires.

> À partir du fichier `reference-td1.csv` et des rôles attribués au sous-groupe, propose une répartition cohérente du travail entre les sept membres : rédaction des vingt références, vérification croisée indépendante, exécution des cinq lots de modèles et consolidation des résultats. Précise les dépendances afin d'éviter toute utilisation de valeurs non vérifiées.

> J'assure le rôle A avec `groq:openai/gpt-oss-120b`. Décris précisément la configuration attendue, les arguments du script fourni, les prérequis avant les appels réels ainsi que les fichiers de trace et d'état qui doivent être conservés pour assurer la reproductibilité.

> Clarifie la distinction entre la validation des montants de référence et l'évaluation de la qualité des requêtes SQL. À partir de la grille du TD, explique quels éléments démontrent l'exactitude des références, la traçabilité des essais et la capacité à diagnostiquer les erreurs des modèles.

### API quota management and batch execution

> Comment vérifier les quotas Groq applicables à `openai/gpt-oss-120b` avant d'exécuter les vingt questions ? Prends en compte les limites en requêtes et en tokens, la marge nécessaire pour d'éventuelles relances, et la différence entre le coût monétaire et les restrictions de la route gratuite.

> L'exécution du lot A a été interrompue après C01 par un `KeyboardInterrupt` (sortie du terminal fournie). Vérifie à partir du fichier `state-A.jsonl` si C01 a déjà été enregistré, puis précise comment reprendre sans dupliquer les appels ni altérer les traces. Examine également l'intérêt d'augmenter `--pause` au regard du budget de tokens par minute.

> Le premier lot A affiche 20 réponses correctes sur 20. Serait-il méthodologiquement pertinent de le répéter pour tester la stabilité des réponses à température 0 ? Distingue la valeur scientifique d'une répétition de sa compatibilité avec le quota et le protocole du TD 1, et indique comment documenter cette limite sans modifier les résultats initiaux.

### Failure diagnosis and evidence consolidation

> Les fichiers de traces et d'état des opérateurs A à E sont maintenant disponibles. Vérifie la couverture des cent couples modèle-question, la conservation des tentatives supplémentaires, la cohérence des `prompt_sha256` pour une même question et la correspondance entre les verdicts et les valeurs de référence. Identifie les étapes restantes avant la consolidation finale.

> Produis le tableau `explanation/explanations-A.csv` à partir des vingt réponses effectivement enregistrées pour GPT-OSS 120B. Pour chaque cellule, justifie le verdict à partir du SQL retourné, du montant calculé et des conventions applicables, en particulier les bornes temporelles et le calcul de l'âge en années révolues.

> Une tentative de synchronisation GitHub a échoué et `git pull` signale un conflit dans `README.md`. Analyse les messages Git et les modifications concurrentes, puis propose une résolution qui conserve les ajouts des différents membres et évite de perdre l'historique ou les artefacts expérimentaux.

### Submission audit, security and individual contribution

> Compare la structure actuelle du dépôt aux critères R1, R2 et R3 ainsi qu'aux consignes de remise. Recherche les éléments insuffisamment justifiés, les écarts entre les fichiers individuels et la synthèse commune, les liens cassés et les informations manquantes. Pour chaque problème, indique une correction vérifiable plutôt qu'une appréciation générale.

> Effectue un audit du dépôt public et de son historique afin d'identifier d'éventuelles clés API exposées, informations sensibles ou fichiers locaux à exclure. Vérifie notamment les règles de `.gitignore` et distingue un secret effectivement divulgué d'un simple nom de variable d'environnement.

> Rédige une note individuelle de contribution fondée sur les références et les traces du rôle A, en distinguant mes actions, l'assistance reçue et les vérifications que j'ai réalisées. Termine par un contrôle des liens et des éléments en attente dans `reports/td1.md`, sans attribuer à mon rôle le travail des autres opérateurs.

## 3. Limits

- The assistant's answers are not reproduced; its contribution is summarised in section 1, and every file it drafted was reviewed before commit.
- Section 2 describes the substance of selected requests in clarified language; it must not be cited as a verbatim transcript.
- No API key, account identifier, e-mail address or local path is reproduced in this file.
