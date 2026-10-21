# TD 1 — Individual contribution: Yasmine Boukrouh (role H)

**Student:** Yasmine Boukrouh  
**Work:** Individual contribution to TD 1  
**Module:** Next-Generation AI / Trustworthy Generative AI, ESILV  
**Session:** 21 October 2026  
**Repository:** [next-gen-ai-DIA3-1](https://github.com/Ikseno/next-gen-ai-DIA3-1)

## Scope of this note

This note has two parts that must not be confused:

1. **My role in the group's deliverables** (role H): references C14 and C19, the five-model summary [`results/five-model-summary-en.csv`](../results/five-model-summary-en.csv) (uploaded to the repository by Alexandre), and the cross-check of Mohamed's references (C01, C02, C15). The figures of the group report ([`td1.md`](td1.md)) come from the group's five batches A–E, run by their operators.
2. **A separate local experiment** that I ran alone, described below. It is **not** the group's experiment and its figures are **not** used in the group's deliverables: it used a runner modified with Codex, the same OpenRouter account for batches C and E, and it met HTTP 401/403 failures on batch A. Its files are kept in the repository history (commit [`3b0a489`](https://github.com/Ikseno/next-gen-ai-DIA3-1/tree/3b0a4894b6e778a91ceee3df4d93f43680e10069/td1-local-run), folder `td1-local-run/`) and were removed from the current tree so that the deliverables describe one experiment.

What the separate run brings to the group: an **independent recomputation of the 20 references** (my own SQL and a CSV-based check), whose 20 values are identical to the group's [`reference-td1.csv`](../reference-td1.csv), and a second measurement of the same models showing that results change between runs at temperature 0 (see section 5 of the group report).

## The separate local experiment

I prepared my Windows environment and ran a local experiment comparing five free language models on the same twenty SQL revenue questions. I used Codex to help prepare code, explain queries, diagnose errors and assemble the results. This report describes my own local work; it does not claim that I performed the other members' work recorded elsewhere in the shared repository.

## Environment preparation

I used my existing Python 3.13.9 virtual environment. I downloaded the student kit, created Groq and OpenRouter accounts, and entered API keys through hidden PowerShell prompts. I ran the access check and obtained successful local integrity checks and access to all five models. I kept credentials out of the uploaded files.

I organised my working files under `ESILV-Trustworthy-AI`, with the experiment files in `td1` and reports in `reports`. I learned that closing PowerShell preserves files but removes API keys set only for that process. I also corrected working-directory and command-pasting mistakes while learning the workflow.

## Reference calculations

 I prepared twenty reference SQL queries and a separate CSV-based calculation. The queries were executed read-only on the supplied database, and all twenty amounts matched the CSV calculation. The two implementations share their case definitions, so this agreement does not replace an independent review of how the questions were interpreted.

The reference review covered integer revenue in cents excluding VAT, inclusive start and exclusive end dates, completed age on a reference date versus age at the time of an order, and filtering individual product lines.

Update after consolidation: my 20 values are identical to the group's references and to Dorian's independent CSV recomputation. Comparison with the instructor's answer key is recorded in the group report.

## Model batches of the separate run (not the group's figures)

I launched all five batches from PowerShell, using the supplied model configuration and the same prompt for each question across models.

| Batch | Model | Correct out of 20 |
|---|---|---:|
| A | GPT-OSS 120B on Groq | 17 |
| B | GPT-OSS 20B on Groq | 17 |
| C | Cohere North Mini Code on OpenRouter | 12 |
| D | Qwen 3.8 27B on Groq | 15 |
| E | Dots 3 Note Preview on OpenRouter | 10 |

The experiment produced 123 recorded batch attempts: 100 initial attempts and 23 second attempts. The 100 final cells comprise 71 correct answers, 27 incorrect answers, one invalid SQL response and one question blocked by rate limits. These are results from this dataset and this run, not a general model ranking.

## Troubleshooting and evidence

During batch A, I encountered seventeen HTTP 403 access failures and two HTTP 401 invalid-key failures. After correcting access and key entry, I recovered those cells using an explicit second attempt. Codex modified the runner to support this recovery while retaining the original records and the maximum of two attempts per cell. It also added a stop-on-access-failure option and improved the launcher so that a key could be reused within the same PowerShell session.

Batch D encountered five HTTP 429 responses across four questions. Some succeeded on their second attempt, but C18 remained blocked after both permitted attempts. I retained that cell as not executed rather than claiming a model answer or making further attempts.

I kept the original per-batch CSV and JSONL logs, including failures. In the public upload, organisation identifiers in API error messages were redacted; SQL and numerical measurements were preserved. The batch totals exclude setup checks; I did not maintain a complete setup-call count or before-and-after allowance record.

## What I observed

All five models answered the six pure-period and four product-family questions correctly. Most incorrect answers concerned age or combined filters.

For example, GPT-OSS 120B used an exact birthday condition for C15, C17 and C19. Customers aged 25 on a date span a full birth-date interval; they are not limited to customers whose 25th birthday falls on that exact day. GPT-OSS 20B also produced incorrect birth-date ranges on three questions.

Qwen's failures included contradictory age predicates and incorrect birthday boundaries. Cohere sometimes added an order-date restriction that the question did not request. Dots produced malformed CAST syntax on C08 and several age filters that omitted valid customers.

I learned to distinguish a valid SQL query with the wrong meaning, invalid SQL, and provider access or rate-limit failures. A zero result is not automatically correct: it must be checked against the independently computed reference.

## Files and GitHub contribution

 I assembled the reference file, all raw attempts, the final comparison CSV, the model summary, a models-by-questions view, the prompt used and a report draft. An offline re-execution check reproduced the saved verdicts for all 99 final responses that received model output, without additional API calls.

I signed in through GitHub CLI and ran the upload script. My local experiment was added under `td1-local-run/`, preserving the group's existing files. The verified upload commit is [`3b0a4894b6e778a91ceee3df4d93f43680e10069`](https://github.com/Ikseno/next-gen-ai-DIA3-1/commit/3b0a4894b6e778a91ceee3df4d93f43680e10069).

Evidence from that upload:

- [Reference SQL and amounts](https://github.com/Ikseno/next-gen-ai-DIA3-1/blob/3b0a4894b6e778a91ceee3df4d93f43680e10069/td1-local-run/td1/reference-td1.csv)
- [All recorded attempts](https://github.com/Ikseno/next-gen-ai-DIA3-1/blob/3b0a4894b6e778a91ceee3df4d93f43680e10069/td1-local-run/td1/traces-td1.csv)
- [Final comparisons and explanations](https://github.com/Ikseno/next-gen-ai-DIA3-1/blob/3b0a4894b6e778a91ceee3df4d93f43680e10069/td1-local-run/td1/model-question-comparison-en.csv)
- [Comparison view](https://github.com/Ikseno/next-gen-ai-DIA3-1/blob/3b0a4894b6e778a91ceee3df4d93f43680e10069/td1-local-run/td1/comparison-view.md)
- [Prompt used](https://github.com/Ikseno/next-gen-ai-DIA3-1/blob/3b0a4894b6e778a91ceee3df4d93f43680e10069/td1-local-run/td1/prompt-used.md)

## Limits and work still pending

I ran the two OpenRouter batches using the same personal account. This differs from the course allocation requiring two different members' accounts; no instructor exception is claimed.

The model summary uses historical course-portfolio metadata. Entries without a documented exact-model index or paid route remain N/A with reasons. This does not establish that no paid route exists, and current metadata review remains pending.

Reconciliation with the group's work is done: the separate run is documented in section 5 of the group report and kept in the repository history; the group's deliverables use only batches A–E run by their operators. This individual report supplements the shared session report and does not replace it.



I drafted the reference queries, CSV cross-check, launcher changes, consolidation, explanations and this individual report. I ran the setup and model commands, provided the outputs, worked through the troubleshooting and performed the GitHub upload. I do not claim to have independently authored all the generated code or independently validated every interpretation. I remain responsible for reviewing and explaining the work I submit.
