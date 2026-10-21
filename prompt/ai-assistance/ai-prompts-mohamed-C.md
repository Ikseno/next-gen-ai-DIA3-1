# TD 1 — Member C (Mohamed Diawara): AI-assistance prompts and disclosure

**Assigned model:** `openrouter:cohere/north-mini-code:free`  
**Session:** 16 October (preparation) and 21 October 2026 (TD 1)  
**Assistant:** Claude (Anthropic), used in a chat linked to my computer (it could read and write files in my project folders; it never received my API keys).  
**Scope:** personal use of an AI assistant to set up, run, analyse and document TD 1. This file is **not** the prompt sent to the tested models: that prompt is the kit's `build_prompt()` output, unchanged, identical for the five models (see [`prompt/prompts-en.md`](../prompts-en.md) and the `prompt_sha256` column of the traces).

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

## 2. AI-assistance requests — technical reformulations

The following requests are **reformulated summaries** of the assistance sought, written in more precise technical language for readability. They are **not verbatim transcripts** of the original conversation.

### Environment setup and access validation

> À partir du kit officiel du TD 1, établis une procédure de préparation reproductible de l’environnement : version de Python, environnement virtuel, dépendances, intégrité des données et vérification de l’accès aux cinq modèles. Identifie les critères précis permettant de considérer la machine comme opérationnelle.

> Propose un script `setup-td1.sh` qui automatise l’initialisation du projet, l’installation des dépendances et les contrôles d’intégrité. Les clés API doivent rester en dehors des fichiers du dépôt et ne jamais apparaître dans les journaux ni dans les sorties de diagnostic.

> Relance les contrôles d’accès prévus par le kit et distingue les validations locales des appels réseau, afin de connaître le résultat de chaque modèle sans confondre une erreur d’environnement avec un problème de disponibilité du fournisseur.

> Diagnostique l’erreur `missing GROQ_API_KEY` sous zsh : vérifie la saisie de la clé, son export dans l’environnement du processus Python et sa disponibilité dans la session courante, sans afficher sa valeur. Explique l’origine de l’échec et la correction minimale.

### Experimental protocol and subgroup organisation

> Décompose le TD 1 en étapes vérifiables : construction indépendante des 20 références, répartition des modèles, exécution des 100 cellules, conservation des traces par tentative, analyse des verdicts et consolidation des livrables. Précise les dépendances entre étapes et les contraintes de quota et de reproductibilité.

> Avant les appels API, comment répartir les 20 questions de référence entre les sept membres tout en assurant une validation indépendante des requêtes SQL et des montants, avant utilisation des réponses comme valeurs de référence ?

> Construis une répartition explicite des responsabilités pour Mohamed, Dorian, Raphaël, Marc, Alexandre, Maya et Yasmine, en séparant la rédaction des références, la validation croisée, les lots de modèles A à E et la consolidation des fichiers.

> Pour le modèle C hébergé sur OpenRouter, précise la manière dont l’orchestrateur construit la requête à partir du prompt commun, utilise l’identifiant exact du modèle et transmet l’authentification par variable d’environnement. Je veux respecter le protocole sans modifier les messages comparés entre modèles.

### Model C failure analysis

> À partir des traces du modèle C, propose une méthode systématique pour analyser les cas non corrects : distinguer réponse SQL invalide, requête exécutée avec valeur erronée, résultat accidentellement correct et erreur d’accès. Pour chaque cas, l’explication doit être justifiée par le SQL effectivement retourné.

> Comment interpréter rigoureusement la colonne `sql` et comparer la logique de filtrage aux conventions de référence, notamment les intervalles semi-ouverts, l’âge en années révolues, les jointures et le calcul du revenu en centimes ? Propose des vérifications SQLite ciblées pour isoler la cause d’un écart.

> Consigne le diagnostic établi pour cette question dans le tableau d’explications, puis passe au cas suivant en conservant la même méthode de comparaison entre requête générée, référence et trace d’exécution.

> Complète `explanation/explanations-C.csv` avec une ligne par question, y compris les cas corrects. Pour les échecs, indique le mécanisme SQL précis ; pour les succès, vérifie la conformité de la logique et ne te limite pas à la seule égalité numérique lorsque celle-ci peut être fortuite.

### Repository, consistency checks and plenary preparation

> Prépare un espace de travail local à partir du dépôt GitHub commun, afin de consolider les fichiers sans écraser les contributions des autres opérateurs et de préserver la provenance de chaque trace.

> Analyse l’échec de `git pull` : identifie l’état du dépôt, la branche courante et les éventuelles modifications locales avant de proposer une correction qui n’entraîne aucune perte de données.

> Effectue un contrôle de cohérence du dépôt : présence des cinq lots de traces, correspondance des 100 couples modèle-question, conservation des 106 tentatives, unicité du `prompt_sha256` par question, liens entre fichiers et absence de secrets.

> Prépare les éléments documentaires complémentaires du dépôt, notamment un `.gitignore` adapté aux clés et environnements locaux ainsi qu’un `README.md` expliquant la structure du projet, la méthodologie et les commandes de reproduction.

> Vérifie `five-model-summary-en.csv` à partir des traces et du portfolio fourni : exactitude des scores par famille de questions, distinction entre coût observé sur une route gratuite et prix documenté d’une route payante, gestion des mesures manquantes et traçabilité des sources.

> Contrôle le document du prompt expérimental : il doit reproduire fidèlement le message système, le template utilisateur, les conventions, les paramètres de génération et les empreintes permettant de vérifier que les cinq modèles ont reçu des instructions équivalentes.

> Prépare une synthèse de plénière factuelle présentant les résultats des cinq modèles, les familles de questions problématiques, les erreurs SQL récurrentes, les limites des mesures et les conséquences possibles pour le routage et le vote entre modèles au TD 2.

## 3. Limits

- Every explanation is a reading of the trace (returned SQL, value, error field), checked with small SQLite queries; causes are stated as observed in the SQL, not as a claim about the model in general.
- The assistant's network access could not reach the course site or GitHub: downloads, `git pull` and `git push` were done by me.
