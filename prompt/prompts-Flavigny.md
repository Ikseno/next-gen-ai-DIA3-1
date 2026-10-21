# TD 1 — Member E: Prompts and supporting evidence

**Model tested:** `openrouter:dots-studio/dots-3-note-preview:free`  
**Session:** 21 October 2026

## 1. Experimental prompts

The exact **system prompt** and **user prompt template** used for Model E are already documented in the subgroup's [`prompts-en.md`](./prompts-en.md). The same prompts were used for all five models, without changes. The script `skeleton-multi-llm-en.py` inserts the database schema and each question into the user template.

The `prompt_sha256` field in the raw traces identifies the exact rendered prompt for each question.

## 2. Examples of assistance prompts

These are examples of actual questions asked while working on Model E:

> Before doing 20 questions what are the files where are they how do I interpret this

> Okay is that enough for you ? are you capable of seeing the wrong answers and make an explanation on all the incorrect ones (for the correct ones the explanation is just "The SQL Query is Correct") ?

> so I put traces, is the format of my traces correct ? And then I put the model E comparison I don't think the others are quite important they're not asked for right

> in five-model-summary it talks about pricing and stuff do we have access to this information ? Does model-question-comparison-en have this information or not ?

## 3. Evidence and verification

- **Raw experiment:** `traces-E.csv` and `state-E.jsonl` record the actual Model E API attempts and SQL outputs.
- **Comparison:** `model-question-comparison-E.csv` records the final verdict and explanation for each of the 20 questions.
- **Result:** 15 correct out of 20 questions (75%); the five incorrect cases are C08, C09, C10, C16 and C18.
- **Verification method — manual and AI-assisted:** I personally performed manual verification of the SQL queries, numerical results and failure explanations by reviewing the generated SQL, the reference queries, the recorded traces and the outputs against `reference-td1.csv`. In addition, AI-assisted cross-checking was used to help identify possible mistakes and review explanations. **The verification was not AI-only: I performed my own checks as well.**
- **Assistance disclosure:** AI assistance was used in preparing or reviewing reference-query approaches, interpreting traces and drafting explanations. The final checking included my own manual verification. The recorded model evaluations themselves were made using the course script and the assigned model API, not an assistant-generated simulation.

This note supplements the subgroup's shared experimental prompt document; it does not replace it.
